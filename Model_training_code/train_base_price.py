import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

from xgboost import XGBRegressor

# ==========================================
# LOAD DATA
# ==========================================
df = pd.read_csv("indian_cars_dataset_final.csv")
df.columns = df.columns.str.strip().str.lower()

print(f"✅ Loaded: {len(df)} rows")

# ==========================================
# CLEAN
# ==========================================
df = df.drop_duplicates().dropna()

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["km_driven"] = pd.to_numeric(df["km_driven"], errors="coerce")
df["base_price"] = pd.to_numeric(df["base_price"], errors="coerce")

df = df.dropna(subset=["year", "km_driven", "base_price"])

df = df[df["km_driven"] < 350000]
df = df[df["base_price"].between(50000, 25000000)]

print(f"✅ Clean dataset: {len(df)} rows")

# ==========================================
# FEATURE ENGINEERING
# ==========================================
current_year = datetime.now().year

df["car_age"] = current_year - df["year"]
df["km_per_year"] = df["km_driven"] / (df["car_age"] + 1)

# ------------------------------------------
# 🔥 RESALE SCORE (VERY IMPORTANT)
# ------------------------------------------
resale_map = {
    "Toyota": 1.25,
    "Hyundai": 1.20,
    "Maruti Suzuki": 1.18,
    "Honda": 1.15,
    "Mahindra": 1.12,
    "Tata": 1.10,
}

df["resale_score"] = df["make"].map(resale_map).fillna(1.0)

# ------------------------------------------
# 🔥 MODEL POPULARITY (DATA-DRIVEN)
# ------------------------------------------
model_counts = df["model"].value_counts()
df["model_popularity"] = df["model"].map(model_counts)

# normalize
df["model_popularity"] = df["model_popularity"] / df["model_popularity"].max()

# ------------------------------------------
# LOG TARGET
# ------------------------------------------
df["log_price"] = np.log1p(df["base_price"])

# ==========================================
# FEATURES
# ==========================================
features = [
    "make",
    "model",
    "fuel",
    "transmission",
    "city",
    "car_age",
    "km_driven",
    "km_per_year",
    "resale_score",        # NEW
    "model_popularity"     # NEW
]

X = df[features]
y = df["log_price"]

# ==========================================
# PREPROCESSOR
# ==========================================
categorical = ["make", "model", "fuel", "transmission", "city"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
    ],
    remainder="passthrough"
)

# ==========================================
# MODEL (IMPROVED XGBOOST)
# ==========================================
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", XGBRegressor(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.5,
        reg_lambda=1.0,
        tree_method="hist",
        random_state=42
    ))
])

# ==========================================
# TRAIN
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42
)

print(f"\n⏳ Training on {len(X_train)} samples...")
model.fit(X_train, y_train)

# ==========================================
# PREDICT
# ==========================================
log_preds = model.predict(X_test)

preds = np.expm1(log_preds)
y_true = np.expm1(y_test)

# ==========================================
# METRICS
# ==========================================
mae = mean_absolute_error(y_true, preds)
r2  = r2_score(y_true, preds)
mape = np.mean(np.abs((y_true - preds) / y_true)) * 100

print(f"\n📊 Final Results:")
print(f"   MAE  : ₹{mae:,.0f}")
print(f"   R²   : {r2:.4f}")
print(f"   MAPE : {mape:.2f}%")

# ==========================================
# SAVE
# ==========================================
joblib.dump(model, "car_price_model.pkl")
print("\n🚀 Model saved → car_price_model.pkl")

model_counts = df["model"].value_counts().to_dict()

meta = {
    "makes": sorted(df["make"].unique().tolist()),
    "models": sorted(df["model"].unique().tolist()),
    "fuels": sorted(df["fuel"].unique().tolist()),
    "transmissions": sorted(df["transmission"].unique().tolist()),
    "cities": sorted(df["city"].unique().tolist()),
    "make_model_map": (
        df.groupby("make")["model"]
        .apply(lambda x: sorted(x.unique().tolist()))
        .to_dict()
    ),
    "model_counts": model_counts   # 🔥 ADD THIS
}

with open("car_model_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("📋 Metadata saved → car_model_meta.json")