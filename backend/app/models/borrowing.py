from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Borrowing(Base):
    __tablename__ = "borrowings"

    id: Mapped[int] = mapped_column("borrowing_id", primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.member_id"))
    borrow_date: Mapped[datetime] = mapped_column("borrow_date")
    due_date: Mapped[datetime] = mapped_column("due_date")
    return_date: Mapped[datetime | None] = mapped_column("return_date")
    fine: Mapped[int | None] = mapped_column("fine")
