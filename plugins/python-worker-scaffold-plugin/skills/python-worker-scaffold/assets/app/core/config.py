"""
Worker configuration using Pydantic Settings.
"""

from functools import lru_cache

from pydantic import AmqpDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    WORKER_NAME: str = Field(default="{{PROJECT_NAME}}", description="Worker name")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # RabbitMQ
    RABBITMQ_URL: AmqpDsn = Field(
        ...,
        description="RabbitMQ connection URL",
    )
    QUEUE_NAME: str = Field(
        default="{{PROJECT_NAME}}_queue",
        description="Queue name to consume from",
    )
    PREFETCH_COUNT: int = Field(
        default=10,
        description="Number of messages to prefetch",
    )
    
    # CloudEvents
    CLOUDEVENTS_SIGNING_KEY: str = Field(
        ...,
        description="Private key for signing CloudEvents (PEM format)",
    )
    CLOUDEVENTS_VERIFICATION_KEY: str = Field(
        ...,
        description="Public key for verifying CloudEvents (PEM format)",
    )
    
    # Worker behavior
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for failed messages",
    )
    RETRY_DELAY: int = Field(
        default=60,
        description="Delay in seconds before retrying",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
