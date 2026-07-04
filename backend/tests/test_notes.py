def test_create_note(auth_client):
    response = auth_client.post(
        "/notes/", json={"title": "First note", "body": "Hello world"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "First note"
    assert data["body"] == "Hello world"
    assert "id" in data
    assert "user_id" in data


def test_get_all_notes(auth_client):
    auth_client.post("/notes/", json={"title": "Note A", "body": ""})
    auth_client.post("/notes/", json={"title": "Note B", "body": ""})

    response = auth_client.get("/notes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_one_note(auth_client):
    created = auth_client.post(
        "/notes/", json={"title": "Fetch me", "body": "body"}
    ).json()

    response = auth_client.get(f"/notes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fetch me"


def test_update_note(auth_client):
    created = auth_client.post(
        "/notes/", json={"title": "Old title", "body": "old"}
    ).json()

    response = auth_client.put(
        f"/notes/{created['id']}", json={"title": "New title", "body": "new"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["body"] == "new"


def test_delete_note(auth_client):
    created = auth_client.post(
        "/notes/", json={"title": "Delete me", "body": ""}
    ).json()

    response = auth_client.delete(f"/notes/{created['id']}")
    assert response.status_code == 204

    response = auth_client.get(f"/notes/{created['id']}")
    assert response.status_code == 404


def test_get_note_404(auth_client):
    response = auth_client.get("/notes/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_unauthenticated_request_is_rejected(client):
    response = client.get("/notes/")
    assert response.status_code == 401


def test_user_cannot_access_another_users_note(client):
    # Register and login as Alice
    client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
    )
    alice_token = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "secret123"},
    ).json()["access_token"]

    # Alice creates a note
    note = client.post(
        "/notes/",
        json={"title": "Alice's note", "body": "private"},
        headers={"Authorization": f"Bearer {alice_token}"},
    ).json()

    # Register and login as Bob
    client.post(
        "/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    bob_token = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "secret123"},
    ).json()["access_token"]

    # Bob tries to read Alice's note — should get 404
    response = client.get(
        f"/notes/{note['id']}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert response.status_code == 404


def test_admin_can_list_all_notes(admin_client, client):
    # Create a second user with their own note
    client.post(
        "/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret123"},
    )
    bob_token = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "secret123"},
    ).json()["access_token"]
    client.post(
        "/notes/",
        json={"title": "Bob's note", "body": ""},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # Admin creates their own note
    admin_client.post("/notes/", json={"title": "Admin note", "body": ""})

    # Admin should see both notes via /notes/all
    response = admin_client.get("/notes/all")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_non_admin_cannot_access_notes_all(auth_client):
    response = auth_client.get("/notes/all")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
