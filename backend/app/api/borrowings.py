from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.borrowing import BorrowingCreate, BorrowingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.book import Book
from backend.app.models.borrowing import Borrowing
from backend.app.models.member import Member

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])


@router.get("/", response_model=list[BorrowingResponse])
def get_borrowings(db: Session = Depends(get_db)):
    """Retrieve all borrowings"""
    return db.scalars(select(Borrowing)).all()


@router.get("/{borrowing_id}", response_model=BorrowingResponse)
def get_borrowing(borrowing_id: int, db: Session = Depends(get_db)):
    """Retrieve a borrowing by its ID"""

    borrowing_found = db.scalar(select(Borrowing).where(Borrowing.id == borrowing_id))
    if borrowing_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing not found."
        )
    return borrowing_found


@router.post("/", response_model=BorrowingResponse, status_code=status.HTTP_201_CREATED)
def create_borrowing(borrowing: BorrowingCreate, db: Session = Depends(get_db)):
    """Add entry for a new borrowing.
    It also checks if the book is already borrowed before creating borrowing.
    """

    book_found = db.scalar(select(Book).where(Book.id == borrowing.book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )

    # check if member exists
    member_found = db.scalar(select(Member).where(Member.id == borrowing.member_id))
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    # check if member is active
    if not member_found.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{member_found.name} is not no longer an active member.",
        )

    # check if requested book is not currently borrowed by someone
    active_borrowing = db.scalar(
        select(Borrowing).where(
            Borrowing.book_id == borrowing.book_id,
            Borrowing.return_date.is_(None),
        )
    )

    if active_borrowing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Book is already borrowed."
        )

    # set borrow_date to later set due_date
    borrow_date = datetime.now()

    borrowing_db = Borrowing(
        book_id=borrowing.book_id,
        member_id=borrowing.member_id,
        borrow_date=borrow_date,
        return_date=None,
        due_date=borrow_date + timedelta(days=14),
        fine=None,
    )
    db.add(borrowing_db)
    db.commit()
    db.refresh(borrowing_db)

    return borrowing_db


@router.patch("/{borrowing_id}/return", response_model=BorrowingResponse)
def update_borrowing(borrowing_id: int, db: Session = Depends(get_db)):
    """Update the return date for a book.
    It also calculates fine if the return date is after due date
    """

    active_borrowing = db.scalar(
        select(Borrowing).where(
            Borrowing.id == borrowing_id,
        )
    )

    if active_borrowing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing does not exist."
        )
    if active_borrowing.return_date:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book has already been returned.",
        )

    return_date = datetime.now()
    active_borrowing.return_date = return_date

    due_date = active_borrowing.due_date

    if return_date > due_date:
        days = (return_date.date() - due_date.date()).days
        fine = days * 10
    else:
        fine = 0

    active_borrowing.fine = fine
    db.commit()
    db.refresh(active_borrowing)

    return active_borrowing


@router.get("/overdue", response_model=list[BorrowingResponse])
def get_overdue_borrowings(db: Session = Depends(get_db)):
    """Retrieve borrowings which are past their due date"""

    today = datetime.now()
    return db.scalars(
        select(Borrowing).where(
            Borrowing.return_date.is_(None),
            today > Borrowing.due_date
        )
        .order_by(Borrowing.due_date)
    ).all()


@router.get("/active", response_model=list[BorrowingResponse])
def get_active_borrowings(db: Session = Depends(get_db)):
    """Retrieve all active borrowings"""

    return db.scalars(
        select(Borrowing).where(
            Borrowing.return_date.is_(None),
        )
        .order_by(Borrowing.due_date)
    ).all()
