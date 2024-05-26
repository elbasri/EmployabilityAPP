from ml_model.predictor import EmploymentPredictor
import os

def train_model():
    predictor = EmploymentPredictor()

    model_path = 'ml_model/trained/model.h5'
    #if os.path.exists(model_path):
    #    predictor.load_model(model_path)
    #    print("Existing model loaded.")
    #else:
    #    print("No existing model found. Training a new model.")

    predictor.full_pipeline()

    if predictor.model:
        predictor.evaluate_model()
    else:
        print("Model not trained or loaded.")

if __name__ == '__main__':
    train_model()
