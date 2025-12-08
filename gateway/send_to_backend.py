import requests

BACKEND_URL = "http://127.0.0.1:8000/predict"   # your FastAPI server


def send_features_to_backend(features: dict):
    try:
        response = requests.post(BACKEND_URL, json=features)
        return response.json()

    except Exception as e:
        print("Error sending features to backend:", e)
        return {"attack_type": "error", "confidence": 0}
