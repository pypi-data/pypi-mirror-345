import subprocess
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


def test_get_jwt_strategy(set_jwt_secret):
    strategy = auth.get_jwt_strategy()
    assert hasattr(strategy, "write_token")
    assert strategy.lifetime_seconds == 3600
    assert strategy.secret == "test-secret"


def test_auth_backend_config(set_jwt_secret):
    backend = auth.auth_backend
    assert backend.name == "jwt"
    assert hasattr(backend, "transport")
    assert hasattr(backend, "get_strategy")


def test_user_manager_secrets(set_jwt_secret):
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


def test_auth_raises_if_secret_missing():
    code = """
import os
import sys
sys.modules.pop("keylin.config", None)
sys.modules.pop("keylin.auth", None)
os.environ.pop("JWT_SECRET", None)
try:
    import keylin.auth
except RuntimeError as e:
    assert "JWT_SECRET environment variable must be set" in str(e)
else:
    raise AssertionError("Did not raise RuntimeError")
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_reset_and_verification_secret_default():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
s = Settings()
assert s.RESET_PASSWORD_SECRET == "my-secret"
assert s.VERIFICATION_SECRET == "my-secret"
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_reset_and_verification_secret_override():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["RESET_PASSWORD_SECRET"] = "reset-secret"
os.environ["VERIFICATION_SECRET"] = "verify-secret"
s = Settings()
assert s.RESET_PASSWORD_SECRET == "reset-secret"
assert s.VERIFICATION_SECRET == "verify-secret"
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_string():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost", "https://example.com"]'
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_list():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost", "https://example.com"]'
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_empty():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = ""
s = Settings()
assert s.allowed_origins == []
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_malformed():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost", "", "https://example.com"]'
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_comma_separated():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = "http://localhost,https://example.com"
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_bracketed_comma_separated():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = "[http://localhost, https://example.com]"
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_quoted_values():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = "'http://localhost','https://example.com'"
s = Settings()
assert s.allowed_origins == ["http://localhost", "https://example.com"]
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_non_string():
    code = """
from keylin.config import Settings
s = Settings(JWT_SECRET="my-secret", ALLOWED_ORIGINS=123)  # Pass non-string directly
assert s.allowed_origins == []
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_settings_allowed_origins_whitespace():
    code = """
import os
from keylin.config import Settings
os.environ["JWT_SECRET"] = "my-secret"
os.environ["ALLOWED_ORIGINS"] = "   "
s = Settings()
assert s.allowed_origins == []
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr + result.stdout
