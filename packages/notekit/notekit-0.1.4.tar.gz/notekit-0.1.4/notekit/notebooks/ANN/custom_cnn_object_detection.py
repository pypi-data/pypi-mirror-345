
#!pip install tensorflow opencv-python matplotlib

"""# 📥 Import Libraries"""

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt
import cv2

"""# 🖼️ Load and Preprocess Sample Image (Simulated Small Dataset)"""

# For demo purpose, let's create synthetic data
# Simulate small object detection dataset — images with 1 object (rectangle) and its bounding box

def generate_image_and_box():
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    x1, y1 = np.random.randint(5, 30), np.random.randint(5, 30)
    x2, y2 = x1 + np.random.randint(10, 30), y1 + np.random.randint(10, 30)
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), -1)
    box = [x1 / 64, y1 / 64, x2 / 64, y2 / 64]  # Normalize coordinates (0-1)
    return img, box

# Create small dataset
X = []
y = []
for _ in range(500):
    img, box = generate_image_and_box()
    X.append(img)
    y.append(box)

X = np.array(X) / 255.0
y = np.array(y)
plt.imshow(X[0])
plt.title(f'Bounding Box (normalized): {y[0]}')
plt.show()

"""# 🧠 Define Simple CNN Model (Output → Bounding Box Coords [x1, y1, x2, y2])"""

model = models.Sequential([
    layers.Conv2D(16, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(4, activation='sigmoid')  # Output normalized box coords (0-1)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.summary()

"""# ⚙️ Train Model"""

history = model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)

"""# 🔍 Test Prediction and Visualize Bounding Box"""

test_img, true_box = generate_image_and_box()
input_img = test_img / 255.0
pred_box = model.predict(np.expand_dims(input_img, axis=0))[0]

# Denormalize predicted box
pred_box = (pred_box * 64).astype(int)
x1, y1, x2, y2 = pred_box
output_img = test_img.copy()
cv2.rectangle(output_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

plt.imshow(output_img)
plt.title(f"Predicted Box: {pred_box}")
plt.show()

"""# 📊 Performance Metrics for Object Detection

| Metric                   | Meaning |
|--------------------------|---------|
| **IoU (Intersection over Union)** | Overlap between predicted box & ground truth box. |
| **MAE / MSE Loss** | Regression error on box coordinates. |
| **Precision & Recall** (if multi-object + classification) | Classification metrics (for class labels). |
| **FPS (Frames per Second)** | Speed metric — how fast model processes images. |
| **Inference Time** | Time per image inference. |

**Note:** Since we are doing just bounding box regression here (no class labels), metrics like mAP, precision, recall aren't directly used. Focus is on **IoU** and **box accuracy**.
"""

