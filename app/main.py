from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.routes import users, medical_reports, google_health, meal_entry, daily_activity_summary, websocket, assessment_streaming
from app.core.config import settings
from app.db.base import Base, engine
from app.core.logging import setup_logger

# Set up logger
logger = setup_logger()

# Import and call create_tables script
from app.db.create_tables import create_all_tables
# Middleware imports moved to where they're used
from contextlib import asynccontextmanager

create_all_tables()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Starting up application...")
    
    # Check Redis connection
    from app.db.redis import check_redis_connection
    redis_connected = check_redis_connection()
    if not redis_connected:
        logger.warning("Redis is not available - some features may be limited")
    
    # This yields control back to FastAPI
    yield
    
    # Shutdown code
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG,
    description="DietGeniusAI API - A nutrition and diet management platform with Google Health integration",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication operations"
        },
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "medical-reports",
            "description": "Medical reports operations"
        },
        {
            "name": "google-health",
            "description": "Google Health API integration for fetching health and fitness data"
        },
        {
            "name": "meal-entries",
            "description": "Meal entries management for tracking meals and nutritional intake"
        },
        {
            "name": "daily-activity",
            "description": "Daily activity summary and assessment operations"
        },
        {
            "name": "assessment-streaming",
            "description": "Real-time assessment streaming with Server-Sent Events"
        }
    ],
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Improved SessionMiddleware settings for OAuth session reliability
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    same_site="lax",
    https_only=False  # Set to True in production with HTTPS
)

# Add custom middleware using decorator approach
from app.utils.logging_middleware import RequestLoggingMiddleware
from app.utils.debug_middleware import DebugMiddleware

# Add middleware using add_middleware method
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(DebugMiddleware)

logger.info(f"Session secret key: {settings.SECRET_KEY}")


# Include routers
from app.api.routes import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(medical_reports.router, prefix="/api/medical-reports", tags=["medical-reports"])
app.include_router(google_health.router, prefix="/api/google-health", tags=["google-health"])
app.include_router(meal_entry.router, prefix="/api/meal-entries", tags=["meal-entries"])
app.include_router(daily_activity_summary.router, prefix="/api/daily-activity", tags=["daily-activity"])
app.include_router(assessment_streaming.router, prefix="/api/assessment-streaming", tags=["assessment-streaming"])
app.include_router(websocket.router)

# Application is now using lifespan parameter for startup/shutdown events

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to DietGeniusAI"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/health/redis")
def redis_health_check():
    """Health check endpoint specifically for Redis connection"""
    from app.db.redis import check_redis_connection
    
    logger.info("Redis health check endpoint accessed")
    redis_connected = check_redis_connection()
    
    if redis_connected:
        return {"status": "healthy", "redis": "connected"}
    else:
        return {"status": "unhealthy", "redis": "disconnected"}