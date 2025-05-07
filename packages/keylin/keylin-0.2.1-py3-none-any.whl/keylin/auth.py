import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from .config import settings
from .db import get_user_db
from .models import User


def get_jwt_strategy() -> JWTStrategy:
    """Return a JWTStrategy using the configured secret and 1 hour lifetime."""
    return JWTStrategy(
        secret=settings.JWT_SECRET,
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager that uses secrets from Pydantic settings."""

    user_db_model = User
    reset_password_token_secret = settings.RESET_PASSWORD_SECRET
    verification_token_secret = settings.VERIFICATION_SECRET


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
