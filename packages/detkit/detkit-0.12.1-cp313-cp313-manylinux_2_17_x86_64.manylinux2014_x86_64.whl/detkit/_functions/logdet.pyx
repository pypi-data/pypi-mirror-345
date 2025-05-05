# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
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
from ._utilities import get_data_type_name
from .sy_logdet import sy_logdet
from .._definitions.types cimport DataType, LongIndexType, FlagType
from .._c_linear_algebra.c_matrix_functions cimport cMatrixFunctions

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['logdet']


# ======
# logdet
# ======

def logdet(
        A,
        sym_pos=False,
        overwrite_A=False,
        use_scipy=True):
    """
    Compute the `logdet` of a matrix.

    The `logdet` function is defined by

    .. math::

        \\mathrm{logdet}(\\mathbf{A}) :=
        \\log_{e} |\\mathrm{det}(\\mathbf{A})|.

    Parameters
    ----------
        A : (n, n) array_like
            Square matrix. The matrix type can be `float32`, `float64`, or
            `float128`. If a matrix of the type `int32` or `int64` is given,
            the type is cast to `float64`.

        sym_pos : bool, default=False
            If `True`, the matrix `A` is assumed to be symmetric and
            positive-definite (SPD). The computation can be twice as fast as
            when the matrix is not SPD. This function does not verify whether
            `A` is symmetric or positive-definite.

        overwrite_A : bool, default=False
            If `True`, the input matrix `A` will be overwritten during the
            computation. It uses less memory and could potentially be slightly
            faster.

        use_scipy : bool, default=True
            If `True`, it uses scipy functions which are the wrappers around
            Fortran routines in BLAS and LAPACK. If `False`, it uses a C++
            library developed in this package.

    Returns
    -------
        logdet : float
            `logdet` of `A`. If `A` is singular, returns ``-numpy.inf``.

        sign : int
            Sign of the determinant of `A` and can be ``+1`` for positive or
            ``-1`` for negative determinant. If `A` is singular, returns ``0``.

    Raises
    ------
        RuntimeError
            Error raised when ``sym_pos=True`` and matrix `A` is not symmetric
            positive-definite.

    Notes
    -----
        The function `logdet` is computed using the following algorithms:

        * When ``sym_pos=False``, the `logdet` function is computed using the
          *PLU decomposition* of `A`.
        * When ``sym_pos=True``, the `logdet` function is computed using the
          Cholesky decomposition of `A`.

        This python function is a wrapper to a C++ implementation.

    See Also
    --------

    memdet
    loggdet
    logpdet

    Examples
    --------
    .. code-block:: python

        >>> import numpy
        >>> from detkit import logdet

        >>> # Generate a random matrix
        >>> n = 1000
        >>> rng = numpy.random.RandomState(0)
        >>> A = rng.rand(n, n)

        >>> # Compute logdet of matrix
        >>> logdet(A)
        (1710.9576831500378, -1)

        >>> # Compute logdet of a symmetric and positive-definite matrix
        >>> B = A.T @ A
        >>> logdet(B, sym_pos=True)
        (3421.9153663693114, 1)

        >>> # Compute logdet of a singular matrix
        >>> A[:, 0] = 0
        >>> logdet(A)
        (-inf, 0)
    """

    if use_scipy:
        return sy_logdet(A, sym_pos=sym_pos, overwrite_A=overwrite_A)

    # A_ will be overwritten by PLU and Cholesky decompositions
    if overwrite_A:
        # Input A will be overwritten
        A_ = A
    else:
        # Input A will remain unaltered
        A_ = numpy.copy(A)

    # Convert int to float type
    data_type_name = get_data_type_name(A_)
    if data_type_name in [b'int32', b'int64']:
        A_ = A_.astype(numpy.float64)
        data_type_name = b'float64'

    sym_pos = int(sym_pos)
    logdet_, sign = pyc_logdet(A_, A_.shape[0], data_type_name, sym_pos)

    return logdet_, sign


# ==========
# pyc logdet
# ==========

cpdef pyc_logdet(
        A,
        num_rows,
        data_type_name,
        sym_pos):
    """
    Dispatches to typed cython functions.
    """

    sign = numpy.array([0], dtype=numpy.int32)
    cdef FlagType[:] mv_sign = sign
    cdef FlagType* c_sign = &mv_sign[0]

    if data_type_name == b'float32':
        logdet_ = pyc_logdet_float(A, num_rows, sym_pos, c_sign)
    elif data_type_name == b'float64':
        logdet_ = pyc_logdet_double(A, num_rows, sym_pos, c_sign)
    elif data_type_name == b'float128':
        logdet_ = pyc_logdet_long_double(A, num_rows, sym_pos, c_sign)
    else:
        raise TypeError('Data type should be "float32", "float64", or ' +
                        '"float128".')

    if (sign[0] == -3):
        message = 'Cholesky decomposition failed since matrix "A" is not ' + \
                  'symmetric positive-definite.'
        if sym_pos:
            message += ' Set "sym_pos" to False.'
        raise RuntimeError(message)
    elif (sign[0] == -4):
        logdet_ = -numpy.inf
        sign[0] = 0
    elif sign[0] == -2:
        logdet_ = -numpy.inf
        sign[0] = 0
    elif sign[0] == 2:
        logdet_ = numpy.inf
        sign[0] = 0

    return logdet_, sign[0]


# ================
# pyc logdet float
# ================

cdef float pyc_logdet_float(
        float[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) noexcept nogil:
    """
    Dispatches to C++ function with 32-bit float type.
    """

    # Get c-pointer from memoryviews
    cdef float* c_A = &A[0, 0]

    # Compute logdet
    cdef float logdet_
    with nogil:
        logdet_ = cMatrixFunctions[float].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_


# =================
# pyc logdet double
# =================

cdef double pyc_logdet_double(
        double[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) noexcept nogil:
    """
    Dispatches to C++ function with 64-bit float type.
    """

    # Get c-pointer from memoryviews
    cdef double* c_A = &A[0, 0]

    # Compute logdet
    cdef double logdet_
    with nogil:
        logdet_ = cMatrixFunctions[double].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_


# ======================
# pyc logdet long double
# ======================

cdef long double pyc_logdet_long_double(
        long double[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) noexcept nogil:
    """
    Dispatches to C++ function with 128-bit float type.
    """

    # Get c-pointer from memoryviews
    cdef long double* c_A = &A[0, 0]

    # Compute logdet
    cdef long double logdet_
    with nogil:
        logdet_ = cMatrixFunctions[long_double].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_
