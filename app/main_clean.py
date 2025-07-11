from fastapi import FastAPI
from app.api.routes import medical_reports

app = FastAPI(title="DietGeniusAI", version="1.0.0")

app.include_router(medical_reports.router, prefix="/api/medical-reports", tags=["medical-reports"])

@app.get("/")
def root():
    return {"message": "Welcome to DietGeniusAI"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}