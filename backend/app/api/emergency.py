from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("")
async def get_emergency_cases(current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    user_id_str = current_user.get("userId") or str(current_user.get("_id", ""))
    user_id_obj = current_user.get("_id")
    user_query = {"$in": [user_id_str, user_id_obj]}
    
    cases_cursor = db.emergency_cases.find({"userId": user_query}, {'_id': 0}).sort("createdAt", -1)
    cases = await cases_cursor.to_list(length=100)
    
    result = []
    for case in cases:
        patient = await db.patients.find_one({"patientId": case["patientId"]}, {'_id': 0, 'patientName': 1})
        
        result.append({
            "emergencyCaseId": case["emergencyCaseId"],
            "predictionId": case.get("predictionId"),
            "patientId": case["patientId"],
            "patientName": patient['patientName'] if patient else "Unknown",
            "scanType": case["scanType"],
            "possibleFinding": case["possibleFinding"],
            "confidence": case["confidence"],
            "priority": case["priority"],
            "createdAt": case["createdAt"],
            "reviewStatus": case["reviewStatus"]
        })
            
    return result
