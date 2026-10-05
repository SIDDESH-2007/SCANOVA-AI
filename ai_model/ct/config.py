import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../datasets/ct'))
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VAL_DIR = os.path.join(DATASET_DIR, 'val')
TEST_DIR = os.path.join(DATASET_DIR, 'test')

SAVED_MODELS_DIR = os.path.join(BASE_DIR, 'saved_models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
PLOTS_DIR = os.path.join(OUTPUTS_DIR, 'plots')
CM_DIR = os.path.join(OUTPUTS_DIR, 'confusion_matrix')
GRADCAM_DIR = os.path.join(OUTPUTS_DIR, 'gradcam')

IMG_SIZE = 224
BATCH_SIZE = 16
LEARNING_RATE = 0.0001
EPOCHS = 10
CLASSES = ['NORMAL', 'HEMORRHAGE']
NUM_CLASSES = len(CLASSES)

MODEL_SAVE_PATH = os.path.join(SAVED_MODELS_DIR, 'ct_hemorrhage.pth')
