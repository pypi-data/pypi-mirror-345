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
from scipy.linalg.cython_blas cimport sgemm, dgemm

__all__ = ['matmul']


# ======
# matmul
# ======

cpdef matmul(
        A,
        B,
        C,
        shape=None,
        trans_a=False,
        trans_b=False,
        alpha=1,
        beta=0,
        overwrite=False):
    """
    Matrix-matrix multiplication for sub-matrices.

    Parameters
    ----------

    A : numpy.ndarray
        A rectangular matrix with either ``float64`` or ``float32`` data type
        stored with column-major ordering.

    A : numpy.ndarray
        A rectangular matrix with either ``float64`` or ``float32`` data type
        stored with column-major ordering.

    B : numpy.ndarray
        A rectangular matrix with either ``float64`` or ``float32`` data type
        stored with row-major or column-major ordering.

    shape : tuple, default=None
        A tuple of size three, determining the shape of an upper-left
        sub-matrices of `A`, `B`, and `C` to be referenced. Namely, if
        ``shape`` is given as the tuple ``(m, n, k)``, then

        * ``m`` is the number of rows of :math:`\\mathrm{op}(\mathbf{A})`.
        * ``n`` is the number of columns of :math:`\\mathrm{op}(\mathbf{A})`,
          which is also the number of rows of :math:`\\mathrm{op}(\mathbf{B})`.
        * ``k`` is the number of columns of :math:`\\mathrm{op}(\mathbf{C})`.

        As such the following sub-matrices are used:
        
        * ``A[:m, :n]`` (or ``A[:n, :m]`` when ``trans_a=True``)
        * ``B[:n, :k]`` (or ``B[:k, :n]`` when ``trans_b=True``)
        * ``C[:m, :k]``
        
        If ``shape`` is `None`, the full shape of ``A[:, :]``,
        ``B[:, :]``, and ``C[:, :]`` are considered provided that their shapes
        are compatible for the matrix product.

    trans_a : bool, default=False
        If `False`, the operator :math:`\\operatorname{op}(\\mathbf{A}) =
        \\mathbf{A}` is used. If `True`, the operator
        :math:`\\operatorname{op}(\\mathbf{A}) = \\mathbf{A}^{\\intercal}` is
        used.

    trans_ab : bool, default=False
        If `False`, the operator :math:`\\operatorname{op}(\\mathbf{B}) =
        \\mathbf{B}` is used. If `True`, the operator
        :math:`\\operatorname{op}(\\mathbf{B}) = \\mathbf{B}^{\\intercal}` is
        used.

    alpha : float, default=1
        The parameter :math:`\\alpha`.

    beta : float, default=0
        The parameter :math:`\\beta`.

    overwrite : bool, default=False
        If `True`, the output `C` is overwritten to the input `C`.

        .. note::

            When ``overwrite`` is set to `True`, the input matrix `C` should
            have column-major (Fortran) ordering.

    Returns
    -------

    C : numpy.ndarray
        A 2D matrix of the same shape as the input matrix `C` (and not the
        shape of the sub-matrix). The upper-left sub-matrix of `C` contains
        the matrix-matrix multiplication corresponding to the sub-matrices
        determined by the ``shape`` argument. If ``overwrite`` is
        set to `True`, the output matrix `C` is becomes a view for the matrix
        `C`.

    See Also
    --------

    detkit.solve_triangular

    References
    ----------

    * `LAPACK <https://www.netlib.org/lapack>`__

    Notes
    -----

    **Matrix-matrix multiplication of sub-matrices:**

    Let :math:`\mathbf{A}_{[:m,:n]}` denote the sub-matrix of the size
    :math:`m \\times n` to be the upper-left corner of matrix
    :math:`\mathbf{A}`. Given matrices :math:`\\mathbf{A}`,
    :math:`\\mathbf{B}`, and :math:`\\mathbf{C}` and parameters :math:`\\alpha`
    and :math:`\\beta`, this function computes

    .. math::

        \\mathbf{X}_{[:m, :k]} =
        \\alpha \\operatorname{op}(\\mathbf{A})_{[:m, :n]}
        \\operatorname{op}(\\mathbf{B})_{[:n, :k]} +
        \\beta \\mathbf{C}_{[:m, :k]},

    if ``overwrite`` is `False`, or

    .. math::

        \\mathbf{C}_{[:m, :k]} \\leftarrow
        \\alpha \\operatorname{op}(\\mathbf{A})_{[:m, :n]}
        \\operatorname{op}(\\mathbf{B})_{[:n, :k]} +
        \\beta \\mathbf{C}_{[:m, :k]},

    if ``overwrite`` is `True`.

    **Interpreting the output matrix:**

    The shape of the output variable `X` is the same as the shape of
    `C`, even if a smaller sub-matrix is considered. Regardless, only the
    corresponding upper-left sub-matrix of `X` has meaningful data. Namely, if
    ``shape=(m, n, k)``, the slice ``X[:m, :k]`` should be considered as the
    result. As such, the relation

        ``X[:m, :k] = alpha * A[:m, :n] @ [:n, :k] + beta * C[:m, :k]``

    or, for instance,
        
        ``X[:m, :k] = alpha * A[:n, :m].T @ [:k, :n].T + beta * C[:m, :k]``

    (when ``trans_a`` and ``trans_b`` are `True`) should hold.

    **Comparison with numpy.matmul:**

    To perfron matrix-matrix multiplication for a sub-matrix of the input
    matrices using ``numpy.matmul`` function (or any other similar matrix
    multiplication functions), you should pass a slice of the matrix to the
    function. This approach is not memory-efficient since the sliced array
    allocates new memory.

    In contrast, using ``detkit.matmul`` together with the ``shape`` argument,
    no memory slice is created during the inner computation, rather, the data
    from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``sgemm`` (for 32-bit
    precision) and ``dgemm`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 34, 35

        >>> from detkit import matmul, Memory
        >>> import numpy
        
        >>> # Create random matrices
        >>> p = 1000
        >>> A = numpy.random.randn(p, p)
        >>> B = numpy.random.randn(p, p)
        >>> C = numpy.random.randn(p, p)

        >>> # Make sure arrays have column-ordering
        >>> A = numpy.asfortranarray(A)
        >>> B = numpy.asfortranarray(B)
        >>> C = numpy.asfortranarray(C)

        >>> # 32-bit precision data
        >>> A = A.astype(numpy.float32)
        >>> B = B.astype(numpy.float32)
        >>> C = C.astype(numpy.float32)

        >>> # Get a copy of C (for the purpose of comparison) since we will
        >>> # overwrite C
        >>> C_copy = numpy.copy(C)

        >>> # Choose size of sub-matrices that are smaller or equal to p
        >>> m, n, k = 900, 800, 700
    
        >>> # Track memory allocation to check if matmul operation is not
        >>> # creating any new memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # Perform matrix-matrix multiplication for sub-matrices
        >>> alpha, beta = numpy.float32(1.0), numpy.float32(2.0)
        >>> X = matmul(A, B, C, shape=(m, n, k), alpha=alpha, beta=beta,
        ...            overwrite=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = m * n * A.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.001

        >>> # Check if alpha * A @ B + beta * C_copy = X holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(alpha * A[:m, :n] @ B[:n, :k] +
        ...                beta * C_copy[:m, :k], X[:m, :k], atol=10*tol))
        True

        >>> # When overwrite is set to True, check if X is indeed a view of C
        >>> numpy.may_share_memory(X, C)
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
    ldc = C.shape[0]

    # Determine the sub-matrix of A and B to be referenced
    if shape is not None:

        if not isinstance(shape, tuple):
            raise ValueError('"shape" should be a tuple.')
        elif len(shape) != 3:
            raise ValueError('"shape" should be a tuple of size three.')

        # Shape of sub-matrices in the product as follows:
        # m is the number of rows of op(A)
        # n is the number of columns of op(A) and number or rows of op(B)
        # k is the number of columns of C
        m, n, k = shape

        # Check m with number of rows of op(A)
        if (((not trans_a) and (m > A.shape[0])) or
            ((trans_a) and (m > A.shape[1]))):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"A".')

        # Check n with number of columns of op(A)
        if (((not trans_a) and (n > A.shape[1])) or
            ((trans_a) and (n > A.shape[0]))):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"A".')

        # Check n with number of rows of op(B)
        if (((not trans_b) and (n > B.shape[0])) or
            ((trans_b) and (n > B.shape[1]))):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

        # Check k with number of columns of op(B)
        if (((not trans_b) and (k > B.shape[1])) or
            ((trans_b) and (k > B.shape[0]))):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

        # Check m and k with number of rows and columns of C
        if (m > C.shape[0]) or (k > C.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"C".')

    else:
        # Number of rows of op(A)
        if trans_a:
            m = A.shape[1]
        else:
            m = A.shape[0]

        # Number of rows of op(B)
        if trans_b:
            n = B.shape[1]
        else:
            n = B.shape[0]

        # Number of columns of op(A)
        k = A.shape[1]

        # Check shape of A and B
        if (((not trans_a) and (not trans_b) and (A.shape[1] != B.shape[0])) or
            ((not trans_a) and (trans_b) and (A.shape[1] != B.shape[1])) or
            ((trans_a) and (not trans_b) and (A.shape[0] != B.shape[0])) or
            ((trans_a) and (trans_b) and (A.shape[0] != B.shape[1]))):
            raise ValueError('Sizes of "op(A)" and "op(B)" do not match.')

        # Check shape of A and C
        if (((not trans_a) and (A.shape[0] != C.shape[0])) or
            ((trans_a) and (A.shape[1] != C.shape[0]))):
            raise ValueError('Sizes of "op(A)" and "C" do not match.')

        # Check shape of B and C
        if (((not trans_b) and (B.shape[1] != C.shape[1])) or
            ((trans_b) and (B.shape[0] != C.shape[1]))):
            raise ValueError('Sizes of "op(B)" and "C" do not match.')

    # Transposition of A
    if trans_a:
        trans_a_ = b'T'
    else:
        trans_a_ = b'N'

    # Transposition of B
    if trans_b:
        trans_b_ = b'T'
    else:
        trans_b_ = b'N'

    # Overwrite or copy
    if overwrite:
        C_ = C
    else:
        C_ = numpy.copy(C, order='F')

    # Check array has column-ordering
    if A.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"A" should be "F" contiguous.')
    if B.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"B" should be "F" contiguous.')
    if C_.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"C" should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Check data type
    if (A.dtype != B.dtype) or (A.dtype != C.dtype):
        raise ValueError('Data type of "A", "B", and "C" should be the same.')

    # Get memoryview of the array
    cdef float[::1, :] A_fp32_f_mv
    cdef float[::1, :] B_fp32_f_mv
    cdef float[::1, :] C_fp32_f_mv
    cdef double[::1, :] A_fp64_f_mv
    cdef double[::1, :] B_fp64_f_mv
    cdef double[::1, :] C_fp64_f_mv

    # Get c pointer of the array
    cdef float* A_fp32_p
    cdef float* B_fp32_p
    cdef float* C_fp32_p
    cdef double* A_fp64_p
    cdef double* B_fp64_p
    cdef double* C_fp64_p

    # dispatch based on floating point precision and order
    if (A.dtype == numpy.float32):

        A_fp32_f_mv = A
        B_fp32_f_mv = B
        C_fp32_f_mv = C_
        A_fp32_p = &A_fp32_f_mv[0, 0]
        B_fp32_p = &B_fp32_f_mv[0, 0]
        C_fp32_p = &C_fp32_f_mv[0, 0]

        _matmul_fp32(A_fp32_p, lda, B_fp32_p, ldb, C_fp32_p, ldc, m, n, k,
                     alpha, beta, trans_a_, trans_b_)

    elif (A.dtype == numpy.float64):

        A_fp64_f_mv = A
        B_fp64_f_mv = B
        C_fp64_f_mv = C_
        A_fp64_p = &A_fp64_f_mv[0, 0]
        B_fp64_p = &B_fp64_f_mv[0, 0]
        C_fp64_p = &C_fp64_f_mv[0, 0]

        _matmul_fp64(A_fp64_p, lda, B_fp64_p, ldb, C_fp64_p, ldc, m, n, k,
                     alpha, beta, trans_a_, trans_b_)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    return C_


# ===========
# matmul fp32
# ===========

cdef void _matmul_fp32(
        float* A,
        int lda,
        float* B,
        int ldb,
        float* C,
        int ldc,
        int m,
        int n,
        int k,
        float alpha,
        float beta,
        char* trans_a,
        char* trans_b) noexcept nogil:
    """
    Process float32 precision.
    """

    with nogil:
        # Note: in sgemm function, the signature accepts (m, k, n) in order,
        # where k is the number of columns of B and C, and n is the number of
        # columns of A and number of rows of B.. That is, to make the correct
        # call to this function, the order should be (m, k, n), and not
        # (m, n, k).
        sgemm(trans_a, trans_b, &m, &k, &n, &alpha, A, &lda, B, &ldb, &beta, C,
              &ldc)


# ===========
# matmul fp64
# ===========

cdef void _matmul_fp64(
        double* A,
        int lda,
        double* B,
        int ldb,
        double* C,
        int ldc,
        int m,
        int n,
        int k,
        double alpha,
        double beta,
        char* trans_a,
        char* trans_b) noexcept nogil:
    """
    Process float64 precision.
    """

    with nogil:
        # Note: in dgemm function, the signature accepts (m, k, n) in order,
        # where k is the number of columns of B and C, and n is the number of
        # columns of A and number of rows of B.. That is, to make the correct
        # call to this function, the order should be (m, k, n), and not
        # (m, n, k).
        dgemm(trans_a, trans_b, &m, &k, &n, &alpha, A, &lda, B, &ldb, &beta, C,
              &ldc)
