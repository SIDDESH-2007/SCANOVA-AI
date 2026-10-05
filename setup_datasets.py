import os
import numpy as np
from PIL import Image

def generate_sample_images(base_path, splits, classes, num_images=5):
    for split in splits:
        for cls in classes:
            folder = os.path.join(base_path, split, cls)
            os.makedirs(folder, exist_ok=True)
            for i in range(num_images):
                file_path = os.path.join(folder, f"sample_{cls}_{i+1}.jpg")
                if not os.path.exists(file_path):
                    # Generate a grayscale-like synthetic medical slice image
                    arr = np.random.randint(20, 200, (224, 224), dtype=np.uint8)
                    # Add circular mask to simulate head scan
                    y, x = np.ogrid[:224, :224]
                    mask = (x - 112)**2 + (y - 112)**2 > 90**2
                    arr[mask] = 0
                    img = Image.fromarray(arr)
                    img.save(file_path)

if __name__ == "__main__":
    print("Setting up sample dataset structures...")
    
    # X-Ray
    generate_sample_images("datasets/xray", ["train", "val", "test"], ["NORMAL", "PNEUMONIA"])
    
    # Brain MRI
    generate_sample_images("datasets/mri", ["Training", "Testing"], ["glioma", "meningioma", "pituitary", "notumor"])
    
    # Brain CT
    generate_sample_images("datasets/ct", ["train", "val", "test"], ["NORMAL", "HEMORRHAGE"])
    
    print("[+] Datasets prepared.")
