from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ReadModel


class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    loan_days: int = Field(14, ge=1, le=90)


class LoanRead(ReadModel):
    id: int
    book_id: int
    member_id: int
    loaned_at: datetime
    due_at: datetime
    returned_at: datetime | None
    is_overdue: bool
