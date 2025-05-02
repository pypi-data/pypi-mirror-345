import numpy as np
import random

# Laplace Mechanism (common for numeric data)
# Randomized Response (common for categorical/binary data)

def laplace_mechanism(value, epsilon, sensitivity=1.0):
    """Adds Laplace noise to a numeric value for LDP."""
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise

def randomized_response(value, epsilon):
    """Implements randomized response for binary data."""
    p = np.exp(epsilon) / (1 + np.exp(epsilon))
    return value if random.random() < p else 1 - value

class LDP:
    @staticmethod
    def add_numerical_noise(value, epsilon):
        return laplace_mechanism(value, epsilon)
    
    def add_categorical_noise(value, epsilon):
        return randomized_response(value, epsilon)


