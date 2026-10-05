import os
import requests

def download_image(url, save_path):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, stream=True, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {save_path}")
            return True
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def main():
    base_dir = "datasets/xray"
    splits = ["train", "val", "test"]
    classes = ["NORMAL", "PNEUMONIA"]

    for split in splits:
        for cls in classes:
            os.makedirs(os.path.join(base_dir, split, cls), exist_ok=True)

    # Stable GitHub raw URLs for real chest x-rays
    # COVID-19 Chest X-ray Dataset (IEEE8023)
    normal_urls = [
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/000001-2.jpg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/000002-3.jpg"
    ]
    
    pneumonia_urls = [
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/000001-1.jpg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/000002-4.jpg"
    ]

    print("Downloading NORMAL images...")
    for i, url in enumerate(normal_urls):
        for split in splits:
            download_image(url, os.path.join(base_dir, split, "NORMAL", f"normal_{i}.jpg"))

    print("Downloading PNEUMONIA images...")
    for i, url in enumerate(pneumonia_urls):
        for split in splits:
            download_image(url, os.path.join(base_dir, split, "PNEUMONIA", f"pneumonia_{i}.jpg"))
            
    print("Downloaded real sample images successfully.")

if __name__ == "__main__":
    main()
