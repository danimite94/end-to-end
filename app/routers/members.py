from fastapi import APIRouter, status

from app.crud import loans as loans_crud
from app.crud import members as crud
from app.dependencies import DbSession, Page
from app.schemas import LoanRead, MemberCreate, MemberRead, MemberUpdate

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[MemberRead])
def list_members(db: DbSession, page: Page):
    return crud.list_members(db, page.skip, page.limit)


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberCreate, db: DbSession):
    return crud.create_member(db, data)


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: int, db: DbSession):
    return crud.get_member(db, member_id)


@router.get("/{member_id}/loans", response_model=list[LoanRead])
def list_member_loans(member_id: int, db: DbSession, page: Page, active: bool | None = None):
    crud.get_member(db, member_id)
    return loans_crud.list_loans(db, page.skip, page.limit, member_id=member_id, active=active)


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(member_id: int, data: MemberUpdate, db: DbSession):
    return crud.update_member(db, member_id, data)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: DbSession) -> None:
    crud.delete_member(db, member_id)
