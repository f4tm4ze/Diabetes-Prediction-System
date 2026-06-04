import pickle
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

# Load the existing model
try:
    print("Loading model...")
    model_data = joblib.load("diabetes_gb.pkl")
    print(f"Model loaded. Type: {type(model_data)}")
    
    # Extract components
    if isinstance(model_data, tuple):
        if len(model_data) == 3:
            model, scaler, columns = model_data
        elif len(model_data) == 2:
            model, scaler = model_data
            columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        else:
            model = model_data[0]
            scaler = None
            columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    else:
        model = model_data
        scaler = None
        columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    
    # Re-save with current environment settings
    print("Re-saving model with current environment...")
    joblib.dump((model, scaler, columns), "diabetes_gb_compatible.pkl", protocol=4)
    print("✅ Model saved as 'diabetes_gb_compatible.pkl'")
    
    # Also save as pickle for compatibility
    with open("diabetes_gb_fixed.pkl", "wb") as f:
        pickle.dump((model, scaler, columns), f, protocol=4)
    print("✅ Model also saved as 'diabetes_gb_fixed.pkl'")
    
except Exception as e:
    print(f"Error: {e}")
    print("Could not fix the model file")
