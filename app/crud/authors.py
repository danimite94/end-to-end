from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.common import commit
from app.exceptions import ConflictError, NotFoundError
from app.models import Author, Book
from app.schemas import AuthorCreate, AuthorUpdate


def get_author(db: Session, author_id: int) -> Author:
    author = db.get(Author, author_id)
    if author is None:
        raise NotFoundError("Author", author_id)
    return author


def list_authors(db: Session, skip: int, limit: int, name: str | None = None) -> list[Author]:
    stmt = select(Author).order_by(Author.id)
    if name:
        stmt = stmt.where(Author.name.ilike(f"%{name}%"))
    return list(db.scalars(stmt.offset(skip).limit(limit)))


def list_author_books(db: Session, author_id: int) -> list[Book]:
    return sorted(get_author(db, author_id).books, key=lambda book: book.id)


def create_author(db: Session, data: AuthorCreate) -> Author:
    author = Author(**data.model_dump())
    db.add(author)
    commit(db)
    return author


def update_author(db: Session, author_id: int, data: AuthorUpdate) -> Author:
    author = get_author(db, author_id)
    for field, value in data.changes().items():
        setattr(author, field, value)
    commit(db)
    return author


def delete_author(db: Session, author_id: int) -> None:
    author = get_author(db, author_id)
    if author.books:
        raise ConflictError(f"Author {author_id} still has {len(author.books)} book(s); delete or reassign them first")
    db.delete(author)
    commit(db)
