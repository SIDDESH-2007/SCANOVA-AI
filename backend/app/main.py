from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, patients, scans, analytics, dashboard, predictions, reports, emergency, settings, notifications
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.services.models.xray_model_service import xray_model
from app.services.models.mri_model_service import mri_model
from app.services.models.ct_model_service import ct_model
import os
import logging

from contextlib import asynccontextmanager

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Load all 3 trained models ONCE on application startup
    logger.info("Initializing medical AI models...")
    xray_model.load_model()
    mri_model.load_model()
    ct_model.load_model()
    
    yield
    await close_mongo_connection()

app = FastAPI(title="Radiology AI Diagnosis API", lifespan=lifespan)

# Static file mounts
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(backend_dir, "generated", "gradcam"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "uploads", "scans"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "generated", "reports"), exist_ok=True)

app.mount("/api/static/gradcam", StaticFiles(directory=os.path.join(backend_dir, "generated", "gradcam")), name="gradcam")
app.mount("/api/static/scans", StaticFiles(directory=os.path.join(backend_dir, "uploads", "scans")), name="scans")
app.mount("/api/static/reports", StaticFiles(directory=os.path.join(backend_dir, "generated", "reports")), name="reports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["Emergency"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
def root():
    return {"message": "Welcome to Radiology AI Diagnosis API"}

@app.get("/api/health")
@app.get("/health")
def health_check():
    xray_status = "loaded" if xray_model.is_loaded else "unavailable"
    return {
        "status": "ok",
        "database": "RADIOLOGY",
        "xrayModel": xray_status
    }
