"""Configuration for JWT creation."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET: str = "changeme"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 3600
    RESET_PASSWORD_SECRET: str | None = None
    VERIFICATION_SECRET: str | None = None
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.JWT_SECRET or self.JWT_SECRET == "changeme":
            raise RuntimeError("JWT_SECRET environment variable must be set")
        if self.RESET_PASSWORD_SECRET is None:
            self.RESET_PASSWORD_SECRET = self.JWT_SECRET
        if self.VERIFICATION_SECRET is None:
            self.VERIFICATION_SECRET = self.JWT_SECRET


settings = Settings()
