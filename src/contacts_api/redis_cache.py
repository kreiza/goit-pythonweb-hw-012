"""
Redis caching service for the Contacts API.

This module provides Redis caching functionality for user data.
"""

import redis
import json
import os
from typing import Optional
from .models import User


# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)


def cache_user(user: User) -> None:
    """
    Cache user data in Redis.
    
    Args:
        user: User object to cache
    """
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_verified": user.is_verified,
        "avatar": user.avatar,
        "role": user.role.value if user.role else "user"
    }
    redis_client.setex(f"user:{user.username}", 3600, json.dumps(user_data))


def get_cached_user(username: str) -> Optional[dict]:
    """
    Get cached user data from Redis.
    
    Args:
        username: Username to lookup
        
    Returns:
        User data dict or None if not found
    """
    cached_data = redis_client.get(f"user:{username}")
    if cached_data:
        return json.loads(cached_data)
    return None


def invalidate_user_cache(username: str) -> None:
    """
    Remove user from cache.
    
    Args:
        username: Username to remove from cache
    """
    redis_client.delete(f"user:{username}")