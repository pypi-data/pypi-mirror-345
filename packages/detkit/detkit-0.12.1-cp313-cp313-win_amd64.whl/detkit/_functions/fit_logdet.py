# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.

# =======
# Imports
# =======

import numpy
import scipy
from pprint import pprint

__all__ = ['FitLogdet']


# ==========
# Fit Logdet
# ==========

class FitLogdet(object):
    """
    Fit and extrapolate log-determinant of large matrices.

    Parameters
    ----------

    m : int, default=2
        Number of terms in the Laurent series with logarithm

    n : int, default=0
        Number of terms in the Laurent series without logarithm

    alpha : float, default=0.0
        The exponent :math:`\\alpha` for the weight function
        :math:`w_{\\alpha}(x) = x^{-\\alpha}`. During the regression,
        both targets and covariates will be multiplied by this weight
        function.

    scale_x : float, default=1.0
        Scales `x` input data by a factor.

    scale_y : float, default=1.0
        Scales `y` input data by a factor.

    Methods
    -------

    fit
        Fit curve to data

    eval
        Evaluate fitted curve.

    Attributes
    ----------

    param
        Parameters of curve fitting.

    res
        Result of curve fitting optimization.

    Notes
    -----

    The fitting model is based on FLODANCE algorithm [1]_, given as

    .. math::

        y(x) w_{\\alpha}(x) = \\left( a_0 + a_{1} x + \\left(
        \\sum_{i=1}^m b_{i} x^{-i} \\right) \\ln(x!) +
        \\sum_{i=1}^n c_{i} x^{-i} \\right) w_{\\alpha}(x)

    where :math:`w(x) = x^{-\\alpha}`.

    References
    ----------

    .. [1] Ameli, S., van der Heide, C., Hodgkinson, L., Roosta, F., and
       Mahoney, M. W. (2025). Determinant Estimation under Memory Constraints
       and Neural Scaling Laws.

    Examples
    --------

    .. code-block:: python

        >>> from detkit import FitLogdet

        >>> # Create an interpolator object using m=6 truncated Laurent series.
        >>> flodet = FitLogdet(m=6)

        >>> # Fit model to data
        >>> flodet.fit(x_fit, y_fit)

        >>> # Evaluate fitted curve
        >>> y_eval = flodet.eval(x_eval)
    """

    # ====
    # init
    # ====

    def __init__(self, m=2, n=0, alpha=0.0, scale_x=1.0, scale_y=1.0):
        """
        Initialization.
        """

        self.m = m
        self.n = n
        self.alpha = alpha
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.param = None
        self.res = None

    # =============
    # design matrix
    # =============

    def _design_matrix(self, x):
        """
        Design matrix ``X`` for linear regression.

        Parameters
        ----------

        x : numpy.array
            One-dimensional array of inputs.

        Returns
        -------

        X : numpy.ndarray
            Two-dimensional array of design matrix. Number of rows are
            ``x.size`` and number of columns are ``4 + m + n``. The columns of
            ``X`` represent basis functions.

        Notes
        -----

        The columns of ``X`` are the basis functions.

        See Also
        --------

        fit
        """

        # Ensure x is an array
        if numpy.isscalar(x):
            x = numpy.array([x])
        else:
            x = numpy.array(x)

        # Three main bases x*log(x), x, and 1. Also, m+1 bases for the Laurent
        # terms log(x)*x^{-1}, and n bases for the Laurent terms x^{-i}.
        offset = 3
        X = numpy.zeros((len(x), offset + self.m + self.n))

        # Main basis
        X[:, 0] = scipy.special.loggamma(x + 1.0)
        X[:, 1] = x
        X[:, 2] = 1.0

        # Basis for Laurent series with log
        for i in range(0, self.m):
            X[:, offset + i] = scipy.special.loggamma(x + 1.0) * x**(-i-1)

        # Basis for Laurent series without log
        for i in range(0, self.n):
            X[:, offset + self.m + i] = x**(-i-1)

        # Weights
        w = x**(-self.alpha)
        X = X * w[:, numpy.newaxis]

        return X

    # =======================
    # second derivative basis
    # =======================

    def _second_derivative_basis(self, i, x):
        """
        Compute second derivative of basis function indexed by i.
        """

        offset = 3
        a = self.alpha

        # Log-gamma and its first and second derivatives (in terms of di-gamma)
        lg_d0 = scipy.special.loggamma(x + 1.0)
        lg_d1 = scipy.special.polygamma(0, x + 1.0)
        lg_d2 = scipy.special.polygamma(1, x + 1.0)

        # The three main terms
        if i == 0:
            # 2nd derivative of log-gamma
            der2 = (-a) * (-a-1) * x**(-a-2) * lg_d0 + \
                2.0 * (-a) * x**(-a-1) * lg_d1 + \
                x**(-a) * lg_d2

        elif i == 1:
            # x term -> second derivative = 0
            der2 = (1.0 - a) * (-a) * x**(-a-1)

        elif i == 2:
            # Constant term -> second derivative = 0
            der2 = (-a) * (-a - 1) * x**(-a - 2)

        elif (offset <= i) and (i <= offset + self.m):
            # Laurent terms with log
            j = i - offset
            der2 = (-j-1-a) * (-j-2-a) * x**(-j-3-a) * lg_d0 + \
                2.0 * (-j-1-a) * x**(-j-2-a) * lg_d1 + \
                x**(-j-1-a) * lg_d2

        else:
            # Laurent terms without log
            j = i - (offset + self.m)
            der2 = (-j-1-a) * (-j-2-a) * x**(-j-3-a)

        return der2

    # ===
    # fit
    # ===

    def fit(self, x, y, lam=0.0, smooth_interval=None, verbose=False):
        """
        Fit model to data.

        Parameters
        ----------

        x : numpy.array
            One-dimensional arrays of length N

        y : numpy.array
            One-dimensional arrays of length N

        lam : float, default=0.0
            Regularization strength. If set to zero, the model reverts to
            standard least squares fitting.

        smooth_interval : tuple (x_low, x_high) or None
            If given, the second derivative penalty is enforced in this range.

        verbose : boolean, default=False
            If `True`, the optimization results will be printed.

        See Also
        --------

        eval
        """

        # Ensure x and y are numpy arrays
        x = numpy.asarray(x, dtype=float)
        y = numpy.asarray(y, dtype=float)

        # Ensure positive x
        mask = x > 0
        w = x**(-self.alpha)
        x = x[mask] * self.scale_x
        y = y[mask] * self.scale_y * w

        if len(x) < self.m + self.n + 3:
            raise ValueError("Not enough valid data points.")

        # Build the design matrix
        X = self._design_matrix(x)

        # -----------------------
        # Regularization Matrix Q
        # -----------------------

        if lam > 0 and smooth_interval is not None:
            x_low, x_high = smooth_interval
            Q = numpy.zeros((X.shape[1], X.shape[1]))

            # Compute Q matrix
            num_basis = X.shape[1]
            for i in range(num_basis):
                for j in range(num_basis):
                    Q[i, j] = numpy.trapz(
                        self._second_derivative_basis(i, x) *
                        self._second_derivative_basis(j, x), x)

            # Regularization matrix
            Q *= lam

        else:
            # No penalty when lam = 0
            Q = numpy.zeros((X.shape[1], X.shape[1]))

        # --------------------------
        # Solve the Penalized System
        # --------------------------

        lhs = X.T @ X + Q
        rhs = X.T @ y

        self.param = numpy.linalg.solve(lhs, rhs)

        # Store residual information
        residuals = numpy.sum((y - X @ self.param) ** 2)
        rank = numpy.linalg.matrix_rank(X)
        singular_values = numpy.linalg.svd(X, compute_uv=False)

        self.res = {
            'residuals': residuals,
            'rank': rank,
            'singular_values': singular_values
        }

        if verbose:
            pprint(self.res)

    # ====
    # eval
    # ====

    def eval(self, x):
        """
        Evaluate fitted curve at a given ``x``.

        Parameters
        ----------

        x : numpy.array
            1D array of length N

        Returns
        -------

        y : numpy.array
            Evaluated values of curve fitting

        See Also
        --------

        fit
        """

        if self.param is None:
            raise RuntimeError('Train the model first.')

        # Ensure input is numpy array, not a list or tuple
        x = numpy.asarray(x, dtype=float) * self.scale_x

        mask = x > 0
        y = numpy.zeros_like(x, dtype=float)

        if numpy.any(mask):
            x_valid = x[mask]
            X = self._design_matrix(x_valid)
            w = x_valid**(-self.alpha)
            y_valid = X @ self.param / w
            y[mask] = y_valid

        return y / self.scale_y
