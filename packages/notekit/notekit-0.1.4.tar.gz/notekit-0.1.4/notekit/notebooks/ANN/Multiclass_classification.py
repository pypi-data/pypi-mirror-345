import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# Activation functions
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1, 0)

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

def cross_entropy_loss(y_true, y_pred):
    m = y_true.shape[0]
    log_likelihood = -np.log(y_pred[range(m), np.argmax(y_true, axis=1)])
    return np.sum(log_likelihood) / m

# Load the Iris dataset
iris = load_iris()
X = iris.data
y = iris.target

# One-hot encode the labels
encoder = OneHotEncoder(sparse_output=False)
y_one_hot = encoder.fit_transform(y.reshape(-1, 1))

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_one_hot, test_size=0.2, random_state=42)

# Initialize the network parameters
input_size = X.shape[1]  # 4 features
hidden_size = 100
output_size = y_one_hot.shape[1]  # 3 classes

# Initialize weights and biases with small random values
W1 = np.random.randn(input_size, hidden_size) * 0.01
b1 = np.zeros((1, hidden_size))

W2 = np.random.randn(hidden_size, output_size) * 0.01
b2 = np.zeros((1, output_size))

# Learning rate
lr = 0.01

# Training loop
epochs = 1000
for epoch in range(epochs):
    # Forward pass
    z1 = np.dot(X_train, W1) + b1
    a1 = relu(z1)
    
    z2 = np.dot(a1, W2) + b2
    a2 = softmax(z2)
    
    # Calculate loss
    loss = cross_entropy_loss(y_train, a2)
    
    # Backward pass
    d_a2 = a2 - y_train
    d_W2 = np.dot(a1.T, d_a2) / X_train.shape[0]
    d_b2 = np.sum(d_a2, axis=0, keepdims=True) / X_train.shape[0]
    
    d_a1 = np.dot(d_a2, W2.T) * relu_derivative(a1)
    d_W1 = np.dot(X_train.T, d_a1) / X_train.shape[0]
    d_b1 = np.sum(d_a1, axis=0, keepdims=True) / X_train.shape[0]
    
    # Update weights and biases
    W2 -= lr * d_W2
    b2 -= lr * d_b2
    W1 -= lr * d_W1
    b1 -= lr * d_b1
    
    if epoch % 100 == 0:
        print(f"Epoch {epoch} - Loss: {loss:.4f}")

# Final evaluation on the test data
z1_test = np.dot(X_test, W1) + b1
a1_test = relu(z1_test)

z2_test = np.dot(a1_test, W2) + b2
a2_test = softmax(z2_test)

predictions = np.argmax(a2_test, axis=1)
y_test_labels = np.argmax(y_test, axis=1)

# Accuracy
accuracy = np.mean(predictions == y_test_labels)
print(f"Test Accuracy: {accuracy * 100:.2f}%")