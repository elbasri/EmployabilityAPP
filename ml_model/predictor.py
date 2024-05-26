import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from config import Config
import os

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
        jobs_data = list(self.jobs_collection.find({}, projection={'_id': False}))
        self.data = pd.DataFrame(jobs_data)
        self.preprocess_data()
        self.ensure_directory('debugData')
        self.data.to_csv('debugData/extracted_data.csv', index=False)

    def preprocess_data(self):
        # Flatten and convert 'experience_required' to numeric
        self.data['experience_required'] = self.data['experience_required'].apply(
            lambda x: np.mean([float(item) for sublist in x for item in (sublist if isinstance(sublist, list) else [sublist])]) if isinstance(x, list) else float(x)
        )

        # Concatenate list items into a single string for 'sector_activity' and 'function'
        for col in ['sector_activity', 'function']:
            self.data[col] = self.data[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)

        # Convert categorical data using get_dummies
        categorical_cols = ['sector_activity', 'function', 'contract_type_offered']
        self.data = pd.get_dummies(self.data, columns=categorical_cols)

        # Handle numeric conversion for study level fields
        for level in ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']:
            self.data[level] = self.data['study_level_required'].apply(lambda x: float(x.get(level, 0)) if isinstance(x, dict) else 0)

        # Identify numeric columns and convert them
        numeric_cols = self.data.columns.drop('Employable', errors='ignore')
        for col in numeric_cols:
            try:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')  # Convert columns to numeric, coercing errors to NaN
            except Exception as e:
                print(f"Error converting {col} to numeric: {e}")

        # Fill NaNs with zero or another appropriate value after attempting conversion
        self.data.fillna(0, inplace=True)

        # Apply MinMaxScaler
        self.data[numeric_cols] = self.scaler.fit_transform(self.data[numeric_cols])

        self.data.to_csv('debugData/preprocessed_data.csv', index=False)
        print("Data preprocessed and saved to 'debugData/preprocessed_data.csv'.")




    def split_data(self):
        features = self.data.columns.drop('Employable')
        X = self.data[features]
        y = self.data['Employable']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.ensure_directory('debugData')
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
        if not self.model:
            self.build_model()
        self.model.fit(self.X_train, self.y_train, epochs=200, batch_size=64, validation_data=(self.X_test, self.y_test), callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)])
        self.model.save('ml_model/trained/model.h5')

    def evaluate_model(self):
        results = self.model.evaluate(self.X_test, self.y_test)
        print(f"Model evaluation results - Loss: {results[0]}, Accuracy: {results[1]}")

    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)
        
    def predict(self, input_data):
        # Convert input_data dict into DataFrame
        input_df = pd.DataFrame([input_data])

        # Preprocess data (same as during training)
        # Dummy encode and scale the numeric columns as required
        input_df = pd.get_dummies(input_df)
        numeric_cols = ['Experience_Required', 'Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        input_df[numeric_cols] = self.scaler.transform(input_df[numeric_cols])

        # Predict using the loaded model
        prediction = self.model.predict(input_df)
        predicted_class = (prediction > 0.5).astype(int)  # Assuming binary classification with a threshold of 0.5
        return predicted_class[0][0]
    
    def full_pipeline(self):
        self.extract_data()
        self.split_data()
        self.train_model()
        self.evaluate_model()
