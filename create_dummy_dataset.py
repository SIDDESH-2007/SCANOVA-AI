import os
import numpy as np
from PIL import Image

def create_dirs(base_path, splits, classes):
    for split in splits:
        for cls in classes:
            path = os.path.join(base_path, split, cls)
            os.makedirs(path, exist_ok=True)
            
            # Create a few dummy images
            for i in range(5): # 5 images per class per split
                img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
                img = Image.fromarray(img_array)
                img.save(os.path.join(path, f"dummy_{i}.jpeg"))

if __name__ == "__main__":
    base = "datasets/xray"
    splits = ["train", "val", "test"]
    classes = ["NORMAL", "PNEUMONIA"]
    create_dirs(base, splits, classes)
    
    # Also create the ai_model directories
    os.makedirs("ai_model/xray/saved_models", exist_ok=True)
    os.makedirs("ai_model/xray/outputs/plots", exist_ok=True)
    os.makedirs("ai_model/xray/outputs/confusion_matrix", exist_ok=True)
    os.makedirs("ai_model/xray/outputs/gradcam", exist_ok=True)
    
    print("Dummy dataset and AI model directories created successfully.")
