from fastapi import APIRouter

from app.api.routes import auth, users, medical_reports, google_health, meal_entry

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(medical_reports.router, prefix="/medical-reports", tags=["medical-reports"])
api_router.include_router(google_health.router, prefix="/google-health", tags=["google-health"])
api_router.include_router(meal_entry.router, prefix="/meal-entries", tags=["meal-entries"])
