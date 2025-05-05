import importlib
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import keylin
from keylin import auth, db, models, schemas


def test_version():
    assert hasattr(keylin, "__version__")
    assert isinstance(keylin.__version__, str)


def test_user_model_fields():
    user = models.User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    assert user.full_name == "Test User"
    assert user.__tablename__ == "user"


def test_user_read_schema():
    user = schemas.UserRead(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    assert user.full_name == "Test User"


def test_user_create_schema():
    user = schemas.UserCreate(
        email="test@example.com", password="password", full_name="Test User"
    )
    assert user.full_name == "Test User"


def test_get_jwt_strategy():
    strategy = auth.get_jwt_strategy()
    assert hasattr(strategy, "write_token")
    assert strategy.lifetime_seconds == 3600
    assert strategy.secret == "test-secret"


def test_auth_backend_config():
    backend = auth.auth_backend
    assert backend.name == "jwt"
    assert hasattr(backend, "transport")
    assert hasattr(backend, "get_strategy")


def test_user_manager_secrets():
    manager = auth.UserManager(user_db=MagicMock())
    assert manager.reset_password_token_secret == "test-secret"
    assert manager.verification_token_secret == "test-secret"


@pytest.mark.asyncio
async def test_get_user_manager_yields_manager():
    mock_user_db = MagicMock()
    gen = auth.get_user_manager(mock_user_db)
    manager = await gen.__anext__()
    assert isinstance(manager, auth.UserManager)


def test_fastapi_users_instance():
    assert hasattr(auth.fastapi_users, "get_auth_router")
    assert hasattr(auth.fastapi_users, "get_register_router")
    assert hasattr(auth.fastapi_users, "get_users_router")


def test_current_active_user_dependency():
    # This is a FastAPI dependency, just check it's callable
    assert callable(auth.current_active_user)


@pytest.mark.asyncio
async def test_get_async_session_yields_session():
    class AsyncSessionContextManager:
        def __init__(self, session):
            self.session = session

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            pass

    mock_session = AsyncMock()
    with patch.object(
        db, "async_session_maker", return_value=AsyncSessionContextManager(mock_session)
    ):
        gen = db.get_async_session()
        session = await gen.__anext__()
        assert session is mock_session


@pytest.mark.asyncio
async def test_get_user_db_yields_user_db():
    mock_session = MagicMock()
    with patch("keylin.db.SQLAlchemyUserDatabase", autospec=True) as mock_db:
        gen = db.get_user_db(mock_session)
        user_db = await gen.__anext__()
        mock_db.assert_called_once_with(mock_session, models.User)
        assert user_db == mock_db.return_value


def test_auth_raises_if_secret_missing(monkeypatch):
    # Remove the secret from the environment
    monkeypatch.delenv("KEYLIN_JWT_SECRET", raising=False)
    # Remove keylin.auth from sys.modules to force reload
    sys.modules.pop("keylin.auth", None)
    with pytest.raises(RuntimeError) as excinfo:
        importlib.import_module("keylin.auth")
    assert "KEYLIN_JWT_SECRET environment variable must be set" in str(excinfo.value)
    # Restore for other tests
    os.environ["KEYLIN_JWT_SECRET"] = "test-secret"
