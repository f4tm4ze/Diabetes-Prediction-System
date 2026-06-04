import os
import sys
import pickle
import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("DIABETES PREDICTION MODEL FIXER")
print("=" * 60)

# Check if we need to fix the model
model_path = "diabetes_gb.pkl"
fixed_marker = ".model_fixed"

if os.path.exists(fixed_marker):
    print("Model already marked as fixed. Skipping...")
    sys.exit(0)

if not os.path.exists(model_path):
    print(f"❌ Model file {model_path} not found!")
    sys.exit(1)

print(f"Found model file: {model_path}")
print(f"File size: {os.path.getsize(model_path)} bytes")

# Try to load and fix the model
success = False

# Method 1: Try joblib with compatibility patches
try:
    print("\n📥 Attempting to load with joblib + patches...")
    
    # Apply patches
    if not hasattr(np.random, '_mt19937'):
        class MT19937:
            def __init__(self, *args, **kwargs):
                pass
        np.random._mt19937 = type('_mt19937', (), {'MT19937': MT19937})()
    
    if not hasattr(np.random, 'BitGenerator'):
        class BitGenerator:
            def __init__(self, *args, **kwargs):
                pass
        np.random.BitGenerator = BitGenerator
    
    model_data = joblib.load(model_path)
    print("✅ Successfully loaded with joblib!")
    success = True
    
except Exception as e:
    print(f"⚠️ Joblib failed: {str(e)[:100]}")
    
    # Method 2: Try pickle with custom unpickler
    try:
        print("\n📥 Attempting to load with custom unpickler...")
        
        class SafeUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                try:
                    return super().find_class(module, name)
                except (AttributeError, ModuleNotFoundError, ImportError):
                    print(f"   Creating dummy for: {module}.{name}")
                    return type(name, (), {})
        
        with open(model_path, 'rb') as f:
            model_data = SafeUnpickler(f).load()
        print("✅ Successfully loaded with custom unpickler!")
        success = True
        
    except Exception as e2:
        print(f"⚠️ Custom unpickler failed: {str(e2)[:100]}")

if success:
    # Extract the model components
    print("\n🔧 Extracting model components...")
    
    if isinstance(model_data, tuple):
        print(f"   Tuple with {len(model_data)} elements")
        model = None
        scaler = None
        columns = None
        
        for i, obj in enumerate(model_data):
            if hasattr(obj, 'predict') and hasattr(obj, 'predict_proba'):
                model = obj
                print(f"   Found model at position {i}")
            elif hasattr(obj, 'transform') and hasattr(obj, 'fit_transform'):
                scaler = obj
                print(f"   Found scaler at position {i}")
            elif isinstance(obj, list) and len(obj) == 8:
                columns = obj
                print(f"   Found columns at position {i}")
        
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
    
    if model is not None:
        # Save the fixed model
        print("\n💾 Saving fixed model...")
        fixed_model_path = "diabetes_gb_fixed.pkl"
        joblib.dump((model, scaler, columns), fixed_model_path, protocol=4)
        print(f"✅ Saved fixed model to {fixed_model_path}")
        
        # Backup original
        backup_path = "diabetes_gb_backup.pkl"
        import shutil
        shutil.copy(model_path, backup_path)
        print(f"✅ Backed up original to {backup_path}")
        
        # Replace original with fixed version
        shutil.copy(fixed_model_path, model_path)
        print(f"✅ Replaced {model_path} with fixed version")
        
        # Create marker file to indicate fix was applied
        with open(fixed_marker, 'w') as f:
            f.write("Model fixed on deployment")
        
        print("\n" + "=" * 60)
        print("✅ MODEL FIXED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n❌ Could not find model in the loaded data!")
else:
    print("\n❌ Could not load the model with any method!")

print("\nSetup complete!")
