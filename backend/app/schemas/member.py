from datetime import datetime
from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    contact: str = Field(min_length=10, max_length=20, pattern=r"^\+?[1-9]\d{9,19}$")
    address: str | None = None


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    contact: str | None = Field(
        default=None, min_length=10, max_length=20, pattern=r"^\+?[1-9]\d{9,19}$"
    )
    address: str | None = None


class MemberResponse(BaseModel):
    id: int
    name: str
    joining_date: datetime
    exit_date: datetime | None
    is_active: bool
    contact: str
    address: str | None = None
