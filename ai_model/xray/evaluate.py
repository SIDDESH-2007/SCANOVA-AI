import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import numpy as np
import os

try:
    from .config import *
    from .dataset import ChestXRayDataset
    from .preprocessing import get_val_transforms
    from .train import create_model
    from .utils import plot_confusion_matrix
except ImportError:
    from config import *
    from dataset import ChestXRayDataset
    from preprocessing import get_val_transforms
    from train import create_model
    from utils import plot_confusion_matrix

def evaluate_model():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    test_dataset = ChestXRayDataset(TEST_DIR, transform=get_val_transforms())
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    model = create_model()
    model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
    model = model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for inputs, labels, _ in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)
    roc_auc = roc_auc_score(all_labels, all_probs)
    
    # Specificity = TN / (TN + FP)
    # Using confusion matrix directly is safer
    from sklearn.metrics import confusion_matrix
    tn, fp, fn, tp = confusion_matrix(all_labels, all_preds).ravel()
    specificity = tn / (tn + fp)
    sensitivity = tp / (tp + fn) # Same as recall
    
    print("=== Evaluation Metrics on Unseen Test Data ===")
    print(f"Accuracy:    {acc:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"Sensitivity: {sensitivity:.4f}")
    print(f"Specificity: {specificity:.4f}")
    print(f"F1 Score:    {f1:.4f}")
    print(f"ROC-AUC:     {roc_auc:.4f}")
    
    plot_confusion_matrix(all_labels, all_preds, CLASSES, os.path.join(CM_DIR, 'confusion_matrix.png'))
    print(f"Confusion matrix saved to {CM_DIR}")

if __name__ == '__main__':
    evaluate_model()
