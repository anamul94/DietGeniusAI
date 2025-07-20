from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import os
from dotenv import load_dotenv

# Force reload of environment variables
load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "DietTracker"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database - Only DATABASE_URL is needed as it contains all connection info
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Security - Provide sensible defaults for development
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30000"))
    
    # CORS - Default to allow localhost for development
    ALLOWED_ORIGINS: Union[str, List[str]] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")

    @field_validator('ALLOWED_ORIGINS', mode='after')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str) and v:
            return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return v
        return []
    
    # Rate Limiting - Default values
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # OAuth - Optional for development
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL: Optional[str] = os.getenv("GOOGLE_DISCOVERY_URL")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Google Health API - Optional for development
    GOOGLE_HEALTH_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_HEALTH_CLIENT_ID")
    GOOGLE_HEALTH_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_HEALTH_CLIENT_SECRET")
    GOOGLE_HEALTH_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_HEALTH_REDIRECT_URI")
    GOOGLE_HEALTH_API_URL: str = os.getenv("GOOGLE_HEALTH_API_URL", "https://www.googleapis.com/fitness/v1")
    GOOGLE_HEALTH_SCOPES: str = os.getenv(
        "GOOGLE_HEALTH_SCOPES",
        "https://www.googleapis.com/auth/fitness.activity.read"
    )
    
    # Memory Configuration - Optional for development
    USER_MEMORY_TABLE: str = os.getenv("USER_MEMORY_TABLE", "user_memory")
    USER_DAILY_LOG_SESSION_TABLE: str = os.getenv("USER_DAILY_LOG_SESSION_TABLE", "user_daily_log")
    GENERAL_SESSION_TABLE: str = os.getenv("GENERAL_SESSION_TABLE", "general_log")
    
    # Langfuse Configuration - Optional for development
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: Optional[str] = os.getenv("LANGFUSE_HOST")
    
    # OpenTelemetry Configuration - Optional for development
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_EXPORTER_OTLP_HEADERS: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: Optional[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: Optional[int] = int(os.getenv("REDIS_DB", 0))
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Validate required settings
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")