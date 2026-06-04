# =============== NUMPY COMPATIBILITY PATCHES (MUST BE FIRST) ==================
import numpy as np
import numpy.random as random

# Fix numpy compatibility issues
if not hasattr(np, '_core'):
    np._core = np.core

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

# =============== IMPORTS ==================
import streamlit as st
import pandas as pd
import joblib
import base64
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

# =============== BACKGROUND IMAGE FUNCTION ==================
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

add_bg_from_local("bg2.jpg")

# ==================== CUSTOM CSS ======================
st.markdown("""
    <style>
        .form-section-wrapper {
            position: absolute;
            width: 750px;
            margin: auto;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 18px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            min-height: 580px;
            background-color: rgba(255, 255, 255, 0.50) !important;
        }
     
        .form-content {
            position: relative;
            z-index: 2;
            padding: 40px;
        }
        
        .main-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .main-title {
            color: #1a5276;
            font-weight: 800;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #1a5276 0%, #3498db 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            color: #5d6d7e;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 40px;
            line-height: 1.6;
        }
        
        .stNumberInput {
            margin-bottom: 25px;
        }
        
        .stNumberInput label {
            font-weight: 600;
            color: black;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }
        
        .stNumberInput input {
            border-radius: 10px;
            border: 2px solid #e8f4fc;
            padding: 12px 16px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8fafc;
            color: #7f8c8d;
        }
        
        .stNumberInput input:focus {
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
            background: white;
            color: #7f8c8d;
        }
        
        .stNumberInput input:hover {
            border-color: #aed6f1;
        }
        
        .stNumberInput button {
            display: none !important;
        }
        
        div[data-testid="stNumberInputContainer"] > div:last-child {
            display: none !important;
        }
        
        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            border: none;
            margin-top: 10px;
            box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
        }
        
        .section-header {
            color: #2c3e50;
            font-weight: 700;
            font-size: 1.3rem;
            margin: 0 0 25px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f4fc;
            text-align: center;
        }
        
        .stHorizontalBlock {
            margin-bottom: 20px;
        }
        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .form-content {
                padding: 25px;
            }
            .main-title {
                font-size: 2rem;
            }
        }
        
        .input-cleaning-active {
            border-color: #3498db !important;
            background-color: #f0f8ff !important;
        }
        
        .result-section-wrapper {
            position: absolute;
            width: 750px;
            margin: 30px auto;
            left: 50%;
            top: -20px; 
            transform: translateX(-50%);
            border-radius: 18px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            min-height: 400px;
            background-color: rgba(255, 255, 255, 0.50) !important;
            padding: 40px;
        }
        .result-content {
            position: relative;
            z-index: 2;
        }
        .result-text {
            color: #2c3e50 !important;
        }
        .result-header {
            color: #2c3e50 !important;
            font-weight: 700;
            font-size: 1.3rem;
            margin: 0 0 25px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(232, 244, 252, 0.7);
            text-align: center;
        }
    </style>
    
    <script>
        function cleanNumberInput(inputElement) {
            let value = inputElement.value;
            let oldValue = inputElement.getAttribute('data-old-value') || '';
            
            value = value.replace(/[+-]/g, '');
            
            if (value.includes('.')) {
                let parts = value.split('.');
                if (parts[0].length > 1) {
                    parts[0] = parts[0].replace(/^0+(?=\\d)/, '');
                }
                value = parts.join('.');
            } else {
                if (value.length > 1) {
                    value = value.replace(/^0+(?=\\d)/, '');
                }
            }
            
            if (value === '' || value === '.' || value === '-') {
                value = '0';
            }
            
            if (value !== oldValue) {
                inputElement.value = value;
                inputElement.setAttribute('data-old-value', value);
                inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                inputElement.dispatchEvent(new Event('change', { bubbles: true }));
                
                inputElement.classList.add('input-cleaning-active');
                setTimeout(() => {
                    inputElement.classList.remove('input-cleaning-active');
                }, 300);
            }
            
            return value;
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            setupInputCleaning();
            document.addEventListener('streamlit:render', function() {
                setTimeout(setupInputCleaning, 100);
            });
        });
        
        function setupInputCleaning() {
            const numberInputs = document.querySelectorAll('input[type="number"]');
            
            numberInputs.forEach(input => {
                if (input.hasAttribute('data-cleaning-initialized')) {
                    return;
                }
                
                cleanNumberInput(input);
                
                input.addEventListener('input', function(e) {
                    setTimeout(() => {
                        cleanNumberInput(this);
                    }, 0);
                });
                
                input.addEventListener('keydown', function(e) {
                    if (e.key === '+' || e.key === '-' || e.key === 'e' || e.key === 'E') {
                        e.preventDefault();
                    }
                });
                
                input.addEventListener('paste', function(e) {
                    setTimeout(() => {
                        cleanNumberInput(this);
                    }, 10);
                });
                
                input.addEventListener('blur', function() {
                    cleanNumberInput(this);
                });
                
                input.setAttribute('data-cleaning-initialized', 'true');
            });
            
            removeIncrementButtons();
        }
        
        function removeIncrementButtons() {
            const stepUpButtons = document.querySelectorAll('[data-testid="stNumberInputStepUp"]');
            const stepDownButtons = document.querySelectorAll('[data-testid="stNumberInputStepDown"]');
            
            stepUpButtons.forEach(btn => {
                btn.style.display = 'none';
                btn.remove();
            });
            
            stepDownButtons.forEach(btn => {
                btn.style.display = 'none';
                btn.remove();
            });
            
            const buttonContainers = document.querySelectorAll('.stNumberInput > div:last-child');
            buttonContainers.forEach(container => {
                if (container.querySelector('[data-testid="stNumberInputStepUp"]') || 
                    container.querySelector('[data-testid="stNumberInputStepDown"]')) {
                    container.style.display = 'none';
                    container.remove();
                }
            });
        }
    </script>
""", unsafe_allow_html=True)

# ===================== SIMPLE MODEL LOADER ==========================
@st.cache_resource
def load_diabetes_model():
    """Load the diabetes prediction model"""
    model_path = "diabetes_gb.pkl"
    
    if not os.path.exists(model_path):
        st.error("❌ Model file not found!")
        st.stop()
    
    # Try different loading methods
    model_data = None
    
    # Method 1: Try joblib
    try:
        model_data = joblib.load(model_path)
    except:
        pass
    
    # Method 2: Try pickle
    if model_data is None:
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
        except:
            pass
    
    # Method 3: Try pickle with latin1 encoding
    if model_data is None:
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f, encoding='latin1')
        except:
            pass
    
    if model_data is None:
        st.error("❌ Could not load model file!")
        st.stop()
    
    # Extract model components
    if isinstance(model_data, tuple):
        if len(model_data) == 3:
            model, scaler, saved_cols = model_data
        elif len(model_data) == 2:
            model, scaler = model_data
            saved_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        else:
            model = model_data[0]
            scaler = None
            saved_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    else:
        model = model_data
        scaler = None
        saved_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    
    if model is None:
        st.error("❌ Could not extract model from file!")
        st.stop()
    
    st.success("✅ Model loaded successfully!")
    return model, scaler, saved_cols

# Load the model
model, scaler, saved_cols = load_diabetes_model()

# ======================= MAIN UI ==========================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">Diabetes Prediction System</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle" style="color: black;">Enter patient health metrics below for diabetes risk assessment</p>',
    unsafe_allow_html=True
)

# Form Section
st.markdown('<div class="form-section-wrapper">', unsafe_allow_html=True)

# Initialize session state
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

default_values = {
    'preg': 0, 'bp': 0, 'ins': 0, 'dpf': 0.0,
    'glu': 0, 'skin': 0, 'bmi': 0.0, 'age': 0
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown('<div class="section-header">Patient Health Metrics</div>', unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns(2, gap="large")

with col1:
    pregnancies = st.number_input(
        "No. of Pregnancies", 0, 20, 
        value=st.session_state.preg, step=1,
        key=f"preg_{st.session_state.reset_counter}"
    )
    
    glucose = st.number_input(
        "Glucose Level (mg/dL)", 0, 300, 
        value=st.session_state.glu, step=1,
        key=f"glu_{st.session_state.reset_counter}"
    )
    
    blood_pressure = st.number_input(
        "Blood Pressure (mm Hg)", 0, 200, 
        value=st.session_state.bp, step=1,
        key=f"bp_{st.session_state.reset_counter}"
    )
    
    skin_thickness = st.number_input(
        "Skin Thickness (mm)", 0, 100, 
        value=st.session_state.skin, step=1,
        key=f"skin_{st.session_state.reset_counter}"
    )

with col2:
    insulin = st.number_input(
        "Insulin Level (μU/ml)", 0, 900, 
        value=st.session_state.ins, step=1,
        key=f"ins_{st.session_state.reset_counter}"
    )
    
    bmi = st.number_input(
        "Body Mass Index", 0.0, 70.0, 
        value=st.session_state.bmi, step=0.1, format="%.1f",
        key=f"bmi_{st.session_state.reset_counter}"
    )
    
    dpf = st.number_input(
        "Diabetes Pedigree Function", 0.0, 3.0, 
        value=st.session_state.dpf, step=0.01, format="%.3f",
        key=f"dpf_{st.session_state.reset_counter}"
    )
    
    age = st.number_input(
        "Age (years)", 0, 120, 
        value=st.session_state.age, step=1,
        key=f"age_{st.session_state.reset_counter}"
    )

# Update session state
st.session_state.preg = pregnancies
st.session_state.glu = glucose
st.session_state.bp = blood_pressure
st.session_state.skin = skin_thickness
st.session_state.ins = insulin
st.session_state.bmi = bmi
st.session_state.dpf = dpf
st.session_state.age = age

# Buttons
st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    predict = st.button("Predict Risk", type="primary", use_container_width=True)

with btn_col2:
    reset_btn = st.button("Reset Form", type="secondary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close form-section-wrapper

# Reset logic
if reset_btn:
    for key in default_values.keys():
        st.session_state[key] = default_values[key]
    st.session_state.reset_counter += 1
    st.rerun()

# Prediction
if predict:
    input_df = pd.DataFrame(
        [[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]],
        columns=saved_cols
    )
    
    if scaler is not None:
        try:
            input_scaled = scaler.transform(input_df)
        except:
            input_scaled = input_df.values
    else:
        input_scaled = input_df.values
    
    try:
        prediction = model.predict(input_scaled)[0]
        prediction_proba = model.predict_proba(input_scaled)[0]
        risk_score = prediction_proba[1] * 100
        
        # Result card
        st.markdown('<div class="result-section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="result-content">', unsafe_allow_html=True)
        st.markdown('<div class="result-header">Prediction Result</div>', unsafe_allow_html=True)
        
        result_col1, result_col2 = st.columns([3, 1])
        
        with result_col1:
            if prediction == 1:
                st.markdown("""
                <div class="result-text">
                <h3 style="color: Red; margin-bottom: 20px;">High Diabetes Risk Detected</h3>
                <p><strong>The patient shows significant indicators for diabetes.</strong></p>
                <p><strong>Immediate Actions Recommended:</strong></p>
                <ul>
                <li>Consult with an endocrinologist</li>
                <li>Schedule HbA1c and fasting glucose tests</li>
                <li>Begin lifestyle modifications</li>
                <li>Regular monitoring required</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-text">
                <h3 style="color: Green; margin-bottom: 20px;">Low Diabetes Risk</h3>
                <p><strong>The patient is unlikely to have diabetes based on current metrics.</strong></p>
                <p><strong>Preventive Measures:</strong></p>
                <ul>
                <li>Maintain healthy BMI (18.5-24.9)</li>
                <li>Regular physical activity (150 mins/week)</li>
                <li>Balanced diet with low sugar intake</li>
                <li>Annual health checkups recommended</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
        
        with result_col2:
            if prediction == 1:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border-radius: 10px; border: 2px solid rgba(231, 76, 60, 0.5); background-color: rgba(253, 242, 242, 0.7);">
                    <h4>Risk Score</h4>
                    <h1 style="font-size: 2.2rem; margin: 0;">{risk_score:.1f}%</h1>
                    <p style="color: Red; font-weight: 600;">HIGH</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border-radius: 10px; border: 2px solid rgba(46, 204, 113, 0.5); background-color: rgba(249, 254, 249, 0.7);">
                    <h4>Risk Score</h4>
                    <h1 style="font-size: 2.2rem; margin: 0;">{risk_score:.1f}%</h1>
                    <p style="color: Green; font-weight: 600;">LOW</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")

# Footer
st.markdown("""
    <div style="text-align: center; color: black; font-size: 0.9rem; margin-top: 40px;">
        <p>This tool provides preliminary assessment only. Always consult with a healthcare professional for accurate diagnosis.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
