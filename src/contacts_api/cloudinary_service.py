"""
Cloudinary service for avatar upload.

This module handles avatar upload to Cloudinary cloud storage.
"""

import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_avatar(file, user_id: int) -> str:
    """
    Upload user avatar to Cloudinary.
    
    Args:
        file: File object to upload
        user_id: User ID for unique naming
        
    Returns:
        Secure URL of uploaded image or None if failed
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            public_id=f"avatars/{user_id}",
            overwrite=True,
            transformation=[
                {"width": 250, "height": 250, "crop": "fill"},
                {"quality": "auto"}
            ]
        )
        return result["secure_url"]
    except Exception as e:
        return None