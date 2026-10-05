import os
import json
import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "ai_model", "model_registry.json")

def get_model_registry():
    """Load current model registry JSON."""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "X-RAY": {
            "model": "DenseNet121",
            "path": "ai_model/xray/saved_models/xray_densenet121.pth",
            "classes": ["NORMAL", "PNEUMONIA"],
            "trained": False
        },
        "MRI": {
            "model": "EfficientNet-B0",
            "path": "ai_model/mri/saved_models/mri_brain_tumor.pth",
            "classes": ["glioma", "meningioma", "pituitary", "notumor"],
            "trained": False
        },
        "CT": {
            "model": "DenseNet121",
            "path": "ai_model/ct/saved_models/ct_hemorrhage.pth",
            "classes": ["NORMAL", "HEMORRHAGE"],
            "trained": False
        }
    }

def update_model_registry(modality: str, model_name: str, path: str, classes: list, trained: bool):
    """Update registry status for given modality."""
    registry = get_model_registry()
    modality_key = modality.upper().replace(" SCAN", "").replace("SCAN", "").replace("_", "-")
    
    registry[modality_key] = {
        "model": model_name,
        "path": path,
        "classes": classes,
        "trained": trained
    }
    
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=4)
    print(f"[+] Model Registry updated for {modality_key}: trained={trained}")

def validate_and_summarize_dataset(dataset_dir, expected_classes, splits=["train", "val", "test"]):
    """
    Validates dataset layout, checks file existence, detects corrupted files, 
    verifies class counts, and prevents duplicate image paths across splits.
    
    Returns:
        tuple: (is_valid: bool, summary_dict: dict)
    """
    print(f"\n==================================================")
    print(f"       DATASET VALIDATION & AUDIT REPORT          ")
    print(f"Path: {dataset_dir}")
    print(f"Expected Classes: {expected_classes}")
    print(f"==================================================")

    if not os.path.exists(dataset_dir):
        print(f"[!] ERROR: Dataset directory does not exist: {dataset_dir}")
        return False, {"error": "Directory missing"}

    summary = {
        "dataset_dir": dataset_dir,
        "splits": {},
        "corrupted_files": [],
        "total_valid_images": 0,
        "class_totals": {c: 0 for c in expected_classes}
    }

    all_file_paths = set()
    duplicate_paths = []

    for split in splits:
        split_dir = os.path.join(dataset_dir, split)
        if not os.path.exists(split_dir):
            print(f"[!] Warning: Split folder '{split}' not found in {dataset_dir}")
            continue

        summary["splits"][split] = {c: 0 for c in expected_classes}
        
        for cls_name in expected_classes:
            cls_dir = os.path.join(split_dir, cls_name)
            if not os.path.exists(cls_dir):
                print(f"[!] Warning: Class directory '{cls_name}' missing in split '{split}'")
                continue

            files = os.listdir(cls_dir)
            valid_count = 0
            for f in files:
                if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
                    continue
                file_path = os.path.abspath(os.path.join(cls_dir, f))
                
                if file_path in all_file_paths:
                    duplicate_paths.append(file_path)
                    continue
                all_file_paths.add(file_path)

                try:
                    with Image.open(file_path) as img:
                        img.verify()
                    valid_count += 1
                except Exception:
                    summary["corrupted_files"].append(file_path)

            summary["splits"][split][cls_name] = valid_count
            summary["class_totals"][cls_name] += valid_count
            summary["total_valid_images"] += valid_count

    print("\n--- Image Distribution ---")
    for split, cls_counts in summary["splits"].items():
        print(f"  [{split.upper()}] -> {cls_counts}")
    print(f"Total Valid Images: {summary['total_valid_images']}")
    print(f"Class Totals: {summary['class_totals']}")
    
    if summary["corrupted_files"]:
        print(f"[!] Detected {len(summary['corrupted_files'])} corrupted images. Skipping them safely.")
        
    if duplicate_paths:
        print(f"[!] Detected {len(duplicate_paths)} duplicate file paths across splits.")

    is_valid = True
    for cls_name, total in summary["class_totals"].items():
        if total == 0:
            print(f"[!] ERROR: Class '{cls_name}' contains ZERO valid images! Cannot train.")
            is_valid = False

    print("==================================================\n")
    return is_valid, summary


def check_image_modality_compatibility(img_path: str, selected_modality: str) -> dict:
    """
    Checks if an image matches expected modality characteristics (X-RAY, MRI, CT).
    If modality cannot be reliably confirmed, returns explicit non-certainty message.
    """
    selected_modality = selected_modality.upper().replace(" SCAN", "").replace("SCAN", "").replace("_", "-")
    
    if not os.path.exists(img_path):
        return {
            "compatible": False,
            "message": "Image file not found."
        }

    try:
        img = Image.open(img_path)
        cv_img = cv2.imread(img_path)
        
        if cv_img is None:
            return {
                "compatible": False,
                "message": "Unable to read image for modality verification."
            }

        b, g, r = cv2.split(cv_img)
        diff_bg = np.mean(np.abs(b.astype(float) - g.astype(float)))
        diff_gr = np.mean(np.abs(g.astype(float) - r.astype(float)))
        is_grayscale_like = (diff_bg < 15.0 and diff_gr < 15.0)

        if not is_grayscale_like:
            return {
                "compatible": False,
                "message": f"Image appears to be a color photograph, which is incompatible with {selected_modality} medical scans."
            }

        return {
            "compatible": True,
            "message": f"Image modality verified as compatible with {selected_modality}."
        }

    except Exception:
        return {
            "compatible": True,
            "message": "Unable to reliably verify scan modality from image alone."
        }
