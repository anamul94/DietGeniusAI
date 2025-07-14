from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.routes import users, medical_reports, google_health
from app.core.config import settings
from app.db.base import Base, engine
from app.core.logging import setup_logger

# Set up logger
logger = setup_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

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
        }
    ],
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Improved SessionMiddleware settings for OAuth session reliability
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    same_site="lax",
    https_only=False # Set to True in production with HTTPS
)
logger.info(f"Session secret key: {settings.SECRET_KEY}")

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
from app.api.routes import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(medical_reports.router, prefix="/api/medical-reports", tags=["medical-reports"])
app.include_router(google_health.router, prefix="/api/google-health", tags=["google-health"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to DietGeniusAI"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}