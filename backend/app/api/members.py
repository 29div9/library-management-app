from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, status
from schemas.member import MemberCreate, MemberUpdate, MemberResponse
from data import members

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("/", response_model=list[MemberResponse])
def get_members():
    return members


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int):
    member_found = next(
        (
            existing_member
            for existing_member in members
            if existing_member["id"] == member_id
        ),
        None,
    )
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    return member_found


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate):
    new_member = member.model_dump()
    for existing_member in members:
        # only comparing contact as its unique as per DB schema
        if existing_member["contact"] == new_member["contact"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact number already exists.",
            )
    new_member["id"] = len(members) + 1
    # not setting it as default in the schema
    # as pydantic should only be responsible for data validation and
    # serialization and not for biz rules
    new_member["joining_date"] = datetime.now()
    new_member["exit_date"] = None
    new_member["is_active"] = True

    members.append(new_member)
    return new_member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberUpdate):
    # first find the member
    member_found = next(
        (
            existing_member
            for existing_member in members
            if existing_member["id"] == member_id
        ),
        None,
    )

    # if the user is updating contact too
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    update = member.model_dump(
        exclude_unset=True
    )  # only include fields that user sent in request
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided.",
        )

    if "contact" in update:
        duplicate_member = next(
            (
                existing_member
                for existing_member in members
                # Ensure no other member already has the requested contact number
                if (
                    existing_member["contact"] == update["contact"]
                    and existing_member["id"] != member_id
                )
            ),
            None,
        )
        if duplicate_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact number already exists.",
            )

    for key, value in update.items():
        member_found[key] = value
    return member_found


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int):
    member_found = next(
        (
            existing_member
            for existing_member in members
            if existing_member["id"] == member_id
        ),
        None,
    )
    if member_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    members.remove(member_found)
    return Response()
