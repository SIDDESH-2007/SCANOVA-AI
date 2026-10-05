from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from datetime import datetime
from bson import ObjectId
import uuid
import os
import shutil
from app.schemas.scan_schema import ScanResponse
from app.core.dependencies import get_current_user
from app.database.mongodb import get_database

from app.utils.normalization import normalize_scan_type

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def scan_helper(scan) -> dict:
    return {
        "id": str(scan["_id"]),
        "scanId": scan["scanId"],
        "patientId": str(scan["patientId"]),
        "userId": str(scan["userId"]),
        "scanType": scan["scanType"],
        "fileName": scan["fileName"],
        "filePath": scan["filePath"],
        "fileSize": scan["fileSize"],
        "status": scan["status"],
        "uploadedAt": scan["uploadedAt"]
    }

@router.post("/upload", response_model=ScanResponse)
async def upload_scan(
    patientName: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    scanType: str = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    db = get_database()
    
    # Validation & Normalization
    scanType = normalize_scan_type(scanType)
    if scanType not in ["X-RAY", "CT", "MRI", "ULTRASOUND"]:
        raise HTTPException(status_code=400, detail="Unsupported scan type.")

        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "dcm", "dicom"]:
         raise HTTPException(status_code=400, detail="Invalid file type")

    # Patient lookup or creation
    patient = await db.patients.find_one({
        "patientName": patientName, 
        "createdBy": current_user["_id"]
    })
    
    if not patient:
        patient_dict = {
            "patientName": patientName,
            "age": age,
            "gender": gender,
            "createdBy": current_user["_id"],
            "createdAt": datetime.utcnow()
        }
        result = await db.patients.insert_one(patient_dict)
        patient_id = result.inserted_id
    else:
        patient_id = patient["_id"]

    # File saving
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    
    # Save Scan metadata
    scan_id_str = f"SCN-{file_id[:8].upper()}"
    scan_dict = {
        "scanId": scan_id_str,
        "patientId": patient_id,
        "userId": current_user["_id"],
        "scanType": scanType.upper(),
        "fileName": file.filename,
        "filePath": file_path,
        "fileSize": file_size,
        "status": "UPLOADED",
        "uploadedAt": datetime.utcnow()
    }
    
    scan_result = await db.scans.insert_one(scan_dict)
    
    # Add Notification
    notification_dict = {
        "userId": current_user["_id"],
        "title": "Scan Uploaded",
        "message": f"A new {scanType.upper()} scan for {patientName} has been uploaded successfully.",
        "read": False,
        "createdAt": datetime.utcnow()
    }
    await db.notifications.insert_one(notification_dict)
    
    new_scan = await db.scans.find_one({"_id": scan_result.inserted_id})
    return scan_helper(new_scan)

@router.get("", response_model=List[ScanResponse])
async def get_scans(current_user = Depends(get_current_user)):
    db = get_database()
    scans_cursor = db.scans.find({"userId": current_user["_id"]}).sort("uploadedAt", -1)
    scans = await scans_cursor.to_list(length=100)
    return [scan_helper(scan) for scan in scans]
