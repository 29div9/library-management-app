from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.book import BookCreate, BookUpdate, BookResponse
from backend.app.schemas.borrowing import BorrowingResponse
from backend.app.schemas.member import MemberResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.book import Book
from backend.app.models.borrowing import Borrowing
from backend.app.models.member import Member

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    """Retrieve all books in the library"""
    return db.scalars(select(Book)).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve a book by its ID"""
    book_found = db.scalar(select(Book).where(Book.id == book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )
    return book_found


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Add a new book to the library"""

    # Check if book already exists
    existing_book = db.scalar(
        select(Book).where(
            Book.name == book.name,
            Book.author == book.author,
            Book.publisher == book.publisher,
            Book.genre == book.genre,
        )
    )
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Book already exists."
        )

    book_db = Book(
        name=book.name,
        author=book.author,
        publisher=book.publisher,
        genre=book.genre,
    )
    db.add(book_db)
    db.commit()
    db.refresh(book_db)

    return book_db


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Update one or more fields of an existing book"""

    book_found = db.scalar(select(Book).where(Book.id == book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    updates = book.model_dump(
        exclude_unset=True
    )  # only include fields that user sent in request

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided.",
        )

    # Check if this new update is not a duplicate of an existing book
    # also, user might not be updating all fields
    # hence, get the ones that they are updating and
    # fetch the rest of the fields from found_book
    updated_name = updates.get("name", book_found.name)
    updated_author = updates.get("author", book_found.author)
    updated_publisher = updates.get("publisher", book_found.publisher)
    updated_genre = updates.get("genre", book_found.genre)

    duplicate_book = db.scalar(
        select(Book).where(
            Book.name == updated_name,
            Book.author == updated_author,
            Book.publisher == updated_publisher,
            Book.genre == updated_genre,
            Book.id != book_id,
        )
    )

    if duplicate_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A book with same details already exist.",
        )

    for key, value in updates.items():
        setattr(book_found, key, value)

    db.commit()
    db.refresh(book_found)

    return book_found


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book from the library"""
    book_found = db.scalar(select(Book).where(Book.id == book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    # If the book is currently borrowed, referential integrity will fail
    # rollback and raise error
    try:
        db.delete(book_found)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book because it has borrowing records.",
        )


@router.get("/{book_id}/borrowings", response_model=list[BorrowingResponse])
def get_book_borrowings(book_id: int, db: Session = Depends(get_db)):
    """Retrieve the borrowing history of a book, newest first"""
    book_found = db.scalar(select(Book).where(Book.id == book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    return db.scalars(
        select(Borrowing).where(
            Borrowing.book_id == book_id
        )
        .order_by(Borrowing.borrow_date.desc())
    ).all()


@router.get("/{book_id}/current-borrower", response_model=MemberResponse)
def get_book_current_borrower(book_id: int, db: Session = Depends(get_db)):
    """Retrieve the current borrower of a book"""
    book_found = db.scalar(select(Book).where(Book.id == book_id))
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    return db.scalar(
        select(Member)
        .join(Borrowing, Borrowing.member_id == Member.id)
        .where(
            Borrowing.book_id == book_id,
            Borrowing.return_date.is_(None),
        )
    )
