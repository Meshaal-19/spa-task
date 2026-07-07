"""
Full happy-path integration test.

Exercises the real request/response cycle end-to-end:
register → login → create note → fetch note
Each step asserts its own status code and shape before passing data to the next.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt


def _get_token(client, *, name="Carol", email="carol@example.com", password="pass1234"):
    """Register a user and return their access token."""
    client.post("/auth/register", json={"name": name, "email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    return resp.json()["access_token"]


def test_register_login_create_fetch(client):
    # 1. Register a new user
    register_response = client.post(
        "/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "pass1234"},
    )
    assert register_response.status_code == 201
    user = register_response.json()
    assert user["email"] == "carol@example.com"
    assert "id" in user

    # 2. Login to get a JWT access token
    login_response = client.post(
        "/auth/login",
        data={"username": "carol@example.com", "password": "pass1234"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # 3. Create a note using the token
    create_response = client.post(
        "/notes/",
        json={"title": "Integration note", "body": "Created during integration test"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    note = create_response.json()
    assert note["title"] == "Integration note"
    assert note["body"] == "Created during integration test"
    assert note["user_id"] == user["id"]
    note_id = note["id"]

    # 4. Fetch that specific note back
    fetch_response = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["id"] == note_id
    assert fetched["title"] == "Integration note"
    assert fetched["user_id"] == user["id"]


def test_expired_token_is_rejected(client):
    from auth import ALGORITHM, SECRET_KEY

    expired_token = jwt.encode(
        {"sub": "999", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    resp = client.get("/notes/", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_invalid_token_is_rejected(client):
    resp = client.get("/notes/", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401
