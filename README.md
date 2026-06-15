# AutoBid 🚗

An AI-powered used car auction platform that integrates vehicle model detection, damage analysis, and price prediction to deliver accurate, automated resale valuations for buyers and sellers.

🔗 **Live Demo**: [auto-bid-nine.vercel.app](https://auto-bid-nine.vercel.app)  
📁 **GitHub**: [github.com/MrigankAbhishek/AutoBid](https://github.com/MrigankAbhishek/AutoBid)

---

## Overview

AutoBid automates the used car valuation process using three custom-trained ML models. A seller uploads a car image — AutoBid identifies the model, detects any damage, adjusts the price accordingly, and lists it for auction. Buyers get transparent, AI-verified listings with real-time bidding.

---

## Screenshots

![Home](https://raw.githubusercontent.com/MrigankAbhishek/AutoBid/main/screenshots/Screenshot%202026-06-15%20120752.png)

![Page2](https://raw.githubusercontent.com/MrigankAbhishek/AutoBid/main/screenshots/Screenshot%202026-06-15%20120800.png)

![Page3](https://raw.githubusercontent.com/MrigankAbhishek/AutoBid/main/screenshots/Screenshot%202026-06-15%20121144.png)

![Page4](https://raw.githubusercontent.com/MrigankAbhishek/AutoBid/main/screenshots/Screenshot%202026-06-15%20121446.png)

---

## Features

- 🔍 **Car Model Detection** — CNN-based classifier identifies the car brand and model from uploaded images
- 🛠️ **Damage Detection** — Classifies vehicle condition as dented, scratched, or undamaged
- 💰 **Price Prediction** — Random Forest model predicts resale value based on age, mileage, fuel type, transmission, and city
- 📉 **Damage-based Price Adjustment** — Automatically reduces predicted price based on detected damage severity
- 🔎 **VIN Decoder** — Validates manufacturer details and extracts model year from VIN
- 🏷️ **Live Auction** — Real-time bidding on listed vehicles
- 📊 **Custom Dataset** — ~65K rows scraped from Spinny across 236 Indian car models

---

## ML Models

### 1. Car Model Classifier
- **Architecture**: EfficientNetB0 (CNN)
- **Task**: Multi-class image classification — identifies car brand and model from seller-uploaded images
- **Performance**: 77% accuracy | Precision: 0.78 | Recall: 0.77 | F1-score: 0.77
- **Dataset**: Custom scraped dataset covering 236 Indian car models

### 2. Vehicle Damage Detection
- **Architecture**: CNN-based image classifier
- **Task**: Classifies vehicle images into dents, scratches, or no-damage
- **Performance**: 75.7% accuracy | Macro F1: 0.74 | Top-2 accuracy: 97.2%
- **Dataset**: 1,775 images (mix of Kaggle + custom collected images)

### 3. Resale Price Prediction
- **Architecture**: Random Forest Regressor
- **Task**: Predicts used car resale price from structured features
- **Features**: Car age, mileage, fuel type, transmission, city
- **Performance**: R² = 0.80 on test data
- **Dataset**: ~65,000 rows scraped from Spinny across 236 Indian car models

---

## Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

### Backend & Database
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

### ML & Data
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![HuggingFace](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

---

## Project Structure

```
AutoBid/
├── Frontend/              ← React + TypeScript frontend
├── Backend/               ← Flask API serving all 3 ML models
│   └── app.py             ← Main API entry point
├── Model_training_code/   ← Training notebooks for all models
│   ├── car_classifier/    ← EfficientNetB0 training
│   ├── damage_detection/  ← Damage classifier training
│   └── price_prediction/  ← Random Forest training
└── Dockerfile             ← Docker config for backend deployment
```

---

## How It Works

```
Seller uploads car image
        ↓
Car Model Classifier (EfficientNetB0)
→ Identifies brand and model (e.g. Maruti Swift 2019)
        ↓
Damage Detection Model (CNN)
→ Classifies as: No Damage / Scratched / Dented
        ↓
Price Prediction Model (Random Forest)
→ Predicts base resale price from structured features
        ↓
Damage Adjustment Logic
→ Reduces price based on damage severity
        ↓
VIN Decoder
→ Validates manufacturer details and model year
        ↓
Listing goes live for auction
```

---

## Dataset

- **Source**: Custom web scraper built to collect data from [Spinny](https://www.spinny.com)
- **Size**: ~65,000 rows
- **Coverage**: 236 Indian car models
- **Features**: Brand, model, year, fuel type, transmission, mileage, city, price
- **Purpose**: Training the vehicle resale price prediction model

---

## Author

**Mrigank Abhishek**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/mrigankabhishek)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MrigankAbhishek)

---

## License

This project is open source and available under the [MIT License](LICENSE).
