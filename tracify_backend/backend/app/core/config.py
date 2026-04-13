"""
Core Configuration Settings for Tracerfy Backend
"""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


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
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
