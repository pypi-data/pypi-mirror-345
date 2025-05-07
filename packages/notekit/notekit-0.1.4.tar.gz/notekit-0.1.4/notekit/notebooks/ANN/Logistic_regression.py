#!pip install tensorflow



import numpy as np
import tensorflow as tf
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Step 1: Load the dataset
data = load_breast_cancer()
X = data.data
y = data.target

# Step 2: Preprocess the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Step 3: Train Logistic Regression Model (Single sigmoid neuron)
logistic_model = Sequential([
    Dense(1, input_dim=X_train.shape[1], activation='sigmoid')
])
logistic_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
logistic_model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

# Step 4: Evaluate Logistic Regression
y_pred_prob_logistic = logistic_model.predict(X_test)
y_pred_logistic = (y_pred_prob_logistic > 0.5).astype("int32").flatten()
acc_logistic = accuracy_score(y_test, y_pred_logistic)
report_logistic = classification_report(y_test, y_pred_logistic)
auc_logistic = roc_auc_score(y_test, y_pred_prob_logistic)

print("\nLogistic Regression Model:")
print("Accuracy:", acc_logistic)
print("Classification Report:\n", report_logistic)
print("ROC AUC Score:", auc_logistic)

# Step 5: Train Neural Network Model (1 hidden layer)
nn_model = Sequential([
    Dense(64, input_dim=X_train.shape[1], activation='relu'),
    Dense(1, activation='sigmoid')
])
nn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
nn_model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

# Step 6: Evaluate Neural Network
y_pred_prob_nn = nn_model.predict(X_test)
y_pred_nn = (y_pred_prob_nn > 0.5).astype("int32").flatten()
acc_nn = accuracy_score(y_test, y_pred_nn)
report_nn = classification_report(y_test, y_pred_nn)
auc_nn = roc_auc_score(y_test, y_pred_prob_nn)

print("\nNeural Network Model:")
print("Accuracy:", acc_nn)
print("Classification Report:\n", report_nn)
print("ROC AUC Score:", auc_nn)
