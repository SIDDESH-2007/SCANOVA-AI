import os
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.utils.phone_utils import normalize_phone_number, normalize_patient_id
from app.services.pdf_report_service import pdf_report_service

logger = logging.getLogger(__name__)

_mongo_client = None

def get_bot_db():
    global _mongo_client
    if _mongo_client is None:
        mongo_url = os.getenv("MONGODB_URL", settings.MONGODB_URL)
        _mongo_client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DATABASE_NAME", settings.DATABASE_NAME)
    return _mongo_client[db_name]

async def verify_patient(patient_id_input: str, phone_input: str) -> Optional[Dict[str, Any]]:
    """
    Verifies patient by patientId AND phoneNumber against RADIOLOGY.patients collection.
    Both fields must belong to the SAME document.
    """
    if not patient_id_input or not phone_input:
        return None

    pid_clean = normalize_patient_id(patient_id_input)
    norm_phone = normalize_phone_number(phone_input)

    if not pid_clean or not norm_phone:
        logger.warning(f"Invalid verification input: patientId='{patient_id_input}', phone='{phone_input}'")
        return None

    db = get_bot_db()
    
    # Query patientId (case-insensitive) AND normalized phoneNumber together
    patient = await db.patients.find_one({
        "patientId": {"$regex": f"^{re.escape(pid_clean)}$", "$options": "i"},
        "phoneNumber": norm_phone
    })
    
    if patient:
        logger.info(f"Patient verification successful for patientId='{patient.get('patientId')}'")
    else:
        logger.warning(f"Patient verification failed for patientId='{pid_clean}', phone='{norm_phone}'")
        
    return patient

async def get_patient_reports(patient_id: str) -> List[Dict[str, Any]]:
    """
    Queries RADIOLOGY.reports for the verified patientId, sorted latest first.
    """
    db = get_bot_db()
    pid_clean = patient_id.strip()

    reports_cursor = db.reports.find({
        "patientId": {"$regex": f"^{re.escape(pid_clean)}$", "$options": "i"}
    }).sort("createdAt", -1)

    reports = await reports_cursor.to_list(length=100)

    result = []
    for r in reports:
        pred_id = r.get("predictionId")
        prediction = await db.predictions.find_one({"predictionId": pred_id}) if pred_id else None
        
        scan_id = r.get("scanId") or (prediction.get("scanId") if prediction else None)
        scan = await db.scans.find_one({"scanId": scan_id}) if scan_id else None

        created_dt = r.get("createdAt")
        formatted_date = created_dt.strftime("%d %b %Y") if isinstance(created_dt, datetime) else "N/A"

        scan_type = (scan.get("scanType") if scan else (prediction.get("scanType") if prediction else "X-Ray")).upper()

        result.append({
            "reportId": r.get("reportId"),
            "predictionId": r.get("predictionId"),
            "patientId": r.get("patientId"),
            "scanType": scan_type,
            "pdfUrl": r.get("pdfUrl"),
            "createdAt": created_dt,
            "formattedDate": formatted_date,
            "prediction": prediction,
            "scan": scan
        })

    logger.info(f"Loaded {len(result)} reports for patient '{pid_clean}'")
    return result

async def get_report_details(report_id: str, verified_patient_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves report summary details.
    RE-VERIFIES report.patientId matches the verified session patientId.
    """
    db = get_bot_db()
    r_clean = report_id.strip()
    pid_clean = verified_patient_id.strip()

    # Security check: Ensure report belongs to verified patient
    report = await db.reports.find_one({
        "reportId": {"$regex": f"^{re.escape(r_clean)}$", "$options": "i"},
        "patientId": {"$regex": f"^{re.escape(pid_clean)}$", "$options": "i"}
    })

    if not report:
        logger.warning(f"Unauthorized report access attempt: reportId='{r_clean}' for patientId='{pid_clean}'")
        return None

    prediction = await db.predictions.find_one({"predictionId": report.get("predictionId")})
    scan_id = report.get("scanId") or (prediction.get("scanId") if prediction else None)
    scan = await db.scans.find_one({"scanId": scan_id}) if scan_id else None
    patient = await db.patients.find_one({"patientId": {"$regex": f"^{re.escape(pid_clean)}$", "$options": "i"}})

    created_dt = report.get("createdAt")
    formatted_date = created_dt.strftime("%d/%m/%Y") if isinstance(created_dt, datetime) else "N/A"

    confidence = prediction.get("confidence", 0) if prediction else 0
    if isinstance(confidence, (int, float)):
        conf_val = float(confidence)
        confidence_pct = conf_val * 100 if conf_val <= 1.0 else conf_val
    else:
        confidence_pct = 0.0

    review_status = prediction.get("reviewStatus", "Pending Radiologist Review") if prediction else "Pending Radiologist Review"
    if review_status == "PENDING":
        review_status = "Pending Radiologist Review"
    elif review_status == "COMPLETED" or review_status == "REVIEWED":
        review_status = "Reviewed by Radiologist"

    return {
        "reportId": report.get("reportId"),
        "predictionId": report.get("predictionId"),
        "patientId": patient.get("patientId") if patient else verified_patient_id,
        "patientName": patient.get("patientName") if patient else "N/A",
        "scanType": (scan.get("scanType") if scan else (prediction.get("scanType") if prediction else "X-Ray")).upper(),
        "createdDate": formatted_date,
        "reviewStatus": review_status,
        "possibleFinding": prediction.get("possibleFinding", "No significant abnormality detected") if prediction else "N/A",
        "confidencePct": f"{confidence_pct:.2f}%",
        "pdfUrl": report.get("pdfUrl"),
        "report": report,
        "scan": scan,
        "prediction": prediction,
        "patient": patient
    }

async def get_report_pdf_path(report_id: str, verified_patient_id: str) -> Optional[str]:
    """
    Resolves the actual PDF file on disk.
    If missing, attempts to regenerate from stored database records.
    """
    details = await get_report_details(report_id, verified_patient_id)
    if not details:
        return None

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    reports_dir = os.path.join(backend_dir, "generated", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    pdf_url = details.get("pdfUrl")
    if pdf_url:
        filename = os.path.basename(pdf_url)
        possible_path = os.path.join(reports_dir, filename)
        if os.path.exists(possible_path):
            return possible_path

    # Check standard naming convention Radiology_Report_{patientId}_{reportId}.pdf
    clean_pid = details["patientId"].replace("-", "")
    clean_rid = details["reportId"].replace("-", "")
    std_filename = f"Radiology_Report_{clean_pid}_{clean_rid}.pdf"
    std_path = os.path.join(reports_dir, std_filename)
    if os.path.exists(std_path):
        return std_path

    # Look for any matching PDF in reports_dir containing report_id
    for f in os.listdir(reports_dir):
        if f.endswith(".pdf") and details["reportId"].replace("-", "") in f.replace("-", ""):
            return os.path.join(reports_dir, f)

    # File missing: Attempt regeneration from stored database data
    logger.info(f"PDF missing on disk for report '{report_id}'. Attempting regeneration...")
    try:
        report = details["report"]
        prediction = details["prediction"]
        scan = details["scan"]
        patient = details["patient"]

        if not prediction or not scan or not patient:
            logger.error("Cannot regenerate report: missing underlying prediction/scan/patient records")
            return None

        # Resolve image path
        image_path = None
        if scan.get("filePath"):
            rel_path = scan["filePath"].replace("/api/static/scans/", "")
            image_path = os.path.join(backend_dir, "uploads", "scans", os.path.basename(rel_path))

        gradcam_path = None
        if prediction and prediction.get("gradcamPath"):
            rel_grad = prediction["gradcamPath"].replace("/api/static/gradcam/", "")
            gradcam_path = os.path.join(backend_dir, "generated", "gradcam", os.path.basename(rel_grad))

        new_pdf_url = pdf_report_service.generate_report(
            report_id=details["reportId"],
            patient=patient,
            scan=scan,
            prediction=prediction,
            image_path=image_path if (image_path and os.path.exists(image_path)) else None,
            gradcam_path=gradcam_path if (gradcam_path and os.path.exists(gradcam_path)) else None
        )

        if new_pdf_url:
            gen_filename = os.path.basename(new_pdf_url)
            gen_path = os.path.join(reports_dir, gen_filename)
            if os.path.exists(gen_path):
                return gen_path
    except Exception as e:
        logger.error(f"Failed to regenerate PDF report: {e}")

    return None
