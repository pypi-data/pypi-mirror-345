from sklearn.kernel_approximation import Nystroem
from sklearn.base import _fit_context
from sklearn.utils.extmath import randomized_svd as svd
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_is_fitted
import numpy as np
from .sinc import SKF


class NystroemSKF(Nystroem):
    def __init__(self, sigma, *, n_components=100, random_state=None, n_jobs=None):
        super().__init__(n_components=n_components, random_state=random_state, n_jobs=n_jobs)
        self.kernel = SKF(sigma)
        self.sigma = sigma

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        X = self._validate_data(X, accept_sparse="csr")
        rnd = check_random_state(self.random_state)
        n_samples = X.shape[0]

        # get basis vectors
        if self.n_components > n_samples:
            n_components = n_samples
            warnings.warn(
                "n_components > n_samples. This is not possible.\n"
                "n_components was set to n_samples, which results"
                " in inefficient evaluation of the full kernel."
            )

        else:
            n_components = self.n_components
        n_components = min(n_samples, n_components)
        inds = rnd.permutation(n_samples)
        basis_inds = inds[:n_components]
        basis = X[basis_inds]

        basis_kernel = self.kernel(basis, basis)

        # sqrt of kernel matrix on basis vectors
        U, S, V = svd(basis_kernel, n_components, random_state=self.random_state)
        S = np.maximum(S, 1e-12)
        self.normalization_ = np.dot(U / np.sqrt(S), V)
        self.components_ = basis
        self.component_indices_ = basis_inds
        self._n_features_out = n_components
        return self

    def transform(self, X):
        check_is_fitted(self)
        X = self._validate_data(X, accept_sparse="csr", reset=False)
        embedded = self.kernel(X, self.components_)
        return np.dot(embedded, self.normalization_.T)
