from datetime import datetime
from fastapi import APIRouter, HTTPException, Response, status
from schemas.member import MemberCreate, MemberUpdate, MemberResponse

router = APIRouter(prefix="/members", tags=["Members"])

members = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "joining_date": "2024-01-15T10:30:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9876543210",
        "address": "12 Maple Street, Springfield",
    },
    {
        "id": 2,
        "name": "Brian Smith",
        "joining_date": "2023-08-10T09:15:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9123456780",
        "address": "45 Oak Avenue, Greenville",
    },
    {
        "id": 3,
        "name": "Catherine Lee",
        "joining_date": "2022-05-20T14:00:00",
        "exit_date": "2025-02-28T17:00:00",
        "is_active": False,
        "contact": "9988776655",
        "address": "78 Pine Road, Fairview",
    },
    {
        "id": 4,
        "name": "David Wilson",
        "joining_date": "2025-01-05T11:45:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9012345678",
        "address": "101 Cedar Lane, Riverside",
    },
    {
        "id": 5,
        "name": "Emma Davis",
        "joining_date": "2023-11-12T16:20:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9345678901",
        "address": "56 Birch Drive, Hillcrest",
    },
    {
        "id": 6,
        "name": "Frank Miller",
        "joining_date": "2021-09-18T08:30:00",
        "exit_date": "2024-12-31T12:00:00",
        "is_active": False,
        "contact": "9765432109",
        "address": "89 Elm Street, Lakeside",
    },
    {
        "id": 7,
        "name": "Grace Anderson",
        "joining_date": "2024-06-22T13:10:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9654321098",
        "address": "33 Willow Court, Brookfield",
    },
    {
        "id": 8,
        "name": "Henry Thomas",
        "joining_date": "2023-03-08T10:00:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9234567891",
        "address": "17 Cherry Avenue, Kingston",
    },
    {
        "id": 9,
        "name": "Isabella Moore",
        "joining_date": "2022-10-30T15:45:00",
        "exit_date": "2025-01-15T09:30:00",
        "is_active": False,
        "contact": "9898989898",
        "address": "64 Aspen Way, Oakwood",
    },
    {
        "id": 10,
        "name": "Jack Robinson",
        "joining_date": "2025-04-14T09:00:00",
        "exit_date": None,
        "is_active": True,
        "contact": "9556677889",
        "address": "150 Walnut Street, Greenfield",
    },
]


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
