from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# Force reload of environment variables
load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "DietTracker"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL: Optional[str] = os.getenv("GOOGLE_DISCOVERY_URL")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Google Health API
    GOOGLE_HEALTH_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_HEALTH_CLIENT_ID", os.getenv("GOOGLE_CLIENT_ID"))
    GOOGLE_HEALTH_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_HEALTH_CLIENT_SECRET", os.getenv("GOOGLE_CLIENT_SECRET"))
    GOOGLE_HEALTH_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_HEALTH_REDIRECT_URI")
    GOOGLE_HEALTH_API_URL: str = os.getenv("GOOGLE_HEALTH_API_URL", "https://www.googleapis.com/fitness/v1")
    GOOGLE_HEALTH_SCOPES: str = os.getenv(
        "GOOGLE_HEALTH_SCOPES",
        "https://www.googleapis.com/auth/fitness.activity.read " +
        "https://www.googleapis.com/auth/fitness.activity.write " +
        "https://www.googleapis.com/auth/fitness.body.read " +
        "https://www.googleapis.com/auth/fitness.body.write " +
        "https://www.googleapis.com/auth/fitness.nutrition.read " +
        "https://www.googleapis.com/auth/fitness.nutrition.write " +
        "https://www.googleapis.com/auth/fitness.sleep.read " +
        "https://www.googleapis.com/auth/fitness.sleep.write " +
        "https://www.googleapis.com/auth/fitness.location.read " +
        "https://www.googleapis.com/auth/fitness.blood_glucose.read " +
        "https://www.googleapis.com/auth/fitness.blood_pressure.read " +
        "https://www.googleapis.com/auth/fitness.heart_rate.read " +
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.read " +
        "https://www.googleapis.com/auth/fitness.reproductive_health.read"
    )
    
    # Memory Configuration
    USER_MEMORY_TABLE: str = os.getenv("USER_MEMORY_TABLE")
    USER_DAILY_LOG_SESSION_TABLE:str=os.getenv("USER_DAILY_LOG_SESSION_TABLE")
    GENERAL_SESSION_TABLE:str=os.getenv("GENERAL_SESSION_TABLE")
    
    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: Optional[str] = os.getenv("LANGFUSE_HOST")
    
    # OpenTelemetry Configuration
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_EXPORTER_OTLP_HEADERS: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Validate required settings
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")