import os
import sys
import subprocess
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")

DATASET_CONFIGS = {
    "xray": {
        "kaggle_id": "paultimothymooney/chest-xray-pneumonia",
        "path": os.path.join(DATASETS_DIR, "xray"),
        "expected_subdirs": ["train", "val", "test"]
    },
    "mri": {
        "kaggle_id": "masoudnickparvar/brain-tumor-mri-dataset",
        "path": os.path.join(DATASETS_DIR, "mri"),
        "expected_subdirs": ["Training", "Testing", "train", "test"]
    },
    "ct": {
        "kaggle_id": "abdulkader90/brain-ct-hemorrhage-dataset",
        "path": os.path.join(DATASETS_DIR, "ct"),
        "expected_subdirs": ["train", "val", "test", "NORMAL", "HEMORRHAGE"]
    }
}

def check_kaggle_cli():
    """Detect if Kaggle CLI is installed."""
    try:
        res = subprocess.run(["kaggle", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"[+] Kaggle CLI detected: {res.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("[-] Kaggle CLI is not installed in the system environment.")
    return False

def install_kaggle():
    """Attempt installing Kaggle package via pip."""
    print("[*] Installing Kaggle CLI package...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "kaggle"], check=True)
        print("[+] Kaggle CLI installed successfully.")
        return True
    except Exception as e:
        print(f"[-] Failed to install kaggle via pip: {e}")
        return False

def check_kaggle_auth():
    """Verify if Kaggle credentials exist and are functional."""
    api_token = os.environ.get("KAGGLE_API_TOKEN")
    user = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    
    kaggle_json_path = os.path.expanduser("~/.kaggle/kaggle.json")
    if os.name == "nt":
        kaggle_json_path = os.path.expanduser(r"~\.kaggle\kaggle.json")
        
    has_config = os.path.exists(kaggle_json_path) or (user and key) or api_token
    
    if not has_config:
        return False

    try:
        res = subprocess.run(["kaggle", "datasets", "list", "--max-size", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print("[+] Kaggle authentication verified.")
            return True
        else:
            print(f"[-] Kaggle auth check failed: {res.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[-] Error testing Kaggle auth: {e}")
        return False

def is_dataset_present(modality):
    config = DATASET_CONFIGS[modality]
    path = config["path"]
    if not os.path.exists(path):
        return False
    
    for root, _, files in os.walk(path):
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.dcm'))]
        if len(image_files) > 10:
            return True
    return False

def download_modality_dataset(modality):
    config = DATASET_CONFIGS[modality]
    os.makedirs(config["path"], exist_ok=True)
    
    print(f"[*] Downloading {modality.upper()} dataset: {config['kaggle_id']} ...")
    cmd = ["kaggle", "datasets", "download", "-d", config["kaggle_id"], "-p", config["path"], "--unzip"]
    try:
        res = subprocess.run(cmd, check=True)
        print(f"[+] {modality.upper()} dataset downloaded and unzipped into {config['path']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to download {modality.upper()} dataset: {e}")
        return False

def main():
    print("=" * 60)
    print("        MEDICAL IMAGING DATASET DOWNLOAD MANAGER")
    print("=" * 60)
    
    cli_available = check_kaggle_cli()
    if not cli_available:
        installed = install_kaggle()
        if installed:
            cli_available = check_kaggle_cli()
            
    auth_ok = check_kaggle_auth() if cli_available else False
    
    if not auth_ok:
        print("\n" + "=" * 60)
        print("Kaggle authentication is required. Download the datasets manually")
        print("from the supplied Kaggle links and place them inside datasets/xray,")
        print("datasets/mri, and datasets/ct.")
        print("=" * 60 + "\n")
        print("Kaggle Dataset URLs:")
        print(" - CHEST X-RAY: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia")
        print(" - BRAIN MRI:   https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset")
        print(" - BRAIN CT:    https://www.kaggle.com/datasets/abdulkader90/brain-ct-hemorrhage-dataset")
        print("\nChecking for manually placed datasets...")
    
    for modality in ["xray", "mri", "ct"]:
        present = is_dataset_present(modality)
        if present:
            print(f"[✓] {modality.upper()} dataset detected in {DATASET_CONFIGS[modality]['path']}")
        elif auth_ok:
            download_modality_dataset(modality)
        else:
            print(f"[×] {modality.upper()} dataset is missing in {DATASET_CONFIGS[modality]['path']}")

if __name__ == "__main__":
    main()
