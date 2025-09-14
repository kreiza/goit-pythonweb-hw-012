"""
Main FastAPI application for Contacts API.

This module contains the FastAPI application with all route definitions.
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from . import crud
from . import models
from . import schemas
from .database import SessionLocal, engine, get_db
from .auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_verified_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .email_service import (
    send_verification_email,
    verify_email_token,
    send_password_reset_email,
)
from .cloudinary_service import upload_avatar

models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Contacts API", description="API для управління контактами")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register new user.

    Args:
        user: User registration data
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If email already registered
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_user = crud.create_user(db=db, user=user)
    await send_verification_email(user.email, user.username)
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    User login endpoint.

    Args:
        form_data: Login form data
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@app.get("/auth/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email with token.

    Args:
        token: Email verification token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or user not found
    """
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.verify_user_email(db, user.id)
    return {"message": "Email verified successfully"}


@app.post("/auth/password-reset")
async def request_password_reset(
    reset_data: schemas.PasswordReset, db: Session = Depends(get_db)
):
    """
    Request password reset.

    Args:
        reset_data: Password reset request data
        db: Database session

    Returns:
        Success message
    """
    reset_token = crud.create_password_reset_token(db, reset_data.email)
    if reset_token:
        await send_password_reset_email(reset_data.email, reset_token)
    return {"message": "If email exists, reset instructions have been sent"}


@app.post("/auth/password-reset/confirm")
def confirm_password_reset(
    reset_data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.

    Args:
        reset_data: Password reset confirmation data
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid
    """
    success = crud.reset_password(db, reset_data.token, reset_data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successfully"}


@app.get("/users/me", response_model=schemas.User)
@limiter.limit("10/minute")
def read_users_me(
    request: Request, current_user: models.User = Depends(get_current_user)
):
    """
    Get current user information.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user


@app.patch("/users/me/avatar", response_model=schemas.User)
def update_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Update user avatar (admin only).

    Args:
        file: Avatar image file
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Updated user data

    Raises:
        HTTPException: If upload fails
    """
    avatar_url = upload_avatar(file.file, current_user.id)
    if not avatar_url:
        raise HTTPException(status_code=400, detail="Failed to upload avatar")

    return crud.update_user_avatar(db, current_user.id, avatar_url)


@app.post(
    "/contacts/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED
)
def create_contact(
    contact: schemas.ContactCreate,
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Create new contact.

    Args:
        contact: Contact creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created contact
    """
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Get user contacts with optional search.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        search: Search query
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of contacts
    """
    if search:
        return crud.search_contacts(db, current_user.id, search)
    return crud.get_contacts(db, current_user.id, skip=skip, limit=limit)


@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Get contact by ID.

    Args:
        contact_id: Contact ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Contact data

    Raises:
        HTTPException: If contact not found
    """
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Update contact.

    Args:
        contact_id: Contact ID
        contact: Contact update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated contact

    Raises:
        HTTPException: If contact not found
    """
    db_contact = crud.update_contact(
        db, contact_id=contact_id, contact=contact, user_id=current_user.id
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(
    contact_id: int,
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Delete contact.

    Args:
        contact_id: Contact ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Deleted contact

    Raises:
        HTTPException: If contact not found
    """
    db_contact = crud.delete_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.get("/contacts/birthdays/upcoming", response_model=List[schemas.Contact])
def get_upcoming_birthdays(
    current_user: models.User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """
    Get contacts with upcoming birthdays.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of contacts with birthdays in next 7 days
    """
    return crud.get_upcoming_birthdays(db, current_user.id)
