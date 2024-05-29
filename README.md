# Employability Prediction API

## Overview
This project aims to predict the employability of individuals based on various criteria using deep learning models. The project has transitioned from traditional regression and XGBoost methods to a Convolutional Neural Network (CNN) based approach to enhance performance.

## Installation

### Prerequisites
- Python 3.8+
- MongoDB
- TensorFlow 2.x
- Scrapy

### Setup
Clone the repository:
```bash
git clone https://github.com/elbasri/EmployabilityAPP.git
cd EmployabilityAPP
```

### Install the required Python packages:

```bash
pip install -r requirements.txt
```
### Running the API

To start the Flask API, run:
```bash
python app.py
```

### Usage
Once the API is running, it will be accessible from http://localhost:5000. You can make POST requests to /predict endpoint to predict employability.

Example request:

To start the Flask API, run:
```bash
import requests

data = {
    "experience_required": 0.3,
    "Bac": 1,
    "Bac +2": 1,
    "Bac +3": 1,
    "Bac +4": 0,
    "Bac +5": 0,
    "Doctorate": 0
}

response = requests.post('http://localhost:5000/predict', json=data)
print(response.json())

```

### Project Structure
    -- app.py: Entry point for the Flask API.
    -- predictor.py: Contains the implementation of the EmploymentPredictor class which includes model training and prediction logic.
    -- requirements.txt: Lists all Python libraries that the project depends on.

### Contributing
  Contributions to this project are welcome. Please ensure to update tests as appropriate.

### License
  This project is supported by the MIT License - see the LICENSE file for details.
