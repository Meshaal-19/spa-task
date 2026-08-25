import pytest


async def test_register(client):
    resp = await client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
    assert resp.status_code == 201


async def test_register_duplicate(client):
    payload = {"username": "dupuser", "password": "pass123"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 400


async def test_login_success(client):
    await client.post("/auth/register", json={"username": "loginuser", "password": "pass123"})
    resp = await client.post("/auth/login", json={"username": "loginuser", "password": "pass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"username": "wrongpass", "password": "correct"})
    resp = await client.post("/auth/login", json={"username": "wrongpass", "password": "wrong"})
    assert resp.status_code == 401


async def test_get_processes_no_auth(client):
    resp = await client.get("/processes")
    assert resp.status_code == 401


async def test_get_processes_with_auth(client, auth_headers):
    resp = await client.get("/processes", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_anomalies(client, auth_headers):
    resp = await client.get("/anomalies", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_investigate_requires_auth(client):
    resp = await client.post("/investigations/999")
    assert resp.status_code == 401
