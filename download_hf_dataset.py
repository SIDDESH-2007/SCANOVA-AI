import os
from datasets import load_dataset

def download_hf_dataset():
    print("Loading HuggingFace dataset...")
    try:
        # A small open chest x-ray dataset on HF
        ds = load_dataset("keremberke/chest-xray-classification", "full", split="train[:100]") # small subset
        
        base_dir = "datasets/xray"
        
        # Clean existing dummy files
        import shutil
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
            
        splits = {"train": "train", "validation": "val", "test": "test"}
        
        # Let's download all splits
        for ds_split, target_split in splits.items():
            try:
                split_data = load_dataset("keremberke/chest-xray-classification", "full", split=f"{ds_split}[:100]")
                for i, item in enumerate(split_data):
                    image = item['image']
                    label = item['labels'] # Usually 0: NORMAL, 1: PNEUMONIA
                    label_name = "NORMAL" if label == 0 else "PNEUMONIA"
                    
                    target_dir = os.path.join(base_dir, target_split, label_name)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    image.convert('RGB').save(os.path.join(target_dir, f"{label_name}_{i}.jpg"))
            except Exception as e:
                print(f"Skipping split {ds_split}: {e}")
                
        print("Dataset downloaded and prepared.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")

if __name__ == "__main__":
    download_hf_dataset()
