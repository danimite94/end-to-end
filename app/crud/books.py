from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.authors import get_author
from app.crud.common import commit
from app.exceptions import ConflictError, NotFoundError
from app.models import Book
from app.schemas import BookCreate, BookUpdate


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise NotFoundError("Book", book_id)
    return book


def list_books(
    db: Session, skip: int, limit: int, title: str | None = None, author_id: int | None = None
) -> list[Book]:
    stmt = select(Book).order_by(Book.id)
    if title:
        stmt = stmt.where(Book.title.ilike(f"%{title}%"))
    if author_id is not None:
        stmt = stmt.where(Book.author_id == author_id)
    return list(db.scalars(stmt.offset(skip).limit(limit)))


def _ensure_isbn_free(db: Session, isbn: str, book_id: int | None = None) -> None:
    existing = db.scalar(select(Book).where(Book.isbn == isbn))
    if existing is not None and existing.id != book_id:
        raise ConflictError(f"A book with ISBN {isbn} already exists (id {existing.id})")


def create_book(db: Session, data: BookCreate) -> Book:
    get_author(db, data.author_id)
    _ensure_isbn_free(db, data.isbn)
    book = Book(**data.model_dump())
    db.add(book)
    commit(db, f"A book with ISBN {data.isbn} already exists")
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    changes = data.changes()
    if "author_id" in changes:
        get_author(db, changes["author_id"])
    if "isbn" in changes:
        _ensure_isbn_free(db, changes["isbn"], book_id)
    if "total_copies" in changes and changes["total_copies"] < book.active_loan_count:
        raise ConflictError(
            f"Book {book_id} has {book.active_loan_count} copies on loan; total_copies cannot go below that"
        )
    for field, value in changes.items():
        setattr(book, field, value)
    commit(db)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    if book.active_loan_count:
        raise ConflictError(f"Book {book_id} has copies on loan; return them first")
    db.delete(book)  # loan history for the book is deleted with it
    commit(db)
