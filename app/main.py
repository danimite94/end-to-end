from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import init_db
from app.exceptions import register_exception_handlers
from app.routers import authors, books, loans, members


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()  # creates the SQLite file and tables on first start
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    register_exception_handlers(app)
    for module in (authors, books, members, loans):
        app.include_router(module.router)

    @app.get("/", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "docs": "/docs"}

    return app


app = create_app()
