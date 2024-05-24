import requests
import json

# URL setup
base_url = 'http://localhost:5000'
login_url = f'{base_url}/login'
predict_url = f'{base_url}/predict'

# User credentials for authentication
credentials = {
    'username': 'admin',
    'password': 'password'
}

# Login to get JWT token
login_response = requests.post(login_url, json=credentials)
token = login_response.json().get('access_token')
#print(token)
if token:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'  # Use the JWT token for authorization
    }

    # Correct test case based on the latest model structure
    data = {
        "Experience_Required": 0,  # Normalized value for simplicity
        "Sector_Activity": 0,        # Example ID for the sector
        "Function": 0,               # Example ID for the function
        "Bac": 0,
        "Bac +2": 0,
        "Bac +3": 0,
        "Bac +4": 0,
        "Bac +5": 0,
        "Doctorate": 0
    }

    # Send request to the protected predict endpoint
    response = requests.post(predict_url, headers=headers, json=data)
    print("Prediction:", response.json())
else:
    print("Failed to authenticate, check username and password")
