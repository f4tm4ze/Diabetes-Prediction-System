# =============== RUN MODEL FIX FIRST ==================
import os
import sys

# Run the setup script if it exists and model needs fixing
if os.path.exists("setup.py") and not os.path.exists(".model_fixed"):
    try:
        print("Running model setup...")
        exec(open("setup.py").read())# =============== COMPLETE APP.PY WITH FORCED MODEL FIX ==================
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

# =============== FORCE MODEL FIX ==================
MODEL_PATH = "diabetes_gb.pkl"

def extract_model_from_pickle():
    """Try to extract just the model weights and create a new model"""
    print("\n" + "="*60)
    print("FORCE MODEL EXTRACTION AND FIX")
    print("="*60)
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ {MODEL_PATH} not found!")
        return None, None, None
    
    print(f"✓ Found {MODEL_PATH} ({os.path.getsize(MODEL_PATH)} bytes)")
    
    # Try to read the pickle file and extract raw data
    try:
        with open(MODEL_PATH, 'rb') as f:
            # Try to load with different methods
            for encoding in [None, 'latin1', 'bytes', 'utf-8']:
                try:
                    if encoding:
                        data = pickle.load(f, encoding=encoding)
                    else:
                        f.seek(0)
                        data = pickle.load(f)
                    print(f"✓ Loaded with encoding: {encoding or 'default'}")
                    break
                except:
                    continue
            
            # Now try to extract the model
            from sklearn.ensemble import GradientBoostingClassifier
            
            model = None
            scaler = None
            columns = None
            
            # Recursively search for the model in the data
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
            
            print("\n🔍 Searching for model in pickle data...")
            model = find_model(data)
            if model:
                print(f"✓ Found model: {type(model).__name__}")
            
            print("🔍 Searching for scaler...")
            scaler = find_scaler(data)
            if scaler:
                print(f"✓ Found scaler: {type(scaler).__name__}")
            
            print("🔍 Searching for column names...")
            columns = find_columns(data)
            if columns:
                print(f"✓ Found columns: {columns}")
            
            if model is None:
                # Last resort - try to get the model from the first element
                if isinstance(data, tuple) and len(data) > 0:
                    if hasattr(data[0], 'predict'):
                        model = data[0]
                        print(f"✓ Using first tuple element as model")
            
            if model:
                # Save the extracted model
                if columns is None:
                    columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                              'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
                
                # Save with joblib
                import joblib
                fixed_path = "diabetes_model_fixed.pkl"
                joblib.dump((model, scaler, columns), fixed_path, protocol=4)
                print(f"\n✅ Saved fixed model to {fixed_path}")
                
                # Also save a marker
                with open(".model_fixed_success", "w") as f:
                    f.write("Model successfully fixed and saved")
                
                return model, scaler, columns
            else:
                print("\n❌ Could not find model in the pickle file")
                return None, None, None
                
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        return None, None, None

# =============== ATTEMPT TO FIX MODEL ==================
import joblib

# Check if we already have a fixed model
if os.path.exists("diabetes_model_fixed.pkl") and os.path.exists(".model_fixed_success"):
    print("Fixed model already exists, loading...")
    try:
        model_data = joblib.load("diabetes_model_fixed.pkl")
        if isinstance(model_data, tuple) and len(model_data) >= 2:
            model, scaler, cols = model_data[0], model_data[1], model_data[2] if len(model_data) > 2 else None
            print("✅ Loaded existing fixed model")
        else:
            model, scaler, cols = None, None, None
    except:
        model, scaler, cols = None, None, None
else:
    # Try to fix the model
    print("No fixed model found, attempting to extract from original...")
    model, scaler, cols = extract_model_from_pickle()

# If still no model, create a simple one for testing
if model is None:
    print("⚠️ Creating a basic model for testing...")
    from sklearn.ensemble import GradientBoostingClassifier
    X_dummy = np.random.randn(200, 8)
    y_dummy = (X_dummy[:, 0] + X_dummy[:, 1] > 0).astype(int)
    model = GradientBoostingClassifier(n_estimators=50, random_state=42)
    model.fit(X_dummy, y_dummy)
    scaler = None
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    print("⚠️ Using demo model for testing")

# =============== IMPORT STREAMLIT ==================
import streamlit as st
import pandas as pd
import base64

# =============== PAGE CONFIG ==================
st.set_page_config(page_title="Diabetes Prediction System", layout="wide")

# =============== BACKGROUND ==================
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
    except:
        pass

add_bg_from_local("bg2.jpg")

# =============== MAIN UI ==================
st.title("🩺 Diabetes Prediction System")
st.markdown("### Enter patient health metrics below for diabetes risk assessment")
st.markdown("---")

# Initialize session state
if 'reset' not in st.session_state:
    st.session_state.reset = False

# Default values
defaults = {
    'pregnancies': 0, 'glucose': 0, 'bp': 0, 'skin': 0,
    'insulin': 0, 'bmi': 0.0, 'dpf': 0.0, 'age': 0
}

# Create two columns
col1, col2 = st.columns(2)

with col1:
    pregnancies = st.number_input("📊 Number of Pregnancies", min_value=0, max_value=20, value=defaults['pregnancies'], step=1)
    glucose = st.number_input("🩸 Glucose Level (mg/dL)", min_value=0, max_value=300, value=defaults['glucose'], step=1)
    blood_pressure = st.number_input("❤️ Blood Pressure (mm Hg)", min_value=0, max_value=200, value=defaults['bp'], step=1)
    skin_thickness = st.number_input("📏 Skin Thickness (mm)", min_value=0, max_value=100, value=defaults['skin'], step=1)

with col2:
    insulin = st.number_input("💉 Insulin Level (μU/ml)", min_value=0, max_value=900, value=defaults['insulin'], step=1)
    bmi = st.number_input("⚖️ Body Mass Index (BMI)", min_value=0.0, max_value=70.0, value=defaults['bmi'], step=0.1, format="%.1f")
    dpf = st.number_input("🧬 Diabetes Pedigree Function", min_value=0.0, max_value=3.0, value=defaults['dpf'], step=0.01, format="%.3f")
    age = st.number_input("🎂 Age (years)", min_value=0, max_value=120, value=defaults['age'], step=1)

# Buttons
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
with col_btn1:
    predict_btn = st.button("🔮 Predict Risk", type="primary", use_container_width=True)
with col_btn2:
    reset_btn = st.button("🔄 Reset Form", use_container_width=True)

# Reset logic
if reset_btn:
    st.session_state.reset = True
    st.rerun()

if st.session_state.reset:
    for key in defaults:
        st.session_state[key] = defaults[key]
    st.session_state.reset = False

# Prediction
if predict_btn:
    # Create input dataframe
    input_data = pd.DataFrame([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]], 
                              columns=cols)
    
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
        st.subheader("📊 Prediction Result")
        
        # Display result with styling
        if prediction == 1:
            st.error("## ⚠️ HIGH DIABETES RISK DETECTED")
            st.markdown(f"### Risk Score: **{risk_score:.1f}%**")
            st.info("""
            **Immediate Actions Recommended:**
            - Consult with an endocrinologist
            - Schedule HbA1c and fasting glucose tests
            - Begin lifestyle modifications
            - Regular monitoring required
            """)
        else:
            st.success("## ✅ LOW DIABETES RISK")
            st.markdown(f"### Risk Score: **{risk_score:.1f}%**")
            st.info("""
            **Preventive Measures:**
            - Maintain healthy BMI (18.5-24.9)
            - Regular physical activity (150 mins/week)
            - Balanced diet with low sugar intake
            - Annual health checkups recommended
            """)
            
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        st.info("Please ensure all inputs are valid numbers.")

# Footer
st.markdown("---")
st.markdown("*This tool provides preliminary assessment only. Always consult with a healthcare professional for accurate diagnosis.*")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)
        print("Model setup completed!")
    except Exception as e:
        print(f"Setup error: {e}")

# =============== NUMPY COMPATIBILITY PATCH ==================
import numpy as np
import numpy.random as random

# Ensure all required numpy modules exist
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

# =============== REST OF IMPORTS ==================
import streamlit as st
import pandas as pd
import joblib
import base64
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
        st.warning(f"Background image '{image_file}' not found. Using default background.")
        pass

add_bg_from_local("bg2.jpg")

# ==================== CUSTOM CSS WITH POSITIONING FIX ======================
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
     
        /* Content container - positioned above the background */
        .form-content {
            position: relative;
            z-index: 2;
            padding: 40px;
        }
        
        /* Main container styling */
        .main-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Title styling */
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
        
        /* Input field styling */
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
        
        /* Hide the +/- increment buttons */
        .stNumberInput button {
            display: none !important;
        }
        
        /* Hide the entire container with increment buttons */
        div[data-testid="stNumberInputContainer"] > div:last-child {
            display: none !important;
        }
        
        /* Alternative: Hide only the buttons but keep the spacing */
        .stNumberInput [data-testid="stNumberInputStepUp"],
        .stNumberInput [data-testid="stNumberInputStepDown"] {
            display: none !important;
        }
        
        /* Button styling */
        .stButton > button {
               position: absolute;   /* needed for right/top to work */
                right: -190px;          /* distance from the right edge of parent */
                top: -80px;            /* optional: adjust vertical position */   
                border-radius: 12px;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                border: none;
                margin-top: 10px;
                box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        
        .predict-btn {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white !important;
        }
        
        .predict-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
            background: linear-gradient(135deg, #2980b9 0%, #1a5276 100%);
        }
        
        .reset-btn {
            background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
            color: white !important;
        }
        
        .reset-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
            background: linear-gradient(135deg, #7f8c8d 0%, #5d6d7e 100%);
        }
        
        /* Section headers */
        .section-header {
            color: #2c3e50;
            font-weight: 700;
            font-size: 1.3rem;
            margin: 0 0 25px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f4fc;
            text-align: center;
        }
        
        /* Make sure columns have proper spacing */
        .stHorizontalBlock {
            margin-bottom: 20px;
        }
        
        /* Remove Streamlit default spacing issues */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .form-content {
                padding: 25px;
            }
            .main-title {
                font-size: 2rem;
            }
        }
        
        /* Input cleaning highlight */
        .input-cleaning-active {
            border-color: #3498db !important;
            background-color: #f0f8ff !important;
        }
    </style>
    
    <script>
        // Function to clean input values (remove +, -, and leading zeros)
        function cleanNumberInput(inputElement) {
            // Get current value
            let value = inputElement.value;
            
            // Store cursor position
            let cursorPos = inputElement.selectionStart;
            let oldValue = inputElement.getAttribute('data-old-value') || '';
            
            // Remove + and - signs
            value = value.replace(/[+-]/g, '');
            
            // Remove leading zeros (but keep single zero if the whole number is zero)
            // For decimal numbers, handle differently
            if (value.includes('.')) {
                // For decimal numbers, remove leading zeros before decimal
                let parts = value.split('.');
                if (parts[0].length > 1) {
                    parts[0] = parts[0].replace(/^0+(?=\\d)/, '');
                }
                value = parts.join('.');
            } else {
                // For whole numbers
                if (value.length > 1) {
                    value = value.replace(/^0+(?=\\d)/, '');
                }
            }
            
            // If value becomes empty after cleaning, set to 0
            if (value === '' || value === '.' || value === '-') {
                value = '0';
            }
            
            // Update the input value if it changed
            if (value !== oldValue) {
                inputElement.value = value;
                
                // Store current value for next comparison
                inputElement.setAttribute('data-old-value', value);
                
                // Trigger input event to update Streamlit's state
                inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                inputElement.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Add visual feedback
                inputElement.classList.add('input-cleaning-active');
                setTimeout(() => {
                    inputElement.classList.remove('input-cleaning-active');
                }, 300);
            }
            
            return value;
        }
        
        // Initialize input cleaning for number inputs
        document.addEventListener('DOMContentLoaded', function() {
            setupInputCleaning();
            
            // Also listen for Streamlit's custom events
            document.addEventListener('streamlit:render', function() {
                setTimeout(setupInputCleaning, 100);
            });
        });
        
        function setupInputCleaning() {
            // Find all number input fields
            const numberInputs = document.querySelectorAll('input[type="number"]');
            
            numberInputs.forEach(input => {
                // Skip if already initialized
                if (input.hasAttribute('data-cleaning-initialized')) {
                    return;
                }
                
                // Initialize with current value
                cleanNumberInput(input);
                
                // Add input event listener for real-time cleaning
                input.addEventListener('input', function(e) {
                    // Use setTimeout to allow the value to update first
                    setTimeout(() => {
                        cleanNumberInput(this);
                    }, 0);
                });
                
                // Add keydown event to prevent + and - keys
                input.addEventListener('keydown', function(e) {
                    if (e.key === '+' || e.key === '-' || e.key === 'e' || e.key === 'E') {
                        e.preventDefault();
                    }
                });
                
                // Add paste event to clean pasted content
                input.addEventListener('paste', function(e) {
                    // Allow the paste to happen first, then clean
                    setTimeout(() => {
                        cleanNumberInput(this);
                    }, 10);
                });
                
                // Also handle blur event for final cleanup
                input.addEventListener('blur', function() {
                    cleanNumberInput(this);
                });
                
                // Mark as initialized
                input.setAttribute('data-cleaning-initialized', 'true');
            });
            
            // Remove the +/- buttons entirely
            removeIncrementButtons();
        }
        
        function removeIncrementButtons() {
            // Remove increment/decrement buttons
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
            
            // Also remove the parent container if it exists
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

# ===================== LOAD MODEL ==========================
@st.cache_resource
def load_diabetes_model():
    """Load the diabetes prediction model"""
    
    # Try different model file paths in order
    model_paths = ["diabetes_gb_fixed.pkl", "diabetes_gb.pkl"]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            try:
                # Try loading with joblib
                model_data = joblib.load(model_path)
                
                # Handle different return formats
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
                
                if model is not None:
                    st.success(f"✅ Model loaded successfully from {model_path}!")
                    return model, scaler, saved_cols
                    
            except Exception as e:
                st.warning(f"Failed to load {model_path}: {str(e)[:100]}")
                continue
    
    # If all models fail, use a simple model for demonstration
    st.warning("Using demonstration model. Please run setup.py to fix the actual model.")
    from sklearn.ensemble import GradientBoostingClassifier
    import numpy as np
    
    dummy_model = GradientBoostingClassifier(n_estimators=50, random_state=42)
    X_dummy = np.random.randn(200, 8)
    y_dummy = (X_dummy[:, 0] + X_dummy[:, 1] > 0).astype(int)
    dummy_model.fit(X_dummy, y_dummy)
    
    return dummy_model, None, ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

# Load the model
model, scaler, saved_cols = load_diabetes_model()

# If saved_cols is None, set default column names
if saved_cols is None:
    saved_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

# ======================= MAIN UI ==========================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header with gradient title
st.markdown('<h1 class="main-title">Diabetes Prediction System</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle" style="color: black;">Enter patient health metrics below for diabetes risk assessment</p>',
    unsafe_allow_html=True
)

# =================== FORM SECTION WITH BACKGROUND CARD ==============
st.markdown('<div class="form-section-wrapper">', unsafe_allow_html=True)

# =================== INITIALIZE SESSION STATE ==============
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

default_values = {
    'preg': 0,
    'bp': 0,
    'ins': 0,
    'dpf': 0.0,
    'glu': 0,
    'skin': 0,
    'bmi': 0.0,
    'age': 0
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ======================= INPUT FORM ========================
st.markdown('<div class="section-header">Patient Health Metrics</div>', unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns(2, gap="large")

with col1:
    pregnancies = st.number_input(
        "No. of Pregnancies", 
        0, 20, 
        value=st.session_state.preg,
        step=1,
        key=f"preg_{st.session_state.reset_counter}",
        help="Enter number of pregnancies"
    )
    
    glucose = st.number_input(
        "Glucose Level (mg/dL)", 
        0, 300, 
        value=st.session_state.glu,
        step=1,
        key=f"glu_{st.session_state.reset_counter}",
        help="Normal range: 70-100 mg/dL"
    )
    
    blood_pressure = st.number_input(
        "Blood Pressure (mm Hg)", 
        0, 200, 
        value=st.session_state.bp,
        step=1,
        key=f"bp_{st.session_state.reset_counter}",
        help="Normal range: 90-120/60-80 mm Hg"
    )
    
    skin_thickness = st.number_input(
        "Skin Thickness (mm)", 
        0, 100, 
        value=st.session_state.skin,
        step=1,
        key=f"skin_{st.session_state.reset_counter}",
        help="Triceps skin fold thickness"
    )

with col2:
    insulin = st.number_input(
        "Insulin Level (μU/ml)", 
        0, 900, 
        value=st.session_state.ins,
        step=1,
        key=f"ins_{st.session_state.reset_counter}",
        help="2-hour serum insulin"
    )
    
    bmi = st.number_input(
        "Body Mass Index", 
        0.0, 70.0, 
        value=st.session_state.bmi,
        step=0.1,
        format="%.1f",
        key=f"bmi_{st.session_state.reset_counter}",
        help="Weight(kg) / Height(m)²"
    )
    
    dpf = st.number_input(
        "Diabetes Pedigree Function", 
        0.0, 3.0, 
        value=st.session_state.dpf,
        step=0.01,
        format="%.3f",
        key=f"dpf_{st.session_state.reset_counter}",
        help="Genetic predisposition score"
    )
    
    age = st.number_input(
        "Age (years)", 
        0, 120, 
        value=st.session_state.age,
        step=1,
        key=f"age_{st.session_state.reset_counter}",
        help="Patient's current age"
    )

# Update session state
st.session_state.preg = pregnancies
st.session_state.bp = blood_pressure
st.session_state.ins = insulin
st.session_state.dpf = dpf
st.session_state.glu = glucose
st.session_state.skin = skin_thickness
st.session_state.bmi = bmi
st.session_state.age = age

# =================== ACTION BUTTONS ========================
st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

with btn_col1:
    predict = st.button("Predict Risk", type="primary", use_container_width=True, key="predict_btn")

with btn_col2:
    reset_btn = st.button("Reset Form", type="secondary", use_container_width=True, key="reset_btn")

# Close the form content and wrapper
st.markdown('</div>', unsafe_allow_html=True)  # Close form-section-wrapper

# ================= RESET BUTTON LOGIC ======================
if reset_btn:
    for key in default_values.keys():
        st.session_state[key] = default_values[key]
    st.session_state.reset_counter += 1
    st.rerun()

# =================== PREDICTION RESULTS ====================
if predict:
    # Input validation
    required_fields = [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]
    if all(value == 0 for value in required_fields):
        st.warning("⚠️ Please enter patient data before predicting.")
    else:
        # Perform prediction
        input_df = pd.DataFrame(
            [[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]],
            columns=saved_cols
        )
        
        # Scale input if scaler exists
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
            
            # Add CSS for result card
            st.markdown("""
                <style>
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
                    .metric-text {
                        color: #2c3e50 !important;
                    }
                    .expand-text {
                        color: #2c3e50 !important;
                    }
                    a[data-testid="stHeaderActionElements"],
                    span[data-testid="stHeaderActionElements"],
                    .st-emotion-cache-ubko3j,
                    .eqpbrs01,
                    .eqpbrs03 {
                        display: none !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Show result in a separate card
            st.markdown('<div class="result-section-wrapper">', unsafe_allow_html=True)
            st.markdown('<div class="result-content">', unsafe_allow_html=True)
            
            st.markdown('<div class="result-header">Prediction Result</div>', unsafe_allow_html=True)
            
            # Result columns
            result_col1, result_col2 = st.columns([3, 1])
            
            with result_col1:
                if prediction == 1:
                    st.markdown("""
                    <div class="result-text">
                    <h3 style="color: Red; margin-bottom: 20px;">High Diabetes Risk Detected</h3>
                    
                    <p style="color: #2c3e50; margin-bottom: 15px;"><strong>The patient shows significant indicators for diabetes.</strong></p>
                    
                    <p style="color: #2c3e50; margin-bottom: 10px;"><strong>Immediate Actions Recommended:</strong></p>
                    <ul style="color: #2c3e50; margin-left: 20px; margin-bottom: 20px;">
                    <li style="margin-bottom: 5px;">Consult with an endocrinologist</li>
                    <li style="margin-bottom: 5px;">Schedule HbA1c and fasting glucose tests</li>
                    <li style="margin-bottom: 5px;">Begin lifestyle modifications</li>
                    <li>Regular monitoring required</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-text">
                    <h3 style="color: Green; margin-bottom: 20px;">Low Diabetes Risk</h3>
                    
                    <p style="color: #2c3e50; margin-bottom: 15px;"><strong>The patient is unlikely to have diabetes based on current metrics.</strong></p>
                    
                    <p style="color: #2c3e50; margin-bottom: 10px;"><strong>Preventive Measures:</strong></p>
                    <ul style="color: #2c3e50; margin-left: 20px; margin-bottom: 20px;">
                    <li style="margin-bottom: 5px;">Maintain healthy BMI (18.5-24.9)</li>
                    <li style="margin-bottom: 5px;">Regular physical activity (150 mins/week)</li>
                    <li style="margin-bottom: 5px;">Balanced diet with low sugar intake</li>
                    <li>Annual health checkups recommended</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
            
            with result_col2:
                risk_score = prediction_proba[1] * 100
                if prediction == 1:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border-radius: 10px; border: 2px solid rgba(231, 76, 60, 0.5); background-color: rgba(253, 242, 242, 0.7);">
                        <h4 style="color: #2c3e50; margin-bottom: 10px; font-size: 1rem;">Risk Score</h4>
                        <h1 style="color: #2c3e50; font-size: 2.2rem; margin: 0; font-weight: 700;">{risk_score:.1f}%</h1>
                        <p style="color: Red; font-size: 0.9rem; margin-top: 5px; font-weight: 600;">HIGH</p>
                        <p style="color: #2c3e50; font-size: 0.8rem; margin-top: 10px; opacity: 0.8;">Medical attention advised</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border-radius: 10px; border: 2px solid rgba(46, 204, 113, 0.5); background-color: rgba(249, 254, 249, 0.7);">
                        <h4 style="color: #2c3e50; margin-bottom: 10px; font-size: 1rem;">Risk Score</h4>
                        <h1 style="color: #2c3e50; font-size: 2.2rem; margin: 0; font-weight: 700;">{risk_score:.1f}%</h1>
                        <p style="color: Green; font-size: 0.9rem; margin-top: 5px; font-weight: 600;">LOW</p>
                        <p style="color: #2c3e50; font-size: 0.8rem; margin-top: 10px; opacity: 0.8;">Within safe range</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Close the result card
            st.markdown('</div>', unsafe_allow_html=True)  # Close result-content
            st.markdown('</div>', unsafe_allow_html=True)  # Close result-section-wrapper
            
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
            st.info("Please ensure all inputs are valid numbers.")

# Footer
st.markdown("""
    <div style="text-align: center; color: black; font-size: 0.9rem; margin-top: 40px;">
        <p>This tool provides preliminary assessment only. Always consult with a healthcare professional for accurate diagnosis.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
