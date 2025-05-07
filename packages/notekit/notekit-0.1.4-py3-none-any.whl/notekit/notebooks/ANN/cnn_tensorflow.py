

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
(train_images, train_labels), (test_images, test_labels) = datasets.mnist.load_data()

# Normalize the images to [0, 1]
train_images = train_images / 255.0
test_images = test_images / 255.0

# Reshape images to add channel dimension
train_images = train_images.reshape((train_images.shape[0], 28, 28, 1))
test_images = test_images.reshape((test_images.shape[0], 28, 28, 1))

# Convert labels to categorical one-hot encoding
train_labels = tf.keras.utils.to_categorical(train_labels)
test_labels = tf.keras.utils.to_categorical(test_labels)

model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(train_images, train_labels, epochs=5,
                    validation_data=(test_images, test_labels))

test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
print(f'\nTest accuracy: {test_acc}')

plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0.8, 1])
plt.legend(loc='lower right')
plt.show()

"""# 📚 Theory for CNN on MNIST

---

## 1️⃣ What is a Convolutional Neural Network (CNN)?

- A CNN is a type of deep learning model specialized in processing **grid-like data** (such as images).
- CNNs automatically and adaptively learn **spatial hierarchies of features** (like edges, textures, shapes).
- Inspired by the **visual cortex** of animals — it captures **spatial relationships** between pixels using small filters (kernels).

---

## 2️⃣ Key CNN Components

| Component              | Purpose                                                    |
|------------------------|------------------------------------------------------------|
| **Convolution Layer**  | Extracts features (edges, patterns) using filters.         |
| **Activation (ReLU)**  | Introduces non-linearity (helps to model complex patterns).|
| **Pooling Layer**      | Reduces spatial dimensions → less computation & controls overfitting. |
| **Flatten Layer**      | Converts 2D feature maps into 1D vector (prepares for dense layers). |
| **Fully Connected Layer (Dense)** | Performs classification based on extracted features. |
| **Softmax Layer**      | Converts outputs into probability distribution over classes. |

---

## 3️⃣ Explanation of Code

| Code Section                        | Purpose                                                |
|-------------------------------------|--------------------------------------------------------|
| `datasets.mnist.load_data()`        | Loads handwritten digit images (28x28 grayscale).      |
| **Normalization** (`/ 255.0`)       | Scales pixel values to [0,1] — speeds up training.     |
| `Conv2D(32, (3,3))`                | 32 filters, 3x3 kernel → learns edge-like features.    |
| `MaxPooling2D((2,2))`              | Reduces image size by 2x → keeps prominent features.   |
| `Flatten()`                         | Converts pooled feature maps to a flat vector.         |
| `Dense(64, relu)`                   | Learns complex combinations of features.               |
| `Dense(10, softmax)`                | Outputs probability for each of 10 classes (digits 0–9). |
| `compile(optimizer='adam', loss='categorical_crossentropy')` | Sets optimizer and loss function suitable for classification. |
| `fit(..., epochs=5)`                | Trains model on data for 5 iterations.                 |
| `evaluate()`                        | Tests model accuracy on unseen data.                   |

---

## 4️⃣ Advantages of CNN

- ✅ Automatic feature extraction (no manual feature engineering).
- ✅ Very effective at **spatial data** (images, videos).
- ✅ Fewer parameters than fully connected networks (weight sharing).
- ✅ High accuracy with relatively low preprocessing.

---

## 5️⃣ Disadvantages of CNN

- ❌ Requires **large datasets** and **high computational power** (GPU recommended).
- ❌ Less interpretable — "black box" (hard to understand what exactly filters learn).
- ❌ Sensitive to orientation and scale variations (basic CNNs).

---

## 6️⃣ Applications of CNN

- 🖼️ Image classification (MNIST, CIFAR-10, ImageNet)
- 🧍 Object detection (YOLO, SSD)
- 📷 Face recognition (FaceNet)
- 🩻 Medical image analysis (MRI, CT scans)
- 🔡 Handwriting recognition (like our MNIST example)
- 🚗 Self-driving cars (road/lane detection)
- 🎥 Video analysis (action recognition, surveillance)
- 🔍 Feature extraction for downstream ML tasks

---

## 7️⃣ Basic CNN Viva Questions

- What is a filter/kernel in CNN?
- What is the purpose of pooling?
- Why is ReLU activation used?
- Why do we normalize images before feeding to CNN?
- Difference between Fully Connected NN vs CNN?
- What is overfitting? How can pooling help prevent it?
- What is Softmax and why do we use it in the output layer?

---

## 8️⃣ Advanced but safe to know

- **Parameter sharing**: Same filter weights applied to different regions — reduces total parameters.
- **Translation invariance**: CNNs can recognize objects even if they're slightly shifted in the image.
- **Stride**: Controls how the filter moves over the image.

---

## 🎯 Summary

If you confidently know:

- **Layers → Function**
- **Code → What it does**
- **Advantages + Applications**

You’re ready for interview/viva on this notebook ✅

"""