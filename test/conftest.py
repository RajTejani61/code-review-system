"""
Test configuration / fixtures for the Code Review System.

IMPORTANT: Environment variables must be set BEFORE any application module is
imported, because config.py reads them at module load time (ChatMistralAI,
SECRET_KEY, etc.).  The os.environ.setdefault() calls below act as a safety net
for local runs; in CI these values come from the workflow env block.
"""
import os

os.environ["TESTING"] = "1"  # Tells main.py lifespan to skip DB create_all
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("LLM_MODEL_NAME", "mistral-small-2603")
os.environ.setdefault("MISTRAL_API_KEY", "test-key-ci")
os.environ.setdefault("DB_USERNAME", "test")
os.environ.setdefault("DB_PASSWORD", "testpassword")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "testdb")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base, get_db
from main import app

# Use in-memory SQLite for testing — no real DB needed
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fresh in-memory SQLite database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """TestClient wired to the in-memory SQLite DB."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
