import numpy as np

class HopfieldNetwork:
    def __init__(self, size):
        self.size = size
        self.weights = np.zeros((size, size))  # Initialize weight matrix to zeros

    def train(self, patterns):
        """Train the Hopfield network using the provided binary patterns."""
        for pattern in patterns:
            pattern = np.array(pattern)
            self.weights += np.outer(pattern, pattern)  # Update the weights matrix
        np.fill_diagonal(self.weights, 0)  # Set diagonal elements to 0 (no self-connection)

    def recall(self, pattern, steps=10):
        """Recall the stored pattern from the network using an initial pattern."""
        pattern = np.array(pattern)
        for _ in range(steps):
            # Update the state of each neuron based on the weighted sum of inputs
            for i in range(self.size):
                # Compute the net input (weighted sum)
                net_input = np.dot(self.weights[i], pattern)
                # Update the neuron state using the sign of net input
                pattern[i] = 1 if net_input >= 0 else -1
        return pattern

# Define 4 binary patterns to store in the network
patterns = [
    [1, -1, 1, -1],
    [-1, 1, 1, -1],
    [1, 1, -1, -1],
    [-1, -1, -1, 1]
]

# Initialize the Hopfield network with 4 neurons
hopfield_net = HopfieldNetwork(size=4)

# Train the network with the patterns
hopfield_net.train(patterns)

# Test the network by recalling the patterns
test_patterns = [
    [1, -1, -1, 1],  # Slightly corrupted version of pattern 1
    [-1, 1, 1, -1],  # Slightly corrupted version of pattern 2
]

# Recall the stored patterns
for test in test_patterns:
    recalled_pattern = hopfield_net.recall(test)
    print("Test Input:", test)
    print("Recalled Output:", recalled_pattern)
    print("-" * 40)
