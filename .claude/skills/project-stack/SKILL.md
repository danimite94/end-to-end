---
name: project-stack
description: The library API's tech stack — frameworks, tooling, layer layout and the conventions that bind them. Use when working out which framework or tool handles something, where new code belongs, or how to install, run, test, or query the project.
---

# Library API stack

A FastAPI CRUD service for a library (authors, books, members, loans) on a local SQLite file.

## Tooling

| Concern | Tool | Notes |
|---|---|---|
| Language | Python 3.12 | Interpreter lives in `.venv/` |
| Environment | uv | Deps in `pyproject.toml` (runtime) and its `dev` group (pytest, ipykernel), locked in `uv.lock`. Add with `uv add <pkg>` / `uv add --dev <pkg>`; `uv sync` removes anything not declared. `package = false`: the project itself is never built or installed |
| Web framework | FastAPI (`fastapi[standard]`) on Starlette | Brings uvicorn, the `fastapi` CLI and `email-validator` |
| Validation / types | Pydantic v2 | Request and response bodies only |
| Database access | SQLAlchemy 2.x ORM | Typed `Mapped[...]` models, sync `Session` |
| Database | SQLite, file `library.db` | URL overridable via `LIBRARY_DATABASE_URL` |
| Tests | pytest + FastAPI `TestClient` | Each test gets a fresh in-memory DB |

Exact installed versions: `uv pip list`.

## Commands

- Install / update env: `uv sync`
- Run: `uv run fastapi dev main.py` (docs at `/docs`)
- Test: `uv run pytest`
- Seed sample data: `uv run seed.py` (no-op if data exists)
- Query: `sqlite3 -header -column library.db "<sql>"`

## Layers

A request flows router → crud → model. Each layer has one job:

- `app/routers/` — HTTP only: path, status code, `response_model`. Thin calls into crud.
- `app/schemas/` — Pydantic types. `*Create` for POST, `*Update` for PATCH, `*Read` for responses. Single-field rules live here (→ 422).
- `app/crud/` — data access and business rules that need stored data. Raise `NotFoundError` (→ 404) or `ConflictError` (→ 409) from `app/exceptions.py`; handlers in `app/main.py` turn them into responses.
- `app/models.py` — tables and DB-level constraints (unique, FK, NOT NULL).
- `app/database.py` — engine, `SessionLocal`, `get_db`, `init_db`. `app/dependencies.py` — `DbSession` and `Page` (skip/limit) annotations.
- `main.py` (root) re-exports `app.main:app` for the CLI.

## Conventions and gotchas

- **No migrations.** `init_db()` runs `create_all` at startup, which only creates missing tables. A model change reaches an existing `library.db` only after deleting the file (and re-running `seed.py`).
- **Foreign keys** are enforced only because `make_engine` sets `PRAGMA foreign_keys=ON` per connection. Raw `sqlite3` sessions must run it themselves.
- **Timestamps** are naive UTC (`models.utcnow()`); SQLite stores no timezone. Defaults like `joined_at`/`loaned_at` are Python-side, so raw SQL inserts must supply them.
- **PATCH** bodies subclass `PatchModel`: list NOT NULL columns in `non_nullable` so an explicit `null` gets a 422 instead of a DB error; apply with `data.changes()`.
- **Read schemas** use `from_attributes`, so model `@property` values (`Book.available_copies`, `Loan.is_overdue`) serialize directly.
- **Commits** go through `crud.common.commit()`, which turns `IntegrityError` into a 409.
- **Tests** override `get_db` in `tests/conftest.py` and never enter the app lifespan, so they never touch `library.db`.
