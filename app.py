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
                    value = value.replace(/^0+(?=\d)/, '');
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

# ===================== LOAD MODEL WITH ERROR HANDLING ==========================
@st.cache_resource
def load_diabetes_model():
    """Load the diabetes prediction model with fallback mechanisms"""
    model_path = "diabetes_gb.pkl"
    
    # Check if model exists
    if not os.path.exists(model_path):
        st.error(f"❌ Model file '{model_path}' not found!")
        st.info("Please ensure the model file is uploaded to the repository.")
        st.stop()
    
    # Try multiple loading strategies
    load_errors = []
    
    # Strategy 1: Normal joblib load
    try:
        model_data = joblib.load(model_path)
        
        # Handle different return formats
        if isinstance(model_data, tuple):
            if len(model_data) == 3:
                model, scaler, saved_cols = model_data
            elif len(model_data) == 2:
                model, scaler = model_data
                saved_cols = None
            else:
                model, scaler, saved_cols = model_data[0], None, None
        else:
            model, scaler, saved_cols = model_data, None, None
        
        # Configure scaler if it exists
        if scaler is not None and hasattr(scaler, 'set_output'):
            scaler = scaler.set_output(transform='pandas')
        
        return model, scaler, saved_cols
        
    except Exception as e:
        load_errors.append(f"Joblib load: {str(e)}")
    
    # Strategy 2: Try with pickle
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        if isinstance(model_data, tuple):
            if len(model_data) == 3:
                model, scaler, saved_cols = model_data
            elif len(model_data) == 2:
                model, scaler = model_data
                saved_cols = None
            else:
                model, scaler, saved_cols = model_data[0], None, None
        else:
            model, scaler, saved_cols = model_data, None, None
        
        if scaler is not None and hasattr(scaler, 'set_output'):
            scaler = scaler.set_output(transform='pandas')
        
        return model, scaler, saved_cols
        
    except Exception as e:
        load_errors.append(f"Pickle load: {str(e)}")
    
    # If all strategies fail, show error
    st.error("❌ Failed to load the diabetes prediction model")
    
    with st.expander("🔧 Troubleshooting Information"):
        st.write("**Load Errors:**")
        for error in load_errors:
            st.code(error)
        
        st.write("**Required Package Versions:**")
        st.code("""
        scikit-learn==1.6.1
        pandas>=2.0.0
        numpy>=1.24.0
        joblib>=1.3.0
        """)
        
        st.write("**Current Package Versions:**")
        try:
            import sklearn
            st.write(f"- scikit-learn: {sklearn.__version__}")
        except:
            st.write("- scikit-learn: Not installed")
        
        try:
            import pandas as pd
            st.write(f"- pandas: {pd.__version__}")
        except:
            st.write("- pandas: Not installed")
    
    st.stop()

# Load the model
model, scaler, saved_cols = load_diabetes_model()

# Verify model loaded successfully
if model is None:
    st.error("Model could not be loaded. Please check the error messages above.")
    st.stop()

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
            columns=saved_cols if saved_cols is not None else ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        )
        
        # Scale input if scaler exists
        if scaler is not None:
            input_scaled = scaler.transform(input_df)
        else:
            input_scaled = input_df.values
        
        prediction = model.predict(input_scaled)[0]
        prediction_proba = model.predict_proba(input_scaled)[0]
        
        # Add CSS for result card with same style as form
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
        
        # Show result in a separate card with same style as form
        st.markdown('<div class="result-section-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="result-content">', unsafe_allow_html=True)
        
        st.markdown('<div class="result-header">Prediction Result</div>', unsafe_allow_html=True)
        
        # Result columns
        result_col1, result_col2 = st.columns([3, 1])
        
        with result_col1:
            if prediction == 1:
                # Custom styled error message with #7f8c8d color
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
                # Custom styled success message with #7f8c8d color
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
                # Custom metric with #7f8c8d color
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

# Footer (outside all cards - this will remain at the bottom)
st.markdown("""
    <div style="text-align: center; color: black; font-size: 0.9rem; margin-top: 40px;">
        <p>This tool provides preliminary assessment only. Always consult with a healthcare professional for accurate diagnosis.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
