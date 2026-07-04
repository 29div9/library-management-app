import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.data import books

client = TestClient(app)


@pytest.fixture
def reset_books():
    """Restore the in-memory books list after each test."""
    original = [book.copy() for book in books]
    yield
    books.clear()
    books.extend(original)


def test_get_books():
    response = client.get("/books/")

    assert response.status_code == 200
    assert len(response.json()) == len(books)


def test_get_book_success():
    response = client.get("/books/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_book_not_found():
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}


def test_create_book_success(reset_books):
    payload = {
        "name": "Refactoring",
        "author": "Martin Fowler",
        "publisher": "Addison-Wesley",
        "genre": "Programming",
    }

    response = client.post("/books/", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == payload["name"]
    assert body["author"] == payload["author"]
    assert body["publisher"] == payload["publisher"]
    assert body["genre"] == payload["genre"]
    assert "id" in body


def test_create_duplicate_book(reset_books):
    payload = {
        "name": books[0]["name"],
        "author": books[0]["author"],
        "publisher": books[0]["publisher"],
        "genre": books[0]["genre"],
    }

    response = client.post("/books/", json=payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "Book already exists."}


def test_patch_book_success(reset_books):
    payload = {"genre": "Computer Science"}

    response = client.patch("/books/1", json=payload)

    assert response.status_code == 200
    assert response.json()["genre"] == "Computer Science"


def test_patch_book_not_found(reset_books):
    payload = {"genre": "Computer Science"}

    response = client.patch("/books/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}


def test_patch_book_empty_body(reset_books):
    response = client.patch("/books/1", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "At least one field must be provided."}


def test_delete_book_success(reset_books):
    response = client.delete("/books/2")

    assert response.status_code == 204

    response = client.get("/books/2")
    assert response.status_code == 404


def test_delete_book_not_found(reset_books):
    response = client.delete("/books/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}
