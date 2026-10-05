import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

def compute_classification_metrics(y_true, y_pred, y_prob=None, class_names=None):
    """
    Computes comprehensive clinical evaluation metrics for binary or multiclass classification.
    Returns dictionary with all metrics and confusion matrix.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    num_classes = len(class_names) if class_names else len(np.unique(y_true))
    
    metrics = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
    }
    
    if num_classes <= 2:
        # Binary Classification Metrics
        metrics["precision"] = round(float(precision_score(y_true, y_pred, zero_division=0)), 4)
        metrics["recall_sensitivity"] = round(float(recall_score(y_true, y_pred, zero_division=0)), 4)
        metrics["f1_score"] = round(float(f1_score(y_true, y_pred, zero_division=0)), 4)
        
        # Specificity = TN / (TN + FP)
        cm = metrics["confusion_matrix"]
        if len(cm) == 2:
            tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            metrics["specificity"] = round(float(specificity), 4)
        else:
            metrics["specificity"] = 0.0
            
        if y_prob is not None:
            try:
                # Handle binary prob array or 1D probs
                prob_vec = y_prob[:, 1] if len(y_prob.shape) > 1 and y_prob.shape[1] > 1 else y_prob
                metrics["roc_auc"] = round(float(roc_auc_score(y_true, prob_vec)), 4)
            except Exception:
                metrics["roc_auc"] = None
        else:
            metrics["roc_auc"] = None
            
    else:
        # Multiclass Metrics (MRI)
        metrics["precision_macro"] = round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4)
        metrics["precision_weighted"] = round(float(precision_score(y_true, y_pred, average="weighted", zero_division=0)), 4)
        
        metrics["recall_macro"] = round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4)
        metrics["recall_weighted"] = round(float(recall_score(y_true, y_pred, average="weighted", zero_division=0)), 4)
        
        metrics["f1_macro"] = round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4)
        metrics["f1_weighted"] = round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4)
        
        if y_prob is not None:
            try:
                metrics["roc_auc_ovr"] = round(float(roc_auc_score(y_true, y_prob, multi_class="ovr")), 4)
            except Exception:
                metrics["roc_auc_ovr"] = None
        else:
            metrics["roc_auc_ovr"] = None

    return metrics
