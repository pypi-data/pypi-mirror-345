import numpy as np

# Sigmoid activation function and its derivative
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

# XOR Input and Output
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])  # Inputs
y = np.array([[0], [1], [1], [0]])  # Expected XOR outputs

# Initialize weights and biases with small random values
np.random.seed(42)
input_size = 2  # Number of input neurons (2 inputs)
hidden_size = 2  # Number of neurons in the hidden layer (set to 2)
output_size = 1  # Number of output neurons (1 output for XOR)

# Weights initialization (with small random values)
W1 = np.random.randn(input_size, hidden_size) * 0.1
b1 = np.zeros((1, hidden_size))

W2 = np.random.randn(hidden_size, output_size) * 0.1
b2 = np.zeros((1, output_size))

# Learning rate
lr = 0.1

# Training loop for 10000 iterations
epochs = 10000
for epoch in range(epochs):
    # Forward pass
    z1 = np.dot(X, W1) + b1  # Weighted sum for hidden layer
    a1 = sigmoid(z1)  # Activation of hidden layer
    
    z2 = np.dot(a1, W2) + b2  # Weighted sum for output layer
    a2 = sigmoid(z2)  # Activation of output layer
    
    # Compute the loss (Mean Squared Error)
    loss = np.mean((y - a2) ** 2)
    
    # Backward pass (gradient computation)
    d_a2 = 2 * (a2 - y) * sigmoid_derivative(a2)
    d_W2 = np.dot(a1.T, d_a2)
    d_b2 = np.sum(d_a2, axis=0, keepdims=True)
    
    d_a1 = np.dot(d_a2, W2.T) * sigmoid_derivative(a1)
    d_W1 = np.dot(X.T, d_a1)
    d_b1 = np.sum(d_a1, axis=0, keepdims=True)
    
    # Update weights and biases using gradient descent
    W2 -= lr * d_W2
    b2 -= lr * d_b2
    W1 -= lr * d_W1
    b1 -= lr * d_b1
    
    if epoch % 1000 == 0:
        print("Epoch", epoch, "- Loss:", loss)

# Save the final weights and biases after training
final_W1 = W1
final_b1 = b1
final_W2 = W2
final_b2 = b2

# Perform prediction with the trained model
def predict(X, W1, b1, W2, b2):
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    a2 = sigmoid(z2)
    return a2

# Test the trained network on XOR inputs using the final weights
predictions = predict(X, final_W1, final_b1, final_W2, final_b2)

# Display predictions and round them to 0 or 1
print("\nFinal output after training:")
for i in range(4):
    print("Input:", X[i], "=> Predicted Output:", predictions[i], "(Rounded:", round(predictions[i][0]), ")")
