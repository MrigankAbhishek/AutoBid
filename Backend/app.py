from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
import os
import json
import urllib.request
from datetime import datetime
from werkzeug.utils import secure_filename
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image

# ======================================================
# AUTO-DOWNLOAD MODELS FROM HUGGING FACE
# ======================================================

HF_BASE = "https://huggingface.co/Tenyson95/autobid-models/resolve/main"

MODEL_FILES = [
    "car_classifier_weights.h5",
    "damage_classifier.weights.h5",
    "car_price_model.pkl",      # ✅ MULTI-CAR MODEL
    "car_model_meta.json",      # ✅ IMPORTANT
    "class_indices.json",
    "damage_class_indices.json",
]

def download_models():
    for filename in MODEL_FILES:
        if not os.path.exists(filename):
            print(f"⬇️ Downloading {filename}...")
            urllib.request.urlretrieve(f"{HF_BASE}/{filename}", filename)
            print(f"✅ {filename} downloaded")
        else:
            print(f"✅ {filename} already exists")

download_models()

# ======================================================
# FLASK APP
# ======================================================

app = Flask(__name__)
CORS(app, origins=[
    "https://auto-bid-nine.vercel.app",
    "http://localhost:5173"
])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

IMG_SIZE = 224

# ======================================================
# LOAD CAR CLASSIFIER
# ======================================================

with open("class_indices.json", "r") as f:
    class_map = json.load(f)

def build_car_model(num_classes):
    base_model = EfficientNetB0(weights=None, include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation='softmax', dtype='float32')(x)
    return Model(inputs=base_model.input, outputs=outputs)

car_model = build_car_model(len(class_map))
car_model.load_weights("car_classifier_weights.h5")
print("✅ Car classifier loaded")

# ======================================================
# LOAD DAMAGE MODEL
# ======================================================

with open("damage_class_indices.json", "r") as f:
    damage_class_map = json.load(f)

damage_classes = list(damage_class_map.keys())

def build_damage_model(num_classes):
    base_model = EfficientNetB0(weights="imagenet", include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.4)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    return Model(inputs=base_model.input, outputs=outputs)

damage_model = build_damage_model(len(damage_classes))
damage_model.load_weights("damage_classifier.weights.h5")
print("✅ Damage classifier loaded")

# ======================================================
# LOAD PRICE MODEL
# ======================================================

price_model = joblib.load("car_price_model.pkl")
print("✅ Multi-car price model loaded")

with open("car_model_meta.json", "r") as f:
    car_meta = json.load(f)

print("✅ Metadata loaded")

# ======================================================
# VIN DECODER
# ======================================================

def decode_indian_vin(vin):
    if not vin or len(vin) != 17:
        return {"valid": False, "error": "VIN must be 17 characters"}
    vin = vin.upper()
    wmi_map = {
        'MA3': 'Maruti Suzuki', 'MBJ': 'Maruti Suzuki',
        'MAL': 'Hyundai', 'MAT': 'Tata Motors', 'MA1': 'Mahindra'
    }
    year_map = {
        'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013,
        'E': 2014, 'F': 2015, 'G': 2016, 'H': 2017,
        'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
        'N': 2022, 'P': 2023, 'R': 2024
    }
    manufacturer = wmi_map.get(vin[:3], "Unknown Manufacturer")
    year = year_map.get(vin[9], "Unknown Year")
    return {"valid": True, "manufacturer": manufacturer, "year": year}

# ======================================================
# HELPERS
# ======================================================

def prepare_image(filepath):
    img = image.load_img(filepath, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

def calculate_penalty(dents, scratches):
    return (dents * 0.02) + (scratches * 0.01)

def parse_make_model(predicted_model_str):
    known_makes = sorted(car_meta["make_model_map"].keys(), key=len, reverse=True)
    for make in known_makes:
        if predicted_model_str.lower().startswith(make.lower()):
            model_part = predicted_model_str[len(make):].strip()
            return make, model_part
    parts = predicted_model_str.split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""

# ======================================================
# ROUTES
# ======================================================

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "AutoBid backend running ✅"})

@app.route("/predict-model", methods=["POST"])
def predict_model():
    files = request.files.getlist("images")
    if len(files) < 4:
        return jsonify({"error": "Upload 4 images"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(files[0].filename))
    files[0].save(filepath)

    img = prepare_image(filepath)
    pred = car_model.predict(img)
    index = np.argmax(pred)

    predicted_model = class_map[str(index)]

    os.remove(filepath)

    return jsonify({"predicted_model": predicted_model})

@app.route("/verify-vin", methods=["POST"])
def verify_vin():
    vin = request.json.get("vin")
    predicted_model = request.json.get("predicted_model")

    vin_data = decode_indian_vin(vin)
    if not vin_data["valid"]:
        return jsonify(vin_data), 400

    manufacturer = vin_data["manufacturer"]
    year = vin_data["year"]

    verified = manufacturer.lower() in predicted_model.lower()

    return jsonify({
        "manufacturer": manufacturer,
        "year": year,
        "verified": verified
    })

# ======================================================
# 🔥 MULTI-CAR PRICE ENDPOINT (FIXED)
# ======================================================

@app.route("/analyze-damage-price", methods=["POST"])
def analyze_damage_price():

    # 🔥 GET INPUT
    raw_model = request.form.get("model", "").strip()
    make = request.form.get("make", "").strip()
    model_name = ""

    # 🔥 AUTO PARSE (handles "Hyundai Creta")
    if raw_model:
        make, model_name = parse_make_model(raw_model)

    # 🔥 FINAL VALIDATION
    if not make or not model_name:
        return jsonify({
            "error": f"Invalid model format: '{raw_model}'"
        }), 400

    year = int(request.form.get("year"))
    km = int(request.form.get("km"))
    fuel = request.form.get("fuel")
    transmission = request.form.get("transmission")
    city = request.form.get("city")

    # DAMAGE
    dents = 0
    scratches = 0

    files = request.files.getlist("images")

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)

        img = prepare_image(path)
        pred = damage_model.predict(img)
        idx = np.argmax(pred)

        if damage_classes[idx] == "dent":
            dents += 1
        elif damage_classes[idx] == "scratch":
            scratches += 1

        os.remove(path)

    # =============================
    # 🔥 EXACT TRAINING FEATURES
    # =============================

    current_year = datetime.now().year
    car_age = current_year - year
    km_per_year = km / (car_age + 1)

    resale_map = {
        "Toyota": 1.25,
        "Hyundai": 1.20,
        "Maruti Suzuki": 1.18,
        "Honda": 1.15,
        "Mahindra": 1.12,
        "Tata": 1.10,
    }

    resale_score = resale_map.get(make, 1.0)

    model_counts = car_meta.get("model_counts", {})
    max_count = max(model_counts.values()) if model_counts else 1
    model_popularity = model_counts.get(model_name, 1) / max_count

    input_df = pd.DataFrame([{
        "make": make,
        "model": model_name,
        "fuel": fuel,
        "transmission": transmission,
        "city": city,
        "car_age": car_age,
        "km_driven": km,
        "km_per_year": km_per_year,
        "resale_score": resale_score,
        "model_popularity": model_popularity
    }])

    log_price = price_model.predict(input_df)[0]
    base_price = float(np.expm1(log_price))

    penalty = calculate_penalty(dents, scratches)
    final_price = base_price * (1 - penalty)

    return jsonify({
        "make": make,
        "model": model_name,
        "base_price": round(base_price),
        "final_price": round(final_price),
        "dents": dents,
        "scratches": scratches,
        "penalty_pct": round(penalty * 100, 2)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)