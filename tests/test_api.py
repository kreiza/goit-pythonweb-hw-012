"""
Integration tests for API endpoints.
"""

import pytest
from datetime import date
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from contacts_api.auth import create_access_token


def get_auth_headers(user):
    """Get authorization headers for user."""
    token = create_access_token(data={"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert not data["is_verified"]


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": test_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_login_user(client, test_user):
    """Test user login."""
    response = client.post(
        "/auth/login", data={"username": test_user.username, "password": "testpass"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login", data={"username": "wronguser", "password": "wrongpass"}
    )

    assert response.status_code == 401


def test_get_current_user(client, test_user):
    """Test getting current user."""
    headers = get_auth_headers(test_user)
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_create_contact(client, test_user):
    """Test contact creation."""
    headers = get_auth_headers(test_user)
    contact_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "0987654321",
        "birthday": "1985-05-15",
    }

    response = client.post("/contacts/", json=contact_data, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["owner_id"] == test_user.id


def test_get_contacts(client, test_user, test_contact):
    """Test getting contacts."""
    headers = get_auth_headers(test_user)
    response = client.get("/contacts/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_contact.id


def test_get_contact_by_id(client, test_user, test_contact):
    """Test getting contact by ID."""
    headers = get_auth_headers(test_user)
    response = client.get(f"/contacts/{test_contact.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_contact.id
    assert data["first_name"] == test_contact.first_name


def test_update_contact(client, test_user, test_contact):
    """Test contact update."""
    headers = get_auth_headers(test_user)
    update_data = {
        "first_name": "Johnny",
        "last_name": "Doe",
        "email": "johnny@example.com",
        "phone": "1234567890",
        "birthday": "1990-01-01",
    }

    response = client.put(
        f"/contacts/{test_contact.id}", json=update_data, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Johnny"
    assert data["email"] == "johnny@example.com"


def test_delete_contact(client, test_user, test_contact):
    """Test contact deletion."""
    headers = get_auth_headers(test_user)
    response = client.delete(f"/contacts/{test_contact.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_contact.id


def test_search_contacts(client, test_user, test_contact):
    """Test contact search."""
    headers = get_auth_headers(test_user)
    response = client.get("/contacts/?search=John", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "John"


def test_unauthorized_access(client):
    """Test unauthorized access."""
    response = client.get("/contacts/")
    assert response.status_code == 401


def test_contact_not_found(client, test_user):
    """Test accessing non-existent contact."""
    headers = get_auth_headers(test_user)
    response = client.get("/contacts/999", headers=headers)
    assert response.status_code == 404
