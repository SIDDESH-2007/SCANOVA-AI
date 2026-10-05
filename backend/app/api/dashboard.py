from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    db = get_database()
    
    user_id_str = current_user.get("userId") or str(current_user.get("_id", ""))
    user_id_obj = current_user.get("_id")
    user_query = {"$in": [user_id_str, user_id_obj]}
    
    # Dashboard counts using exact criteria
    total_patients = await db.patients.count_documents({"createdBy": user_query})
    total_scans = await db.scans.count_documents({"userId": user_query})
    
    xray_scans = await db.scans.count_documents({"userId": user_query, "scanType": "X-RAY"})
    ct_scans = await db.scans.count_documents({"userId": user_query, "scanType": "CT"})
    mri_scans = await db.scans.count_documents({"userId": user_query, "scanType": "MRI"})
    ultrasound_scans = await db.scans.count_documents({"userId": user_query, "scanType": "ULTRASOUND"})
    
    total_reports = await db.reports.count_documents({"userId": user_query})
    emergency_cases = await db.emergency_cases.count_documents({"userId": user_query})
    pending_reviews = await db.predictions.count_documents({"userId": user_query, "reviewStatus": {"$regex": "Pending", "$options": "i"}})
    
    # Recent scans for the dashboard UI
    scans_cursor = db.scans.find({"userId": user_query}).sort("uploadedAt", -1).limit(5)
    recent_scans = await scans_cursor.to_list(length=5)
    
    from bson import ObjectId
    for scan in recent_scans:
        patient_id = scan.get("patientId")
        patient = None
        if isinstance(patient_id, ObjectId):
            patient = await db.patients.find_one({"_id": patient_id}, {"_id": 0, "patientName": 1})
        elif isinstance(patient_id, str):
            patient = await db.patients.find_one({"patientId": patient_id}, {"_id": 0, "patientName": 1})
            if not patient and len(patient_id) == 24:
                try:
                    patient = await db.patients.find_one({"_id": ObjectId(patient_id)}, {"_id": 0, "patientName": 1})
                except Exception:
                    pass
                    
        scan["patientName"] = patient["patientName"] if patient else "Unknown"
        scan["date"] = scan.get("uploadedAt")
        if "_id" in scan:
            del scan["_id"]

    return {
        "totalPatients": total_patients,
        "totalScans": total_scans,
        "xrayScans": xray_scans,
        "ctScans": ct_scans,
        "mriScans": mri_scans,
        "ultrasoundScans": ultrasound_scans,
        "totalReports": total_reports,
        "emergencyCases": emergency_cases,
        "pendingReviews": pending_reviews,
        "recentScans": recent_scans
    }
