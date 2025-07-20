from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Force reload of environment variables
load_dotenv(override=True)

class MinimalSettings(BaseSettings):
    # Include only essential settings
    PROJECT_NAME: str = "DietTracker"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

try:
    settings = MinimalSettings()
    print("Settings loaded successfully:")
    print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"SECRET_KEY: {settings.SECRET_KEY}")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"Error loading settings: {e}")
    import traceback
    traceback.print_exc()