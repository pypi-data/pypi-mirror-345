import numpy as np

# Parameters
num_features = 4
num_classes = 3
vigilance = 0.75

# Binary input patterns
data = np.array([
    [1, 0, 0, 1],
    [1, 0, 1, 1],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 1]
])

# Initialize weights
w_bottom_up = np.ones((num_classes, num_features))
w_top_down = 0.5 * np.ones((num_classes, num_features))
committed = [False] * num_classes

# Training logic
for input_vector in data:
    print("Input:", input_vector)
    found = False
    for i in range(num_classes):
        if not committed[i]:
            print(f"Assigning to uncommitted neuron {i}")
            w_bottom_up[i] = input_vector
            w_top_down[i] = input_vector
            committed[i] = True
            found = True
            break
        else:
            match = np.all(input_vector * w_top_down[i] == input_vector)
            vigilance_score = np.sum(input_vector * w_top_down[i]) / np.sum(input_vector)
            if match and vigilance_score >= vigilance:
                print(f"Updating weights for neuron {i}")
                w_bottom_up[i] = input_vector * w_bottom_up[i]
                w_top_down[i] = input_vector * w_top_down[i]
                found = True
                break
            else:
                print(f"Neuron {i} rejected (match or vigilance failed)")
    if not found:
        print("No suitable neuron found")

# Display final weights
print("\nFinal Bottom-Up Weights:")
print(w_bottom_up)
print("\nFinal Top-Down Weights:")
print(w_top_down)