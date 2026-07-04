from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    author: str
    publisher: str
    genre: str


class BookUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = None
    publisher: str | None = None
    genre: str | None = None


class BookResponse(BaseModel):
    id: int
    name: str
    author: str
    publisher: str
    genre: str


class BookAvailabilityResponse(BaseModel):
    available: bool
