"""
Unit tests for CRUD operations.
"""

import pytest
from datetime import date
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from contacts_api import crud, schemas, models


def test_create_user(db_session):
    """Test user creation."""
    user_data = schemas.UserCreate(
        username="newuser",
        email="new@example.com",
        password="password123"
    )
    user = crud.create_user(db_session, user_data)
    
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.hashed_password is not None
    assert not user.is_verified


def test_get_user_by_email(db_session, test_user):
    """Test getting user by email."""
    user = crud.get_user_by_email(db_session, test_user.email)
    assert user.id == test_user.id
    assert user.email == test_user.email


def test_verify_user_email(db_session, test_user):
    """Test email verification."""
    test_user.is_verified = False
    db_session.commit()
    
    verified_user = crud.verify_user_email(db_session, test_user.id)
    assert verified_user.is_verified


def test_create_contact(db_session, test_user):
    """Test contact creation."""
    contact_data = schemas.ContactCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="0987654321",
        birthday=date(1985, 5, 15)
    )
    contact = crud.create_contact(db_session, contact_data, test_user.id)
    
    assert contact.first_name == "Jane"
    assert contact.last_name == "Smith"
    assert contact.owner_id == test_user.id


def test_get_contacts(db_session, test_user, test_contact):
    """Test getting user contacts."""
    contacts = crud.get_contacts(db_session, test_user.id)
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id


def test_search_contacts(db_session, test_user, test_contact):
    """Test contact search."""
    contacts = crud.search_contacts(db_session, test_user.id, "John")
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"


def test_update_contact(db_session, test_user, test_contact):
    """Test contact update."""
    update_data = schemas.ContactUpdate(
        first_name="Johnny",
        last_name="Doe",
        email="johnny@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1)
    )
    updated_contact = crud.update_contact(db_session, test_contact.id, update_data, test_user.id)
    
    assert updated_contact.first_name == "Johnny"
    assert updated_contact.email == "johnny@example.com"


def test_delete_contact(db_session, test_user, test_contact):
    """Test contact deletion."""
    deleted_contact = crud.delete_contact(db_session, test_contact.id, test_user.id)
    assert deleted_contact.id == test_contact.id
    
    # Verify contact is deleted
    contact = crud.get_contact(db_session, test_contact.id, test_user.id)
    assert contact is None