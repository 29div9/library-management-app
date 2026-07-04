from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from backend.app.schemas.borrowing import BorrowingResponse

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.member import Member
from backend.app.models.borrowing import Borrowing
from backend.app.database import get_db

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("/", response_model=list[MemberResponse])
def get_members(db: Session = Depends(get_db)):
    """Retrieve all members of the library"""
    return db.scalars(select(Member)).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """Retrieve a member by its ID"""
    member_found = db.scalar(select(Member).where(Member.id == member_id))
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    return member_found


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """Add a new member to the library"""

    # only comparing contact as its unique as per DB schema
    existing_member = db.scalar(select(Member).where(Member.contact == member.contact))
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact number already exists.",
        )

    # setting the defaults here and not setting it them in the schema
    # as pydantic should only be responsible for data validation and
    # serialization and not for biz rules
    new_member = Member(
        name=member.name,
        joining_date=datetime.now(),
        exit_date=None,
        is_active=True,
        contact=member.contact,
        address=member.address,
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberUpdate, db: Session = Depends(get_db)):
    """Update one or more fields of an existing member"""

    member_found = db.scalar(select(Member).where(Member.id == member_id))

    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    updates = member.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided.",
        )

    if "contact" in updates:
        updated_contact = updates.get("contact", member_found.contact)

        duplicate_member = db.scalar(
            select(Member).where(
                Member.contact == updated_contact, Member.id != member_id
            )
        )

        if duplicate_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact number already exists.",
            )
    # this will update only the fields provided by user
    for key, value in updates.items():
        setattr(member_found, key, value)

    db.commit()
    db.refresh(member_found)

    return member_found


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """Delete a member from the library"""

    member_found = db.scalar(select(Member).where(Member.id == member_id))
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    try:
        db.delete(member_found)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete member because it has borrowing records.",
        )


@router.get("/{member_id}/borrowings", response_model=list[BorrowingResponse])
def get_member_borrowings(member_id: int, db: Session = Depends(get_db)):
    """Retrieve the borrowing history of a member"""

    member = db.scalar(
        select(Member).where(Member.id == member_id)
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )
    return db.scalars(
        select(Borrowing).where(
            Borrowing.member_id == member_id
        )
        .order_by(Borrowing.borrow_date.desc())
    ).all()


@router.get("/{member_id}/active-borrowings", response_model=list[BorrowingResponse])
def get_member_active_borrowings(member_id: int, db: Session = Depends(get_db)):
    """Retrieve the active borrowings of a member"""

    member = db.scalar(
        select(Member).where(Member.id == member_id)
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )
    return db.scalars(
        select(Borrowing).where(
            Borrowing.member_id == member_id,
            Borrowing.return_date.is_(None)
        )
        .order_by(Borrowing.borrow_date) # default ASC order to show books to be returned first
    ).all()
