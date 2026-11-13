from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, StringConstraints

from app.schemas.common import PatchModel, ReadModel


def _strip_isbn(value: object) -> object:
    return value.replace("-", "").replace(" ", "").upper() if isinstance(value, str) else value


def _not_in_future(year: int) -> int:
    if year > date.today().year:
        raise ValueError("published_year cannot be in the future")
    return year


# Accepts ISBN-10 or ISBN-13, with or without hyphens/spaces; stored without them.
ISBN = Annotated[str, BeforeValidator(_strip_isbn), StringConstraints(pattern=r"^(\d{9}[\dX]|\d{13})$")]
Title = Annotated[str, Field(min_length=1, max_length=300)]
Year = Annotated[int, Field(ge=0), AfterValidator(_not_in_future)]
Copies = Annotated[int, Field(ge=1, le=1000)]


class BookCreate(BaseModel):
    title: Title
    isbn: ISBN
    author_id: int
    published_year: Year | None = None
    total_copies: Copies = 1


class BookUpdate(PatchModel):
    non_nullable = frozenset({"title", "isbn", "author_id", "total_copies"})

    title: Title | None = None
    isbn: ISBN | None = None
    author_id: int | None = None
    published_year: Year | None = None
    total_copies: Copies | None = None


class BookRead(ReadModel):
    id: int
    title: str
    isbn: str
    author_id: int
    published_year: int | None
    total_copies: int
    available_copies: int
