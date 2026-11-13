from fastapi import APIRouter, status

from app.crud import loans as crud
from app.dependencies import DbSession, Page
from app.schemas import LoanCreate, LoanRead

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=list[LoanRead])
def list_loans(
    db: DbSession,
    page: Page,
    member_id: int | None = None,
    book_id: int | None = None,
    active: bool | None = None,
):
    return crud.list_loans(db, page.skip, page.limit, member_id, book_id, active)


@router.post("", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def checkout_book(data: LoanCreate, db: DbSession):
    return crud.checkout(db, data)


@router.get("/{loan_id}", response_model=LoanRead)
def get_loan(loan_id: int, db: DbSession):
    return crud.get_loan(db, loan_id)


@router.post("/{loan_id}/return", response_model=LoanRead)
def return_book(loan_id: int, db: DbSession):
    return crud.return_loan(db, loan_id)


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(loan_id: int, db: DbSession) -> None:
    crud.delete_loan(db, loan_id)
