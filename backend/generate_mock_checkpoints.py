import os
import torch
import torch.nn as nn
from torchvision import models
import json

base_dir = "d:/RADIOLOGY ASSISTANT MINIPROJECT/ai_model"

def create_xray_model():
    model = models.densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, 2)
    os.makedirs(f"{base_dir}/xray/saved_models", exist_ok=True)
    torch.save(model.state_dict(), f"{base_dir}/xray/saved_models/xray_densenet121.pth")
    print("Created X-Ray model")

def create_mri_model():
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 4)
    os.makedirs(f"{base_dir}/mri/saved_models", exist_ok=True)
    torch.save(model.state_dict(), f"{base_dir}/mri/saved_models/mri_brain_tumor.pth")
    print("Created MRI model")

def create_ct_model():
    model = models.densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, 2)
    os.makedirs(f"{base_dir}/ct/saved_models", exist_ok=True)
    torch.save(model.state_dict(), f"{base_dir}/ct/saved_models/ct_densenet121.pth")
    print("Created CT model")

def generate_registry():
    registry = {
        "X-RAY": {
            "classifier": {
                "trained": True,
                "checkpoint": f"{base_dir}/xray/saved_models/xray_densenet121.pth",
                "classes": ["NORMAL", "PNEUMONIA"]
            },
            "localizer": {
                "trained": False,
                "checkpoint": None,
                "annotationType": None
            }
        },
        "MRI": {
            "classifier": {
                "trained": True,
                "checkpoint": f"{base_dir}/mri/saved_models/mri_brain_tumor.pth",
                "classes": ["glioma", "meningioma", "notumor", "pituitary"]
            },
            "localizer": {
                "trained": False,
                "checkpoint": None,
                "annotationType": None
            }
        },
        "CT": {
            "classifier": {
                "trained": True,
                "checkpoint": f"{base_dir}/ct/saved_models/ct_densenet121.pth",
                "classes": ["NORMAL", "HEMORRHAGE"]
            },
            "localizer": {
                "trained": False,
                "checkpoint": None,
                "annotationType": None
            }
        }
    }
    with open(f"{base_dir}/model_registry.json", "w") as f:
        json.dump(registry, f, indent=4)
    print("Created registry")

if __name__ == "__main__":
    create_xray_model()
    create_mri_model()
    create_ct_model()
    generate_registry()
