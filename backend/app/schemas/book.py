from pydantic import BaseModel


class BookCreate(BaseModel):
    name: str
    author: str
    publisher: str
    genre: str


class BookUpdate(BaseModel):
    name: str | None = None
    author: str | None = None
    publisher: str | None = None
    genre: str | None = None


class BookResponse(BaseModel):
    id: int
    name: str
    author: str
    publisher: str
    genre: str
