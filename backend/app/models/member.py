from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column("member_id", primary_key=True)
    name: Mapped[str] = mapped_column("member_name", String(300))
    joining_date: Mapped[datetime] = mapped_column("joining_date")
    exit_date: Mapped[datetime | None] = mapped_column("exit_date")
    is_active: Mapped[bool] = mapped_column("is_active")
    contact: Mapped[str] = mapped_column(String(20), unique=True)
    address: Mapped[str | None] = mapped_column(String(1000))
