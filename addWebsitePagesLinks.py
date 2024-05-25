import requests

#example
base_url = "https://www.rekrute.com/offres.html?p="
endpoint = "http://localhost:5000/add_url"

for i in range(1, 51):
    url = f"{base_url}{i}"
    payload = {'url': url}
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        print(f"URL {url} added successfully.")
    else:
        print(f"Failed to add URL {url}. Response: {response.json()}")
