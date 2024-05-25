import requests
import json

# URL setup
base_url = 'http://localhost:5000'
predict_url = f'{base_url}/predict'

data = {
        "Experience_Required": 1,  # Normalized value for simplicity
        "Sector_Activity": 1,        # Example ID for the sector
        "Function": 1,               # Example ID for the function
        "Bac": 1,
        "Bac +2": 1,
        "Bac +3": 1,
        "Bac +4": 1,
        "Bac +5": 1,
        "Doctorate": 1
    }
# Send request to the protected predict endpoint
response = requests.post(predict_url, json=data)
print("Prediction:", response.json())