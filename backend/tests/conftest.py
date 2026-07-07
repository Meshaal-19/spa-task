import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from models import User

TEST_DATABASE_URL = "sqlite:///./test.db"


def _make_engine(url: str):
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


engine = _make_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(reset_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client):
    """A TestClient whose user has is_admin=True, set directly in the DB."""
    client.post(
        "/auth/register",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "secret123",
        },
    )
    # Flip is_admin directly — there is intentionally no public API for this
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@example.com").first()
        user.is_admin = True
        db.commit()
    finally:
        db.close()

    token = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "secret123"},
    ).json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def auth_client(client):
    """A TestClient pre-loaded with a registered user's Bearer token."""
    client.post(
        "/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )
    token_response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "secret123"},
    )
    token = token_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
