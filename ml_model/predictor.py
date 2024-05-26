import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from config import Config
import os
import numpy as np
import shutil

class EmploymentPredictor:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.jobs_collection = self.db[Config.JOBS_COLLECTION]
        self.model = None
        self.scaler = MinMaxScaler()

    def ensure_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def extract_data(self):
        jobs_data = list(self.jobs_collection.find({}, projection={
            '_id': False, 
            'experience_required': True, 
            'study_level_required': True, 
            'Employable': True
        }))
        self.data = pd.DataFrame(jobs_data)
        self.preprocess_data()
        self.ensure_directory('debugData')
        self.data.to_csv('debugData/extracted_data.csv', index=False)

    def preprocess_data(self):
        # Flatten and convert 'experience_required' to numeric by taking the first value of the nested list
        self.should_remember_user = False
        self.data['experience_required'] = self.data['experience_required'].apply(
            lambda x: float(x[0][0]) if isinstance(x, list) and len(x) > 0 and isinstance(x[0], list) and len(x[0]) > 0 else (float(x[0]) if isinstance(x, list) and len(x) > 0 else 0.0)
        )

        # Extract study level fields and ensure they are numeric
        for level in ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']:
            self.data[level] = self.data['study_level_required'].apply(lambda x: float(x.get(level, 0)) if isinstance(x, dict) and level in x else 0)

        # Specify numeric columns explicitly to include 'experience_required' and the education levels
        numeric_cols = ['experience_required', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        
        # Convert columns to numeric, coercing errors to NaN
        self.data[numeric_cols] = self.data[numeric_cols].apply(pd.to_numeric, errors='coerce')

        # Fill NaNs with zero or another appropriate value after attempting conversion
        self.data.fillna(0, inplace=True)

        # Apply MinMaxScaler
        self.data[numeric_cols] = self.scaler.fit_transform(self.data[numeric_cols])

        self.data.to_csv('debugData/preprocessed_data.csv', index=False)
        print("Data preprocessed and saved to 'debugData/preprocessed_data.csv'.")


    def split_data(self):
        # Define the columns to include in the model
        feature_columns = ['experience_required', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        
        # Select only the defined columns and the target variable 'Employable'
        data_model = self.data[feature_columns + ['Employable']]
        
        # Split data into features and target
        X = data_model[feature_columns]
        y = data_model['Employable']
        
        # Split the data into training and testing sets
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        
        # Ensure the directory exists for saving CSV files
        self.ensure_directory('debugData')
        
        # Save the split data into CSV files for debugging or further use
        self.X_train.to_csv('debugData/training_data.csv', index=False)
        self.y_train.to_csv('debugData/training_labels.csv', index=False)
        self.X_test.to_csv('debugData/testing_data.csv', index=False)
        self.y_test.to_csv('debugData/testing_labels.csv', index=False)


    def build_model(self):
        input_shape = self.X_train.shape[1]  # Ensures correct input shape is used
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(512, activation='relu', input_shape=(input_shape,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def train_model(self):
        delete_existing_model('ml_model/trained/model.h5')
        delete_existing_model('ml_model/trained/scaler.npz')
        self.build_model()
        #if not self.model:
        #    self.build_model()
        self.model.fit(self.X_train, self.y_train, epochs=2000, batch_size=64, validation_data=(self.X_test, self.y_test), callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=100, restore_best_weights=True)])
        self.model.save('ml_model/trained/model.h5')
        np.savez('ml_model/trained/scaler.npz', scale=self.scaler.scale_, min_=self.scaler.min_)

    def evaluate_model(self):
        results = self.model.evaluate(self.X_test, self.y_test)
        print(f"Model evaluation results - Loss: {results[0]}, Accuracy: {results[1]}")

    def load_model(self, model_path, scaler_path):
        self.model = tf.keras.models.load_model(model_path)
        scaler_state = np.load(scaler_path)
        self.scaler.scale_ = scaler_state['scale']
        self.scaler.min_ = scaler_state['min_']

    def predict(self, input_data):
        # Convert input_data dict into DataFrame
        input_df = pd.DataFrame([input_data])

        # Ensure only expected columns are included
        expected_cols = ['experience_required', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        input_df = input_df[expected_cols]

        # Convert columns to numeric, coercing errors to NaN
        input_df = input_df.apply(pd.to_numeric, errors='coerce')

        # Fill NaNs with zero or another appropriate value
        input_df.fillna(0, inplace=True)

        # Scaling numeric features as was done during training
        input_df[expected_cols] = self.scaler.transform(input_df[expected_cols])

        # Predict using the loaded model
        prediction = self.model.predict(input_df)
        predicted_class = (prediction > 0.5).astype(int)  # Assuming binary classification with a threshold of 0.5
        return predicted_class[0][0]


    
    def full_pipeline(self):
        self.extract_data()
        self.split_data()
        self.train_model()
        self.evaluate_model()


def delete_existing_model(model_path):
    """ Delete existing model files to ensure clean state """
    # Check if the file exists
    if os.path.exists(model_path):
        # If it's a directory (like TensorFlow model directory), delete the directory
        if os.path.isdir(model_path):
            shutil.rmtree(model_path)
        else:
            # If it's a file, delete the file
            os.remove(model_path)
        print("Deleted existing model at path:", model_path)
    else:
        print("No model found at path to delete:", model_path)
