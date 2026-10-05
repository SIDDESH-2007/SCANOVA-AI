from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.api.auth import get_current_user
from app.database.mongodb import get_database

from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/")
async def get_reports(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.get("userId") or str(current_user.get("_id", ""))
    reports_cursor = db.reports.find({"userId": user_id}, {'_id': 0}).sort("createdAt", -1)
    reports = await reports_cursor.to_list(length=100)
    
    result = []
    for report in reports:
        patient = await db.patients.find_one({"patientId": report["patientId"]}, {'_id': 0, 'patientName': 1})
        prediction = await db.predictions.find_one({"predictionId": report["predictionId"]}, {'_id': 0})
        
        if prediction:
            result.append({
                "reportId": report["reportId"],
                "patientId": report.get("patientId"),
                "patientName": patient['patientName'] if patient else "Unknown",
                "scanType": prediction.get("scanType", "Unknown"),
                "possibleFinding": prediction.get("possibleFinding", "Unknown"),
                "confidence": prediction.get("confidence", 0),
                "caseType": prediction.get("caseType", "NORMAL"),
                "createdAt": report["createdAt"],
                "reviewStatus": prediction.get("reviewStatus", "Pending"),
                "pdfUrl": report["pdfUrl"]
            })
            
    return result

@router.get("/{report_id}/pdf")
async def download_pdf_report(report_id: str):
    db = get_database()
    report = await db.reports.find_one({"reportId": report_id}, {'_id': 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report record not found.")
        
    pdf_url = report.get("pdfUrl")
    if not pdf_url:
        raise HTTPException(status_code=404, detail="PDF file URL missing.")
        
    filename = os.path.basename(pdf_url)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(backend_dir, "generated", "reports", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF report file does not exist.")
        
    patient_id = report.get("patientId", "PATIENT")
    download_filename = f"Radiology_Report_{patient_id}_{report_id}.pdf"
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=download_filename
    )

