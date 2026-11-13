from fastapi import APIRouter, status

from app.crud import books as crud
from app.dependencies import DbSession, Page
from app.schemas import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookRead])
def list_books(db: DbSession, page: Page, title: str | None = None, author_id: int | None = None):
    return crud.list_books(db, page.skip, page.limit, title, author_id)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, db: DbSession):
    return crud.create_book(db, data)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: DbSession):
    return crud.get_book(db, book_id)


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, data: BookUpdate, db: DbSession):
    return crud.update_book(db, book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: DbSession) -> None:
    crud.delete_book(db, book_id)
