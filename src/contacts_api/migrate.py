"""
Database migration script.

This script handles database schema migrations.
"""

from sqlalchemy import text
from .database import engine


def migrate_add_user_role_and_reset_token():
    """Add role and reset_token columns to users table."""
    with engine.connect() as conn:
        # Add role column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(10) DEFAULT 'user'
            """))
            conn.commit()
            print("Added role column to users table")
        except Exception as e:
            print(f"Role column might already exist: {e}")
        
        # Add reset_token column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN reset_token VARCHAR(255)
            """))
            conn.commit()
            print("Added reset_token column to users table")
        except Exception as e:
            print(f"Reset_token column might already exist: {e}")


if __name__ == "__main__":
    migrate_add_user_role_and_reset_token()