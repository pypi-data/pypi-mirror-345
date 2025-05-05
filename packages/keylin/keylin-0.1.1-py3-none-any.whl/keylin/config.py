"""Configuration for JWT creation."""

import os

JWT_SECRET = os.getenv("KEYLIN_JWT_SECRET", "changeme")
JWT_ALGORITHM = os.getenv("KEYLIN_JWT_ALGORITHM", "HS256")
JWT_EXPIRE_SECONDS = int(os.getenv("KEYLIN_JWT_EXPIRE_SECONDS", "3600"))
