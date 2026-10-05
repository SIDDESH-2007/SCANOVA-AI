import torch
from torch.utils.data import DataLoader
import numpy as np
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_model.common.metrics import compute_classification_metrics

try:
    from .config import *
    from .dataset import BrainMRIDataset
    from .preprocessing import get_val_transforms
    from .train import create_model
    from .utils import plot_confusion_matrix
except ImportError:
    from config import *
    from dataset import BrainMRIDataset
    from preprocessing import get_val_transforms
    from train import create_model
    from utils import plot_confusion_matrix

def evaluate_model():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    if not os.path.exists(MODEL_SAVE_PATH):
        print(f"[!] MRI Model file missing at {MODEL_SAVE_PATH}")
        return

    test_dataset = BrainMRIDataset(TEST_DIR, transform=get_val_transforms())
    if len(test_dataset) == 0:
        print("[!] No test dataset found for MRI.")
        return

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
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            
    metrics = compute_classification_metrics(all_labels, all_preds, np.array(all_probs), CLASSES)
    
    print("=== Evaluation Metrics on Unseen Brain MRI Test Data ===")
    print(f"Accuracy:           {metrics['accuracy']:.4f}")
    print(f"Precision (Macro):   {metrics.get('precision_macro', 0):.4f}")
    print(f"Precision (Weight): {metrics.get('precision_weighted', 0):.4f}")
    print(f"Recall (Macro):      {metrics.get('recall_macro', 0):.4f}")
    print(f"Recall (Weighted):  {metrics.get('recall_weighted', 0):.4f}")
    print(f"F1 Score (Macro):   {metrics.get('f1_macro', 0):.4f}")
    print(f"F1 Score (Weight):  {metrics.get('f1_weighted', 0):.4f}")
    
    plot_confusion_matrix(all_labels, all_preds, CLASSES, os.path.join(CM_DIR, 'confusion_matrix.png'))
    print(f"Confusion matrix saved to {CM_DIR}")

if __name__ == '__main__':
    evaluate_model()
