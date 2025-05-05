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
from scipy.linalg.cython_lapack cimport spotrf, dpotrf

__all__ = ['cho_factor']



# ==========
# cho factor
# ==========

cpdef cho_factor(A, m=None, lower=True, overwrite=False):
    """
    Cholesky decomposition of a sub-matrix.

    Parameters
    ----------

    A : numpy.ndarray
        A symmetric positive-definite matrix with either ``float64`` or
        ``float32`` data type stored with either row-major or column major
        ordering.

    m : int, default=None
        An integer determining the shape of an upper-left sub-matrix the
        ``A[:m, :m]`` to be considered. If `None`, the full matrix ``A[:, :]``
        is used.

    lower : bool, default=True
        If `True`, `cho` is assumed to be a lower-triangular Cholesky factor
        :math:`\\mathbf{L}` such that :math:`\\mathbf{A} = \\mathbf{L}
        \\mathbf{L}^{\\intercal}`. If `False`, `cho` is assumed to be an
        upper-triangular Cholesky factor :math:`\\mathbf{U}` such that
        :math:`\\mathbf{A} = \\mathbf{U}^{\\intercal} \\mathbf{U}`.

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
        the Cholesky factor of the sub-matrix of `A`. Namely, the upper or
        lower triangular parts of the sub-matrix of `lu` consist  of the
        matrix `L` (if ``lower=true``) or `U` (if ``lower=False``) matrix.
        If ``overwrite`` is set to `True`, the output matrix `lu` is becomes a
        view for the matrix `A`.

    See Also
    --------

    detkit.ldl_factor
    detkit.lu_factor
    detkit.cho_solve

    References
    ----------

    * `LAPACK <https://www.netlib.org/lapack>`__

    Notes
    -----

    **Cholesky decomposition of sub-matrix:**

    Let :math:`\mathbf{A}_{[:p,:p]}` denote the sub-matrix of the size
    :math:`p \\times p` to be the upper-left corner of matrix
    :math:`\mathbf{A}`. Its Cholesky decomposition is given by:

    .. math::

        \\mathbf{A}_{[:p, :p]} = \\mathbf{L} \\mathbf{L}^{\\intercal},

    or

    .. math::

        \\mathbf{A}_{[:p, :p]} = \\mathbf{U}^{\\intercal} \\mathbf{U},

    where :math:`\\mathbf{L}` is a lower-triangular matrix of
    the size :math:`p \\times p` and :math:`\\mathbf{U}` is an upper-triangular
    matrix of the size :math:`p \\times p`.

    **Interpreting L or U factors from the output cho:**

    Note that the output matrix ``cho`` is given as the same shape as ``A``,
    and only its upper-left sub-matrix should be used to extract the matrices
    :math:`\\mathbf{L}` and :math:`\\mathbf{U}` as follows.

    Let ``p, p = shape`` be the given shape of the upper-left sub-matrix, which
    may be smaller than the shape of ``A``. Then, ``L = cho[:p, :p]``
    and ``U = cho[:p, :p]``.

    **Comparison with scipy.linalg.cho_factor:**

    To compute the Cholesky factorization of a sub-matrix of the input matrix
    using ``scipy.linalg.cho_factor`` function, you should pass a slice of the
    matrix to the function. This approach is not memory-efficient since
    the sliced array allocates new memory.

    In contrast, using ``detkit.cho_factor`` together with the ``shape``
    argument, no memory slice is created during the inner computation, rather,
    the data from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``spotrf`` (for 32-bit
    precision) and ``dpotrf`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 24

        >>> from detkit import cho_factor, Memory
        >>> import numpy
        
        >>> # Create a symmetrc positive-definite matrix with 32-bit precision
        >>> # and column-major ordering
        >>> n = 1000
        >>> A = numpy.random.randn(n, n) + 2*n * numpy.eye(n, n)
        >>> A = A.T @ A
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Get a copy of A (for the purpose of comparison) since we will
        >>> # overwrite A
        >>> A_copy = numpy.copy(A)

        >>> # Track memory allocation to check if Chplesky decomposition is not
        >>> # creating any new memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # Choleksy factorization of the upper-left sub-matrix with a
        >>> # smaller shape
        >>> m = 800
        >>> cho = cho_factor(A, m=m, lower=True, overwrite=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = m**2 * A.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.004

        >>> # Extract L factor from cho matrix
        >>> L = numpy.tril(cho[:m, :m])

        >>> # Check if A_copy = L@L.T holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(A_copy[:m, :m], L @ L.T, atol=10*atol))
        True

        >>> # When overwrite is set to True, check if cho is indeed a view of A
        >>> numpy.may_share_memory(cho, A)
        True

    In the above example, the object ``mem`` of class :class:`detkit.Memory`
    tracks memory allocation. The peak of allocated memory during the matrix
    multiplication is three orders of magnitude smaller than the size of one
    of the matrices slices, confirming that no new array slice was created
    during the operation.
    """

    # Size of sub-matrix
    if m is None:
        if A.shape[0] != A.shape[1]:
            raise ValueError('Matrix should be square.')
        m = A.shape[0]
    else:
        if (m > A.shape[0]) or (m > A.shape[1]):
            raise ValueError('Sub-matrix size "m" is larger than matrix size.')
        
    # A is upper or lower triangular
    if lower:
        uplo = b'L'
    else:
        uplo = b'U'

    # Overwrite to A or create new array
    if overwrite:
        cho = A
    else:
        cho = numpy.copy(A, order='F')

    cdef float[:, ::1] A_fp32_c_mv
    cdef float[::1, :] A_fp32_f_mv
    cdef double[:, ::1] A_fp64_c_mv
    cdef double[::1, :] A_fp64_f_mv

    cdef float* A_fp32_p
    cdef double* A_fp64_p
    cdef int info

    # dispatch based on floating point precision and order
    if (A.dtype == numpy.float32):
        # Treat C and F contiguous the same as it is assumed array is symmetric
        if cho.flags['C_CONTIGUOUS']:
            A_fp32_c_mv = cho
            A_fp32_p = &A_fp32_c_mv[0, 0]
            lda = A.shape[1]
        elif cho.flags['F_CONTIGUOUS']:
            A_fp32_f_mv = cho
            A_fp32_p = &A_fp32_f_mv[0, 0]
            lda = A.shape[0]
        else:
            raise ValueError('Array should be either "C" or "F" contiguous.')

        info = _cho_factor_fp32(A_fp32_p, lda, m, uplo)

    elif (A.dtype == numpy.float64):
        # Treat C and F contiguous the same as it is assumed array is symmetric
        if cho.flags['C_CONTIGUOUS']:
            A_fp64_c_mv = cho
            A_fp64_p = &A_fp64_c_mv[0, 0]
            lda = A.shape[1]
        elif cho.flags['F_CONTIGUOUS']:
            A_fp64_f_mv = cho
            A_fp64_p = &A_fp64_f_mv[0, 0]
            lda = A.shape[0]
        else:
            raise ValueError('Array should be either "C" or "F" contiguous.')

        info = _cho_factor_fp64(A_fp64_p, lda, m, uplo)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('Cholesky decomposition failed with error code: %d'
                         % info)

    return cho


# ===============
# cho factor fp32
# ===============

cdef int _cho_factor_fp32(
        float* A,
        int lda,
        int m,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        spotrf(uplo, &m, A, &lda, &info)

    return info


# ===============
# cho factor fp64
# ===============

cdef int _cho_factor_fp64(
        double* A,
        int lda,
        int m,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        dpotrf(uplo, &m, A, &lda, &info)

    return info
