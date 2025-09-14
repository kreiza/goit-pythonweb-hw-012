"""
Pydantic schemas for request/response validation.

This module defines all Pydantic models used for API request and response validation.
"""

from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from .models import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str


class User(UserBase):
    """Schema for user response."""

    id: int
    is_verified: bool
    avatar: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Schema for token data."""

    username: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str


class ContactBase(BaseModel):
    """Base contact schema with common fields."""

    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for contact creation."""

    pass


class ContactUpdate(ContactBase):
    """Schema for contact update."""

    pass


class Contact(ContactBase):
    """Schema for contact response."""

    id: int
    owner_id: int

    class Config:
        from_attributes = True
