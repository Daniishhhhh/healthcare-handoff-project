"""Configuration settings loaded from environment variables."""

import os
from typing import Optional


class Settings:
    """Application settings from environment variables (zero dependencies)."""

    # App
    app_name: str = os.getenv("APP_NAME", "Healthcare Handoff Backend")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Redis
    redis_url: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379")

    # JWT & Security
    secret_key: str = os.getenv("SECRET_KEY", "change_me_in_production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiry_hours: int = int(os.getenv("JWT_EXPIRY_HOURS", "1"))

    # Features
    enable_background_jobs: bool = os.getenv("ENABLE_BACKGROUND_JOBS", "False").lower() == "true"
    notification_service_enabled: bool = os.getenv("NOTIFICATION_SERVICE_ENABLED", "False").lower() == "true"

    # CORS (hardcoded)
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()