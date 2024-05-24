import requests

response = requests.post('http://localhost:5000/train', data={'data_path': '/home/abdennacer/Documents/GitHub/EmployabilityAPP/testdata.csv'})
print(response.json())
