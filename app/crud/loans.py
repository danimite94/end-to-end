from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.books import get_book
from app.crud.common import commit
from app.crud.members import get_member
from app.exceptions import ConflictError, NotFoundError
from app.models import Loan, utcnow
from app.schemas import LoanCreate


def get_loan(db: Session, loan_id: int) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise NotFoundError("Loan", loan_id)
    return loan


def list_loans(
    db: Session,
    skip: int,
    limit: int,
    member_id: int | None = None,
    book_id: int | None = None,
    active: bool | None = None,
) -> list[Loan]:
    stmt = select(Loan).order_by(Loan.id)
    if member_id is not None:
        stmt = stmt.where(Loan.member_id == member_id)
    if book_id is not None:
        stmt = stmt.where(Loan.book_id == book_id)
    if active is True:
        stmt = stmt.where(Loan.returned_at.is_(None))
    elif active is False:
        stmt = stmt.where(Loan.returned_at.is_not(None))
    return list(db.scalars(stmt.offset(skip).limit(limit)))


def checkout(db: Session, data: LoanCreate) -> Loan:
    book = get_book(db, data.book_id)
    member = get_member(db, data.member_id)
    if book.available_copies < 1:
        raise ConflictError(f"No copies of book {book.id} are available")
    if any(loan.book_id == book.id and loan.returned_at is None for loan in member.loans):
        raise ConflictError(f"Member {member.id} already has book {book.id} on loan")
    now = utcnow()
    loan = Loan(book=book, member=member, loaned_at=now, due_at=now + timedelta(days=data.loan_days))
    db.add(loan)
    commit(db)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan(db, loan_id)
    if loan.returned_at is not None:
        raise ConflictError(f"Loan {loan_id} was already returned")
    loan.returned_at = utcnow()
    commit(db)
    return loan


def delete_loan(db: Session, loan_id: int) -> None:
    db.delete(get_loan(db, loan_id))
    commit(db)
