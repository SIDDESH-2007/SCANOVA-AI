from torchvision import transforms
try:
    from .config import IMG_SIZE
except ImportError:
    from config import IMG_SIZE

# ImageNet normalization statistics
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

def get_train_transforms():
    """Medically safe augmentations for X-Rays."""
    return transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        # Small rotations and shifts are safe for X-Rays
        transforms.RandomAffine(degrees=5, translate=(0.05, 0.05)),
        transforms.ColorJitter(brightness=0.1),
        transforms.ToTensor(),
        normalize
    ])

def get_val_transforms():
    """No augmentation for validation and testing."""
    return transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        normalize
    ])
