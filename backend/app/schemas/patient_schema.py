from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PatientCreate(BaseModel):
    patientName: str
    age: int
    gender: str
    phoneNumber: Optional[str] = None

class PatientResponse(PatientCreate):
    id: str
    patientId: Optional[str] = None
    createdBy: str
    createdAt: datetime
