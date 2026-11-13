from fastapi import APIRouter, status

from app.crud import authors as crud
from app.dependencies import DbSession, Page
from app.schemas import AuthorCreate, AuthorRead, AuthorUpdate, BookRead

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=list[AuthorRead])
def list_authors(db: DbSession, page: Page, name: str | None = None):
    return crud.list_authors(db, page.skip, page.limit, name)


@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(data: AuthorCreate, db: DbSession):
    return crud.create_author(db, data)


@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, db: DbSession):
    return crud.get_author(db, author_id)


@router.get("/{author_id}/books", response_model=list[BookRead])
def list_author_books(author_id: int, db: DbSession):
    return crud.list_author_books(db, author_id)


@router.patch("/{author_id}", response_model=AuthorRead)
def update_author(author_id: int, data: AuthorUpdate, db: DbSession):
    return crud.update_author(db, author_id, data)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: DbSession) -> None:
    crud.delete_author(db, author_id)
