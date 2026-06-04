import os
import sys
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

# =============== APPLY NUMPY PATCHES FIRST ==================
if not hasattr(np, '_core'):
    np._core = np.core

import numpy.random as random
if not hasattr(random, '_mt19937'):
    class _MT19937:
        class MT19937:
            def __init__(self, *args, **kwargs):
                pass
    random._mt19937 = _MT19937()

if not hasattr(random, 'BitGenerator'):
    class BitGenerator:
        def __init__(self, *args, **kwargs):
            pass
    random.BitGenerator = BitGenerator

if not hasattr(np.random, '_mt19937'):
    np.random._mt19937 = random._mt19937
if not hasattr(np.random, 'BitGenerator'):
    np.random.BitGenerator = random.BitGenerator

# =============== MODEL ==================
MODEL_PATH = "diabetes_gb.pkl"

def extract_model_from_pickle():
    """Try to extract just the model weights and create a new model"""
    print("\n" + "="*60)
    print("FORCE MODEL EXTRACTION AND FIX")
    print("="*60)
    
    if not os.path.exists(MODEL_PATH):
        print(f"{MODEL_PATH} not found!")
        return None, None, None
    
    print(f"Found {MODEL_PATH} ({os.path.getsize(MODEL_PATH)} bytes)")
    
    try:
        with open(MODEL_PATH, 'rb') as f:
            data = None
            for encoding in [None, 'latin1', 'bytes', 'utf-8']:
                try:
                    if encoding:
                        f.seek(0)
                        data = pickle.load(f, encoding=encoding)
                    else:
                        f.seek(0)
                        data = pickle.load(f)
                    print(f"Loaded with encoding: {encoding or 'default'}")
                    break
                except:
                    continue
            
            if data is None:
                print("Could not load with any encoding")
                return None, None, None
            
            from sklearn.ensemble import GradientBoostingClassifier
            
            model = None
            scaler = None
            columns = None
            
            def find_model(obj, depth=0):
                if depth > 5:
                    return None
                if hasattr(obj, 'predict') and hasattr(obj, 'predict_proba'):
                    return obj
                if isinstance(obj, (list, tuple)):
                    for item in obj:
                        result = find_model(item, depth+1)
                        if result is not None:
                            return result
                if hasattr(obj, '__dict__'):
                    for key, value in obj.__dict__.items():
                        result = find_model(value, depth+1)
                        if result is not None:
                            return result
                return None
            
            def find_scaler(obj, depth=0):
                if depth > 5:
                    return None
                if hasattr(obj, 'transform') and hasattr(obj, 'fit_transform'):
                    return obj
                if isinstance(obj, (list, tuple)):
                    for item in obj:
                        result = find_scaler(item, depth+1)
                        if result is not None:
                            return result
                if hasattr(obj, '__dict__'):
                    for key, value in obj.__dict__.items():
                        result = find_scaler(value, depth+1)
                        if result is not None:
                            return result
                return None
            
            def find_columns(obj, depth=0):
                if depth > 5:
                    return None
                if isinstance(obj, list) and len(obj) == 8 and all(isinstance(x, str) for x in obj):
                    return obj
                if isinstance(obj, (list, tuple)):
                    for item in obj:
                        result = find_columns(item, depth+1)
                        if result is not None:
                            return result
                if hasattr(obj, '__dict__'):
                    for key, value in obj.__dict__.items():
                        result = find_columns(value, depth+1)
                        if result is not None:
                            return result
                return None
            
            print("\nSearching for model in pickle data...")
            model = find_model(data)
            if model:
                print(f"Found model: {type(model).__name__}")
            
            print("Searching for scaler...")
            scaler = find_scaler(data)
            if scaler:
                print(f"Found scaler: {type(scaler).__name__}")
            
            print("Searching for column names...")
            columns = find_columns(data)
            if columns:
                print(f"Found columns: {columns}")
            
            if model is None:
                if isinstance(data, tuple) and len(data) > 0:
                    if hasattr(data[0], 'predict'):
                        model = data[0]
                        print(f"Using first tuple element as model")
            
            if model:
                if columns is None:
                    columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                              'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
                
                import joblib
                fixed_path = "diabetes_model_fixed.pkl"
                joblib.dump((model, scaler, columns), fixed_path, protocol=4)
                print(f"\nSaved fixed model to {fixed_path}")
                
                with open(".model_fixed_success", "w") as f:
                    f.write("Model successfully fixed and saved")
                
                return model, scaler, columns
            else:
                print("\nCould not find model in the pickle file")
                return None, None, None
                
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return None, None, None

# =============== FIX MODEL ==================
import joblib

model = None
scaler = None
cols = None

if os.path.exists("diabetes_model_fixed.pkl") and os.path.exists(".model_fixed_success"):
    print("Fixed model already exists, loading...")
    try:
        model_data = joblib.load("diabetes_model_fixed.pkl")
        if isinstance(model_data, tuple) and len(model_data) >= 2:
            model = model_data[0]
            scaler = model_data[1]
            cols = model_data[2] if len(model_data) > 2 else None
            print("Loaded existing fixed model")
        else:
            model, scaler, cols = None, None, None
    except Exception as e:
        print(f"Error loading fixed model: {e}")
        model, scaler, cols = None, None, None

if model is None:
    print("No fixed model found, attempting to extract from original...")
    model, scaler, cols = extract_model_from_pickle()

if model is None:
    print("Creating a basic model for testing...")
    from sklearn.ensemble import GradientBoostingClassifier
    X_dummy = np.random.randn(200, 8)
    y_dummy = (X_dummy[:, 0] + X_dummy[:, 1] > 0).astype(int)
    model = GradientBoostingClassifier(n_estimators=50, random_state=42)
    model.fit(X_dummy, y_dummy)
    scaler = None
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    print("Using demo model for testing")

if cols is None:
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

# =============== IMPORT STREAMLIT ==================
import streamlit as st
import pandas as pd
import base64

# =============== PAGE CONFIG ==================
st.set_page_config(page_title="Diabetes Prediction System", layout="wide")

# =============== CUSTOM CSS ==================
st.markdown("""
    <style>
    /* Baby blue background for main app */
    .stApp {
        background-color: #89CFF0 !important;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Center headings */
    h1, h2, h3 {
        text-align: center;
    }
    
    /* Hero container */
    .hero-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-container h1 {
        background: linear-gradient(135deg, #0F4C5F 0%, #1C6E7E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.8rem !important;
        letter-spacing: -0.5px;
    }
    
    .hero-container p {
        color: #1a4c64;
        font-size: 2rem !important;
        font-weight: 500;
        max-width: 700px;
        margin: 0 auto;
        text-align: center;
        line-height: 1.6;
    }
    
    /* Section headers */
    .stMarkdown h4 {
        color: #0F4C5F !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.2rem !important;
        margin-top: 0.5rem !important;
        letter-spacing: 0.3px;
    }
    
    .stMarkdown h3 {
        color: #0F4C5F !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Input labels */
    .stNumberInput label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #1a4c64 !important;
        margin-bottom: 0.6rem !important;
    }
    
    /* Input styling */
    .stNumberInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #d4e4f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        background-color: #ffffff !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #5aa9c9 !important;
        box-shadow: 0 0 0 3px rgba(90, 169, 201, 0.15) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1f6e8c !important;
        color: white !important;
        border-radius: 40px !important;
        padding: 0.9rem 2.5rem !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background-color: #0e5a75 !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(15, 76, 95, 0.25) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Metric styling */
    div[data-testid="stMetric"] {
        background-color: white !important;
        border-radius: 15px !important;
        padding: 1.2rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #e8f0f5 !important;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: #666 !important;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1f6e8c !important;
        margin: 0.8rem 0 !important;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* Alert/Info box styling */
    .stAlert {
        border-radius: 12px !important;
        padding: 1.2rem !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
    }
    
    .stAlert p {
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        margin: 0.5rem 0 !important;
    }
    
    .stAlert strong {
        font-weight: 700 !important;
        font-size: 0.97rem !important;
    }
    
    /* Error message */
    .stError {
        font-size: 0.95rem !important;
    }
    
    .stError h3 {
        font-size: 2rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Success message */
    .stSuccess h3 {
        font-size: 2rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(31, 110, 140, 0.1), rgba(90, 169, 201, 0.05)) !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #0F4C5F !important;
        padding: 0.8rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(31, 110, 140, 0.15), rgba(90, 169, 201, 0.1)) !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #1f6e8c, transparent) !important;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, #1f6e8c, #0F4C5F) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.8rem !important;
    }
    
    [data-testid="stDataFrame"] td {
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        color: #333 !important;
        background-color: white !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover td {
        background-color: #f0f7fb !important;
    }
    
    /* Disclaimer styling */
    .disclaimer-text {
        text-align: center;
        color: white !important;
        background-color: transparent;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
    
    .disclaimer-text p {
        color: white !important;
        margin: 0.6rem 0 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    .disclaimer-text strong {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Subheader styling for results */
    [data-testid="stMarkdownContainer"] > h3:first-of-type {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Result message styling */
    .stError h3, .stSuccess h3 {
        font-size: 2rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# =============== MAIN UI ==================
st.markdown("""
<div class="hero-container">
    <h1>Diabetes Risk Assessment</h1>
    <p>Enter patient clinical measurements to generate a diabetes risk prediction.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Initialize session state
if 'reset' not in st.session_state:
    st.session_state.reset = False

# Default values
defaults = {
    'pregnancies': 0, 
    'glucose': 0, 
    'bp': 0, 
    'skin': 0,
    'insulin': 0, 
    'bmi': 0.0, 
    'dpf': 0.0, 
    'age': 0
}

# Create two columns for inputs
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### Patient Metrics")
    pregnancies = st.number_input(
        "Number of Pregnancies", 
        min_value=0, 
        max_value=20, 
        value=defaults['pregnancies'], 
        step=1,
        key="pregnancies_input"
    )
    
    glucose = st.number_input(
        "Glucose Level (mg/dL)", 
        min_value=0, 
        max_value=300, 
        value=defaults['glucose'], 
        step=1,
        key="glucose_input"
    )
    
    blood_pressure = st.number_input(
        "Blood Pressure (mm Hg)", 
        min_value=0, 
        max_value=200, 
        value=defaults['bp'], 
        step=1,
        key="bp_input"
    )
    
    skin_thickness = st.number_input(
        "Skin Thickness (mm)", 
        min_value=0, 
        max_value=100, 
        value=defaults['skin'], 
        step=1,
        key="skin_input"
    )

with col2:
    st.markdown("#### Clinical Measurements")
    insulin = st.number_input(
        "Insulin Level (μU/ml)", 
        min_value=0, 
        max_value=900, 
        value=defaults['insulin'], 
        step=1,
        key="insulin_input"
    )
    
    bmi = st.number_input(
        "Body Mass Index (BMI)", 
        min_value=0.0, 
        max_value=70.0, 
        value=defaults['bmi'], 
        step=0.1, 
        format="%.1f",
        key="bmi_input"
    )
    
    dpf = st.number_input(
        "Diabetes Pedigree Function", 
        min_value=0.0, 
        max_value=3.0, 
        value=defaults['dpf'], 
        step=0.01, 
        format="%.3f",
        key="dpf_input"
    )
    
    age = st.number_input(
        "Age (years)", 
        min_value=0, 
        max_value=120, 
        value=defaults['age'], 
        step=1,
        key="age_input"
    )

st.markdown("---")
btn_col1, btn_col2 = st.columns(2, gap="medium")

with btn_col1:
    predict_btn = st.button("Predict Risk", type="primary", use_container_width=True)

with btn_col2:
    reset_btn = st.button("Reset Form", use_container_width=True)

# Reset logic
if reset_btn:
    st.session_state.pregnancies_input = defaults['pregnancies']
    st.session_state.glucose_input = defaults['glucose']
    st.session_state.bp_input = defaults['bp']
    st.session_state.skin_input = defaults['skin']
    st.session_state.insulin_input = defaults['insulin']
    st.session_state.bmi_input = defaults['bmi']
    st.session_state.dpf_input = defaults['dpf']
    st.session_state.age_input = defaults['age']
    st.rerun()

# Prediction
if predict_btn:
    # Check if any data was entered
    if all(v == 0 for v in [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]):
        st.warning("Please enter patient information before generating an assessment.")
    else:
        # Create input dataframe
        input_data = pd.DataFrame(
            [[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]], 
            columns=cols
        )
        
        # Scale if needed
        if scaler is not None:
            try:
                input_scaled = scaler.transform(input_data)
            except:
                input_scaled = input_data.values
        else:
            input_scaled = input_data.values
        
        # Make prediction
        try:
            prediction = model.predict(input_scaled)[0]
            proba = model.predict_proba(input_scaled)[0]
            risk_score = proba[1] * 100
            
            st.markdown("---")
            st.subheader("Prediction Result")
            
            # Display result with styling
            if prediction == 1:
                st.error("### HIGH DIABETES RISK DETECTED")
                st.markdown(f"**Risk Score:** {risk_score:.1f}%")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("Confidence Level", f"{max(proba)*100:.1f}%", "High Risk")
                with col_info2:
                    st.metric("Risk Category", "HIGH", "Medical attention needed")
                
                st.info("""
                **Immediate Actions Recommended:**
                - Consult with an endocrinologist immediately
                - Schedule HbA1c and fasting glucose tests
                - Begin lifestyle modifications (diet and exercise)
                - Regular monitoring of blood glucose levels
                - Discuss medication options with healthcare provider
                """)
            else:
                st.success("### LOW DIABETES RISK")
                st.markdown(f"**Risk Score:** {risk_score:.1f}%")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("Confidence Level", f"{max(proba)*100:.1f}%", "Low Risk")
                with col_info2:
                    st.metric("Risk Category", "LOW", "Preventive measures")
                
                st.info("""
                **Preventive Measures:**
                - Maintain healthy BMI (18.5-24.9)
                - Regular physical activity (150 mins/week)
                - Balanced diet with low sugar intake
                - Annual health checkups recommended
                - Periodic blood glucose monitoring
                """)
                
            # Show input summary
            with st.expander("View Patient Data Summary"):
                summary_data = {
                    "Metric": ["Pregnancies", "Glucose", "Blood Pressure", "Skin Thickness", 
                              "Insulin", "BMI", "Diabetes Pedigree", "Age"],
                    "Value": [pregnancies, glucose, blood_pressure, skin_thickness, 
                             insulin, bmi, dpf, age]
                }
                summary_df = pd.DataFrame(summary_data)
                st.table(summary_df)
            
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
            st.info("Please ensure all inputs are valid numbers and try again.")

# Footer with white text disclaimer
st.markdown("---")
st.markdown(
    """
    <div class="disclaimer-text">
        <p><strong>Disclaimer:</strong> This tool provides preliminary assessment only based on the data entered. 
        It is not a substitute for professional medical advice, diagnosis, or treatment. 
        Always consult with a healthcare professional for accurate diagnosis and treatment recommendations.</p>
        <p style="font-size: 1rem; margin-top: 1rem;">© 2025 Diabetes Prediction System</p>
    </div>
    """, 
    unsafe_allow_html=True
)
