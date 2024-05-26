import pandas as pd
import numpy as np
import re
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
from config import Config
from sklearn.impute import SimpleImputer

class EmploymentPredictor:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.jobs_collection = self.db[Config.JOBS_COLLECTION]
        self.model = None
        self.scaler = StandardScaler()
        self.min_max_scaler = MinMaxScaler()
        self.imputer = SimpleImputer(strategy='mean')

    def extract_data(self):
        # Fetch data from MongoDB collection
        jobs_data = list(self.jobs_collection.find({}, projection={'_id': False}))
        self.data = pd.DataFrame(jobs_data)
        
        # Preprocess the data immediately after extraction
        self.preprocess_data()
        
    def clean_text(self, text):
        """ Clean text by removing extra spaces, newlines, and non-alphanumeric characters. """
        return re.sub(r'\s+', ' ', str(text)).strip()

    def preprocess_data(self):
        # Clean the text fields, ensure the field exists before applying the function
        if 'company_name' in self.data.columns:
            self.data['Company_Name'] = self.data['company_name'].apply(self.clean_text)
        if 'job_title' in self.data.columns:
            self.data['Job_Title'] = self.data['job_title'].apply(self.clean_text)

        # Extract the first relevant value from lists
        self.data['Sector_Activity'] = self.data.get('sector_activity', pd.Series()).apply(
            lambda x: x[0] if isinstance(x, list) and x else None
        )
        self.data['Function'] = self.data.get('function', pd.Series()).apply(
            lambda x: x[0] if isinstance(x, list) and x else None
        )
        self.data['Experience_Required'] = self.data.get('experience_required', pd.Series()).apply(
            lambda x: x[0][0] if isinstance(x, list) and x and isinstance(x[0], list) and x[0] else 0
        )
        # Normalize Experience_Required to a 0-1 scale
        self.data['Experience_Required'] = self.min_max_scaler.fit_transform(self.data[['Experience_Required']])

        # Normalize study_level_required into multiple columns and concat them
        if 'study_level_required' in self.data.columns:
            education_df = pd.json_normalize(self.data['study_level_required'])
            self.data = pd.concat([self.data.drop('study_level_required', axis=1), education_df], axis=1)
        else:
            # Add default columns for education if 'study_level_required' is missing
            for level in ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']:
                self.data[level] = 0

    def split_data(self):
        features = ['Experience_Required', 'Sector_Activity', 'Function', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        X = self.data[features]
        y = self.data['Employable']

        # Impute missing values
        X = pd.DataFrame(self.imputer.fit_transform(X), columns=features)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)


    def train_model(self):
        self.model = LogisticRegression()
        self.model.fit(self.X_train, self.y_train)
        print("Model training complete.")

    def evaluate_model(self):
        y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"Model accuracy: {accuracy}")
        # Print coefficients
        print("Feature coefficients:")
        feature_names = ['Experience_Required', 'Sector_Activity', 'Function', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        for name, coef in zip(feature_names, self.model.coef_[0]):
            print(f"{name}: {coef}")

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
