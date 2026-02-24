import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ==========================================
# 1. ROBUST LOAD (Fixes "Expected X fields" Error)
# ==========================================
csv_file = 'raw_prices.csv'

try:
    # Try 1: Standard load with Latin1
    df = pd.read_csv(csv_file, encoding='latin1')
except:
    try:
        print("⚠️ Standard load failed. Trying Python engine with auto-separator...")
        # Try 2: Python engine is smarter at detecting separators
        df = pd.read_csv(csv_file, sep=None, engine='python', encoding='latin1')
    except:
        print("⚠️ Auto-sep failed. Skipping bad lines...")
        # Try 3: Brute force - skip lines that don't match
        # Note: on_bad_lines='skip' requires pandas >= 1.3. 
        # For older versions use error_bad_lines=False
        try:
             df = pd.read_csv(csv_file, encoding='latin1', on_bad_lines='skip')
        except:
             df = pd.read_csv(csv_file, encoding='latin1', error_bad_lines=False)

print(f"✅ Loaded Data: {len(df)} rows found.")
print(f"Columns found: {list(df.columns)}")

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# ==========================================
# 2. FILTER & PREPROCESS
# ==========================================
df = df.drop_duplicates().dropna()

# Filter for Alto 800 if mixed data exists
if 'model' in df.columns:
    # Remove 'Alto 800' string to allow fuzzy matching if needed, or keep strictly
    df = df[df['model'].astype(str).str.contains('Alto 800', case=False, na=False)]

# Remove outliers / weird values
# Ensure columns are numeric
df['km_driven'] = pd.to_numeric(df['km_driven'], errors='coerce')
df = df.dropna(subset=['km_driven'])
df = df[df["km_driven"] < 300000]

# flexible price column check
price_col = 'base_price' if 'base_price' in df.columns else 'price'

if price_col not in df.columns:
    print(f"❌ CRITICAL ERROR: Could not find 'price' or 'base_price' column.")
    print(f"Available columns: {df.columns.tolist()}")
    exit()

# Ensure price is numeric
df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
df = df.dropna(subset=[price_col])
df = df[df[price_col].between(50000, 500000)]

# Feature Engineering
current_year = datetime.now().year
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df["car_age"] = current_year - df["year"]

# ==========================================
# 3. DEFINE FEATURES
# ==========================================
features = ["car_age", "km_driven", "fuel", "transmission", "city"]

# Validate columns exist
missing = [f for f in features if f not in df.columns]
if missing:
    # Try to fix common name mismatches
    if 'fuel ' in df.columns: df.rename(columns={'fuel ': 'fuel'}, inplace=True)
    if 'source' in df.columns: df.rename(columns={'source': 'city'}, inplace=True) 
    
    # Check again
    missing = [f for f in features if f not in df.columns]
    if missing:
        print(f"❌ Still missing columns: {missing}")
        exit()

X = df[features]
y = df[price_col]

print(f"✅ Training on {len(df)} cleaned records...")

# ==========================================
# 4. BUILD & TRAIN PIPELINE
# ==========================================
categorical_features = ["fuel", "transmission", "city"]
preprocessor = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)],
    remainder="passthrough"
)

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=500, max_depth=15, random_state=42))
])

model.fit(X, y)

# ==========================================
# 5. SAVE
# ==========================================
joblib.dump(model, "alto800_base_model.pkl")

print("\n🚀 Success! 'alto800_base_model.pkl' created.")
print(f"Stats - MAE: ₹{round(mean_absolute_error(y, model.predict(X)), 2)}")