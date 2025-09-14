"""
Email service for sending verification and password reset emails.

This module handles email sending functionality using FastMail.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


def create_email_token(data: dict) -> str:
    """
    Create JWT token for email verification.
    
    Args:
        data: Data to encode in token
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_email_token(token: str) -> str:
    """
    Verify email token and extract email.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Email address or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        return email
    except jwt.JWTError:
        return None


async def send_verification_email(email: str, username: str) -> None:
    """
    Send email verification message.
    
    Args:
        email: Recipient email address
        username: Username for personalization
    """
    token = create_email_token({"sub": email})
    verification_url = f"http://localhost:8000/auth/verify-email/{token}"
    
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=f"Hello {username}! Please verify your email by clicking: {verification_url}",
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_password_reset_email(email: str, reset_token: str) -> None:
    """
    Send password reset email.
    
    Args:
        email: Recipient email address
        reset_token: Password reset token
    """
    reset_url = f"http://localhost:8000/auth/password-reset/confirm?token={reset_token}"
    
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click here to reset your password: {reset_url}",
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)