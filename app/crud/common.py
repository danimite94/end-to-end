from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError


def commit(db: Session, conflict_message: str = "Request conflicts with existing data") -> None:
    """Commit, turning database constraint violations into a 409 instead of a 500."""
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(conflict_message) from exc
