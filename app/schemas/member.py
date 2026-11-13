from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import PatchModel, ReadModel

Name = Annotated[str, Field(min_length=1, max_length=200)]


class MemberCreate(BaseModel):
    name: Name
    email: EmailStr


class MemberUpdate(PatchModel):
    non_nullable = frozenset({"name", "email"})

    name: Name | None = None
    email: EmailStr | None = None


class MemberRead(ReadModel):
    id: int
    name: str
    email: str
    joined_at: datetime
