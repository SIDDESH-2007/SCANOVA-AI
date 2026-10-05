from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.get("userId") or str(current_user.get("_id", ""))
    
    cursor = db.notifications.find({"userId": user_id}, {'_id': 0}).sort("createdAt", -1).limit(50)
    notifications = await cursor.to_list(length=50)
    
    return notifications

@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.get("userId") or str(current_user.get("_id", ""))
    
    result = await db.notifications.update_one(
        {"notificationId": notification_id, "userId": user_id},
        {"$set": {"isRead": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found or already read")
        
    return {"success": True}

@router.put("/read-all")
async def mark_all_as_read(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.get("userId") or str(current_user.get("_id", ""))
    
    await db.notifications.update_many(
        {"userId": user_id, "isRead": False},
        {"$set": {"isRead": True}}
    )
    
    return {"success": True}
