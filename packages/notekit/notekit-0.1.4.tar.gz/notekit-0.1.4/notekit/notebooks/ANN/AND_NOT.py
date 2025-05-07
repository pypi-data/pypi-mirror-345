def andnot_neuron(a, b):
    """McCulloch-Pitts neuron for A AND NOT B"""
    w1 = 1   # weight for input A
    w2 = -1  # weight for input B (negated)
    theta = 1  # threshold

    # Weighted sum
    net_input = a * w1 + b * w2

    # Step activation function
    if net_input >= theta:
        return 1
    else:
        return 0

def generate_truth_table():
    inputs = [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ]

    print("A B | A AND NOT B")
    print("------------------")
    for pair in inputs:
        a = pair[0]
        b = pair[1]
        output = andnot_neuron(a, b)
        print(a, b, "|", output)

# Run the truth table generator
generate_truth_table()
