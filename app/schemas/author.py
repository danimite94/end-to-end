from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.common import PatchModel, ReadModel

Name = Annotated[str, Field(min_length=1, max_length=200)]


class AuthorCreate(BaseModel):
    name: Name
    bio: str | None = None


class AuthorUpdate(PatchModel):
    non_nullable = frozenset({"name"})

    name: Name | None = None
    bio: str | None = None


class AuthorRead(ReadModel):
    id: int
    name: str
    bio: str | None
