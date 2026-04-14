"""
Core Configuration Settings for Tracerfy Backend
"""

import json
from typing import Any, List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Tracerfy API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Professional Skip Tracing Services for Real Estate & Lead Generation"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:admin123@localhost:5432/tracify"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING: bool = False
    
    # Rate Limiting
    ENABLE_RATE_LIMITING: bool = True
    ADVANCED_RATE_LIMITING: bool = False
    SLOW_REQUEST_THRESHOLD: float = 2.0
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Payment Gateway (Stripe)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # DNC Registry APIs
    FEDERAL_DNC_API_URL: Optional[str] = None
    FEDERAL_DNC_API_KEY: Optional[str] = None
    STATE_DNC_API_URL: Optional[str] = None
    STATE_DNC_API_KEY: Optional[str] = None
    DMA_API_URL: Optional[str] = None
    DMA_API_KEY: Optional[str] = None
    TCPA_LITIGATOR_API_URL: Optional[str] = None
    TCPA_LITIGATOR_API_KEY: Optional[str] = None
    
    # Celery
    ENABLE_CELERY: bool = False
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return v
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Any) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return v


# Create settings instance
settings = Settings()
