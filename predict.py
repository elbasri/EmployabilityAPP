import requests
import json

# URL setup
base_url = 'http://localhost:5000'
predict_url = f'{base_url}/predict'

data = {
        "experience_required": 0.3,
        "Bac": 1,
        "Bac +2": 1,
        "Bac +3": 1,
        "Bac +4": 0,
        "Bac +5": 0,
        "Doctorate": 0
    }
# Send request to the protected predict endpoint
response = requests.post(predict_url, json=data)
print("Prediction:", response.json())