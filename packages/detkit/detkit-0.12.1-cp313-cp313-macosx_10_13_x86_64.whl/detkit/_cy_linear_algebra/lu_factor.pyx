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
from scipy.linalg.cython_lapack cimport sgetrf, dgetrf

__all__ = ['lu_factor']


# ====================
# pivot to permutation
# ====================

def _pivot_to_permutation(piv, m):
    """
    Convert pivot to permutation.

    For a matrix of size (m, n) where m = min([m, n]), the pivots "piv" are of
    the size k, and "perm" is of the size m (number of rows).
    """

    perm = numpy.arange(m)

    for i in range(len(piv)):
        perm[i], perm[piv[i]] = perm[piv[i]], perm[i]

    return perm


# =========
# lu factor
# =========

cpdef lu_factor(A, shape=None, overwrite=False):
    """
    LU decomposition of a sub-matrix.

    Parameters
    ----------

    A : numpy.ndarray
        A generic rectangular matrix with either ``float64`` or ``float32``
        data type stored with either row-major or column major ordering.

    shape : tuple, default=None
        A tuple of size two, determining the shape of an upper-left sub-matrix
        of `A` to be referenced. Namely, if ``shape`` is given as the tuple
        ``(m, n)``, the sub-matrix ``A[:m, :n]`` is considered. If `None`, the
        full shape of ``A[:, :]`` is used.

    overwrite : bool, default=False
        If `True`, the input matrix `A` will be overwritten as the output,
        allowing to save memory. In this case, the output matrix `lu` will
        point to the same location in the memory as the input matrix `A`.

        .. note::

            When ``overwrite`` is set to `True`, the matrix `A` should have
            column-major (Fortran) ordering.

    Returns
    -------

    lu : numpy.ndarray
        A 2D matrix of the same shape as the input matrix `A` (and not the
        shape of the sub-matrix). The upper-left sub-matrix of `lu` contains
        the LU factor of the sub-matrix of `A`. Namely, the upper and lower
        triangular parts of the sub-matrix of `lu` consist of both matrices
        `L` and `U`. The diagonals of `L` (which consists of ``1``) are
        not stored (see notes for details). If ``overwrite`` is set to `True`,
        the output matrix `lu` is becomes a view for the matrix `A`.

    perm : numpy.array
        Permutation indices of row pivoting (zero-based indexing). This array
        is of the size ``A.shape[0]``, regardless of the given shape of the
        sub-matrix.

    See Also
    --------

    detkit.ldl_factor
    detkit.cho_factor
    detkit.lu_solve

    References
    ----------

    * `LAPACK <https://www.netlib.org/lapack>`__

    Notes
    -----

    **LU decomposition of sub-matrix:**

    Let :math:`\mathbf{A}_{[:p,:q]}` denote the sub-matrix of the size
    :math:`p \\times q` to be the upper-left corner of matrix
    :math:`\mathbf{A}`. Its LU decomposition is given by:

    .. math::

        \\mathbf{A}_{[:p, :q]} = \\mathbf{P} \\mathbf{L} \\mathbf{U},

    where :math:`\mathbf{P}` is a permutation matrix of the size
    :math:`p \\times p`, :math:`\\mathbf{L}` is a lower-triangular matrix of
    the size :math:`p \\times k` with diagonals :math:`1`, where
    :math:`k = \\min(p, q)`, and :math:`\\mathbf{U}` is an upper-triangular
    matrix of the size :math:`k \\times q`.

    **Interpreting L and U factors from the output lu:**

    Note that the output matrix ``lu`` is given as the same shape as ``A``, and
    only its upper-left sub-matrix should be used to extract the matrices
    :math:`\\mathbf{L}` and :math:`\\mathbf{U}` as follows.

    Let ``p, q = shape`` be the given shape of the upper-left sub-matrix, which
    may be smaller than the shape of ``A``. Also, let ``k = min(p, q)``. Then,
    ``L = lu[:p, :k]`` (excluding the diagonals) and ``U = lu[:k, :q]``.

    The diagonals of ``L`` are not stored in the above matrix, and you should
    assume the diagonals of ``L`` are ``1`` (see example below to adjust the
    diagonals of ``L`` to one manually).

    **Interpreting permutation array:**

    The output ``perm`` is a 1D array of the size of the number of rows of the
    input matrix `A` (and not the number of rows of the sub-matrix). The array
    ``A[perm, :]`` is equivalent of
    :math:`\\mathbf{P}^{\\intercal} \\mathbf{A}`. As such, the relation
    relation
    :math:`\\mathbf{P}^{\\intercal} \mathbf{A} = \mathbf{L} \\mathbf{U}` can be
    achieved by ``A[perm[:p], :] = L @ U``.

    **Comparison with scipy.linalg.lu_factor:**

    To compute the LU factorization of a sub-matrix of the input matrix using
    ``scipy.linalg.lu_factor`` function, you should pass a slice of the
    matrix to the function. This approach is not memory-efficient since
    the sliced array allocates new memory.

    In contrast, using ``detkit.lu_factor`` together with the ``shape``
    argument, no memory slice is created during the inner computation, rather,
    the data from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``sgetrf`` (for 32-bit
    precision) and ``dgetrf`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 20

        >>> from detkit import lu_factor, Memory
        >>> import numpy
        
        >>> # Create a matrix with 32-bit precision and column-major ordering
        >>> A = numpy.random.randn(1000, 900) + 100 * numpy.eye(1000, 900)
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Get a copy of A (for the purpose of comparison) since we will
        >>> # overwrite A
        >>> A_copy = numpy.copy(A)

        >>> # Track memory allocation to check if LU decomposition is not
        >>> # creating any new memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # LU factorization of the upper-left sub-matrix of smaller shape
        >>> p, q = 800, 700
        >>> lu, perm = lu_factor(A, shape=(p, q), overwrite=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = p * q * A.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.001

        >>> # Extract L and U factors from lu matrix
        >>> k = min(p, q)
        >>> U = numpy.triu(lu[:k, :q])
        >>> L = numpy.tril(lu[:p, :k], -1)
        >>> for i in range(k):
        ...    L[i, i] = 1.0

        >>> # Check if A_copy = PLU holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(A_copy[perm[:p], :q], L @ U, atol=10*atol))
        True

        >>> # When overwrite is set to True, check if lu is indeed a view of A
        >>> numpy.may_share_memory(lu, A)
        True

    In the above example, the object ``mem`` of class :class:`detkit.Memory`
    tracks memory allocation. The peak of allocated memory during the matrix
    multiplication is three orders of magnitude smaller than the size of one
    of the matrices slices, confirming that no new array slice was created
    during the operation.
    """

    if shape is None:
        m, n = A.shape
    elif len(shape) != 2:
        raise ValueError('"shape" should have length of two.')
    else:
        # Use the given shape for an upper-left sub-matrix of the input matrix
        m = shape[0]
        n = shape[1]

        if (m > A.shape[0]) or (n > A.shape[1]):
            raise ValueError('The given "shape" cannot be larger then the ' +
                             'shape of A.')

    # lda is the Leading dimension of A, which is the number of the rows of
    # `A`. This is not the number of rows of the sub-matrix, rather, the number
    # of rows of the actual matrix `A` on the memory.
    lda = A.shape[0]

    # Overwrite or copy
    if overwrite:
        lu = A
    else:
        lu = numpy.copy(A, order='F')

    # Check array has column-ordering
    if lu.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('Array should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Pivot
    k = numpy.min([m, n])
    piv = numpy.empty(k, dtype=numpy.int32)
    cdef int[:] piv_mv = piv
    cdef int* piv_p = &piv_mv[0]

    # Get memoryview of the array
    cdef float[::1, :] A_fp32_f_mv
    cdef double[::1, :] A_fp64_f_mv

    # Get c pointer of the array
    cdef float* A_fp32_p
    cdef double* A_fp64_p

    # dispatch based on floating point precision and order
    if (A.dtype == numpy.float32):
        if lu.flags['F_CONTIGUOUS']:
            A_fp32_f_mv = lu
            A_fp32_p = &A_fp32_f_mv[0, 0]
        else:
            raise ValueError('Array should be "F" contiguous.')

        info = _lu_factor_fp32(A_fp32_p, piv_p, m, n, lda)

    elif (A.dtype == numpy.float64):
        if lu.flags['F_CONTIGUOUS']:
            A_fp64_f_mv = lu
            A_fp64_p = &A_fp64_f_mv[0, 0]
        else:
            raise ValueError('Array should be "F" contiguous.')

        info = _lu_factor_fp64(A_fp64_p, piv_p, m, n, lda)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('LU decomposition failed with error code: %d' % info)

    # Shift to from 1-based indexing (Fortran style) to zero-based indexing
    piv = piv - 1

    # Convert pivoting (of size k) to permutation indices (of size m)
    perm = _pivot_to_permutation(piv, m)

    return lu, perm


# ==============
# lu factor fp32
# ==============

cdef int _lu_factor_fp32(
        float* A,
        int* piv,
        int m,
        int n,
        int lda) noexcept nogil:
    """
    Process float32 precision.
    """

    cdef int info

    with nogil:
        sgetrf(&m, &n, A, &lda, piv, &info)

    return info


# ==============
# lu factor fp64
# ==============

cdef int _lu_factor_fp64(
        double* A,
        int* piv,
        int m,
        int n,
        int lda) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    with nogil:
        dgetrf(&m, &n, A, &lda, piv, &info)

    return info
