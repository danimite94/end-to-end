from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.common import commit
from app.exceptions import ConflictError, NotFoundError
from app.models import Member
from app.schemas import MemberCreate, MemberUpdate


def get_member(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise NotFoundError("Member", member_id)
    return member


def list_members(db: Session, skip: int, limit: int) -> list[Member]:
    return list(db.scalars(select(Member).order_by(Member.id).offset(skip).limit(limit)))


def _ensure_email_free(db: Session, email: str, member_id: int | None = None) -> None:
    existing = db.scalar(select(Member).where(Member.email == email))
    if existing is not None and existing.id != member_id:
        raise ConflictError(f"A member with email {email} already exists")


def create_member(db: Session, data: MemberCreate) -> Member:
    _ensure_email_free(db, data.email)
    member = Member(**data.model_dump())
    db.add(member)
    commit(db, f"A member with email {data.email} already exists")
    return member


def update_member(db: Session, member_id: int, data: MemberUpdate) -> Member:
    member = get_member(db, member_id)
    changes = data.changes()
    if "email" in changes:
        _ensure_email_free(db, changes["email"], member_id)
    for field, value in changes.items():
        setattr(member, field, value)
    commit(db)
    return member


def delete_member(db: Session, member_id: int) -> None:
    member = get_member(db, member_id)
    if any(loan.returned_at is None for loan in member.loans):
        raise ConflictError(f"Member {member_id} still has books on loan; return them first")
    db.delete(member)  # loan history for the member is deleted with it
    commit(db)
