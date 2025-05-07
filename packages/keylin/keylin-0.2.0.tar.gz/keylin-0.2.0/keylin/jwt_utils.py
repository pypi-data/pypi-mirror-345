# keylin/jwt_utils.py

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from .config import settings


def create_jwt_for_user(
    user_id: uuid.UUID, email: str, expires_seconds: int = 3600
) -> str:
    """Create a JWT for a test user.

    Args:
        username (str): The username/email for the token subject.
        user_id (int): The user ID (default: 1).
        expires_delta (int): Expiry in seconds (default: JWT_EXPIRE_SECONDS).

    Returns:
        str: Encoded JWT token.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(seconds=expires_seconds or settings.JWT_EXPIRE_SECONDS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": exp,
        "iat": now,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
