import json
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import numpy as np

def calculate_metrics(y_true, y_pred, y_probs, classes):
    metrics = {}
    metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
    metrics["precision_macro"] = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
    metrics["recall_macro"] = float(recall_score(y_true, y_pred, average='macro', zero_division=0))
    metrics["f1_macro"] = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    
    try:
        if len(classes) == 2:
            metrics["roc_auc"] = float(roc_auc_score(y_true, [p[1] for p in y_probs]))
        else:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_probs, multi_class='ovr'))
    except Exception as e:
        metrics["roc_auc"] = None
        
    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
    
    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True, zero_division=0)
    metrics["classification_report"] = report
    
    return metrics

def save_metrics(metrics, output_path):
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=4)
