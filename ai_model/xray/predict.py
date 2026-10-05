import torch
import torch.nn.functional as F
from PIL import Image
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_model.common.image_quality import validate_image_quality
from ai_model.common.utilities import check_image_modality_compatibility

try:
    from .config import *
    from .preprocessing import get_val_transforms
    from .train import create_model
    from .gradcam import GradCAM, overlay_heatmap
except ImportError:
    from config import *
    from preprocessing import get_val_transforms
    from train import create_model
    from gradcam import GradCAM, overlay_heatmap

def get_possible_finding_and_cause(predicted_class: str):
    """Returns standardized clinical wording required by specification."""
    if predicted_class == 'PNEUMONIA':
        finding = "Possible pneumonia pattern detected"
        cause = "The trained model identified image patterns within the lung region that contributed to the pneumonia-class prediction. Highlighted Grad-CAM regions indicate areas that influenced the model."
    else:  # NORMAL
        finding = "No pneumonia pattern detected by the model"
        cause = "The trained model did not identify opacity patterns typical of pneumonia within the analyzed lung regions."
    
    return finding, cause

def predict_xray(image_path: str, save_gradcam: bool = True, output_gradcam_dir: str = None) -> dict:
    if not os.path.exists(MODEL_SAVE_PATH):
        return {"error": "Chest X-Ray model unavailable. Checkpoint missing."}

    # 1. Quality Check
    quality = validate_image_quality(image_path)
    if not quality["imageValid"]:
        return {
            "imageValidation": quality,
            "error": quality["qualityReason"]
        }

    # 2. Modality Check
    modality_check = check_image_modality_compatibility(image_path, "X-RAY")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = create_model()
    model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
    model = model.to(device)
    model.eval()

    transform = get_val_transforms()
    img = Image.open(image_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = F.softmax(output, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)

    predicted_class = CLASSES[predicted_idx.item()]
    conf_val = float(confidence.item())
    conf_percentage = conf_val * 100.0

    possible_finding, possible_cause = get_possible_finding_and_cause(predicted_class)

    if conf_percentage >= 90.0:
        confidence_level = "High Model Confidence"
    elif conf_percentage >= 75.0:
        confidence_level = "Moderate Model Confidence"
    else:
        confidence_level = "Low Model Confidence"

    gradcam_path = None
    if save_gradcam:
        try:
            target_dir = output_gradcam_dir or GRADCAM_DIR
            os.makedirs(target_dir, exist_ok=True)
            gradcam_path = os.path.join(target_dir, f"xray_gradcam_{os.path.basename(image_path)}")
            
            target_layer = model.features.denseblock4.denselayer16.conv2
            cam = GradCAM(model, target_layer)
            heatmap = cam.generate(input_tensor, target_class=predicted_idx.item())
            overlay_heatmap(image_path, heatmap, gradcam_path)
        except Exception as e:
            print(f"[!] Grad-CAM generation error for X-Ray: {e}")
            gradcam_path = None

    return {
        "imageValidation": quality,
        "modalityCheck": modality_check,
        "prediction": predicted_class,
        "possibleFinding": possible_finding,
        "possibleCause": possible_cause,
        "confidence": round(conf_val, 4),
        "confidenceLevel": confidence_level,
        "model": "DenseNet121",
        "gradcamPath": gradcam_path
    }
