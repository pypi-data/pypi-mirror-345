import numpy as np

# Laplace Mechanism for continuous data.
# Gaussian Mechanism for continuous data (commonly used in GDP).
    
def laplace_mechanism(query_result, sensitivity, epsilon):
    """Applies the Laplace mechanism for GDP."""
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale, 1)
    return query_result + noise[0]

def gaussian_mechanism(query_result, epsilon=0.5, delta=1e-5, sensitivity=1.0):
    """Adds Gaussian noise to a global query result."""
    sigma = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon
    noise = np.random.normal(0, sigma)
    return query_result + noise

class GDP:
    @staticmethod
    def add_noise(query_result, sensitivity, epsilon):
        return laplace_mechanism(query_result, sensitivity, epsilon)
    
    @staticmethod
    def add_gaussian_noise(query_result):
        return gaussian_mechanism(query_result)


