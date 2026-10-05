from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("")
async def get_patients(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.get("userId") or str(current_user.get("_id", ""))
    
    patients_cursor = db.patients.find({"createdBy": user_id}, {'_id': 0}).sort("createdAt", -1)
    patients = await patients_cursor.to_list(length=100)
    
    result = []
    for p in patients:
        pid = p.get("patientId")
        scans_count = await db.scans.count_documents({"patientId": pid}) if pid else 0
        last_scan = await db.scans.find_one({"patientId": pid}, sort=[("uploadedAt", -1)]) if pid else None
        
        result.append({
            "patientId": pid,
            "patientName": p.get("patientName", "Unknown"),
            "age": p.get("age"),
            "gender": p.get("gender"),
            "createdAt": p.get("createdAt"),
            "totalScans": scans_count,
            "lastScanDate": last_scan["uploadedAt"] if last_scan else p.get("createdAt")
        })
        
    return result

@router.get("/{patient_id}")
async def get_patient_details(patient_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    patient = await db.patients.find_one({"patientId": patient_id}, {'_id': 0})
    if not patient and len(patient_id) == 24:
        patient = await db.patients.find_one({"_id": ObjectId(patient_id)}, {'_id': 0})
        
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    pid = patient.get("patientId")
    scans_cursor = db.scans.find({"patientId": pid}, {'_id': 0}).sort("uploadedAt", -1)
    scans = await scans_cursor.to_list(length=100)
    
    scan_history = []
    for s in scans:
        pred = await db.predictions.find_one({"scanId": s["scanId"]}, {'_id': 0})
        rep = await db.reports.find_one({"predictionId": pred["predictionId"]}, {'_id': 0}) if pred else None
        
        scan_history.append({
            "scanId": s["scanId"],
            "scanType": s.get("scanType"),
            "originalImage": s.get("filePath"),
            "date": s.get("uploadedAt"),
            "status": s.get("status"),
            "possibleFinding": pred.get("possibleFinding") if pred else "N/A",
            "confidence": pred.get("confidence") if pred else 0,
            "confidenceLevel": pred.get("confidenceLevel") if pred else "N/A",
            "reviewStatus": pred.get("reviewStatus") if pred else "Pending",
            "predictionId": pred.get("predictionId") if pred else None,
            "reportId": rep.get("reportId") if rep else None,
            "pdfUrl": rep.get("pdfUrl") if rep else None
        })
        
    return {
        "patient": patient,
        "scanHistory": scan_history
    }

