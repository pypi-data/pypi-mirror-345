import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    """Compute the softmax of vector x."""
    e_x = np.exp(x)  # Subtract max for numerical stability
    return e_x / e_x.sum(axis=0, keepdims=True)

def attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    tmp = np.dot(Q, K.T)
    d_k = K.shape[-1]
    scores = tmp / np.sqrt(d_k)  # Scale scores by sqrt(d_k)
    weights = softmax(scores)  # Apply softmax to get attention weights
    return np.dot(weights, V)  # Compute the final output by multiplying weights with V