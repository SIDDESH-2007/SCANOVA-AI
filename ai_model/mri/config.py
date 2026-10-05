import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../datasets/mri'))
TRAIN_DIR = os.path.join(DATASET_DIR, 'Training') if os.path.exists(os.path.join(DATASET_DIR, 'Training')) else os.path.join(DATASET_DIR, 'train')
TEST_DIR = os.path.join(DATASET_DIR, 'Testing') if os.path.exists(os.path.join(DATASET_DIR, 'Testing')) else os.path.join(DATASET_DIR, 'test')
VAL_DIR = os.path.join(DATASET_DIR, 'val')

SAVED_MODELS_DIR = os.path.join(BASE_DIR, 'saved_models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
PLOTS_DIR = os.path.join(OUTPUTS_DIR, 'plots')
CM_DIR = os.path.join(OUTPUTS_DIR, 'confusion_matrix')
GRADCAM_DIR = os.path.join(OUTPUTS_DIR, 'gradcam')

IMG_SIZE = 224
BATCH_SIZE = 16
LEARNING_RATE = 0.0001
EPOCHS = 10
CLASSES = ['glioma', 'meningioma', 'pituitary', 'notumor']
NUM_CLASSES = len(CLASSES)

MODEL_SAVE_PATH = os.path.join(SAVED_MODELS_DIR, 'mri_brain_tumor.pth')
