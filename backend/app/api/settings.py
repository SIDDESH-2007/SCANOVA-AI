from fastapi import APIRouter, Depends, HTTPException, Body
from bson import ObjectId
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("/")
async def get_settings(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(current_user["_id"])}, {"passwordHash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "preferences": user.get("preferences", {}),
        "twoFactorEnabled": user.get("twoFactorEnabled", False)
    }

@router.put("/preferences")
async def update_preferences(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    # Simple merge of preferences
    user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    current_prefs = user.get("preferences", {})
    
    if "dashboard" in data:
        current_prefs["dashboard"] = {**current_prefs.get("dashboard", {}), **data["dashboard"]}
    if "dateFormat" in data:
        current_prefs["dateFormat"] = data["dateFormat"]
    if "notifications" in data:
        current_prefs["notifications"] = {**current_prefs.get("notifications", {}), **data["notifications"]}
        
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"preferences": current_prefs}}
    )
    return {"success": True, "preferences": current_prefs}

@router.put("/profile")
async def update_profile(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    db = get_database()
    updates = {}
    allowed_fields = ["fullName", "hospital", "department", "specialization", "phone"]
    for field in allowed_fields:
        if field in data:
            updates[field] = data[field]
            
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
        
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": updates}
    )
    return {"success": True, "message": "Profile updated successfully"}
