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
from scipy.linalg.cython_lapack cimport sgetrs, dgetrs

__all__ = ['lu_solve']



# ====================
# permutation to pivot
# ====================

def _permutation_to_pivot(perm):
    """
    Convert permutation back to pivot.
    """

    n = len(perm)
    piv = numpy.arange(n, dtype=numpy.int32)

    for i in range(n):
        # Find the index in perm that was originally swapped with i
        for j in range(i, n):
            if perm[j] == i:
                piv[i], piv[j] = piv[j], piv[i]
                perm[i], perm[j] = perm[j], perm[i]
                break

    return piv


# ========
# lu solve
# ========

cpdef lu_solve(lu, perm, B, shape=None, trans=False, overwrite=False):
    """
    Solve linear system given a sub-matrix output of LU decomposition.

    Parameters
    ----------

    lu : numpy.ndarray
        The LU decomposing of a matrix with either ``float64`` or ``float32``
        data type stored column-major ordering. This matrix can be obtained
        from :func:`detkit.lu_factor`.

    perm : numpy.array
        Permutation indices of row pivoting (zero-based indexing). This array
        can be obtained from :func:`detkit.lu_factor`.

    B : numpy.ndarray
        Matrix of the right-hand side. A rectangular matrix with either
        ``float64`` or ``float32`` data type stored with row-major or
        column-major ordering. However, if ``overwrite=True``, then ``B``
        should have column-major ordering only.

    shape : tuple, default=None
        A tuple of size two, determining the shape of an upper-left
        sub-matrices of ``lu`` and ``B`` to be referenced. Namely, if ``shape``
        is given as the tuple ``(m, n)``, the sub-matrices ``lu[:m, :m]`` and
        ``B[:m, :n]`` are used. If `None`, the full shape of ``lu[:, :]`` and
        ``B[:, :]`` are considered.

    trans : boolean, default=False
        If `True`, the system :math:`\\mathbf{A} \\mathbf{X} = \\mathbf{B}` is
        solved. If `False`, the system :math:`\\mathbf{A}^{\\intercal}
        \\mathbf{X} = \\mathbf{B}` is solved.

    overwrite : bool, default=False
        If `True`, the input matrix ``B`` will be overwritten as the output,
        allowing to save memory. In this case, the output matrix ``X`` will
        point to the same location in the memory as the input matrix ``B``.

        .. note::

            When ``overwrite`` is set to `True`, the matrix ``B`` should have
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

    detkit.lu_factor
    detkit.ldl_solve
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

        \\mathbf{A}_{[:m, :m]} \\mathbf{X}_{[:m, :n]} = \\mathbf{B}_{[:m, :n]},

    if ``trans`` is `False`, or

    .. math::

        \\mathbf{A}_{[:m, :m]}^{\\intercal} \\mathbf{X}_{[:m, :n]} =
        \\mathbf{B}_{[:m, :n]},

    if ``trans`` is `True`.

    **LU Factor Input Argument:**

    The input to this function is the LU factor of :math:`\\mathbf{A}` (
    and not :math:`\\mathbf{A}` itself). Namely, 

    .. math::

        \\mathbf{A}_{[:m, :m]} = \\mathbf{P}_{:m, :m} \\mathbf{L}_{[:m, :m]}
        \\mathbf{U}_{[:m, :m]}.

    The shape of ``lu`` can be larger than the shape of the :math:`m \\times
    m` sub-matrix, however, its upper-left :math:`m  \\times m` sub-matrix will
    be referenced during the computation.

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


    **Comparison with scipy.linalg.lu_solve:**

    To solve a linear system for a sub-matrix of the input matrices using
    ``scipy.linalg.lu_solve`` function, you should pass a slice of the
    matrix to the function. This approach is not memory-efficient since
    the sliced array allocates new memory.

    In contrast, using ``detkit.lu_solve`` together with the ``shape``
    argument, no memory slice is created during the inner computation, rather,
    the data from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``sgetrs`` (for 32-bit
    precision) and ``dgetrs`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 30, 31

        >>> from detkit import lu_factor, lu_solve, Memory
        >>> import numpy
        
        >>> # Create a matrix with 32-bit precision and column-major ordering
        >>> A = numpy.random.randn(1000, 900) + 100 * numpy.eye(1000, 900)
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

        >>> # Track memory allocation to check if either of the LU
        >>> # decomposition or solving linear system is now creating any new
        >>> # memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # LU factorization of the upper-left sub-matrix
        >>> p, q = 800, 700
        >>> lu, perm = lu_factor(A, shape=(p, p), overwrite=True)

        >>> # Solve a linear system
        >>> X = lu_solve(lu, perm, B, shape=(p, q), trans=False,
        ...              overwrite=True)

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

    # Determine the sub-matrix of lu and B to be referenced
    if shape is not None:

        if not isinstance(shape, tuple):
            raise ValueError('"shape" should be a tuple.')
        elif len(shape) != 2:
            raise ValueError('"shape" should be a tuple of size two.')

        # Shape of sub-matrix of lu is n by n
        n = shape[0]

        if (n > lu.shape[0]) or (n > lu.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"lu".')

        # Shape of sub-matrix of B is n by nrhs (number of right hand sides)
        nrhs = shape[1]

        if (n > B.shape[0]) or (nrhs > B.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

    else:
        if lu.shape[0] != lu.shape[1]:
            raise ValueError('"lu" should be a square matrix.')

        if lu.shape[0] != B.shape[0]:
            raise ValueError('Number of rows of "lu" and "B" should match.')

        n = lu.shape[0]
        nrhs = B.shape[1]

    # Check perm size
    if perm.size != n:
        raise ValueError('The size of "perm" should equal the number of ' +
                         'rows of sub-matrix.')
        
    #  Transposition operator
    if trans:
        trans = b'T'
    else:
        trans = b'N'

    # Overwrite to B or create new array
    if overwrite:
        X = B
    else:
        X = numpy.copy(B, order='F')

    # Check lu has column-ordering.
    if lu.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"lu" should be "F" contiguous.')

    # Check X has column-ordering.
    if X.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"B" should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Convert permutation to pivots
    piv = _permutation_to_pivot(perm)

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
    if (lu.dtype == numpy.float32):

        # Get pointer to lu
        if lu.flags['F_CONTIGUOUS']:
            A_fp32_f_mv = lu
            A_fp32_p = &A_fp32_f_mv[0, 0]
            lda = lu.shape[0]
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

        info = _lu_solve_fp32(A_fp32_p, lda, piv_p, B_fp32_p, ldb, n, nrhs,
                              trans)

    elif (lu.dtype == numpy.float64):

        # Get pointer to lu
        if lu.flags['F_CONTIGUOUS']:
            A_fp64_f_mv = lu
            A_fp64_p = &A_fp64_f_mv[0, 0]
            lda = lu.shape[0]
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

        info = _lu_solve_fp64(A_fp64_p, lda, piv_p, B_fp64_p, ldb, n, nrhs,
                              trans)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('LU decomposition failed with error code: %d' % info)

    return X


# =============
# lu solve fp32
# =============

cdef int _lu_solve_fp32(
        float* lu,
        int lda,
        int* piv,
        float* B,
        int ldb,
        int n,
        int nrhs,
        char* trans) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        sgetrs(trans, &n, &nrhs, lu, &lda, piv, B, &ldb, &info)

    return info


# =============
# lu solve fp64
# =============

cdef int _lu_solve_fp64(
        double* lu,
        int lda,
        int* piv,
        double* B,
        int ldb,
        int n,
        int nrhs,
        char* trans) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info

    # decomposition
    with nogil:
        dgetrs(trans, &n, &nrhs, lu, &lda, piv, B, &ldb, &info)

    return info
