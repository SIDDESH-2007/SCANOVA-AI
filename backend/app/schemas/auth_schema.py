from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    fullName: str
    email: EmailStr
    hospital: str
    department: str
    specialization: str
    phone: str
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    fullName: str
    email: EmailStr
    hospital: str
    department: str
    specialization: str
    phone: str
    createdAt: datetime
    twoFactorEnabled: Optional[bool] = False
    preferences: Optional[Dict[str, Any]] = None

class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[UserResponse] = None
    requiresTwoFactor: Optional[bool] = False
    userId: Optional[str] = None
