from flask import Flask, request, jsonify, render_template
import pymongo
import pandas as pd
from config import Config
from ml_model.predictor import EmploymentPredictor
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Setup MongoDB connection
client = pymongo.MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]
jobs_collection = db[Config.JOBS_COLLECTION]
urls_collection = db[Config.URLS_COLLECTION]

predictor = EmploymentPredictor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not predictor.model:
        predictor.load_model(Config.base_Path + 'ml_model/trained/model.joblib')
    
    input_data = request.json
    required_fields = ['Experience_Required', 'Sector_Activity', 'Function', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
    if not all(field in input_data for field in required_fields):
        return jsonify({'error': 'Missing one or more required fields'}), 400

    input_df = pd.DataFrame([input_data])
    prediction = predictor.model.predict(input_df)
    return jsonify({'prediction': prediction.tolist()})

@app.route('/add_url', methods=['POST'])
def add_url():
    url = request.json.get('url')
    if url:
        urls_collection.insert_one({'url': url})
        return jsonify({'message': 'URL added successfully'})
    else:
        return jsonify({'error': 'No URL provided'}), 400

if __name__ == "__main__":
    app.run(debug=True)
