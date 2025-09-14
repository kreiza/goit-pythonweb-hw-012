"""
CRUD operations for the Contacts API.

This module contains all database operations for users and contacts.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, extract
from datetime import date, timedelta
from . import models
from . import schemas
from .auth import get_password_hash, generate_reset_token
from .redis_cache import invalidate_user_cache


def get_user_by_email(db: Session, email: str) -> models.User:
    """
    Get user by email address.
    
    Args:
        db: Database session
        email: Email address to search for
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_reset_token(db: Session, token: str) -> models.User:
    """
    Get user by reset token.
    
    Args:
        db: Database session
        token: Reset token
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.reset_token == token).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create new user.
    
    Args:
        db: Database session
        user: User creation schema
        
    Returns:
        Created user object
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_user_email(db: Session, user_id: int) -> models.User:
    """
    Verify user email.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Updated user object
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
        invalidate_user_cache(user.username)
    return user


def update_user_avatar(db: Session, user_id: int, avatar_url: str) -> models.User:
    """
    Update user avatar.
    
    Args:
        db: Database session
        user_id: User ID
        avatar_url: New avatar URL
        
    Returns:
        Updated user object
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.avatar = avatar_url
        db.commit()
        db.refresh(user)
        invalidate_user_cache(user.username)
    return user


def create_password_reset_token(db: Session, email: str) -> str:
    """
    Create password reset token for user.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        Reset token or None if user not found
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    db.commit()
    invalidate_user_cache(user.username)
    return reset_token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """
    Reset user password using token.
    
    Args:
        db: Database session
        token: Reset token
        new_password: New password
        
    Returns:
        True if successful, False otherwise
    """
    user = get_user_by_reset_token(db, token)
    if not user:
        return False
    
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    invalidate_user_cache(user.username)
    return True


def get_contact(db: Session, contact_id: int, user_id: int) -> models.Contact:
    """
    Get contact by ID for specific user.
    
    Args:
        db: Database session
        contact_id: Contact ID
        user_id: Owner user ID
        
    Returns:
        Contact object or None if not found
    """
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user_id
    ).first()


def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[models.Contact]:
    """
    Get contacts for user with pagination.
    
    Args:
        db: Database session
        user_id: Owner user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of contact objects
    """
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id
    ).offset(skip).limit(limit).all()


def search_contacts(db: Session, user_id: int, query: str) -> list[models.Contact]:
    """
    Search contacts by name or email.
    
    Args:
        db: Database session
        user_id: Owner user ID
        query: Search query
        
    Returns:
        List of matching contact objects
    """
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        or_(
            models.Contact.first_name.ilike(f"%{query}%"),
            models.Contact.last_name.ilike(f"%{query}%"),
            models.Contact.email.ilike(f"%{query}%")
        )
    ).all()


def get_upcoming_birthdays(db: Session, user_id: int) -> list[models.Contact]:
    """
    Get contacts with birthdays in the next 7 days.
    
    Args:
        db: Database session
        user_id: Owner user ID
        
    Returns:
        List of contacts with upcoming birthdays
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        and_(
            extract('month', models.Contact.birthday) >= today.month,
            extract('day', models.Contact.birthday) >= today.day,
            extract('month', models.Contact.birthday) <= next_week.month,
            extract('day', models.Contact.birthday) <= next_week.day
        )
    ).all()


def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int) -> models.Contact:
    """
    Create new contact.
    
    Args:
        db: Database session
        contact: Contact creation schema
        user_id: Owner user ID
        
    Returns:
        Created contact object
    """
    db_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int) -> models.Contact:
    """
    Update existing contact.
    
    Args:
        db: Database session
        contact_id: Contact ID
        contact: Contact update schema
        user_id: Owner user ID
        
    Returns:
        Updated contact object or None if not found
    """
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user_id
    ).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int) -> models.Contact:
    """
    Delete contact.
    
    Args:
        db: Database session
        contact_id: Contact ID
        user_id: Owner user ID
        
    Returns:
        Deleted contact object or None if not found
    """
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user_id
    ).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact