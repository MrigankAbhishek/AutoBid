from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import BatchNormalization

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

IMG_SIZE = 224

# ======================================================
# LOAD CAR CLASSIFIER
# ======================================================

with open("class_indices.json", "r") as f:
    class_map = json.load(f)

def build_car_model(num_classes):
    base_model = EfficientNetB0(
        weights=None,              # MUST MATCH TRAINING
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.3)(x)

    outputs = Dense(
        num_classes,
        activation='softmax',
        dtype='float32'           # MUST MATCH TRAINING
    )(x)

    model = Model(inputs=base_model.input, outputs=outputs)
    return model


# Load class mapping
with open("class_indices.json", "r") as f:
    class_map = json.load(f)

num_classes = len(class_map)

# Build model
car_model = build_car_model(num_classes)

# Load trained weights
car_model.load_weights("car_classifier_weights.h5")

print("✅ Car classifier loaded successfully (architecture matched)")

# ======================================================
# LOAD DAMAGE MODEL
# ======================================================

with open("damage_class_indices.json", "r") as f:
    damage_class_map = json.load(f)

def build_damage_model(num_classes):
    base_model = EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.4)(x)
    outputs = Dense(num_classes, activation='softmax')(x)

    return Model(inputs=base_model.input, outputs=outputs)

damage_model = build_damage_model(len(damage_class_map))
damage_model.load_weights("damage_classifier.weights.h5")

damage_classes = list(damage_class_map.keys())

print("✅ Damage classifier loaded")

# ======================================================
# LOAD PRICE MODEL (ALTO 800 ONLY)
# ======================================================

price_model = joblib.load("alto800_base_model.pkl")
print("✅ Alto 800 price model loaded")

# ======================================================
# VIN DECODER
# ======================================================

def decode_indian_vin(vin):

    if not vin or len(vin) != 17:
        return {"valid": False, "error": "VIN must be 17 characters"}

    vin = vin.upper()

    wmi_map = {
        'MA3': 'Maruti Suzuki',
        'MBJ': 'Maruti Suzuki',
        'MAL': 'Hyundai',
        'MAT': 'Tata Motors',
        'MA1': 'Mahindra'
    }

    year_map = {
        'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013,
        'E': 2014, 'F': 2015, 'G': 2016, 'H': 2017,
        'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
        'N': 2022, 'P': 2023, 'R': 2024
    }

    manufacturer = wmi_map.get(vin[:3], "Unknown Manufacturer")
    year = year_map.get(vin[9], "Unknown Year")

    return {
        "valid": True,
        "manufacturer": manufacturer,
        "year": year
    }

# ======================================================
# HELPERS
# ======================================================

def prepare_image(filepath):
    img = image.load_img(filepath, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def calculate_penalty(dents, scratches):
    return (dents * 0.02) + (scratches * 0.01)

# ======================================================
# 1️⃣ MODEL PREDICTION
# ======================================================

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

# ======================================================
# 2️⃣ VIN VERIFY
# ======================================================

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
# 3️⃣ DAMAGE + PRICE
# ======================================================

@app.route("/analyze-damage-price", methods=["POST"])
def analyze_damage_price():

    print("---- ANALYZE DAMAGE DEBUG ----")
    print("MODEL:", request.form.get("model"))
    print("YEAR:", request.form.get("year"))
    print("FUEL:", request.form.get("fuel"))
    print("KM:", request.form.get("km"))
    print("TRANSMISSION:", request.form.get("transmission"))
    print("CITY:", request.form.get("city"))
    print("-------------------------------")

    model_name = request.form.get("model")

    # Safer Alto check
    if not model_name or "alto" not in model_name.lower():
        return jsonify({"error": "Price model available only for Alto 800"}), 400

    # Validate required fields BEFORE converting
    if not request.form.get("year") or not request.form.get("km"):
        return jsonify({"error": "Year and KM are required"}), 400

    try:
        year = int(request.form.get("year"))
        km = int(request.form.get("km"))
    except:
        return jsonify({"error": "Invalid year or KM value"}), 400

    fuel = request.form.get("fuel")
    transmission = request.form.get("transmission")
    city = request.form.get("city")

    if not fuel or not transmission or not city:
        return jsonify({"error": "Fuel, transmission and city are required"}), 400

    files = request.files.getlist("images")

    dents = 0
    scratches = 0

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)

        img = prepare_image(filepath)
        pred = damage_model.predict(img)
        index = np.argmax(pred)
        damage_type = damage_classes[index]

        if damage_type == "dent":
            dents += 1
        elif damage_type == "scratch":
            scratches += 1

        os.remove(filepath)

    # Price calculation
    current_year = datetime.now().year
    car_age = current_year - year

    input_data = pd.DataFrame([{
        "car_age": car_age,
        "km_driven": km,
        "fuel": fuel,
        "transmission": transmission,
        "city": city
    }])

    base_price = float(price_model.predict(input_data)[0])
    penalty = calculate_penalty(dents, scratches)
    final_price = base_price * (1 - penalty)

    print("SUCCESS: Returning price", final_price)

    return jsonify({
        "dents": dents,
        "scratches": scratches,
        "base_price": base_price,
        "final_price": final_price
    })


if __name__ == "__main__":
    app.run(debug=True)
