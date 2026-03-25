"""
CLI configuration using Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """CLI settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = Field(default="{{PROJECT_NAME}}", description="Application name")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Output
    OUTPUT_FORMAT: str = Field(
        default="table",
        description="Default output format (table, json, csv)",
    )
    
    # Add your configuration here
    # API_KEY: str | None = Field(default=None, description="API key")
    # API_URL: str = Field(default="https://api.example.com", description="API URL")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
