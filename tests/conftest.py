"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from contacts_api.database import Base, get_db
from contacts_api.main import app
from contacts_api import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    from contacts_api.auth import get_password_hash

    user = models.User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_contact(db_session, test_user):
    """Create test contact."""
    from datetime import date

    contact = models.Contact(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        owner_id=test_user.id,
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact
