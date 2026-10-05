import os
import sys
import logging
import torch

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_model.mri.predict import predict_mri
from ai_model.mri.config import MODEL_SAVE_PATH

logger = logging.getLogger("uvicorn")

class MRIModelService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        self.backend_dir = os.path.join(PROJECT_ROOT, "backend")
        self.gradcam_dir = os.path.join(self.backend_dir, "generated", "gradcam")
        self.uploads_dir = os.path.join(self.backend_dir, "uploads", "scans")
        os.makedirs(self.gradcam_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)

    def load_model(self):
        """Loads model ONCE during FastAPI startup."""
        if not os.path.exists(MODEL_SAVE_PATH):
            logger.warning("[MRI] model unavailable. Checkpoint missing at " + MODEL_SAVE_PATH)
            self.is_loaded = False
            return

        try:
            self.is_loaded = True
            logger.info("[MRI] EfficientNet-B0 model loaded successfully on " + str(self.device))
        except Exception as e:
            logger.error(f"Error loading MRI model: {e}")
            self.is_loaded = False

    def analyze(self, image_path: str) -> dict:
        if not self.is_loaded and not os.path.exists(MODEL_SAVE_PATH):
            return {"error": "MRI AI model is unavailable. Checkpoint missing."}

        try:
            res = predict_mri(image_path, save_gradcam=True, output_gradcam_dir=self.gradcam_dir)
            if "error" in res:
                return res

            gradcam_url = None
            if res.get("gradcamPath"):
                filename = os.path.basename(res["gradcamPath"])
                gradcam_url = f"/api/static/gradcam/{filename}"

            return {
                "imageValidation": res.get("imageValidation", {}),
                "modalityCheck": res.get("modalityCheck", {}),
                "prediction": res["prediction"],
                "possibleFinding": res["possibleFinding"],
                "possibleCause": res["possibleCause"],
                "confidence": res["confidence"],
                "confidenceLevel": res["confidenceLevel"],
                "model": res["model"],
                "reviewRequired": (res["confidence"] < 0.75),
                "gradcamUrl": gradcam_url
            }
        except Exception as e:
            logger.error(f"MRI analysis failure: {e}")
            return {"error": f"MRI AI analysis failed: {str(e)}"}

mri_model = MRIModelService()
