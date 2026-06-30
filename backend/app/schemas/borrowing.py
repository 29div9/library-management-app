from datetime import datetime
from pydantic import BaseModel


class BorrowingCreate(BaseModel):
    book_id: int
    member_id: int


class BorrowingResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: datetime | None
    fine: float | None
