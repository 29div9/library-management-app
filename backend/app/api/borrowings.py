from datetime import datetime, timedelta
from typing import cast
from fastapi import APIRouter, HTTPException, status
from app.schemas.borrowing import BorrowingCreate, BorrowingResponse
from app.data import books, borrowings, members

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])


@router.get("/", response_model=list[BorrowingResponse])
def get_borrowings():
    """Retrieve all borrowings"""
    return borrowings


@router.get("/{borrowing_id}", response_model=BorrowingResponse)
def get_borrowing(borrowing_id: int):
    """Retrieve a borrowing by its ID"""
    borrowing_found = next(
        (
            existing_borrowing
            for existing_borrowing in borrowings
            if existing_borrowing["id"] == borrowing_id
        ),
        None,
    )
    if borrowing_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing not found."
        )
    return borrowing_found


@router.post("/", response_model=BorrowingResponse, status_code=status.HTTP_201_CREATED)
def create_borrowing(borrowing: BorrowingCreate):
    """Add entry for a new borrowing.
    It also checks if the book is already borrowed before creating borrowing.
    """
    new_borrowing = borrowing.model_dump()
    # check if library has the book
    book_found = next(
        (book for book in books if book["id"] == new_borrowing["book_id"]),
        None,
    )
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )

    # check if member exists
    member_found = next(
        (member for member in members if member["id"] == new_borrowing["member_id"]),
        None,
    )
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    # check if member is active
    if not member_found["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{member_found['name']} is not no longer an active member.",
        )

    # check if requested book is not currently borrowed by someone
    active_borrowing = next(
        (
            active_borrowing
            for active_borrowing in borrowings
            if active_borrowing["book_id"] == new_borrowing["book_id"]
            and active_borrowing["return_date"] is None
        ),
        None,
    )

    if active_borrowing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Book is already borrowed."
        )
    new_borrowing["id"] = len(borrowings) + 1
    new_borrowing["borrow_date"] = datetime.now()
    new_borrowing["return_date"] = None
    new_borrowing["due_date"] = new_borrowing["borrow_date"] + timedelta(days=14)
    new_borrowing["fine"] = None

    borrowings.append(new_borrowing)

    return new_borrowing


@router.patch("/{borrowing_id}", response_model=BorrowingResponse)
def update_borrowing(borrowing_id: int):
    """Update the return date for a book.
    It also calculates fine if the return date is after due date
    """
    # check if borrowing exists
    active_borrowing = next(
        (
            active_borrowing
            for active_borrowing in borrowings
            if active_borrowing["id"] == borrowing_id
        ),
        None,
    )

    if active_borrowing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing does not exist."
        )
    if active_borrowing["return_date"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book has already been returned.",
        )

    return_date = datetime.now()
    active_borrowing["return_date"] = return_date

    due_date = cast(datetime, active_borrowing["due_date"])  # explicit casting for mypy

    if return_date > due_date:
        days = (return_date.date() - due_date.date()).days
        fine = days * 10
    else:
        fine = 0

    active_borrowing["fine"] = fine

    return active_borrowing
