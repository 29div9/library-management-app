from fastapi import APIRouter, HTTPException, Response, status
from schemas.book import BookCreate, BookUpdate, BookResponse

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

books = [
    {
        "id": 1,
        "name": "Clean Code",
        "author": "Robert C. Martin",
        "publisher": "Prentice Hall",
        "genre": "Programming"
    },
    {
        "id": 2,
        "name": "The Pragmatic Programmer",
        "author": "Andrew Hunt, David Thomas",
        "publisher": "Addison-Wesley",
        "genre": "Programming"
    },
    {
        "id": 3,
        "name": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "publisher": "Addison-Wesley",
        "genre": "Software Engineering"
    },
    {
        "id": 4,
        "name": "Python Crash Course",
        "author": "Eric Matthes",
        "publisher": "No Starch Press",
        "genre": "Programming"
    },
    {
        "id": 5,
        "name": "Atomic Habits",
        "author": "James Clear",
        "publisher": "Avery",
        "genre": "Self-Help"
    },
    {
        "id": 6,
        "name": "The Alchemist",
        "author": "Paulo Coelho",
        "publisher": "HarperOne",
        "genre": "Fiction"
    },
    {
        "id": 7,
        "name": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "publisher": "J. B. Lippincott & Co.",
        "genre": "Fiction"
    },
    {
        "id": 8,
        "name": "1984",
        "author": "George Orwell",
        "publisher": "Secker & Warburg",
        "genre": "Fiction"
    },
    {
        "id": 9,
        "name": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "publisher": "George Allen & Unwin",
        "genre": "Fantasy"
    },
    {
        "id": 10,
        "name": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "publisher": "Harper",
        "genre": "History"
    },
]


@router.get("/", response_model=list[BookResponse])
def get_books():
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    book_found = next(
        (existing_book for existing_book in books if existing_book["id"] == book_id),
        None
    )
    if book_found is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found.",
        )
    return book_found


@router.post(
    "/",
    response_model=BookResponse,
    status_code=201
)
def create_book(book: BookCreate):
    new_book = book.model_dump()
    # Check if book already exists
    for existing_book in books:
        if (
                existing_book["name"] == new_book["name"] and
                existing_book["author"] == new_book["author"] and
                existing_book["publisher"] == new_book["publisher"] and
                existing_book["genre"] == new_book["genre"]
        ):
            raise HTTPException(
                status=409,
                detail="Book already exists."
            )
    new_book["id"] = len(books) + 1
    books.append(new_book)
    return new_book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookUpdate):
    update = book.model_dump(exclude_unset=True)  # only include fields that user sent in request

    if not update:
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided."
        )

    book_found = next(
        (existing_book for existing_book in books if existing_book["id"] == book_id),
        None
    )
    if book_found is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found.",
        )
    for key, value in update.items():
        book_found[key] = value

    return book_found


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    book_found = next((book for book in books if book["id"] == book_id), None)
    if book_found is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found.",
        )
    books.remove(book_found)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
