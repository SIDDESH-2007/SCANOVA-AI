# AI-Powered Diagnosis Support - Chest X-Ray Module

## Dataset Source
This module uses the **Chest X-Ray Images (Pneumonia)** dataset from Kaggle.
URL: [https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)

## Folder Structure
Ensure your dataset is placed at `datasets/xray/` relative to the root project directory, with `train`, `val`, and `test` subdirectories.

```
datasets/xray/
├── train/
│   ├── NORMAL/
│   └── PNEUMONIA/
├── val/
└── test/
```

## Model Architecture
- **Base**: DenseNet121 (pretrained on ImageNet)
- **Classifier**: Modified to 2 output classes (NORMAL, PNEUMONIA)
- **Loss**: Weighted CrossEntropyLoss (to handle class imbalance)
- **Explainability**: Grad-CAM targeted at the final dense block.

## Commands

### 1. Training
Run training with early stopping:
```bash
python -m ai_model.xray.train
```

### 2. Evaluation
Calculate accuracy, precision, recall, and ROC-AUC on the test set:
```bash
python -m ai_model.xray.evaluate
```

### 3. Prediction
Run inference on a single image. This will output a JSON containing the prediction, confidence level, and a path to the generated Grad-CAM heatmap.
```bash
python -m ai_model.xray.predict --image "path/to/xray.jpg"
```

## Important Medical Disclaimer
This model is intended for educational and clinical decision support research only. It must not be used as a standalone medical diagnosis system. Final interpretation must be performed by a qualified healthcare professional.
