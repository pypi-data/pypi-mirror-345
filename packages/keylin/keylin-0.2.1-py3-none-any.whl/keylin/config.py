import json
from typing import Any, ClassVar

from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    Attributes:
        JWT_SECRET: Secret key for JWT signing.
        DATABASE_URL: Database connection string.
        RESET_PASSWORD_SECRET: Secret for password reset tokens.
        VERIFICATION_SECRET: Secret for email verification tokens.
        allowed_origins: List of allowed CORS origins.
        JWT_ALGORITHM: Algorithm for JWT signing.
    """

    JWT_SECRET: str = "changeme"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 3600
    RESET_PASSWORD_SECRET: str | None = None
    VERIFICATION_SECRET: str | None = None
    ALLOWED_ORIGINS: Any = ""

    @computed_field
    def allowed_origins(self) -> list[str]:
        """Parse allowed_origins from ALLOWED_ORIGINS string.

        Accepts:
        - JSON array string: '["http://localhost", "https://example.com"]'
        - Comma-separated string: "http://localhost,https://example.com"
        """
        v = self.ALLOWED_ORIGINS
        if not isinstance(v, str):
            return []

        v = v.strip()
        if not v:
            return []

        # If it looks like a JSON array, try parsing it
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [s for s in parsed if s and isinstance(s, str)]
            except json.JSONDecodeError:
                # Not valid JSON, treat as comma-separated with brackets
                v = v[1:-1]

        # Treat as comma-separated
        parts = [p.strip().strip('"').strip("'") for p in v.split(",")]
        return [p for p in parts if p]

    model_config: ClassVar[dict[str, Any]] = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.JWT_SECRET or self.JWT_SECRET == "changeme":
            raise RuntimeError("JWT_SECRET environment variable must be set")
        if self.RESET_PASSWORD_SECRET is None:
            self.RESET_PASSWORD_SECRET = self.JWT_SECRET
        if self.VERIFICATION_SECRET is None:
            self.VERIFICATION_SECRET = self.JWT_SECRET


settings = Settings()
