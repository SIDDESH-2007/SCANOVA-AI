import os
import cv2
import numpy as np
from PIL import Image

def validate_image_quality(img_path: str) -> dict:
    """
    Validates medical image readability, resolution, contrast/blank state, and blurriness.
    Returns:
        dict: {
            "imageValid": bool,
            "qualityStatus": "Good" | "Moderate" | "Poor" | "Invalid",
            "qualityReason": str
        }
    """
    if not os.path.exists(img_path):
        return {
            "imageValid": False,
            "qualityStatus": "Invalid",
            "qualityReason": "Image file does not exist."
        }

    try:
        # 1. PIL verification (corruption check)
        with Image.open(img_path) as img:
            img.verify()
        
        # Re-open after verify() as PIL documentation recommends
        with Image.open(img_path) as img:
            width, height = img.size

        # 2. Resolution check
        if width < 50 or height < 50:
            return {
                "imageValid": False,
                "qualityStatus": "Invalid",
                "qualityReason": f"Image resolution is too low ({width}x{height}). Minimum required resolution is 50x50 pixels."
            }

        # 3. OpenCV grayscale loading & contrast check
        cv_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if cv_img is None:
            return {
                "imageValid": False,
                "qualityStatus": "Invalid",
                "qualityReason": "File corrupted or image format unreadable by OpenCV."
            }

        # 4. Variance check (blank image or extreme low contrast)
        pixel_variance = float(np.var(cv_img))
        if pixel_variance < 50.0:
            return {
                "imageValid": False,
                "qualityStatus": "Invalid",
                "qualityReason": "Image appears blank or has insufficient visual contrast for diagnostic analysis."
            }

        # 5. Blurriness check via Laplacian variance
        laplacian_var = float(cv2.Laplacian(cv_img, cv2.CV_64F).var())
        if laplacian_var < 45.0:
            return {
                "imageValid": False,
                "qualityStatus": "Invalid",
                "qualityReason": "Image is excessively blurry for reliable AI evaluation."
            }

        # 6. Quality Status Determination
        if laplacian_var > 300.0 and pixel_variance > 1000.0:
            quality_status = "Good"
            quality_reason = "Image meets clinical quality standards with sharp resolution and high contrast."
        elif laplacian_var > 100.0:
            quality_status = "Moderate"
            quality_reason = "Image quality is adequate for model inference."
        else:
            quality_status = "Poor"
            quality_reason = "Image exhibits slight blur or lower contrast; manual review recommended."

        return {
            "imageValid": True,
            "qualityStatus": quality_status,
            "qualityReason": quality_reason
        }

    except Exception as e:
        return {
            "imageValid": False,
            "qualityStatus": "Invalid",
            "qualityReason": f"Image verification error: {str(e)}"
        }
