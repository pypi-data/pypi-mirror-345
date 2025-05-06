import numpy as np
import math

class SincODE:
    """
    Solves ordinary differential equations (ODEs) using Sinc Kernel Function.
    """

    def __init__(
        self,
        ode_function,
        forcing_function,
        kernel_mode=False,
        solver_method=np.linalg.solve,
    ):
        """
        Initialize the SincODE solver.

        Parameters:
        - ode_function (callable): Function returning the differential operator matrix.
        - forcing_function (callable): Function returning the right-hand side vector.
        - kernel_mode (bool): If True, treats ode_function as a kernel operator.
        - solver_method (callable): Linear solver (e.g., np.linalg.solve or a custom method).
        """
        self.ode_function = ode_function
        self.forcing_function = forcing_function
        self.primal_mode = not kernel_mode
        self.predict = np.vectorize(self._predict)
        self.solver_method = solver_method

    def _derivative_even(self, nu):
        """
        Construct matrix for the 2ν-th derivative using the Sinc basis.

        Parameters:
        - nu (int): Half the derivative order (i.e., computes order 2*nu).

        Returns:
        - ndarray: Dense matrix of the even-order derivative operator.
        """
        D = np.zeros((self.dimension, self.dimension))
        for i in range(self.dimension):
            for j in range(self.dimension):
                if i == j:
                    term = (
                        ((math.pi / self.h) ** (2 * nu)) * ((-1) ** nu) / (2 * nu + 1)
                    )
                else:
                    term = 0
                    for k in range(nu):
                        numerator = (
                            2
                            * nu
                            * math.factorial(nu)
                            * ((-1) ** (j - i))
                            * ((-1) ** (k + 1))
                            * (math.pi ** (2 * k))
                            * ((j - i) ** (2 * k))
                        )
                        denominator = (
                            self.h ** (2 * nu)
                            * ((j - i) ** (2 * nu))
                            * math.factorial(2 * k + 1)
                        )
                        term += numerator / denominator
                D[i, j] = term
        return D

    def _derivative_odd(self, nu):
        """
        Construct matrix for the (2ν+1)-th derivative using the Sinc basis.

        Parameters:
        - nu (int): Floor of half the derivative order (i.e., computes order 2*nu+1).

        Returns:
        - ndarray: Dense matrix of the odd-order derivative operator.
        """
        D = np.zeros((self.dimension, self.dimension))
        for i in range(self.dimension):
            for j in range(self.dimension):
                if i == j:
                    D[i, j] = 0
                else:
                    term_sum = 0
                    for k in range(nu + 1):
                        term = (
                            ((-1) ** (j - i))
                            * math.factorial(2 * nu + 1)
                            * ((-1) ** k)
                            * (np.pi ** (2 * k))
                            * ((j - i) ** (2 * k))
                        )
                        term /= (
                            (self.h ** (2 * nu + 1))
                            * ((j - i) ** (2 * nu + 1))
                            * math.factorial(2 * k + 1)
                        )
                        term_sum += term
                    D[i, j] = term_sum
        return D

    def derivative(self, nu):
        """
        Construct the derivative matrix of order ν.

        Parameters:
        - nu (int): Derivative order (must be non-negative).

        Returns:
        - ndarray: Derivative matrix D^(ν).
        """
        assert nu >= 0, ValueError("nu must be non-negative")
        if nu == 0:
            return np.eye(self.dimension)
        elif nu % 2 == 0:
            return self._derivative_even(nu // 2)
        else:
            return self._derivative_odd(nu // 2)

    def __getitem__(self, index):
        """
        Access derivative matrices by index.

        Parameters:
        - index (int or tuple):
            - If int and primal mode is active: returns D^index.
            - If tuple and dual mode is active: returns D^p @ D^q for index = (p, q).

        Returns:
        - ndarray: The selected operator matrix.
        """
        if isinstance(index, tuple) and len(index) == 2 and not self.primal_mode:
            p, q = index
            Dp = self.derivative(p)
            Dq = self.derivative(q)
            return Dp @ Dq
        elif isinstance(index, int) and self.primal_mode:
            return self.derivative(index)
        else:
            if self.primal_mode:
                raise ValueError(
                    "Invalid index format. In primal mode use e.g., obj[1] or obj[4]"
                )
            else:
                raise ValueError(
                    "Invalid index format. In kernel mode use e.g., obj[0,1] or obj[2,2]"
                )

    def solve(self, n, sigma):
        """
        Solve the linear system of SincODE.

        Parameters:
        - n (int): Half the number of collocation points (dimension = 2n + 1).
        - sigma (float): Scaling parameter for the coordinate map.
        """
        self.dimension = 2 * n + 1
        self.h = np.sqrt(np.pi**2 / (sigma * n))

        k = np.arange(-n, n + 1)
        self.xi = k * self.h

        omega = self.ode_function(self, self.xi)
        F = self.forcing_function(self.xi)

        if self.primal_mode:
            Omega = omega.T @ omega
        else:
            Omega = omega

        self.alpha = self.solver_method(Omega, F)
        self.omega = omega

    def _predict(self, x):
        """
        Evaluate the approximate solution at point x.

        Parameters:
        - x (float): Evaluation point.

        Returns:
        - float: Approximated solution value at x.
        """
        if self.primal_mode:
            w = self.omega @ self.alpha
            return np.sinc((x - self.xi) / self.h) @ w
        else:
            raise ValueError("Prediction is only available in primal mode.")
