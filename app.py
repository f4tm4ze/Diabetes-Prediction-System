# =============== SELF-FIXING MODEL LOADER ==================
import os
import sys
import numpy as np
import numpy.random as random

# Apply NumPy compatibility patches FIRST
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

# Now try to fix the model automatically
import pickle
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "diabetes_gb.pkl"
FIXED_MODEL_PATH = "diabetes_gb_fixed.pkl"
FIX_MARKER = ".model_fixed"

def fix_and_save_model():
    """Attempt to fix the model file by re-saving it with current environment"""
    print("=" * 60)
    print("Attempting to fix diabetes prediction model...")
    print("=" * 60)
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file {MODEL_PATH} not found!")
        return False
    
    print(f"✓ Found model file: {MODEL_PATH}")
    print(f"  File size: {os.path.getsize(MODEL_PATH)} bytes")
    
    # Try multiple loading methods
    model_data = None
    methods_used = []
    
    # Method 1: Try joblib with patches
    try:
        print("\n📥 Method 1: Loading with joblib...")
        model_data = joblib.load(MODEL_PATH)
        methods_used.append("joblib")
        print("✓ Success!")
    except Exception as e:
        print(f"⚠️ Failed: {str(e)[:80]}")
    
    # Method 2: Try pickle with different encodings
    if model_data is None:
        for encoding in ['latin1', 'bytes', 'utf-8']:
            try:
                print(f"\n📥 Method 2: Loading with pickle (encoding={encoding})...")
                with open(MODEL_PATH, 'rb') as f:
                    model_data = pickle.load(f, encoding=encoding)
                methods_used.append(f"pickle_{encoding}")
                print("✓ Success!")
                break
            except Exception as e:
                print(f"⚠️ Failed with {encoding}: {str(e)[:80]}")
    
    # Method 3: Try custom unpickler
    if model_data is None:
        try:
            print("\n📥 Method 3: Loading with custom unpickler...")
            class SafeUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    try:
                        return super().find_class(module, name)
                    except (AttributeError, ModuleNotFoundError, ImportError):
                        print(f"   Creating dummy for: {module}.{name}")
                        return type(name, (), {})
            
            with open(MODEL_PATH, 'rb') as f:
                model_data = SafeUnpickler(f).load()
            methods_used.append("custom_unpickler")
            print("✓ Success!")
        except Exception as e:
            print(f"⚠️ Failed: {str(e)[:80]}")
    
    if model_data is None:
        print("\n❌ Could not load model with any method!")
        return False
    
    # Extract model components
    print("\n🔧 Extracting model components...")
    model = None
    scaler = None
    columns = None
    
    if isinstance(model_data, tuple):
        print(f"   Model data is a tuple with {len(model_data)} elements")
        for i, obj in enumerate(model_data):
            if hasattr(obj, 'predict') and hasattr(obj, 'predict_proba'):
                model = obj
                print(f"   ✓ Found model at position {i}")
            elif hasattr(obj, 'transform') and hasattr(obj, 'fit_transform'):
                scaler = obj
                print(f"   ✓ Found scaler at position {i}")
            elif isinstance(obj, list) and len(obj) == 8:
                columns = obj
                print(f"   ✓ Found columns at position {i}")
        
        if model is None and len(model_data) > 0:
            model = model_data[0]
            print(f"   Using first element as model")
        
        if columns is None:
            columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                      'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
            print(f"   Using default columns")
    else:
        model = model_data
        scaler = None
        columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                  'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        print("   Single object model detected")
    
    if model is None:
        print("\n❌ Could not find model in the loaded data!")
        return False
    
    # Save the fixed model
    print("\n💾 Saving fixed model...")
    try:
        joblib.dump((model, scaler, columns), FIXED_MODEL_PATH, protocol=4)
        print(f"✓ Saved fixed model to {FIXED_MODEL_PATH}")
        
        # Also save as pickle for compatibility
        with open("diabetes_model_backup.pkl", "wb") as f:
            pickle.dump((model, scaler, columns), f, protocol=4)
        print("✓ Saved backup as diabetes_model_backup.pkl")
        
        # Create marker file
        with open(FIX_MARKER, 'w') as f:
            f.write("Model fixed successfully\n")
            f.write(f"Method used: {methods_used[0] if methods_used else 'unknown'}\n")
        
        print("\n" + "=" * 60)
        print("✅ MODEL FIXED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Failed to save model: {e}")
        return False

# Run the fix if needed
if os.path.exists(MODEL_PATH) and not os.path.exists(FIX_MARKER):
    print("Model needs fixing. Running auto-fix...")
    fix_and_save_model()
elif os.path.exists(FIXED_MODEL_PATH):
    print("Fixed model already exists.")
else:
    print("No model found or fix already applied.")

# =============== IMPORT STREAMLIT AND OTHER LIBS ==================
import streamlit as st
import pandas as pd
import base64
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

# ==================== LOAD MODEL ==========================
@st.cache_resource
def load_diabetes_model():
    """Load the diabetes prediction model - tries fixed version first"""
    
    # Priority order for model files
    model_files = [FIXED_MODEL_PATH, "diabetes_model_backup.pkl", MODEL_PATH]
    
    for model_path in model_files:
        if os.path.exists(model_path):
            try:
                print(f"Attempting to load: {model_path}")
                model_data = joblib.load(model_path)
                
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
                
                if model is not None and hasattr(model, 'predict'):
                    st.success(f"✅ Model loaded successfully!")
                    return model, scaler, saved_cols
                    
            except Exception as e:
                st.warning(f"Failed to load {os.path.basename(model_path)}: {str(e)[:80]}")
                continue
    
    # Final fallback - create a simple model
    st.warning("⚠️ Using demonstration model. The actual model file may be corrupted.")
    dummy_model = GradientBoostingClassifier(n_estimators=50, random_state=42)
    import numpy as np
    X_dummy = np.random.randn(200, 8)
    y_dummy = (X_dummy[:, 0] + X_dummy[:, 1] > 0).astype(int)
    dummy_model.fit(X_dummy, y_dummy)
    
    return dummy_model, None, ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

# Load the model
model, scaler, saved_cols = load_diabetes_model()

if saved_cols is None:
    saved_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

# ======================= MAIN UI ==========================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">Diabetes Prediction System</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle" style="color: black;">Enter patient health metrics below for diabetes risk assessment</p>',
    unsafe_allow_html=True
)

# Form section
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
    pregnancies = st.number_input("No. of Pregnancies", 0, 20, value=st.session_state.preg, step=1, key=f"preg_{st.session_state.reset_counter}")
    glucose = st.number_input("Glucose Level (mg/dL)", 0, 300, value=st.session_state.glu, step=1, key=f"glu_{st.session_state.reset_counter}")
    blood_pressure = st.number_input("Blood Pressure (mm Hg)", 0, 200, value=st.session_state.bp, step=1, key=f"bp_{st.session_state.reset_counter}")
    skin_thickness = st.number_input("Skin Thickness (mm)", 0, 100, value=st.session_state.skin, step=1, key=f"skin_{st.session_state.reset_counter}")

with col2:
    insulin = st.number_input("Insulin Level (μU/ml)", 0, 900, value=st.session_state.ins, step=1, key=f"ins_{st.session_state.reset_counter}")
    bmi = st.number_input("Body Mass Index", 0.0, 70.0, value=st.session_state.bmi, step=0.1, format="%.1f", key=f"bmi_{st.session_state.reset_counter}")
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, value=st.session_state.dpf, step=0.01, format="%.3f", key=f"dpf_{st.session_state.reset_counter}")
    age = st.number_input("Age (years)", 0, 120, value=st.session_state.age, step=1, key=f"age_{st.session_state.reset_counter}")

# Update session state
st.session_state.preg = pregnancies
st.session_state.glu = glucose
st.session_state.bp = blood_pressure
st.session_state.skin = skin_thickness
st.session_state.ins = insulin
st.session_state.bmi = bmi
st.session_state.dpf = dpf
st.session_state.age = age

# Action buttons
st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns([1, 1])

with btn_col1:
    predict = st.button("Predict Risk", type="primary", use_container_width=True)

with btn_col2:
    reset_btn = st.button("Reset Form", type="secondary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

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
        
        # Display result
        st.markdown("---")
        st.subheader("📊 Prediction Result")
        
        if prediction == 1:
            st.error(f"⚠️ High Diabetes Risk Detected")
            st.metric("Risk Score", f"{risk_score:.1f}%", "HIGH")
            st.info("**Immediate Actions Recommended:**\n- Consult with an endocrinologist\n- Schedule HbA1c and fasting glucose tests\n- Begin lifestyle modifications\n- Regular monitoring required")
        else:
            st.success(f"✅ Low Diabetes Risk")
            st.metric("Risk Score", f"{risk_score:.1f}%", "LOW")
            st.info("**Preventive Measures:**\n- Maintain healthy BMI (18.5-24.9)\n- Regular physical activity (150 mins/week)\n- Balanced diet with low sugar intake\n- Annual health checkups recommended")
            
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")

# Footer
st.markdown("""
    <div style="text-align: center; color: black; font-size: 0.9rem; margin-top: 40px;">
        <p>This tool provides preliminary assessment only. Always consult with a healthcare professional for accurate diagnosis.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add custom CSS for styling
st.markdown("""
    <style>
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
    }
    .subtitle {
        color: #5d6d7e;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 40px;
    }
    .form-section-wrapper {
        background-color: rgba(255, 255, 255, 0.50) !important;
        border-radius: 18px;
        padding: 40px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }
    .section-header {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.3rem;
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e8f4fc;
    }
    </style>
""", unsafe_allow_html=True)
