import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Library API"
    # Defaults to a SQLite file in the directory the server is started from.
    database_url: str = os.getenv("LIBRARY_DATABASE_URL", "sqlite:///./library.db")


settings = Settings()
