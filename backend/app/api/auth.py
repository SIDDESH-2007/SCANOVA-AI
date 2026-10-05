from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import datetime
from bson import ObjectId
import pyotp
from app.schemas.auth_schema import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "fullName": user["fullName"],
        "email": user["email"],
        "hospital": user["hospital"],
        "department": user["department"],
        "specialization": user["specialization"],
        "phone": user["phone"],
        "createdAt": user["createdAt"],
        "twoFactorEnabled": user.get("twoFactorEnabled", False),
        "preferences": user.get("preferences", {})
    }

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = get_database()
    
    # Check if email exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
        
    user_dict = user.dict(exclude={"password"})
    user_dict["passwordHash"] = get_password_hash(user.password)
    user_dict["createdAt"] = datetime.utcnow()
    user_dict["twoFactorEnabled"] = False
    user_dict["twoFactorSecret"] = None
    user_dict["preferences"] = {
        "dashboard": {
            "showRecentScans": True,
            "showScanDistribution": True,
            "showEmergencySummary": True,
            "showPendingReviews": True
        },
        "dateFormat": "DD/MM/YYYY",
        "notifications": {
            "systemNotifications": True,
            "emergencyAlerts": True,
            "reportAlerts": True,
            "pendingReviewAlerts": True
        }
    }
    
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    
    return user_helper(new_user)

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    db = get_database()
    
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    if user.get("twoFactorEnabled"):
        return {
            "requiresTwoFactor": True,
            "userId": str(user["_id"])
        }
        
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_helper(user)
    }

@router.post("/2fa/verify-login", response_model=TokenResponse)
async def verify_login_2fa(data: dict = Body(...)):
    user_id = data.get("userId")
    token = data.get("token")
    if not user_id or not token:
        raise HTTPException(status_code=400, detail="Missing user ID or token")
        
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("twoFactorEnabled"):
        raise HTTPException(status_code=400, detail="2FA not enabled or user not found")
        
    totp = pyotp.TOTP(user["twoFactorSecret"])
    if not totp.verify(token):
        raise HTTPException(status_code=401, detail="Invalid 2FA token")
        
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_helper(user)
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return user_helper(current_user)

@router.post("/2fa/setup")
async def setup_2fa(current_user: dict = Depends(get_current_user)):
    db = get_database()
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=current_user["email"], issuer_name="RadiologyAssistant")
    
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"tempTwoFactorSecret": secret}}
    )
    
    return {"secret": secret, "qrUri": provisioning_uri}

@router.post("/2fa/verify-setup")
async def verify_setup_2fa(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
        
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    secret = user.get("tempTwoFactorSecret")
    if not secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
        
    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        raise HTTPException(status_code=400, detail="Invalid 2FA token")
        
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {
            "$set": {"twoFactorEnabled": True, "twoFactorSecret": secret},
            "$unset": {"tempTwoFactorSecret": ""}
        }
    )
    
    return {"success": True, "message": "2FA enabled successfully"}

@router.post("/2fa/disable")
async def disable_2fa(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    password = data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required to disable 2FA")
        
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    if not verify_password(password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid password")
        
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"twoFactorEnabled": False, "twoFactorSecret": None}}
    )
    
    return {"success": True, "message": "2FA disabled successfully"}
