def test_create_note(client, user):
    response = client.post(
        "/notes/",
        json={"title": "First note", "body": "Hello world", "user_id": user["id"]},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "First note"
    assert data["body"] == "Hello world"
    assert data["user_id"] == user["id"]
    assert "id" in data


def test_get_all_notes(client, user):
    client.post("/notes/", json={"title": "Note A", "body": "", "user_id": user["id"]})
    client.post("/notes/", json={"title": "Note B", "body": "", "user_id": user["id"]})

    response = client.get("/notes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_one_note(client, user):
    created = client.post(
        "/notes/", json={"title": "Fetch me", "body": "body", "user_id": user["id"]}
    ).json()

    response = client.get(f"/notes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fetch me"


def test_update_note(client, user):
    created = client.post(
        "/notes/", json={"title": "Old title", "body": "old", "user_id": user["id"]}
    ).json()

    response = client.put(
        f"/notes/{created['id']}", json={"title": "New title", "body": "new"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["body"] == "new"


def test_delete_note(client, user):
    created = client.post(
        "/notes/", json={"title": "Delete me", "body": "", "user_id": user["id"]}
    ).json()

    response = client.delete(f"/notes/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/notes/{created['id']}")
    assert response.status_code == 404


def test_get_note_404(client):
    response = client.get("/notes/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
