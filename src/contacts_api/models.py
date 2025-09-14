"""
Database models for the Contacts API application.

This module defines SQLAlchemy models for users and contacts.
"""

from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum


class UserRole(enum.Enum):
    """User roles enumeration."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        hashed_password: Hashed password
        is_verified: Email verification status
        avatar: Avatar URL
        role: User role (user/admin)
        reset_token: Password reset token
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    reset_token = Column(String(255), nullable=True)
    
    contacts = relationship("Contact", back_populates="owner")


class Contact(Base):
    """
    Contact model for storing contact information.
    
    Attributes:
        id: Primary key
        first_name: Contact's first name
        last_name: Contact's last name
        email: Contact's email address
        phone: Contact's phone number
        birthday: Contact's birthday
        additional_data: Additional information
        owner_id: Foreign key to User
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="contacts")