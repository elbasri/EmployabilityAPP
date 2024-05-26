import pandas as pd
import numpy as np
import re
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib
from config import Config
from sklearn.impute import SimpleImputer
import os

class EmploymentPredictor:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.jobs_collection = self.db[Config.JOBS_COLLECTION]
        self.model = None
        self.scaler = StandardScaler()
        self.min_max_scaler = MinMaxScaler()
        self.imputer = SimpleImputer(strategy='mean')

    def ensure_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def extract_data(self):
        # Fetch data from MongoDB collection
        jobs_data = list(self.jobs_collection.find({}, projection={'_id': False}))
        self.data = pd.DataFrame(jobs_data)  # Corrected variable name
        self.preprocess_data()
        # Save the extracted data to CSV for debugging
        self.ensure_directory('debugData')
        self.data.to_csv('debugData/extracted_data.csv', index=False)
        print("Data extracted and saved to 'debugData/extracted_data.csv'.")

    def clean_text(self, text):
        """ Clean text by removing extra spaces, newlines, and non-alphanumeric characters. """
        return re.sub(r'\s+', ' ', str(text)).strip()

    def preprocess_data(self):
        # Clean the text fields, ensure the field exists before applying the function
        if 'company_name' in self.data.columns:
            self.data['Company_Name'] = self.data['company_name'].apply(self.clean_text)
        if 'job_title' in self.data.columns:
            self.data['Job_Title'] = self.data['job_title'].apply(self.clean_text)

        # Extract and preprocess data for model features
        self.data['Sector_Activity'] = self.data.get('sector_activity', pd.Series()).apply(lambda x: x[0] if isinstance(x, list) and x else None)
        self.data['Function'] = self.data.get('function', pd.Series()).apply(lambda x: x[0] if isinstance(x, list) and x else None)
        self.data['Experience_Required'] = self.data.get('experience_required', pd.Series()).apply(lambda x: x[0][0] if isinstance(x, list) and x and isinstance(x[0], list) and x[0] else 0)
        self.data['Experience_Required'] = self.min_max_scaler.fit_transform(self.data[['Experience_Required']])
        if 'study_level_required' in self.data.columns:
            education_df = pd.json_normalize(self.data['study_level_required'])
            self.data = pd.concat([self.data.drop('study_level_required', axis=1), education_df], axis=1)
        else:
            for level in ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']:
                self.data[level] = 0

    def split_data(self):
        features = ['Experience_Required', 'Sector_Activity', 'Function', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        X = self.data[features]
        y = self.data['Employable']
        X = pd.DataFrame(self.imputer.fit_transform(X), columns=features)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        # Save the split data to CSV for debugging
        self.ensure_directory('debugData')
        pd.DataFrame(self.X_train, columns=features).to_csv('debugData/training_data.csv', index=False)
        pd.DataFrame(self.y_train).to_json('debugData/training_labels.json')
        pd.DataFrame(self.X_test, columns=features).to_csv('debugData/testing_data.csv', index=False)
        pd.DataFrame(self.y_test).to_json('debugData/testing_labels.json')

    def train_model(self):
        self.model = XGBClassifier(objective='binary:logistic', learning_rate=0.1, n_estimators=100, max_depth=5, subsample=0.8)
        self.model.fit(self.X_train, self.y_train)
        print("Model training complete.")

    def evaluate_model(self):
        y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"Model accuracy: {accuracy}")
        print("Feature importances:", self.model.feature_importances_)

    def save_model(self, path):
        joblib.dump(self.model, path)
        print("Model saved to", path)

    def load_model(self, path):
        self.model = joblib.load(path)
        print("Model loaded from", path)

    def full_pipeline(self):
        self.extract_data()
        self.split_data()
        self.train_model()
        self.evaluate_model()

# Example usage:
# predictor = EmploymentPredictor()
# predictor.full_pipeline()
# predictor.save_model("path_to_save_model.joblib")
