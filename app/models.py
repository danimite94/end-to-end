from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    # SQLite has no timezone support, so timestamps are stored as naive UTC.
    return datetime.now(UTC).replace(tzinfo=None)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    bio: Mapped[str | None] = mapped_column(Text)

    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    published_year: Mapped[int | None] = mapped_column(Integer)
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"), index=True)

    author: Mapped[Author] = relationship(back_populates="books")
    loans: Mapped[list["Loan"]] = relationship(back_populates="book", cascade="all, delete-orphan")

    @property
    def active_loan_count(self) -> int:
        return sum(1 for loan in self.loans if loan.returned_at is None)

    @property
    def available_copies(self) -> int:
        return self.total_copies - self.active_loan_count


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    loans: Mapped[list["Loan"]] = relationship(back_populates="member", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True)
    loaned_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    due_at: Mapped[datetime] = mapped_column(DateTime)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime)

    book: Mapped[Book] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")

    @property
    def is_overdue(self) -> bool:
        return self.returned_at is None and self.due_at < utcnow()
