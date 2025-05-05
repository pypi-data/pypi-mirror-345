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

from ._utilities import get_data_type_name
from .._definitions.types cimport LongIndexType, DataType
from .._c_linear_algebra.c_matrix_decompositions cimport cMatrixDecompositions

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['orthogonalize']


# =============
# orthogonalize
# =============

cpdef orthogonalize(A):
    """
    Orthogonalize the columns of matrix.

    Parameters
    ----------

    A : array_like
        Input matrix. This matrix will be overwritten in place of the output
        orthogonal matrix.

    See Also
    --------

    detkit.ortho_complement

    Notes
    -----

    The Gram-Schmidt method is used to orthogonalize the columns of the input
    matrix :math:`\\mathbf{X}` so that it satisfies

    .. math::

        \\mathbf{X}^{\\intercal} \\mathbf{X} = \\mathbf{I},

    where :math:`\\mathbf{I}` is the identity matrix.

    .. warning::

        The input matrix will be overwritten inplace.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 14

        >>> # Create a random matrix
        >>> import numpy
        >>> numpy.random.seed(0)
        >>> A = numpy.random.rand(6, 3)

        >>> # Check orthogonality of A
        >>> numpy.around(A.T @ A, decimals=3)
        array([[1.267, 1.845, 1.42 ],
               [1.845, 2.97 , 2.065],
               [1.42 , 2.065, 2.687]])

        >>> # Orthogonalize matrix
        >>> from detkit import orthogonalize
        >>> orthogonalize(A)

        >>> # Check orthogonality of A again
        >>> numpy.around(A.T @ A, decimals=15)
        array([[ 1., -0., -0.],
               [-0.,  1.,  0.],
               [-0.,  0.,  1.]])
    """

    data_type_name = get_data_type_name(A)

    if data_type_name == b'float32':
        _pyc_gram_schmidt_float(A, A.shape[0], A.shape[1])
    elif data_type_name == b'float64':
        _pyc_gram_schmidt_double(A, A.shape[0], A.shape[1])
    elif data_type_name == b'float128':
        _pyc_gram_schmidt_long_double(A, A.shape[0], A.shape[1])
    else:
        raise TypeError('Data type should be "float32", "float64", or ' +
                        '"float128".')


# ======================
# pyc gram schmidt float
# ======================

cdef void _pyc_gram_schmidt_float(
        float[:, ::1] A,
        const LongIndexType num_rows,
        const LongIndexType num_columns) noexcept nogil:
    """
    Gram-Schmidt orthogonalization of the columns of a matrix, specialized for
    float type.
    """

    # Get c-pointer from memoryviews
    cdef float* c_A = &A[0, 0]

    with nogil:
        cMatrixDecompositions[float].gram_schmidt(c_A, num_rows, num_columns)


# =======================
# pyc gram schmidt double
# =======================

cdef void _pyc_gram_schmidt_double(
        double[:, ::1] A,
        const LongIndexType num_rows,
        const LongIndexType num_columns) noexcept nogil:
    """
    Gram-Schmidt orthogonalization of the columns of a matrix, specialized for
    double type.
    """

    # Get c-pointer from memoryviews
    cdef double* c_A = &A[0, 0]

    with nogil:
        cMatrixDecompositions[double].gram_schmidt(c_A, num_rows, num_columns)


# ============================
# pyc gram schmidt long double
# ============================

cdef void _pyc_gram_schmidt_long_double(
        long double[:, ::1] A,
        const LongIndexType num_rows,
        const LongIndexType num_columns) noexcept nogil:
    """
    Gram-Schmidt orthogonalization of the columns of a matrix, specialized for
    long double type.
    """

    # Get c-pointer from memoryviews
    cdef long double* c_A = &A[0, 0]

    with nogil:
        cMatrixDecompositions[long_double].gram_schmidt(c_A, num_rows, num_columns)
