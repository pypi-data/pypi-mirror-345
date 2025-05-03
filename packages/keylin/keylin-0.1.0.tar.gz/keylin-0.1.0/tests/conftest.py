import os
import sys
from pathlib import Path

# Ensure the project root is in sys.path for test imports
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))


# Set required environment variables for tests
def pytest_configure(config):
    os.environ.setdefault("KEYLIN_JWT_SECRET", "test-secret")
