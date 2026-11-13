import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, init_db, make_engine
from app.main import app


@pytest.fixture
def client():
    # Each test gets its own in-memory SQLite database; library.db is never touched.
    engine = make_engine("sqlite://", poolclass=StaticPool)
    init_db(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # not entered as a context manager, so the lifespan doesn't create library.db
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
