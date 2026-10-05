import os
from PIL import Image
from torch.utils.data import Dataset
try:
    from .config import CLASSES
except ImportError:
    from config import CLASSES

# Normalization mapping for CT folders
CLASS_SYNONYMS = {
    "NORMAL": ["normal", "normal_control", "non_hemorrhage", "no_hemorrhage", "healthy"],
    "HEMORRHAGE": ["hemorrhage", "hemorrhagic", "intracranial_hemorrhage", "bleed", "bleeding"]
}

class BrainCTDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        
        if not os.path.exists(data_dir):
            return

        # Check subfolders in data_dir
        subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

        for subdir in subdirs:
            subdir_lower = subdir.lower()
            target_class_idx = None
            
            # Map folder name to target class index
            for idx, target_cls in enumerate(CLASSES):
                synonyms = CLASS_SYNONYMS.get(target_cls, [target_cls.lower()])
                if target_cls.lower() in subdir_lower or any(syn in subdir_lower for syn in synonyms):
                    target_class_idx = idx
                    break
                    
            if target_class_idx is None:
                continue

            full_subdir = os.path.join(data_dir, subdir)
            for img_name in os.listdir(full_subdir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.dcm', '.bmp')):
                    self.image_paths.append(os.path.join(full_subdir, img_name))
                    self.labels.append(target_class_idx)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, label, img_path
