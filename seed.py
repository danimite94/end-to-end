"""Fill library.db with sample data. Run: .venv/bin/python seed.py"""
from datetime import timedelta

from sqlalchemy import select

from app.crud import authors, books, loans, members
from app.database import SessionLocal, init_db
from app.models import Author
from app.schemas import AuthorCreate, BookCreate, LoanCreate, MemberCreate

AUTHORS = [
    ("Ursula K. Le Guin", "American author of science fiction and fantasy."),
    ("Octavia E. Butler", "American science fiction author, MacArthur Fellow."),
    ("George Orwell", "English novelist and essayist."),
    ("Jane Austen", "English novelist of the Regency era."),
]

BOOKS = [  # (title, isbn, author index, year, copies)
    ("The Left Hand of Darkness", "9780441478125", 0, 1969, 2),
    ("A Wizard of Earthsea", "9780547773742", 0, 1968, 1),
    ("Kindred", "9780807083697", 1, 1979, 3),
    ("Parable of the Sower", "9781538732182", 1, 1993, 1),
    ("Nineteen Eighty-Four", "9780451524935", 2, 1949, 3),
    ("Animal Farm", "9780451526342", 2, 1945, 2),
    ("Pride and Prejudice", "9780141439518", 3, 1813, 2),
    ("Emma", "9780141439587", 3, 1815, 1),
]

MEMBERS = [
    ("Ada Lovelace", "ada@example.com"),
    ("Alan Turing", "alan@example.com"),
    ("Grace Hopper", "grace@example.com"),
    ("Katherine Johnson", "katherine@example.com"),
    ("Linus Pauling", "linus@example.com"),
]


def main() -> None:
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(Author.id).limit(1)) is not None:
            print("library.db already has data; nothing to do.")
            return

        a = [authors.create_author(db, AuthorCreate(name=n, bio=b)) for n, b in AUTHORS]
        bk = [
            books.create_book(db, BookCreate(title=t, isbn=i, author_id=a[ai].id, published_year=y, total_copies=c))
            for t, i, ai, y, c in BOOKS
        ]
        m = [members.create_member(db, MemberCreate(name=n, email=e)) for n, e in MEMBERS]

        loans.checkout(db, LoanCreate(book_id=bk[0].id, member_id=m[0].id))
        loans.checkout(db, LoanCreate(book_id=bk[2].id, member_id=m[1].id, loan_days=21))
        loans.checkout(db, LoanCreate(book_id=bk[7].id, member_id=m[2].id))  # Emma's only copy

        returned = loans.checkout(db, LoanCreate(book_id=bk[4].id, member_id=m[3].id))
        loans.return_loan(db, returned.id)

        # Backdate one loan so there is an overdue example.
        overdue = loans.checkout(db, LoanCreate(book_id=bk[5].id, member_id=m[0].id))
        overdue.loaned_at -= timedelta(days=30)
        overdue.due_at = overdue.loaned_at + timedelta(days=14)
        db.commit()

        print(f"Seeded {len(a)} authors, {len(bk)} books, {len(m)} members, 5 loans.")


if __name__ == "__main__":
    main()
