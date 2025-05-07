import numpy as np

# Sigmoid and its derivative
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

# Input data (XOR)
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

# Expected outputs
y = np.array([[0], [1], [1], [0]])

# Initialize weights and biases with small values
W1 = np.array([[0.1, 0.2],
               [0.2, 0.1]])
b1 = np.array([[0.1, 0.1]])

W2 = np.array([[0.1],
               [0.2]])
b2 = np.array([[0.1]])

# Learning rate
lr = 0.1

# Forward pass function
def forward_pass(X, W1, b1, W2, b2):
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)

    z2 = np.dot(a1, W2) + b2
    a2 = sigmoid(z2)

    return z1, a1, z2, a2

# Backward pass function
def backward_pass(X, y, z1, a1, a2, W1, b1, W2, b2, lr):
    error = y - a2
    d_a2 = error * sigmoid_derivative(a2)

    error_hidden = np.dot(d_a2, W2.T)
    d_a1 = error_hidden * sigmoid_derivative(a1)

    # Update weights and biases
    W2 += lr * np.dot(a1.T, d_a2)
    b2 += lr * np.sum(d_a2, axis=0, keepdims=True)

    W1 += lr * np.dot(X.T, d_a1)
    b1 += lr * np.sum(d_a1, axis=0, keepdims=True)

    return W1, b1, W2, b2, np.mean(np.square(error))

# Training loop
epochs = 100000
for epoch in range(epochs):
    z1, a1, z2, a2 = forward_pass(X, W1, b1, W2, b2)
    W1, b1, W2, b2, loss = backward_pass(X, y, z1, a1, a2, W1, b1, W2, b2, lr)

    if epoch % 1000 == 0:
        print(f"Epoch {epoch} - Loss: {loss:.4f}")

# Final output
print("\nFinal Output After Training:")
print(np.round(a2, 3))
