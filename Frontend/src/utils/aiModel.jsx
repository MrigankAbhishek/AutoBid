import * as tf from '@tensorflow/tfjs';
import CAR_CLASSES from './class_indices.json'; // Ensure this file exists!

let model = null;

export const loadCarModel = async () => {
  try {
    // Looks for 'model.json' inside 'public/public_model/'
    model = await tf.loadLayersModel('/public_model/model.json');
    console.log("✅ AI Car Model Loaded");
  } catch (error) {
    console.error("❌ Failed to load AI Model:", error);
  }
};

export const predictCar = async (imageElement) => {
  if (!model) await loadCarModel();

  if (!model) return { car: "AI Loading Error", confidence: 0 };

  // 1. Preprocess the image (Must match Python training: 224x224, Normalized)
  const tensor = tf.browser.fromPixels(imageElement)
    .resizeNearestNeighbor([224, 224])
    .toFloat()
    .div(255.0)
    .expandDims();

  // 2. Predict
  const predictions = await model.predict(tensor).data();
  
  // 3. Find top result
  const maxPrediction = Math.max(...predictions);
  const classIndex = predictions.indexOf(maxPrediction);
  
  tensor.dispose(); // Clean up memory

  return {
    car: CAR_CLASSES[classIndex] || "Unknown Car",
    confidence: (maxPrediction * 100).toFixed(1)
  };
};