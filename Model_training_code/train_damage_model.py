import os
import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

print("TensorFlow Version:", tf.__version__)

# ==========================================
# CONFIG
# ==========================================

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10

DATASET_PATH = "damage_dataset"  # <-- change if needed

# ==========================================
# DATA GENERATORS
# ==========================================

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    subset='validation'
)

# ==========================================
# CLASS WEIGHTS
# ==========================================

from collections import Counter

counter = Counter(train_generator.classes)
max_count = float(max(counter.values()))

class_weight_dict = {}

for class_id, count in counter.items():
    class_weight_dict[int(class_id)] = float(max_count / float(count))

print("Class Weights:", class_weight_dict)

# ==========================================
# MODEL
# ==========================================

base_model = EfficientNetB0(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.4)(x)
output = Dense(len(train_generator.class_indices), activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ==========================================
# CALLBACKS
# ==========================================

callbacks = [
    EarlyStopping(patience=3, restore_best_weights=True),
    ReduceLROnPlateau(patience=2)
]

# ==========================================
# TRAIN
# ==========================================

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    class_weight=class_weight_dict,
    callbacks=callbacks
)


# ============================
# SAVE WEIGHTS ONLY
# ============================

model.save_weights("damage_classifier.weights.h5")

# Save class indices
import json
with open("damage_class_indices.json", "w") as f:
    json.dump(train_generator.class_indices, f)

print("✅ Weights and class indices saved successfully")
