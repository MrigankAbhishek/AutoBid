import tensorflow as tf
from tensorflow.keras import mixed_precision
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau, Callback, EarlyStopping
from PIL import ImageFile
import json
import os

# ==========================================
# 1. SETUP & GPU OPTIMIZATION
# ==========================================
ImageFile.LOAD_TRUNCATED_IMAGES = True

mixed_precision.set_global_policy('mixed_float16')
print("⚡ Mixed Precision Enabled")

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"🚀 GPU Active: {gpus[0].name}")

# ==========================================
# 2. CONFIG
# ==========================================
DATA_DIR = 'dataset_indian_cars_pro'
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_WARMUP = 10
EPOCHS_FINE = 40

# ==========================================
# 3. DATA PIPELINE (CORRECT)
# ==========================================

# TRAIN (with augmentation)
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.25,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    validation_split=0.2
)

# VALIDATION (NO AUGMENTATION)
val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

NUM_CLASSES = train_generator.num_classes

# ==========================================
# 4. MODEL
# ==========================================
base_model = EfficientNetB0(
    weights='imagenet',
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
    NUM_CLASSES,
    activation='softmax',
    dtype='float32'  # IMPORTANT for mixed precision
)(x)

model = Model(inputs=base_model.input, outputs=outputs)

# ==========================================
# 5. SAFE WEIGHT SAVER
# ==========================================
class BestWeightSaver(Callback):
    def __init__(self, name):
        super().__init__()
        self.best = 0.0
        self.name = name

    def on_epoch_end(self, epoch, logs=None):
        acc = logs.get('val_accuracy')
        if acc and acc > self.best:
            print(f"\n🌟 New Best: {self.best:.4f} → {acc:.4f}")
            self.best = acc
            self.model.save_weights(f"{self.name}_weights.h5")
            print("✅ Weights Saved")

saver = BestWeightSaver("car_classifier")

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=3,
    min_lr=1e-7,
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=7,
    restore_best_weights=True,
    verbose=1
)

# ==========================================
# 6. PHASE 1 – WARMUP
# ==========================================
print("\n🔥 PHASE 1: Warm-up")
base_model.trainable = False

model.compile(
    optimizer=Adam(1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_WARMUP,
    callbacks=[saver]
)

# ==========================================
# 7. PHASE 2 – FINE TUNING (CORRECT)
# ==========================================
print("\n🧊 PHASE 2: Fine-tuning")

base_model.trainable = True

# 🚨 Freeze BatchNorm layers
for layer in base_model.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False

model.compile(
    optimizer=Adam(1e-4),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
)

model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_FINE,
    callbacks=[saver, reduce_lr, early_stop]
)

# ==========================================
# 8. SAVE CLASS MAP
# ==========================================
class_map = {v: k for k, v in train_generator.class_indices.items()}

with open("class_indices.json", "w") as f:
    json.dump(class_map, f)

print("\n✅ TRAINING COMPLETE")
print("📦 Saved: car_classifier_weights.h5")
print("📄 Saved: class_indices.json")
