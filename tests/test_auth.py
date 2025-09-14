"""
Unit tests for authentication module.
"""

import pytest
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from contacts_api import auth, models


def test_verify_password():
    """Test password verification."""
    password = "testpassword"
    hashed = auth.get_password_hash(password)
    
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrongpassword", hashed)


def test_get_password_hash():
    """Test password hashing."""
    password = "testpassword"
    hashed = auth.get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0


def test_create_access_token():
    """Test access token creation."""
    data = {"sub": "testuser"}
    token = auth.create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiry():
    """Test access token creation with custom expiry."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = auth.create_access_token(data, expires_delta)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_authenticate_user(db_session, test_user):
    """Test user authentication."""
    # Test successful authentication
    user = auth.authenticate_user(db_session, test_user.username, "testpass")
    assert user.id == test_user.id
    
    # Test failed authentication - wrong password
    user = auth.authenticate_user(db_session, test_user.username, "wrongpass")
    assert user is False
    
    # Test failed authentication - wrong username
    user = auth.authenticate_user(db_session, "wronguser", "testpass")
    assert user is False


def test_generate_reset_token():
    """Test reset token generation."""
    token = auth.generate_reset_token()
    
    assert isinstance(token, str)
    assert len(token) > 0