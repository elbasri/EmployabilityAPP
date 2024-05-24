from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pymongo
import pandas as pd
from config import Config
from ml_model.predictor import EmploymentPredictor
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


client = pymongo.MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]
jobs_collection = db[Config.JOBS_COLLECTION]
urls_collection = db[Config.URLS_COLLECTION]

app.config['JWT_SECRET_KEY'] = 'NCR123tocken986094534i5jh6jhgfdg950NCR123tocken4589350NCR123tocken'
jwt = JWTManager(app)

predictor = EmploymentPredictor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username == 'admin' and password == 'password': 
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/predict', methods=['POST'])
@jwt_required()
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
