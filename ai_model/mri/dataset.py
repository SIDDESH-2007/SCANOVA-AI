import os
from PIL import Image
from torch.utils.data import Dataset
try:
    from .config import CLASSES
except ImportError:
    from config import CLASSES

class BrainMRIDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        
        if not os.path.exists(data_dir):
            return

        for label_idx, class_name in enumerate(CLASSES):
            # Also handle variations in folder naming if dataset uses capitalization
            possible_dirs = [
                os.path.join(data_dir, class_name),
                os.path.join(data_dir, class_name.capitalize()),
                os.path.join(data_dir, class_name.lower())
            ]
            
            target_dir = None
            for p_dir in possible_dirs:
                if os.path.exists(p_dir):
                    target_dir = p_dir
                    break
                    
            if not target_dir:
                continue
                
            for img_name in os.listdir(target_dir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
                    self.image_paths.append(os.path.join(target_dir, img_name))
                    self.labels.append(label_idx)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, label, img_path
