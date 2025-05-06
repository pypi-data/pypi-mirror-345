import numpy as np
from numba import jit

@jit('double[:,:](double[:,:], double[:,:], double)', nogil=True, nopython=True, parallel=False, cache=True)
def sinc_kernel(x, y, sigma):
    x_expanded = x[:, np.newaxis, :]
    y_expanded = y[np.newaxis, :, :]
    diff_x = (x_expanded - y_expanded) / sigma
    phi_x = np.sinc(diff_x).reshape(x.shape[0], -1)
    
    y_expanded_j = y[:, np.newaxis, :]
    y_expanded_n = y[np.newaxis, :, :]
    diff_y = (y_expanded_j - y_expanded_n) / sigma
    phi_y = np.sinc(diff_y).reshape(y.shape[0], -1)
    
    kernel = phi_x @ phi_y.T
    return kernel


class SKF:
    """
    Callable wrapper for the sinc_kernel function.

    Example:
        svm = SVC(kernel=SKF(sigma=0.5))
        svm.fit(X_train, y_train)
    """
    def __init__(self, sigma: float):
        self.sigma = sigma

    def __call__(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        # Forward to the underlying sinc_kernel
        return sinc_kernel(X, Y, self.sigma)

    def __repr__(self):
        return f"{self.__class__.__name__}(sigma={self.sigma})"
