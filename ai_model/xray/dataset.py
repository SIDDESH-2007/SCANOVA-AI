import os
from PIL import Image
from torch.utils.data import Dataset
try:
    from .config import CLASSES
except ImportError:
    from config import CLASSES

class ChestXRayDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        
        # Expected to have NORMAL and PNEUMONIA subfolders
        for label_idx, class_name in enumerate(CLASSES):
            class_dir = os.path.join(data_dir, class_name)
            if not os.path.exists(class_dir):
                continue
                
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.dcm')):
                    self.image_paths.append(os.path.join(class_dir, img_name))
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
