from app.core.config import settings
import os

# Print environment variable for debugging
print(f"Raw ALLOWED_ORIGINS env var: {os.getenv('ALLOWED_ORIGINS')}")

# Print parsed settings
print(f"Parsed ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
print(f"Type: {type(settings.ALLOWED_ORIGINS)}")

# Verify other settings are loading correctly
print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
print(f"FRONTEND_URL: {settings.FRONTEND_URL}")