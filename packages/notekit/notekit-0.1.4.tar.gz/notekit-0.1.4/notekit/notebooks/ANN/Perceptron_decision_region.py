import numpy as np
import matplotlib.pyplot as plt

# AND gate input and output
X = np.array([[0,0], [0,1], [1,0], [1,1]])
y = np.array([0, 0, 0, 1])

# Initialize weights and bias
w = np.zeros(2)
b = 0
lr = 0.1

# Perceptron learning rule
for _ in range(10):
    for i in range(len(X)):
        output = 1 if np.dot(X[i], w) + b >= 0 else 0
        error = y[i] - output
        w += lr * error * X[i]
        b += lr * error

# Simple 2D Plot
for i in range(len(X)):
    color = 'blue' if y[i] == 0 else 'red'
    plt.scatter(X[i][0], X[i][1], color=color)

# Plot decision boundary: w1*x + w2*y + b = 0 → y = -(w1*x + b)/w2
x_vals = np.array([0, 1])
y_vals = -(w[0] * x_vals + b) / w[1]
plt.plot(x_vals, y_vals, 'k--')  # dashed black line

plt.title("Perceptron Decision Boundary (AND Gate)")
plt.xlabel("Input 1")
plt.ylabel("Input 2")
plt.grid(True)
plt.xlim(-0.1, 1.1)
plt.ylim(-0.1, 1.1)
plt.show()
