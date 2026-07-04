"""
Full happy-path integration test.

Exercises the real request/response cycle end-to-end:
register → login → create note → fetch note
Each step asserts its own status code and shape before passing data to the next.
"""


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
