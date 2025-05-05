# SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the license found in the LICENSE.txt file in the root
# directory of this source tree.


# =======
# Imports
# =======

import numpy
from .._functions import orthogonalize


# =============
# Design Matrix
# =============

def design_matrix(
        num_rows=2**9,
        num_cols=2**8,
        ortho=False):
    """
    Generate design matrix.

    Parameters
    ----------

    num_rows : int, default=2**9
        Number of rows of the matrix.

    num_cols : int, default=2**8
        Number of columns of the matrix.

    ortho : bool, default=False
        If `True`, the matrix is orthonormalized.

    Returns
    -------

    X : numpy.ndarray
        A 2D array

    See Also
    --------

    detkit.covariance_matrix
    detkit.orthogonalize

    Notes
    -----

    The design matrix is created as follows:

    .. math::

        X_{ij} =
        \\begin{cases}
            1 & j = 1, \\\\
            \\sin(t_i \\pi j) & j = 2k, \\\\
            \\cos(t_i \\pi j) & j = 2k+1,
        \\end{cases}

    where :math:`t_i = \\frac{i}{n}` and :math:`n` is the number of the rows
    of the matrix.

    **Orthonormalization:**

    The matrix :math:`\\mathbf{X}` is orthonormalized by Gram-Schmidt process
    using :func:`detkit.orthogonalize` function.

    Examples
    --------

    .. code-block:: python

        >>> import detkit
        >>> n, m = 2**9, 2**2
        >>> X = detkit.datasets.design_matrix(n, m, ortho=True)
        [[ 0.04419417 -0.09094864  0.06243905 -0.09532571]
         [ 0.04419417 -0.09006862  0.06243787 -0.09299386]
         [ 0.04419417 -0.08918863  0.06243433 -0.09066257]
         ...
         [ 0.04419417 -0.08918863 -0.06243433 -0.09066257]
         [ 0.04419417 -0.09006862 -0.06243787 -0.09299386]
         [ 0.04419417 -0.09094864 -0.06243905 -0.09532571]]

    Check if the above matrix is orthonormal:

    .. code-block::python

        >>> import numpy
        >>> I = numpy.eye(m, m)
        >>> numpy.allclose(X.T @ X, I)
        True
    """

    if num_cols > num_rows:
        raise ValueError('Number of columns should be smaller or equal to ' +
                         'the number of rows.')

    X = numpy.zeros((num_rows, num_cols), dtype=float)
    X[:, 0] = 1

    # Fill the rest with sin and cosine functions
    t = numpy.linspace(0, 1, num_rows)
    for j in range(1, num_cols, 2):

        X[:, j] = numpy.sin(t * numpy.pi * float(j))

        if j+1 < num_cols:
            X[:, j+1] = numpy.cos(t * numpy.pi * float(j))

    # Orthonormalize the output matrix
    if ortho:
        orthogonalize(X)

    return X
