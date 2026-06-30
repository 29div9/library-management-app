from fastapi import APIRouter, HTTPException, Response, status
from schemas.book import BookCreate, BookUpdate, BookResponse
from data import books

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookResponse])
def get_books():
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    book_found = next(
        (existing_book for existing_book in books if existing_book["id"] == book_id),
        None,
    )
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )
    return book_found


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_book = book.model_dump()
    # Check if book already exists
    for existing_book in books:
        if (
            existing_book["name"] == new_book["name"]
            and existing_book["author"] == new_book["author"]
            and existing_book["publisher"] == new_book["publisher"]
            and existing_book["genre"] == new_book["genre"]
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Book already exists."
            )
    new_book["id"] = len(books) + 1
    books.append(new_book)
    return new_book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookUpdate):
    book_found = next(
        (existing_book for existing_book in books if existing_book["id"] == book_id),
        None,
    )
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    update = book.model_dump(
        exclude_unset=True
    )  # only include fields that user sent in request

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided.",
        )

    for key, value in update.items():
        book_found[key] = value

    return book_found


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    book_found = next((book for book in books if book["id"] == book_id), None)
    if book_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )
    books.remove(book_found)
    return Response()
