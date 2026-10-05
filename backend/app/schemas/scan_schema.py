from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScanCreate(BaseModel):
    patientId: str
    scanType: str

class ScanResponse(BaseModel):
    id: str
    scanId: str
    patientId: str
    userId: str
    scanType: str
    fileName: str
    filePath: str
    fileSize: int
    status: str
    uploadedAt: datetime
