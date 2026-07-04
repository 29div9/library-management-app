from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column("book_id", primary_key=True)
    name: Mapped[str] = mapped_column("book_name", String(300))
    author: Mapped[str] = mapped_column(String(255))
    publisher: Mapped[str] = mapped_column(String(300))
    genre: Mapped[str] = mapped_column(String(255))
