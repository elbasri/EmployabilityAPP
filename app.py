from flask import Flask, request, jsonify
import pymongo
from ml_model.predictor import EmploymentPredictor
from config import Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Setup MongoDB connection
client = pymongo.MongoClient(Config.MONGO_URI)

# Initialize the predictor and load the trained model
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
        return jsonify({'prediction': int(prediction)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
