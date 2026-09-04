"""
Configuration for Mneme Audit M1.

Supports both local development (TCP) and Cloud Run (Unix socket via Cloud SQL Auth Proxy).
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mneme_audit",
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    DB_POOL_DISABLED: bool = os.getenv("DB_POOL_DISABLED", "false").lower() == "true"
    # Connection pool settings for production
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    # Cloud SQL specific (for Cloud Run with Cloud SQL Auth Proxy)
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "mneme_audit")

    # Application
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    AUDIT_SCHEMA_VERSION: int = 1

    # Frontend
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "https://mnemehq.com,https://www.mnemehq.com,http://localhost:3001,http://127.0.0.1:3001",
    )

    # Secret Manager
    DB_PASSWORD_SECRET: str = os.getenv("DB_PASSWORD_SECRET", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def resolved_database_url(self) -> str:
        """Resolve the database URL for the current environment.
        
        Priority:
        1. Explicit DATABASE_URL env var
        2. Cloud SQL Unix socket (Cloud Run production)
        3. TCP connection with explicit credentials
        3. Default local development
        """
        # Explicit DATABASE_URL takes precedence
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")

        # Cloud Run with Cloud SQL Auth Proxy (Unix socket)
        if self.CLOUD_SQL_CONNECTION_NAME:
            # Format: postgresql+asyncpg://user:pass@/dbname?host=/cloudsql/project:region:instance
            password = self.DB_PASSWORD
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{password}"
                f"@/{self.DB_NAME}?host=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
            )

        # TCP connection with explicit credentials
        if self.DB_PASSWORD and self.DB_USER != "postgres":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@localhost:5432/{self.DB_NAME}"
            )

        # Default local development
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/mneme_audit"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()