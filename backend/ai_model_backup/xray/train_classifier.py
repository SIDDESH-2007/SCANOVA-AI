import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import json
import copy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend dir to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from backend.ai_model.common.metrics import calculate_metrics, save_metrics
except:
    pass

def train_model(model, dataloaders, criterion, optimizer, num_epochs=10, device='cpu'):
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        logger.info(f'Epoch {epoch}/{num_epochs - 1}')
        logger.info('-' * 10)

        for phase in ['train', 'validation']:
            if phase not in dataloaders:
                continue
                
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)

            logger.info(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            if phase == 'validation' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_model_wts)
    return model

def evaluate_model(model, dataloader, class_names, device='cpu'):
    model.eval()
    y_true = []
    y_pred = []
    y_probs = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
            y_probs.extend(probs.cpu().numpy())
            
    # if common.metrics is available
    if 'backend.ai_model.common.metrics' in sys.modules:
        metrics = calculate_metrics(y_true, y_pred, y_probs, class_names)
        return metrics
    return None

def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    data_dir = os.path.abspath(os.path.join(CURRENT_DIR, "../../../datasets/xray"))
    save_dir = os.path.join(CURRENT_DIR, "saved_models")
    os.makedirs(save_dir, exist_ok=True)
    
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'validation': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'test': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    image_datasets = {}
    dataloaders = {}
    
    for x in ['train', 'validation', 'test']:
        p = os.path.join(data_dir, x)
        if os.path.exists(p):
            image_datasets[x] = datasets.ImageFolder(p, data_transforms[x])
            dataloaders[x] = DataLoader(image_datasets[x], batch_size=16, shuffle=(x=='train'), num_workers=0)
            
    if 'train' not in image_datasets:
        logger.error("Training data not found.")
        return
        
    class_names = image_datasets['train'].classes
    logger.info(f"Classes: {class_names}")

    model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Linear(num_ftrs, len(class_names))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)

    # Train (only a couple of epochs for speed in this environment)
    model = train_model(model, dataloaders, criterion, optimizer, num_epochs=2, device=device)
    
    # Save Model
    save_path = os.path.join(save_dir, "xray_densenet121.pth")
    torch.save(model.state_dict(), save_path)
    logger.info(f"Model saved to {save_path}")
    
    # Evaluate
    if 'test' in dataloaders:
        metrics = evaluate_model(model, dataloaders['test'], class_names, device=device)
        if metrics:
            save_metrics(metrics, os.path.join(CURRENT_DIR, "metrics.json"))
            logger.info("Metrics saved to metrics.json")

    # Update metadata
    meta = {
        "modelName": "XRayDenseNet121",
        "version": "1.0",
        "modality": "X-RAY",
        "classes": class_names,
        "localization": False
    }
    with open(os.path.join(save_dir, "metadata.json"), 'w') as f:
        json.dump(meta, f, indent=4)

if __name__ == '__main__':
    main()
