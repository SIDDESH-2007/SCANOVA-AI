from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid
import os
import shutil
import re

from app.api.auth import get_current_user
from app.database.mongodb import get_database

from app.services.models.xray_model_service import xray_model
from app.services.models.ct_model_service import ct_model
from app.services.models.mri_model_service import mri_model
from app.services.models.model_router import normalize_scan_type
from app.services.pdf_report_service import pdf_report_service

from app.utils.phone_utils import normalize_phone_number, normalize_patient_id

router = APIRouter()

@router.post("/analyze")
async def analyze_scan(
    patientName: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    scanType: str = Form(...),
    caseType: str = Form(...),
    patientId: Optional[str] = Form(None),
    phoneNumber: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("userId") or str(current_user.get("_id", "USER"))
    scanType = normalize_scan_type(scanType)
    caseType = caseType.upper()
    
    target_patient_id = normalize_patient_id(patientId) if patientId else None
    if not target_patient_id:
        target_patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"

    norm_phone = normalize_phone_number(phoneNumber) if phoneNumber else None
    if not norm_phone:
        raise HTTPException(
            status_code=400,
            detail="Valid phone number is required. Please enter a valid 10-digit mobile number."
        )
    
    # 1. Route to correct model service
    if scanType == "X-RAY":
        model_service = xray_model
    elif scanType == "CT":
        if not ct_model.is_loaded:
            raise HTTPException(status_code=400, detail="CT AI model is not connected yet.")
        model_service = ct_model
    elif scanType == "MRI":
        if not mri_model.is_loaded:
            raise HTTPException(status_code=400, detail="MRI AI model is not connected yet.")
        model_service = mri_model
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported scan type: {scanType}")

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".bmp", ".tif"]:
        if file_extension in [".dcm", ".dicom"]:
            raise HTTPException(status_code=400, detail="DICOM format detected. PNG/JPG conversion required.")
        raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(model_service.uploads_dir, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded image file.")
        
    db = get_database()
    
    # 2. Patient Record Handling with Phone Number Conflict Check
    now = datetime.utcnow()
    existing_patient = await db.patients.find_one({
        "patientId": {"$regex": f"^{re.escape(target_patient_id)}$", "$options": "i"}
    })

    if existing_patient:
        target_patient_id = existing_patient.get("patientId", target_patient_id)
        existing_phone = existing_patient.get("phoneNumber") or existing_patient.get("phone") or existing_patient.get("mobile")
        norm_existing_phone = normalize_phone_number(existing_phone) if existing_phone else None

        if norm_existing_phone and norm_existing_phone != norm_phone:
            raise HTTPException(
                status_code=400,
                detail="The entered phone number does not match the registered phone number for this Patient ID."
            )

        await db.patients.update_one(
            {"_id": existing_patient["_id"]},
            {
                "$set": {
                    "patientName": patientName,
                    "age": age,
                    "gender": gender,
                    "phoneNumber": norm_phone,
                    "caseType": caseType,
                    "updatedAt": now
                }
            }
        )
    else:
        new_patient_doc = {
            "patientId": target_patient_id,
            "patientName": patientName,
            "phoneNumber": norm_phone,
            "age": age,
            "gender": gender,
            "caseType": caseType,
            "createdBy": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        await db.patients.insert_one(new_patient_doc)

    patient = await db.patients.find_one({"patientId": target_patient_id})
    
    # 3. Create Scan Record
    scan_id = f"SCAN-{uuid.uuid4().hex[:8].upper()}"
    file_size = os.path.getsize(file_path)
    
    new_scan = {
        "scanId": scan_id,
        "patientId": target_patient_id,
        "userId": user_id,
        "scanType": scanType,
        "caseType": caseType,
        "fileName": file.filename,
        "filePath": f"/api/static/scans/{unique_filename}",
        "fileSize": file_size,
        "uploadedAt": datetime.utcnow(),
        "status": "PROCESSING"
    }
    await db.scans.insert_one(new_scan.copy())
    
    # 4. Model Inference
    analysis_result = model_service.analyze(file_path)
    
    if "error" in analysis_result:
        await db.scans.update_one({"scanId": scan_id}, {"$set": {"status": "FAILED"}})
        await db.notifications.insert_one({
            "notificationId": f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
            "userId": user_id,
            "type": "ANALYSIS_FAILED",
            "title": "Analysis Failed",
            "message": f"{scanType} analysis failed for patient {target_patient_id}.",
            "relatedPatientId": target_patient_id,
            "isRead": False,
            "createdAt": datetime.utcnow()
        })
        raise HTTPException(status_code=400, detail=analysis_result["error"])
        
    # Check Image Quality Validation
    img_valid = analysis_result.get("imageValidation", {}).get("imageValid", True)
    if not img_valid:
        await db.scans.update_one({"scanId": scan_id}, {"$set": {"status": "FAILED"}})
        reason = analysis_result.get("imageValidation", {}).get("qualityReason", "Image quality check failed.")
        raise HTTPException(status_code=400, detail=reason)

    # 5. Save Prediction to MongoDB
    prediction_id = f"PRED-{uuid.uuid4().hex[:8].upper()}"
    new_prediction = {
        "predictionId": prediction_id,
        "scanId": scan_id,
        "patientId": target_patient_id,
        "userId": user_id,
        "scanType": scanType,
        "model": analysis_result["model"],
        "predictedClass": analysis_result["prediction"],
        "confidence": analysis_result["confidence"],
        "confidenceLevel": analysis_result["confidenceLevel"],
        "possibleFinding": analysis_result["possibleFinding"],
        "possibleCause": analysis_result.get("possibleCause", "N/A"),
        "gradcamPath": analysis_result.get("gradcamUrl", None),
        "imageValidation": analysis_result.get("imageValidation", {}),
        "createdAt": datetime.utcnow(),
        "reviewStatus": "PENDING"
    }
    await db.predictions.insert_one(new_prediction.copy())
    await db.scans.update_one({"scanId": scan_id}, {"$set": {"status": "COMPLETED"}})
    
    # 6. Generate PDF Report
    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    abs_image_path = file_path
    abs_gradcam_path = None
    if analysis_result.get("gradcamUrl"):
        gradcam_filename = os.path.basename(analysis_result["gradcamUrl"])
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_gradcam_path = os.path.join(backend_dir, "generated", "gradcam", gradcam_filename)

    pdf_url = pdf_report_service.generate_report(
        report_id=report_id,
        patient={"patientId": target_patient_id, "patientName": patientName, "age": age, "gender": gender},
        scan=new_scan,
        prediction=new_prediction,
        image_path=abs_image_path,
        gradcam_path=abs_gradcam_path
    )
    
    if pdf_url:
        new_report = {
            "reportId": report_id,
            "predictionId": prediction_id,
            "patientId": target_patient_id,
            "userId": user_id,
            "pdfUrl": pdf_url,
            "createdAt": datetime.utcnow()
        }
        await db.reports.insert_one(new_report)
    
    # 7. Emergency Case Registration
    if caseType == "EMERGENCY":
        await db.emergency_cases.insert_one({
            "emergencyCaseId": f"EMG-{uuid.uuid4().hex[:8].upper()}",
            "patientId": target_patient_id,
            "scanId": scan_id,
            "predictionId": prediction_id,
            "scanType": scanType,
            "possibleFinding": analysis_result["possibleFinding"],
            "confidence": analysis_result["confidence"],
            "priority": "Critical",
            "userId": user_id,
            "createdAt": datetime.utcnow(),
            "reviewStatus": "PENDING"
        })
        
        await db.notifications.insert_one({
            "notificationId": f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
            "userId": user_id,
            "type": "EMERGENCY_ALERT",
            "title": "Emergency Scan Requires Review",
            "message": f"Patient {target_patient_id} has an emergency {scanType} analysis awaiting radiologist review.",
            "relatedPatientId": target_patient_id,
            "relatedReportId": report_id,
            "isRead": False,
            "createdAt": datetime.utcnow()
        })
    else:
        await db.notifications.insert_one({
            "notificationId": f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
            "userId": user_id,
            "type": "REPORT_GENERATED",
            "title": "Analysis Completed",
            "message": f"{scanType} analysis completed for patient {target_patient_id}.",
            "relatedPatientId": target_patient_id,
            "relatedReportId": report_id,
            "isRead": False,
            "createdAt": datetime.utcnow()
        })

    return {
        "success": True,
        "patient": {
            "patientId": target_patient_id,
            "patientName": patientName
        },
        "scan": {
            "scanId": scan_id,
            "scanType": scanType,
            "caseType": caseType,
            "url": f"/api/static/scans/{unique_filename}"
        },
        "imageValidation": analysis_result.get("imageValidation", {}),
        "analysis": {
            "predictionId": prediction_id,
            "prediction": analysis_result["prediction"],
            "possibleFinding": analysis_result["possibleFinding"],
            "possibleCause": analysis_result.get("possibleCause", "N/A"),
            "confidence": analysis_result["confidence"],
            "confidenceLevel": analysis_result["confidenceLevel"],
            "model": analysis_result["model"],
            "gradcamUrl": analysis_result.get("gradcamUrl", None)
        },
        "report": {
            "reportId": report_id if pdf_url else None,
            "pdfUrl": pdf_url
        },
        "reviewRequired": analysis_result["reviewRequired"]
    }

@router.get("/{prediction_id}")
async def get_prediction(prediction_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("userId") or str(current_user.get("_id", "USER"))
    db = get_database()
    prediction = await db.predictions.find_one({"predictionId": prediction_id, "userId": user_id}, {'_id': 0})
    if not prediction:
        # Fallback query without userId restriction if needed
        prediction = await db.predictions.find_one({"predictionId": prediction_id}, {'_id': 0})
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found.")
        
    patient = await db.patients.find_one({"patientId": prediction["patientId"]}, {'_id': 0})
    scan = await db.scans.find_one({"scanId": prediction["scanId"]}, {'_id': 0})
    report = await db.reports.find_one({"predictionId": prediction_id}, {'_id': 0})
    
    return {
        "prediction": prediction,
        "patient": patient,
        "scan": scan,
        "report": report
    }

@router.get("/")
async def get_predictions(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("userId") or str(current_user.get("_id", "USER"))
    db = get_database()
    predictions_cursor = db.predictions.find({"userId": user_id}, {'_id': 0}).sort("createdAt", -1)
    predictions = await predictions_cursor.to_list(length=100)
    
    result = []
    for pred in predictions:
        patient = await db.patients.find_one({"patientId": pred["patientId"]}, {'_id': 0, 'patientName': 1})
        pred['patientName'] = patient['patientName'] if patient else "Unknown"
        result.append(pred)
        
    return result
