import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.data import books, members, borrowings

client = TestClient(app)


@pytest.fixture
def reset_data():
    """Restore the in-memory data after each test."""
    original_books = [book.copy() for book in books]
    original_members = [member.copy() for member in members]
    original_borrowings = [borrowing.copy() for borrowing in borrowings]

    yield

    books.clear()
    books.extend(original_books)

    members.clear()
    members.extend(original_members)

    borrowings.clear()
    borrowings.extend(original_borrowings)


def test_get_borrowings():
    """Should return all borrowing records."""
    response = client.get("/borrowings/")

    assert response.status_code == 200
    assert len(response.json()) == len(borrowings)


def test_get_borrowing_success():
    """Should return an existing borrowing."""
    response = client.get("/borrowings/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_borrowing_not_found():
    """Should return 404 when the borrowing does not exist."""
    response = client.get("/borrowings/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Borrowing not found."
    }


def test_create_borrowing_success(reset_data):
    """Should create a borrowing for an available book."""
    payload = {
        "book_id": 2,
        "member_id": 1
    }

    response = client.post("/borrowings/", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["book_id"] == 2
    assert body["member_id"] == 1
    assert body["return_date"] is None
    assert body["fine"] is None
    assert "borrow_date" in body
    assert "due_date" in body
    assert "id" in body


def test_create_borrowing_book_not_found(reset_data):
    """Should return 404 when the requested book does not exist."""
    payload = {
        "book_id": 999,
        "member_id": 1
    }

    response = client.post("/borrowings/", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Book not found."
    }


def test_create_borrowing_member_not_found(reset_data):
    """Should return 404 when the member does not exist."""
    payload = {
        "book_id": 2,
        "member_id": 999
    }

    response = client.post("/borrowings/", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Member not found."
    }


def test_create_borrowing_inactive_member(reset_data):
    """Should reject borrowing requests from inactive members."""
    payload = {
        "book_id": 2,
        "member_id": 3  # inactive in sample data
    }

    response = client.post("/borrowings/", json=payload)

    assert response.status_code == 400
    assert "not no longer an active member" in response.json()["detail"]


def test_create_borrowing_book_already_borrowed(reset_data):
    """Should reject borrowing a book that is currently on loan."""
    payload = {
        "book_id": 3,  # active borrowing in sample data
        "member_id": 1
    }

    response = client.post("/borrowings/", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Book is already borrowed."
    }


def test_return_book_success(reset_data):
    """Should successfully return a borrowed book."""
    response = client.patch("/borrowings/2")

    assert response.status_code == 200

    body = response.json()

    assert body["return_date"] is not None
    assert body["fine"] >= 0


def test_return_book_not_found(reset_data):
    """Should return 404 for a non-existent borrowing."""
    response = client.patch("/borrowings/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Borrowing does not exist."
    }


def test_return_book_already_returned(reset_data):
    """Should reject returning a book that has already been returned."""
    response = client.patch("/borrowings/1")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Book has already been returned."
    }


def test_return_book_calculates_fine(reset_data):
    """Should calculate a fine for overdue returns."""
    borrowing = next(b for b in borrowings if b["id"] == 2)

    # Force the borrowing to be overdue
    borrowing["due_date"] = borrowing["borrow_date"]

    response = client.patch("/borrowings/2")

    assert response.status_code == 200
    assert response.json()["fine"] > 0
