from flask import Flask, request, jsonify
import pymongo
from ml_model.predictor import EmploymentPredictor
from config import Config
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

# Setup MongoDB connection
client = pymongo.MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]  # Assuming you have DATABASE_NAME in your Config

# Initialize the predictor and load the trained model and scaler
predictor = EmploymentPredictor()
predictor.load_model('ml_model/trained/model.h5', 'ml_model/trained/scaler.npz')

@app.route('/')
def index():
    return 'Employability Prediction API is running'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()
        prediction = predictor.predict(input_data)
        
        # Save prediction and input data to MongoDB
        stats_data = {
            **input_data,
            'prediction': int(prediction),
            'timestamp': datetime.datetime.now()
        }
        db.stats.insert_one(stats_data)
        
        return jsonify({'prediction': int(prediction)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/counts', methods=['GET'])
def get_counts():
    try:
        jobs_count = db.jobs_collection.count_documents({})
        stats_count = db.stats.count_documents({})
        employable_count = db.stats.count_documents({'prediction': 1})
        non_employable_count = db.stats.count_documents({'prediction': 0})
        
        counts = {
            "jobs_count": jobs_count,
            "stats_count": stats_count,
            "employable_count": employable_count,
            "non_employable_count": non_employable_count
        }
        return jsonify(counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    try:
        predictions = list(db.stats.find({}, {'_id': 0}))
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
