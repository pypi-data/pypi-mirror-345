import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is in sys.path for test imports
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Set the JWT_SECRET environment variable at the top of conftest.py
os.environ["JWT_SECRET"] = "test-secret"


# Function-scoped fixture for tests that require JWT_SECRET
@pytest.fixture(scope="function")
def set_jwt_secret():
    """Set JWT_SECRET for tests that require it, and restore after."""
    old = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = "test-secret"
    yield
    if old is not None:
        os.environ["JWT_SECRET"] = old
    else:
        del os.environ["JWT_SECRET"]
