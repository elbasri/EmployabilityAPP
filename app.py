from flask import Flask, request, jsonify
import pymongo
from ml_model.predictor import EmploymentPredictor
from config import Config
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

client = pymongo.MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME] 

predictor = EmploymentPredictor()
predictor.load_model('ml_model/trained/model.h5', 'ml_model/trained/scaler.npz')


def extract_education(text):
    """ Map educational levels to structured format. """
    levels = ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
    values = [0] * len(levels)

    if 'Bac' in text and 'Bac +' not in text:
        values[0] = 1 

    if 'Bac +2' in text:
        values[0:2] = [1, 1] 

    if 'Bac +3' in text:
        values[0:3] = [1, 1, 1]

    if 'Bac +4' in text:
        values[0:4] = [1, 1, 1, 1] 

    if 'Bac +5' in text or 'Bac +5 et plus' in text:
        values[0:5] = [1, 1, 1, 1, 1] 

    if 'Doctorat' in text or 'Doctorate' in text:
        values[:] = [1, 1, 1, 1, 1, 1]  

    return dict(zip(levels, values))


@app.route('/')
def index():
    return 'Employability Prediction API is running'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()
        print("Original input data:", input_data)

        education_data = extract_education(input_data['study_level'])
        input_data.update(education_data) 

        del input_data['study_level']

        print("Updated input data for prediction:", input_data)
        prediction = predictor.predict(input_data)
        
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
        predictions = list(db.stats.find({}, {'_id': 0}).sort('timestamp', -1))
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
