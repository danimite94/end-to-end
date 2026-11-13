def make_author(client, name="Ursula K. Le Guin"):
    r = client.post("/authors", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def make_book(client, author_id, isbn="978-0-441-47812-5", copies=1):
    r = client.post(
        "/books",
        json={"title": "The Left Hand of Darkness", "isbn": isbn, "author_id": author_id,
              "published_year": 1969, "total_copies": copies},
    )
    assert r.status_code == 201, r.text
    return r.json()


def make_member(client, email="ada@example.com"):
    r = client.post("/members", json={"name": "Ada", "email": email})
    assert r.status_code == 201, r.text
    return r.json()


def test_author_crud(client):
    author = make_author(client)
    assert client.get(f"/authors/{author['id']}").json()["name"] == "Ursula K. Le Guin"

    r = client.patch(f"/authors/{author['id']}", json={"bio": "SF writer"})
    assert r.json()["bio"] == "SF writer"
    assert r.json()["name"] == "Ursula K. Le Guin"

    assert client.get("/authors", params={"name": "le guin"}).json()[0]["id"] == author["id"]
    assert client.delete(f"/authors/{author['id']}").status_code == 204
    assert client.get(f"/authors/{author['id']}").status_code == 404


def test_patch_rejects_null_for_required_field(client):
    author = make_author(client)
    assert client.patch(f"/authors/{author['id']}", json={"name": None}).status_code == 422


def test_book_validation_and_isbn_normalisation(client):
    author = make_author(client)
    book = make_book(client, author["id"])
    assert book["isbn"] == "9780441478125"
    assert book["available_copies"] == 1

    assert client.post("/books", json={"title": "X", "isbn": "123", "author_id": author["id"]}).status_code == 422
    assert client.post("/books", json={"title": "X", "isbn": "9780441478125", "author_id": 999}).status_code == 404
    dup = client.post("/books", json={"title": "X", "isbn": "9780441478125", "author_id": author["id"]})
    assert dup.status_code == 409


def test_cannot_delete_author_with_books(client):
    author = make_author(client)
    make_book(client, author["id"])
    assert client.delete(f"/authors/{author['id']}").status_code == 409
    assert len(client.get(f"/authors/{author['id']}/books").json()) == 1


def test_member_email_unique_and_validated(client):
    make_member(client)
    assert client.post("/members", json={"name": "B", "email": "ada@example.com"}).status_code == 409
    assert client.post("/members", json={"name": "B", "email": "not-an-email"}).status_code == 422


def test_loan_lifecycle(client):
    author = make_author(client)
    book = make_book(client, author["id"], copies=1)
    ada = make_member(client)
    bob = make_member(client, "bob@example.com")

    r = client.post("/loans", json={"book_id": book["id"], "member_id": ada["id"]})
    assert r.status_code == 201, r.text
    loan = r.json()
    assert loan["returned_at"] is None and loan["is_overdue"] is False
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 0

    # No copies left, and the book / member can't be deleted while the loan is open.
    assert client.post("/loans", json={"book_id": book["id"], "member_id": bob["id"]}).status_code == 409
    assert client.delete(f"/books/{book['id']}").status_code == 409
    assert client.delete(f"/members/{ada['id']}").status_code == 409
    assert client.patch(f"/books/{book['id']}", json={"total_copies": 1}).status_code == 200

    assert len(client.get(f"/members/{ada['id']}/loans", params={"active": True}).json()) == 1

    r = client.post(f"/loans/{loan['id']}/return")
    assert r.status_code == 200 and r.json()["returned_at"] is not None
    assert client.post(f"/loans/{loan['id']}/return").status_code == 409
    assert client.get(f"/books/{book['id']}").json()["available_copies"] == 1

    assert client.delete(f"/books/{book['id']}").status_code == 204
    assert client.get(f"/loans/{loan['id']}").status_code == 404


def test_pagination_limits(client):
    for i in range(3):
        make_author(client, f"Author {i}")
    assert len(client.get("/authors", params={"limit": 2}).json()) == 2
    assert len(client.get("/authors", params={"skip": 2}).json()) == 1
    assert client.get("/authors", params={"limit": 0}).status_code == 422
