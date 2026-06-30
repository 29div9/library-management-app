import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.data import members

client = TestClient(app)


@pytest.fixture
def reset_members():
    """Restore the in-memory members list after each test."""
    original = [member.copy() for member in members]
    yield
    members.clear()
    members.extend(original)


def test_get_members():
    """Should return all library members."""
    response = client.get("/members/")

    assert response.status_code == 200
    assert len(response.json()) == len(members)


def test_get_member_success():
    """Should return an existing member."""
    response = client.get("/members/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_member_not_found():
    """Should return 404 when the member does not exist."""
    response = client.get("/members/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Member not found."
    }


def test_create_member_success(reset_members):
    """Should create a new library member."""
    payload = {
        "name": "John Doe",
        "contact": "9876501234",
        "address": "221B Baker Street"
    }

    response = client.post("/members/", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == payload["name"]
    assert body["contact"] == payload["contact"]
    assert body["address"] == payload["address"]
    assert body["is_active"] is True
    assert body["exit_date"] is None
    assert "joining_date" in body
    assert "id" in body


def test_create_member_duplicate_contact(reset_members):
    """Should return 409 when the contact number already exists."""
    payload = {
        "name": "Another User",
        "contact": members[0]["contact"],
        "address": "Some Address"
    }

    response = client.post("/members/", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Contact number already exists."
    }


def test_patch_member_success(reset_members):
    """Should update a member's address."""
    payload = {
        "address": "New Address"
    }

    response = client.patch("/members/1", json=payload)

    assert response.status_code == 200
    assert response.json()["address"] == "New Address"


def test_patch_member_contact_success(reset_members):
    """Should update a member's contact number."""
    payload = {
        "contact": "9999999999"
    }

    response = client.patch("/members/1", json=payload)

    assert response.status_code == 200
    assert response.json()["contact"] == "9999999999"


def test_patch_member_duplicate_contact(reset_members):
    """Should reject updating to an existing contact number."""
    payload = {
        "contact": members[1]["contact"]
    }

    response = client.patch("/members/1", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Contact number already exists."
    }


def test_patch_member_not_found(reset_members):
    """Should return 404 when updating a non-existent member."""
    payload = {
        "address": "New Address"
    }

    response = client.patch("/members/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Member not found."
    }


def test_patch_member_empty_body(reset_members):
    """Should reject an empty PATCH request."""
    response = client.patch("/members/1", json={})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "At least one field must be provided."
    }


def test_delete_member_success(reset_members):
    """Should delete an existing member."""
    response = client.delete("/members/1")

    assert response.status_code == 204

    response = client.get("/members/1")
    assert response.status_code == 404


def test_delete_member_not_found(reset_members):
    """Should return 404 when deleting a non-existent member."""
    response = client.delete("/members/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Member not found."
    }
