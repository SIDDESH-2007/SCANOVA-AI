import requests
import os

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("1. Testing Registration")
    reg_data = {
        "fullName": "Test Doctor",
        "email": "testdoc_workflow@example.com",
        "password": "password123",
        "hospital": "Test Hospital",
        "department": "Radiology",
        "specialization": "General",
        "phone": "1234567890"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if r.status_code == 409:
        print("User already registered, proceeding to login...")
    elif r.status_code != 200:
        print("Registration failed:", r.text)
        return
    else:
        print("Registration successful!")

    print("2. Testing Login")
    login_data = {
        "email": "testdoc_workflow@example.com",
        "password": "password123"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if r.status_code != 200:
        print("Login failed:", r.text)
        return
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful! Token acquired.")

    print("3. Testing Dashboard")
    r = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if r.status_code != 200:
        print("Dashboard failed:", r.text)
        return
    print("Dashboard loaded successfully! Data:", r.json())

    # Wait, testing prediction requires uploading a file
    # I'll create a dummy image to upload
    from PIL import Image
    import numpy as np
    dummy_img_path = "test_image.jpg"
    noise = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(noise, 'RGB')
    img.save(dummy_img_path)

    print("4. Testing Prediction Upload")
    with open(dummy_img_path, "rb") as f:
        files = {"file": (dummy_img_path, f, "image/jpeg")}
        data = {
            "patientName": "John Test",
            "age": 45,
            "gender": "Male",
            "scanType": "X-RAY",
            "caseType": "NORMAL",
            "phoneNumber": "1234567890"
        }
        r = requests.post(f"{BASE_URL}/predictions/analyze", headers=headers, data=data, files=files)
        
    os.remove(dummy_img_path)
    if r.status_code != 200:
        print("Prediction failed:", r.text)
        return
    
    pred_data = r.json()
    print("Prediction successful! Result:", pred_data)

    print("5. Testing Reports/Predictions List")
    r = requests.get(f"{BASE_URL}/predictions", headers=headers)
    if r.status_code != 200:
        print("Fetching predictions failed:", r.text)
        return
    print("Predictions fetched successfully! Count:", len(r.json()))
    
    print("\nALL WORKFLOWS EXECUTED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
