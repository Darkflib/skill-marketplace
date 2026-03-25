"""
Application configuration using Pydantic Settings.

Environment variables are automatically loaded from .env file.
"""

from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = Field(default="{{PROJECT_NAME}}", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for signing")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL",
    )
    
    # Redis
    REDIS_URL: RedisDsn = Field(
        ...,
        description="Redis connection URL",
    )
    
    # Optional: External APIs
    # API_KEY: str | None = Field(default=None, description="External API key")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
