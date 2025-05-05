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
from scipy.linalg.cython_lapack cimport strtrs, dtrtrs

__all__ = ['solve_triangular']


# ================
# solve triangular
# ================

cpdef solve_triangular(
        A,
        B,
        shape=None,
        trans=False,
        lower=False,
        unit_diagonal=False,
        overwrite=False):
    """
    Solve triangular linear system given a sub-matrix.

    Parameters
    ----------

    A : numpy.ndarray
        Matrix of coefficients. A triangular matrix with either ``float64`` or
        ``float32`` data type stored with column-major ordering.

    B : numpy.ndarray
        Matrix of the right-hand side. A rectangular matrix with either
        ``float64`` or ``float32`` data type stored with row-major or
        column-major ordering.

    shape : tuple, default=None
        A tuple of size two, determining the shape of an upper-left
        sub-matrices of `A` and `B` to be referenced. Namely, if ``shape`` is
        given as the tuple ``(m, n)``, the sub-matrices ``A[:m, :m]`` and
        ``B[:m, :n]`` are used. If `None`, the full shape of ``A[:, :]`` and
        ``B[:, :]`` are considered.

    trans : bool, default=False
        If `False`, the system :math:`\\mathbf{A} \\mathbf{X} = \\mathbf{B}` is
        solved. If `True`, the system :math:`\\mathbf{A}^{\\intercal}
        \\mathbf{X} = \\mathbf{B}` is solved.

    lower : bool, default=False
        If `True`, `A` is assumed to be lower-triangular. If `False`, `A` is
        assumed to be upper-triangular.

    unit_diagonal : bool, default=False
        If `True`, the diagonals of `A` are assumed to be `1`, even though
        a different value of diagonals are stored on the memory.

    overwrite : bool, default=False
        If `True`, the output `X` is overwritten to `B`, hence, `X` and `B`
        would share the same memory. If `False`, a new memory will be
        allocated for the output `X`.

        .. note::

            When ``overwrite`` is set to `True`, the matrix `B` should have
            column-major (Fortran) ordering.

    Returns
    -------

    X : numpy.ndarray
        A 2D matrix of the same shape as the input matrix `B` (and not the
        shape of the sub-matrix). The upper-left sub-matrix of `B` contains
        the solution to the linear system of equations corresponding to the
        sub-matrices determined by the ``shape`` argument. If ``overwrite`` is
        set to `True`, the output matrix `X` is becomes a view for the matrix
        `B`.

    See Also
    --------

    detkit.lu_factor
    detkit.ldl_solve
    detkit.cho_solve
    detkit.cho_factor
    detkit.lu_factor
    detkit.ldl_factor

    References
    ----------

    * `LAPACK <https://www.netlib.org/lapack>`__

    Notes
    -----

    **Linear system of equations for sub-matrix:**

    Let :math:`\mathbf{B}_{[:m,:n]}` denote the sub-matrix of the size
    :math:`m \\times n` to be the upper-left corner of matrix
    :math:`\mathbf{B}`. Given matrices :math:`\\mathbf{A}` and
    :math:`\\mathbf{B}`, this function solves

    .. math::

        \\mathbf{A}_{[:m, :m]} \\mathbf{X}_{[:m, :n]} = \\mathbf{B}_{[:m, :n]},

    if ``trans`` is `False`, or

    .. math::

        \\mathbf{A}_{[:m, :m]}^{\\intercal} \\mathbf{X}_{[:m, :n]} =
        \\mathbf{B}_{[:m, :n]},

    if ``trans`` is `True`.

    **Interpreting the output matrix:**

    The shape of the output variable `X` is the same as the shape of `B`, even
    if a smaller sub-matrix is considered. Regardless, only the corresponding
    upper-left sub-matrix of `X` has meaningful data. Namely, if
    ``shape=(m, n)``, the slice ``X[:m, :n]`` should be considered as the
    referenced. As such, the relation

        ``A[:m, :m] @ X[:m, :n] = B[:m, :n]``

    or
        
        ``A[:m, :m].T @ X[:m, :n] = B[:m, :n]``

    (when ``trans`` is `True`) should hold.

    **Comparison with scipy.linalg.solve_triangular:**

    To solve a linear system for a sub-matrix of the input matrices using
    ``scipy.linalg.solve_triangular`` function, you should pass a slice of the
    matrix to the function. This approach is not memory-efficient since
    the sliced array allocates new memory.

    In contrast, using ``detkit.solve_triangular`` together with the ``shape``
    argument, no memory slice is created during the inner computation, rather,
    the data from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``strtrs`` (for 32-bit
    precision) and ``dtrtrs`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 28, 29

        >>> from detkit import solve_triangular, Memory
        >>> import numpy
        
        >>> # Create a lower-triangular matrix with 32-bit precision and
        >>> # column-major ordering
        >>> A = numpy.random.randn(1000, 900) + 100 * numpy.eye(1000, 900)
        >>> A = numpy.tril(A)
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Create the matrix of right-hand side
        >>> B = numpy.random.randn(900, 800)
        >>> B = numpy.asfortranarray(B)
        >>> B = B.astype(numpy.float32)

        >>> # Get a copy of B (for the purpose of comparison) since we will
        >>> # overwrite B
        >>> B_copy = numpy.copy(B)

        >>> # Track memory allocation to check if solve_triangular operation is
        >>> # not creating any new memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # Solve the system A X = B for the sub-matrix A[:m, :m] and
        >>> # B[:m, :n]
        >>> m, n = (800, 700)
        >>> X = solve_triangular(A, B, shape=(m, n), lower=True,
        ...                      overwrite=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = m * n * B.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.001

        >>> # Check if A @ X = B_copy holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(A[:m, :m] @ X[:m, :n], B_copy[:m, :n],
        ...                      atol=10*atol))
        True

        >>> # When overwrite is set to True, check if X is indeed a view of B
        >>> numpy.may_share_memory(X, B)
        True
        
    In the above example, the object ``mem`` of class :class:`detkit.Memory`
    tracks memory allocation. The peak of allocated memory during the matrix
    multiplication is three orders of magnitude smaller than the size of one
    of the matrices slices, confirming that no new array slice was created
    during the operation.
    """

    # lda is the Leading dimension of A, which is the number of the rows of
    # `A`. This is not the number of rows of the sub-matrix, rather, the number
    # of rows of the actual matrix `A` on the memory.
    lda = A.shape[0]
    ldb = B.shape[0]

    # Determine the sub-matrix of A and B to be referenced
    if shape is not None:

        if not isinstance(shape, tuple):
            raise ValueError('"shape" should be a tuple.')
        elif len(shape) != 2:
            raise ValueError('"shape" should be a tuple of size two.')

        # Shape of sub-matrix of A is n by n
        n = shape[0]

        if (n > A.shape[0]) or (n > A.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"A".')

        # Shape of sub-matrix of B is n by nrhs (number of right hand sides)
        nrhs = shape[1]

        if (n > B.shape[0]) or (nrhs > B.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

    else:
        if A.shape[0] != A.shape[1]:
            raise ValueError('"A" should be a square matrix.')

        if A.shape[0] != B.shape[0]:
            raise ValueError('Number of rows of "A" and "B" should match.')

        n = A.shape[0]
        nrhs = B.shape[1]

    # A is upper or lower triangular
    if lower:
        uplo = b'L'
    else:
        uplo = b'U'

    # Transposition
    if trans:
        trans_ = b'T'
    else:
        trans_ = b'N'

    # Unit diagonals
    if unit_diagonal:
        unit_diagonal_ = b'U'
    else:
        unit_diagonal_ = b'N'

    # Overwrite or copy
    if overwrite:
        X = B
    else:
        X = numpy.copy(B, order='F')

    # Check arrays have column-ordering
    if A.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"A" should be "F" contiguous.')
    if X.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"B" should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Check data type
    if A.dtype != B.dtype:
        raise ValueError('Data type of "A" and "B" should be the same.')

    # Get memoryview of the array
    cdef float[::1, :] A_fp32_f_mv
    cdef float[::1, :] B_fp32_f_mv
    cdef double[::1, :] A_fp64_f_mv
    cdef double[::1, :] B_fp64_f_mv

    # Get c pointer of the array
    cdef float* A_fp32_p
    cdef float* B_fp32_p
    cdef double* A_fp64_p
    cdef double* B_fp64_p

    # dispatch based on floating point precision and order
    if (A.dtype == numpy.float32):

        A_fp32_f_mv = A
        B_fp32_f_mv = X
        A_fp32_p = &A_fp32_f_mv[0, 0]
        B_fp32_p = &B_fp32_f_mv[0, 0]

        info = _solve_triangular_fp32(A_fp32_p, lda, B_fp32_p, ldb, n, nrhs,
                                      uplo, trans_, unit_diagonal_)

    elif (A.dtype == numpy.float64):

        A_fp64_f_mv = A
        B_fp64_f_mv = X
        A_fp64_p = &A_fp64_f_mv[0, 0]
        B_fp64_p = &B_fp64_f_mv[0, 0]

        info = _solve_triangular_fp64(A_fp64_p, lda, B_fp64_p, ldb, n, nrhs,
                                      uplo, trans_, unit_diagonal_)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('solve triangular failed with error code: %d' % info)

    return X


# =====================
# solve triangular fp32
# =====================

cdef int _solve_triangular_fp32(
        float* A,
        int lda,
        float* B,
        int ldb,
        int n,
        int &nrhs,
        char* uplo,
        char* trans,
        char* diag) noexcept nogil:
    """
    Process float32 precision.
    """

    cdef int info

    with nogil:
        strtrs(uplo, trans, diag, &n, &nrhs, A, &lda, B, &ldb, &info)

    return info


# =====================
# solve triangular fp64
# =====================

cdef int _solve_triangular_fp64(
        double* A,
        int lda,
        double* B,
        int ldb,
        int n,
        int &nrhs,
        char* uplo,
        char* trans,
        char* diag) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    with nogil:
        dtrtrs(uplo, trans, diag, &n, &nrhs, A, &lda, B, &ldb, &info)

    return info
