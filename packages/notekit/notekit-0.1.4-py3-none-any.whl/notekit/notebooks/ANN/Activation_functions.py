import numpy as np
import matplotlib.pyplot as plt

def sigmoid(x):
    """Sigmoid activation function"""
    return 1 / (1 + np.exp(-x))

def tanh(x):
    """Hyperbolic tangent activation function"""
    return np.tanh(x)

def relu(x):
    """Rectified Linear Unit (ReLU) activation function"""
    return np.maximum(0, x)

def linear(x):
    """Linear activation function (identity function)"""
    return x

# Create a range of input values
x = np.linspace(-10, 10, 100)

# Create a single figure with increased figure size
plt.figure(figsize=(12, 8))

# Plot different activation functions with line width adjustments
plt.plot(x, sigmoid(x), label='Sigmoid', color='blue', linewidth=2)
plt.plot(x, tanh(x), label='Tanh', color='red', linewidth=2)
plt.plot(x, relu(x), label='ReLU', color='green', linewidth=2)
plt.plot(x, linear(x), label='Linear', color='orange', linestyle='-.', linewidth=2)

# Customize the plot
plt.title('Comparison of Activation Functions', fontsize=18)
plt.xlabel('Input', fontsize=14)
plt.ylabel('Output', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left', fontsize=12)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.7)
plt.axvline(x=0, color='black', linestyle='-', linewidth=0.7)

# Adjusting the y-axis limits for better visualization
plt.ylim(-1.5, 2)

# Enhance the ticks for better clarity
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Show the plot
plt.tight_layout()
plt.show()
