import asyncio
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from app.database.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.services.models.xray_model_service import xray_model
from app.services.models.mri_model_service import mri_model
from app.services.models.ct_model_service import ct_model

async def run_test():
    await connect_to_mongo()
    db = get_database()
    print("[+] Database connected:", db.name)
    
    xray_model.load_model()
    mri_model.load_model()
    ct_model.load_model()
    
    # Test X-Ray
    xray_res = xray_model.analyze("../datasets/xray/test/NORMAL/sample_NORMAL_1.jpg")
    print("[✓] X-Ray Prediction:", xray_res.get("prediction"), "| Confidence:", xray_res.get("confidence"))
    
    # Test MRI
    mri_res = mri_model.analyze("../datasets/mri/Testing/glioma/sample_glioma_1.jpg")
    print("[✓] MRI Prediction:", mri_res.get("prediction"), "| Confidence:", mri_res.get("confidence"))
    
    # Test CT
    ct_res = ct_model.analyze("../datasets/ct/test/HEMORRHAGE/sample_HEMORRHAGE_1.jpg")
    print("[✓] CT Prediction:", ct_res.get("prediction"), "| Confidence:", ct_res.get("confidence"))
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(run_test())
