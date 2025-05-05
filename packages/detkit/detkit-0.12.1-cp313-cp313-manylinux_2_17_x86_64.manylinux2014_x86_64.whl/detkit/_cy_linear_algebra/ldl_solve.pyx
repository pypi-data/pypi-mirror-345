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
from scipy.linalg.cython_lapack cimport ssytrs, dsytrs

__all__ = ['ldl_solve']



# =========
# ldl solve
# =========

cpdef ldl_solve(ldu, piv, B, shape=None, lower=True, overwrite=False):
    """
    Solve symmetric positive-definite linear system given a sub-matrix of
    LDL decomposition.

    Parameters
    ----------

    ldu : numpy.ndarray
        The LDL decomposing of a symmetric matrix with either ``float64`` or
        ``float32`` data type stored column-major ordering. This matrix can
        be obtained from :func:`detkit.ldl_factor`.

    piv : numpy.array
        Row pivoting indices (zero-based indexing). This array can be
        obtained from :func:`detkit.ldl_factor`.

    B : numpy.ndarray
        Matrix of the right-hand side. A rectangular matrix with either
        ``float64`` or ``float32`` data type stored with row-major or
        column-major ordering. However, if ``overwrite=True``, then ``B``
        should have column-major ordering only.

    shape : tuple, default=None
        A tuple of size two, determining the shape of an upper-left
        sub-matrices of `ldu` and ``B`` to be referenced. Namely, if ``shape``
        is given as the tuple ``(m, n)``, the sub-matrices ``ldu[:m, :m]`` and
        ``B[:m, :n]`` are used. If `None`, the full shape of ``ldu[:, :]`` and
        ``B[:, :]`` are considered.

    lower : bool, default=True
        If `True`, ``ldu`` is assumed to contain the lower-triangular LDL
        factor :math:`\\mathbf{L}` such that :math:`\\mathbf{A} = \\mathbf{L}
        \\mathbf{D} \\mathbf{L}^{\\intercal}`. If `False`, ``ldu`` is assumed
        to contain the upper-triangular LDL factor :math:`\\mathbf{U}` such
        that
        :math:`\\mathbf{A} = \\mathbf{U} \\mathbf{D} \\mathbf{U}^{\\intercal}`.

    overwrite : bool, default=False
        If `True`, the input matrix ``B`` will be overwritten as the output,
        allowing to save memory. In this case, the output matrix ``X`` will
        point to the same location in the memory as the input matrix ``B``.

        .. note::

            When ``overwrite`` is set to `True`, the matrix `B` should have
            column-major (Fortran) ordering.

    Returns
    -------

    X : numpy.ndarray
        A 2D matrix of the same shape as the input matrix ``B`` (and not the
        shape of the sub-matrix). The upper-left sub-matrix of ``B`` contains
        the solution to the linear system of equations corresponding to the
        sub-matrices determined by the ``shape`` argument. If ``overwrite`` is
        set to `True`, the output matrix ``X`` is becomes a view for the matrix
        ``B``.

    See Also
    --------

    detkit.ldl_factor
    detkit.lu_solve
    detkit.cho_solve

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

        \\mathbf{A}_{[:m, :m]} \\mathbf{X}_{[:m, :n]} = \\mathbf{B}_{[:m, :n]}.

    **LDL Factor Input Argument:**

    The input to this function is the LDL factor of :math:`\\mathbf{A}` (
    and not :math:`\\mathbf{A}` itself). Namely, if ``lower=True``, it is
    assumed that the input argument ``ldu`` is the factor
    :math:`\\mathbf{L} \\mathbf{D} \\mathbf{L}^{\\intercal}`
    where

    .. math::

        \\mathbf{A}_{[:m, :m]} =
        \\mathbf{P}_{[:m, :m]}
        \\mathbf{L}_{[:m, :m]}
        \\mathbf{D}_{[:m, :m]} \\mathbf{L}_{[:m, :m]}^{\\intercal}
        \\mathbf{P}_{[:m, :m]}^{\\intercal}.

    Similarly, if ``lower=False``, it is assumed that the input argument
    ``ldu`` is the factor :math:`\\mathbf{U} \\mathbf{D}
    \\mathbf{U}^{\\intercal}` where

    .. math::

        \\mathbf{A}_{:m, :m} = 
        \\mathbf{P}_{[:m, :m]} \\mathbf{U}_{[:m, :m]}
        \\mathbf{D}_{[:m, :m]} \\mathbf{U}_{[:m, :m]}^{\\intercal}
        \\mathbf{P}_{[:m, :m]}^{\\intercal}.

    The shape of ``ldu`` can be larger than the shape of the :math:`m \\times
    m` sub-matrix, however, its upper-left :math:`m  \\times m` sub-matrix will
    be referenced during the computation.

    The LDL factor of a matrix can be obtained from :func:`detkit.ldl_factor`
    and its output can be passed to the parameters ``ldu`` and ``piv`` in
    :func:`detkit.ldl_solve`.

    .. note::

        When computing LDL decomposition with :func:`detkit.ldl_factor` to
        be used for :func:`detkit.ldl_solve`, set the argument
        ``return_as_lapack=True`` in :func:`detkit.ldl_factor`.

    **Interpreting the output matrix:**

    The shape of the output variable `X` is the same as the shape of `B`, even
    if a smaller sub-matrix is considered. Regardless, only the corresponding
    upper-left sub-matrix of `X` has meaningful data. Namely, if
    ``shape=(m, n)``, the slice ``X[:m, :n]`` should be considered as the
    referenced. As such, the following relation should hold:

        ``A[:m, :m] @ X[:m, :n] = B[:m, :n]``

    **Comparison with scipy:**

    Scipy does not provide a similar function.

    **Implementation:**

    This function is a wrapper around LAPACK's ``sgetrf`` (for 32-bit
    precision) and ``dgetrf`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 33, 34

        >>> from detkit import ldl_factor, ldl_solve, Memory
        >>> import numpy
        
        >>> # Create a symmetric matrix with 32-bit precision and column-major
        >>> # ordering
        >>> A = numpy.random.randn(1000, 1000) + 100 * numpy.eye(1000, 1000)
        >>> A = A + A.T
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Matrix of the right-hand side
        >>> B = numpy.random.randn(1000, 2000)
        >>> B = numpy.asfortranarray(B)
        >>> B = B.astype(numpy.float32)

        >>> # Get a copy of A and B (for the purpose of comparison) since we
        >>> # will overwrite A and B
        >>> A_copy = numpy.copy(A)
        >>> B_copy = numpy.copy(B)

        >>> # Track memory allocation to check if either of the LDL
        >>> # decomposition or solving linear system is now creating any new
        >>> # memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # LDL factorization of the upper-left sub-matrix
        >>> p, q = 800, 700
        >>> ldu, piv = ldl_factor(A, m=p, lower=True, overwrite=True,
        ...                       return_as_lapack=True)

        >>> # Solve a linear system
        >>> X = ldl_solve(ldu, piv, B, shape=(p, q), lower=True,
        ...               overwrite=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = p * q * B.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.001

        >>> # Check if A_copy @ X = B_copy holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(A_copy[:p, :p] @ X[:p, :q], B_copy[:p, :q],
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

    # Determine the sub-matrix of ldu and B to be referenced
    if shape is not None:

        if not isinstance(shape, tuple):
            raise ValueError('"shape" should be a tuple.')
        elif len(shape) != 2:
            raise ValueError('"shape" should be a tuple of size two.')

        # Shape of sub-matrix of ldu is n by n
        n = shape[0]

        if (n > ldu.shape[0]) or (n > ldu.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"ldu".')

        # Shape of sub-matrix of B is n by nrhs (number of right hand sides)
        nrhs = shape[1]

        if (n > B.shape[0]) or (nrhs > B.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

    else:
        if ldu.shape[0] != ldu.shape[1]:
            raise ValueError('"ldu" should be a square matrix.')

        if ldu.shape[0] != B.shape[0]:
            raise ValueError('Number of rows of "ldu" and "B" should match.')

        n = ldu.shape[0]
        nrhs = B.shape[1]
        
    # ldu is upper or lower triangle factor
    if lower:
        uplo = b'L'
    else:
        uplo = b'U'

    # Overwrite to B or create new array
    if overwrite:
        X = B
    else:
        X = numpy.copy(B, order='F')

    # Check ldu has column-ordering.
    if ldu.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"ldu" should be "F" contiguous.')

    # Check X has column-ordering.
    if X.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"B" should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Shift pivots from 0-based indexing to 1-based indexing (Fortran style)
    piv = piv + 1

    # Get pivot pointer
    cdef int[:] piv_mv = piv
    cdef int* piv_p = &piv_mv[0]

    cdef float[::1, :] A_fp32_f_mv
    cdef float[::1, :] B_fp32_f_mv
    cdef double[::1, :] A_fp64_f_mv
    cdef double[::1, :] B_fp64_f_mv

    cdef float* A_fp32_p
    cdef float* B_fp32_p
    cdef double* A_fp64_p
    cdef double* B_fp64_p
    cdef int info

    # dispatch based on floating point precision and order
    if (ldu.dtype == numpy.float32):

        # Get pointer to ldu
        if ldu.flags['F_CONTIGUOUS']:
            A_fp32_f_mv = ldu
            A_fp32_p = &A_fp32_f_mv[0, 0]
            lda = ldu.shape[0]
        else:
            raise ValueError('Array should be "F" contiguous.')

        # Get pointer to B
        if X.flags['F_CONTIGUOUS']:
            B_fp32_f_mv = X
            B_fp32_p = &B_fp32_f_mv[0, 0]
            ldb = X.shape[0]
        else:
            raise ValueError('"B" should be "F" contiguous. Alternatively, ' +
                             'set "overwrite" to "True".')

        info = _ldl_solve_fp32(A_fp32_p, lda, piv_p, B_fp32_p, ldb, n, nrhs,
                               uplo)

    elif (ldu.dtype == numpy.float64):

        # Get pointer to ldu
        if ldu.flags['F_CONTIGUOUS']:
            A_fp64_f_mv = ldu
            A_fp64_p = &A_fp64_f_mv[0, 0]
            lda = ldu.shape[0]
        else:
            raise ValueError('Array should be "F" contiguous.')

        # Get pointer to B
        if X.flags['F_CONTIGUOUS']:
            B_fp64_f_mv = X
            B_fp64_p = &B_fp64_f_mv[0, 0]
            ldb = X.shape[0]
        else:
            raise ValueError('"B" should be "F" contiguous. Alternatively, ' +
                             'set "overwrite" to "True".')

        info = _ldl_solve_fp64(A_fp64_p, lda, piv_p, B_fp64_p, ldb, n, nrhs,
                               uplo)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('LDL decomposition failed with error code: %d' % info)

    return X


# ==============
# ldl solve fp32
# ==============

cdef int _ldl_solve_fp32(
        float* ldu,
        int lda,
        int* piv,
        float* B,
        int ldb,
        int n,
        int nrhs,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        ssytrs(uplo, &n, &nrhs, ldu, &lda, piv, B, &ldb, &info)

    return info


# ==============
# ldl solve fp64
# ==============

cdef int _ldl_solve_fp64(
        double* ldu,
        int lda,
        int* piv,
        double* B,
        int ldb,
        int n,
        int nrhs,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        dsytrs(uplo, &n, &nrhs, ldu, &lda, piv, B, &ldb, &info)

    return info
