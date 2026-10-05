import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models
import numpy as np
import os
import sys

# Ensure parent directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_model.common.utilities import validate_and_summarize_dataset, update_model_registry
from ai_model.common.metrics import compute_classification_metrics

try:
    from .config import *
    from .dataset import ChestXRayDataset
    from .preprocessing import get_train_transforms, get_val_transforms
    from .utils import plot_training_history
except ImportError:
    from config import *
    from dataset import ChestXRayDataset
    from preprocessing import get_train_transforms, get_val_transforms
    from utils import plot_training_history

def create_model():
    """Load ImageNet pretrained DenseNet121 and adapt top classifier layer."""
    model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
    
    # Freeze initial feature layers for transfer learning
    for param in list(model.parameters())[:-30]:
        param.requires_grad = False
        
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Linear(num_ftrs, NUM_CLASSES)
    return model

def calculate_class_weights(dataset):
    labels = dataset.labels
    if len(labels) == 0:
        return torch.ones(NUM_CLASSES)
    class_counts = np.bincount(labels, minlength=NUM_CLASSES)
    total_samples = len(labels)
    class_weights = total_samples / (NUM_CLASSES * np.maximum(class_counts, 1))
    return torch.FloatTensor(class_weights)

def train_model():
    print("=" * 60)
    print("        STARTING CHEST X-RAY DENSENET121 TRAINING")
    print("=" * 60)
    
    # 1. Dataset Validation
    is_valid, summary = validate_and_summarize_dataset(DATASET_DIR, CLASSES)
    if not is_valid or summary.get("total_valid_images", 0) == 0:
        print("[!] CHEST X-RAY dataset invalid or empty. Aborting training.")
        update_model_registry("X-RAY", "DenseNet121", MODEL_SAVE_PATH, CLASSES, trained=False)
        return False

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # 2. Datasets & DataLoaders
    train_dataset = ChestXRayDataset(TRAIN_DIR, transform=get_train_transforms())
    val_dataset = ChestXRayDataset(VAL_DIR, transform=get_val_transforms())
    
    if len(train_dataset) == 0:
        print("[!] No training images available.")
        return False

    class_weights = calculate_class_weights(train_dataset).to(device)
    print(f"Computed Class Weights: {class_weights.cpu().numpy()}")
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    model = create_model().to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)
    
    history = {'train_acc': [], 'val_acc': [], 'train_loss': [], 'val_loss': []}
    best_val_loss = float('inf')
    best_val_acc = 0.0
    patience_counter = 0
    patience_limit = 4
    
    for epoch in range(EPOCHS):
        current_lr = optimizer.param_groups[0]['lr']
        print(f"\nEpoch {epoch+1}/{EPOCHS} | LR: {current_lr:.6f}")
        print("-" * 45)
        
        # Train Loop
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels, _ in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data).item()
            
        epoch_train_loss = running_loss / len(train_dataset)
        epoch_train_acc = running_corrects / len(train_dataset)
        
        # Validation Loop
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        
        with torch.no_grad():
            for inputs, labels, _ in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data).item()
                
        epoch_val_loss = val_loss / len(val_dataset) if len(val_dataset) > 0 else epoch_train_loss
        epoch_val_acc = val_corrects / len(val_dataset) if len(val_dataset) > 0 else epoch_train_acc
        
        scheduler.step(epoch_val_loss)
        
        history['train_loss'].append(epoch_train_loss)
        history['train_acc'].append(epoch_train_acc)
        history['val_loss'].append(epoch_val_loss)
        history['val_acc'].append(epoch_val_acc)
        
        print(f"Epoch {epoch+1:02d} Summary:")
        print(f"  Training Loss:    {epoch_train_loss:.4f} | Training Acc:   {epoch_train_acc*100:.2f}%")
        print(f"  Validation Loss:  {epoch_val_loss:.4f} | Validation Acc: {epoch_val_acc*100:.2f}%")
        print(f"  Learning Rate:    {current_lr:.6f}")
        
        # Checkpoint Best Model
        if epoch_val_loss < best_val_loss or epoch_val_acc > best_val_acc:
            best_val_loss = min(best_val_loss, epoch_val_loss)
            best_val_acc = max(best_val_acc, epoch_val_acc)
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  => Best Checkpoint Saved to: {MODEL_SAVE_PATH}")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience_limit:
                print(f"Early stopping triggered at epoch {epoch+1}")
                break

    plot_training_history(history, os.path.join(PLOTS_DIR, 'training_history.png'))
    update_model_registry("X-RAY", "DenseNet121", MODEL_SAVE_PATH, CLASSES, trained=True)
    print("CHEST X-RAY training completed successfully.\n")
    return True

if __name__ == '__main__':
    train_model()
