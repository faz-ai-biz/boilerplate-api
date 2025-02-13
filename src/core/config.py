# src/core/config.py
from typing import Any, ClassVar, Dict

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project settings
    API_VERSION: str  # API version (e.g., "1.0.0")
    COMPOSE_PROJECT_NAME: str = "set-project-name"
    ENVIRONMENT: str = "dev"  # Environment setting (dev/test/prod) with default="dev"
    PROJECT_NAME: str  # Name of your project

    # API Server Settings
    HOST: str = "127.0.0.1"  # Default to localhost
    PORT: int = 8000

    # Database Configuration
    POSTGRES_DB: str = "set-db-name"
    POSTGRES_HOST: str = "set-db-host"
    POSTGRES_PASSWORD: str = "set-postgres-password"
    POSTGRES_PORT: int = 5432
    POSTGRES_TEST_DB: str = "set-test-db-name"
    POSTGRES_TEST_HOST: str = "localhost"
    POSTGRES_TEST_PORT: int = 5432
    POSTGRES_USER: str = "set-postgres-user"

    # Security Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"  # JWT encryption algorithm (default="HS256")
    LOGIN_RATE_LIMIT_REQUESTS: int = 20
    LOGIN_RATE_LIMIT_WINDOW: int = 60
    REFRESH_SECRET_KEY: str  # JWT refresh token secret key
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str  # JWT/encryption secret key
    TOKEN_AUDIENCE: str = "your-app-users"
    TOKEN_ISSUER: str = "your-app-name"

    # Auth Settings
    AUTH_ALGORITHM: str = "HS256"
    AUTH_REFRESH_SECRET_KEY: str
    AUTH_SECRET_KEY: str
    AUTH_TOKEN_AUDIENCE: str = "fastapi-users"
    AUTH_TOKEN_ISSUER: str = "fastapi-auth-service"

    # CORS Configuration
    ALLOWED_ORIGINS: str  # Allowed origins for CORS (Cross-Origin Resource Sharing)

    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"  # Redis connection string with default

    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # Logging level with default="INFO"

    # Token type constants
    TOKEN_TYPE_ACCESS: ClassVar[str] = "access"  # nosec B105
    TOKEN_TYPE_REFRESH: ClassVar[str] = "refresh"  # nosec B105

    # Database Configuration (Generated)
    _DATABASE_URL: str = ""
    _TEST_DATABASE_URL: str = ""

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Dynamically compute database URL"""
        if self._DATABASE_URL != "":
            return self._DATABASE_URL
        else:
            self._DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            return self._DATABASE_URL

    @computed_field
    @property
    def TEST_DATABASE_URL(self) -> str:
        """Dynamically compute test database URL"""
        if self._TEST_DATABASE_URL != "":
            return self._TEST_DATABASE_URL
        else:
            self._TEST_DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_TEST_HOST}:{self.POSTGRES_TEST_PORT}/{self.POSTGRES_TEST_DB}"
            return self._TEST_DATABASE_URL

    class Config:
        # Configuration for loading environment variables
        env_file = ".env"  # Specifies which env file to load
        env_file_encoding = "utf-8"  # Specifies the file encoding


# Create a global settings instance
settings = Settings()
