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
from scipy.linalg.cython_lapack cimport ssytrf, dsytrf
from libc.stdlib cimport malloc, free

__all__ = ['ldl_factor']


# ============
# sanitize piv
# ============

def _sanitize_piv(a, lower=True):
    """
    Taken from ``scipy.linalg.decomp_ldl.py``.

    This helper function takes the rather strangely encoded permutation array
    returned by the LAPACK routines ?(HE/SY)TRF and converts it into
    regularized permutation and diagonal pivot size format.

    Since FORTRAN uses 1-indexing and LAPACK uses different start points for
    upper and lower formats there are certain offsets in the indices used
    below.

    Let's assume a result where the matrix is 6x6 and there are two 2x2
    and two 1x1 blocks reported by the routine. To ease the coding efforts,
    we still populate a 6-sized array and fill zeros as the following ::

        pivots = [2, 0, 2, 0, 1, 1]

    This denotes a diagonal matrix of the form ::

        [x x        ]
        [x x        ]
        [    x x    ]
        [    x x    ]
        [        x  ]
        [          x]

    In other words, we write 2 when the 2x2 block is first encountered and
    automatically write 0 to the next entry and skip the next spin of the
    loop. Thus, a separate counter or array appends to keep track of block
    sizes are avoided. If needed, zeros can be filtered out later without
    losing the block structure.

    Parameters
    ----------

    a : ndarray
        The permutation array ipiv returned by LAPACK

    lower : bool, optional
        The switch to select whether upper or lower triangle is chosen in
        the LAPACK call.

    Returns
    -------

    swap_ : ndarray
        The array that defines the row/column swap operations. For example,
        if row two is swapped with row four, the result is [0, 3, 2, 3].

    pivots : ndarray
        The array that defines the block diagonal structure as given above.

    """

    n = a.size
    swap_ = numpy.arange(n)
    pivots = numpy.zeros_like(swap_, dtype=int)
    skip_2x2 = False

    # Some upper/lower dependent offset values
    # range (s)tart, r(e)nd, r(i)ncrement
    x, y, rs, re, ri = (1, 0, 0, n, 1) if lower else (-1, -1, n-1, -1, -1)

    for ind in range(rs, re, ri):
        # If previous spin belonged already to a 2x2 block
        if skip_2x2:
            skip_2x2 = False
            continue

        cur_val = a[ind]
        # do we have a 1x1 block or not?
        if cur_val > 0:
            if cur_val != ind+1:
                # Index value != array value --> permutation required
                swap_[ind] = swap_[cur_val-1]
            pivots[ind] = 1
        # Not.
        elif cur_val < 0 and cur_val == a[ind+x]:
            # first neg entry of 2x2 block identifier
            if -cur_val != ind+2:
                # Index value != array value --> permutation required
                swap_[ind+x] = swap_[-cur_val-1]
            pivots[ind+y] = 2
            skip_2x2 = True
        else:  # Doesn't make sense, give up
            raise ValueError('While parsing the permutation array '
                             'in "scipy.linalg.ldl", invalid entries '
                             'found. The array syntax is invalid.')
    return swap_, pivots


# ===========
# get d and l
# ===========

def _get_d_and_l(ldu, pivs, lower=True, hermitian=False):
    """
    Taken from ``scipy.linalg.decomp_ldl.py``.

    Helper function to extract the diagonal and triangular matrices for
    LDL.T factorization.

    Parameters
    ----------

    ldu : ndarray
        The compact output returned by the LAPACK routing

    pivs : ndarray
        The sanitized array of {0, 1, 2} denoting the sizes of the pivots. For
        every 2 there is a succeeding 0.

    lower : bool, optional
        If set to False, upper triangular part is considered.

    hermitian : bool, optional
        If set to False a symmetric complex array is assumed.

    Returns
    -------

    d : ndarray
        The block diagonal matrix.

    lu : ndarray
        The upper/lower triangular matrix
    """

    is_c = numpy.iscomplexobj(ldu)
    d = numpy.diag(numpy.diag(ldu))
    n = d.shape[0]
    blk_i = 0  # block index

    # row/column offsets for selecting sub-, super-diagonal
    x, y = (1, 0) if lower else (0, 1)

    lu = numpy.tril(ldu, -1) if lower else numpy.triu(ldu, 1)
    diag_inds = numpy.arange(n)
    lu[diag_inds, diag_inds] = 1

    for blk in pivs[pivs != 0]:
        # increment the block index and check for 2s
        # if 2 then copy the off diagonals depending on uplo
        inc = blk_i + blk

        if blk == 2:
            d[blk_i+x, blk_i+y] = ldu[blk_i+x, blk_i+y]
            # If Hermitian matrix is factorized, the cross-offdiagonal element
            # should be conjugated.
            if is_c and hermitian:
                d[blk_i+y, blk_i+x] = ldu[blk_i+x, blk_i+y].conj()
            else:
                d[blk_i+y, blk_i+x] = ldu[blk_i+x, blk_i+y]

            lu[blk_i+x, blk_i+y] = 0.
        blk_i = inc

    return d, lu


# ====================
# construct tri factor
# ====================

def _construct_tri_factor(lu, swap_vec, pivs, lower=True):
    """
    Taken from ``scipy.linalg.decomp_ldl.py``.

    Helper function to construct explicit outer factors of LDL factorization.

    If lower is True the permuted factors are multiplied as L(1)*L(2)*...*L(k).
    Otherwise, the permuted factors are multiplied as L(k)*...*L(2)*L(1). See
    LAPACK documentation for more details.

    Parameters
    ----------

    lu : ndarray
        The triangular array that is extracted from LAPACK routine call with
        ones on the diagonals.

    swap_vec : ndarray
        The array that defines the row swapping indices. If the kth entry is m
        then rows k,m are swapped. Notice that the mth entry is not necessarily
        k to avoid undoing the swapping.

    pivs : ndarray
        The array that defines the block diagonal structure returned by
        _ldl_sanitize_ipiv().

    lower : bool, optional
        The boolean to switch between lower and upper triangular structure.

    Returns
    -------

    lu : ndarray
        The square outer factor which satisfies the L * D * L.T = A

    perm : ndarray
        The permutation vector that brings the lu to the triangular form

    Notes
    -----

    Note that the original argument "lu" is overwritten.

    """

    n = len(pivs)
    perm = numpy.arange(n)
    # Setup the reading order of the permutation matrix for upper/lower
    rs, re, ri = (n-1, -1, -1) if lower else (0, n, 1)

    for ind in range(rs, re, ri):
        s_ind = swap_vec[ind]
        if s_ind != ind:
            # Column start and end positions
            col_s = ind if lower else 0
            col_e = n if lower else ind+1

            # If we stumble upon a 2x2 block include both cols in the perm.
            if pivs[ind] == (0 if lower else 2):
                col_s += -1 if lower else 0
                col_e += 0 if lower else 1
            lu[[s_ind, ind], col_s:col_e] = lu[[ind, s_ind], col_s:col_e]
            perm[[s_ind, ind]] = perm[[ind, s_ind]]

    return lu, numpy.argsort(perm)


# ==========
# ldl factor
# ==========

cpdef ldl_factor(
        A,
        m=None,
        lower=True,
        overwrite=False,
        return_as_lapack=False):
    """
    LDL decomposition of a sub-matrix.

    Parameters
    ----------

    A : numpy.ndarray
        A symmetric matrix with either ``float64`` or ``float32`` data type
        stored with either row-major or column major ordering.

    m : int, default=None
        An integer determining the shape of an upper-left sub-matrix
        ``A[:m, :m]`` to be considered. If `None`, the full matrix ``A[:, :]``
        is used.

    lower : bool, default=True
        If `True`, `ldu` is assumed to contain the lower-triangular factor
        :math:`\\mathbf{L}` such that :math:`\\mathbf{A} = \\mathbf{L}
        \\mathbf{D} \\mathbf{L}^{\\intercal}`. If `False`, `ldu` is assumed to
        contain the upper-triangular factor :math:`\\mathbf{U}` such that
        :math:`\\mathbf{A} = \\mathbf{U} \\mathbf{D} \\mathbf{U}^{\\intercal}`.

    overwrite : bool, default=False
        If `True`, the input matrix `A` will be overwritten as the output,
        allowing to save memory. In this case, the output matrix `ldu` will
        point to the same location in the memory as the input matrix `A`.

        .. note::

            When ``overwrite`` is set to `True`, the matrix `A` should have
            column-major (Fortran) ordering.

    return_as_lapack : boolean, default=False
        If `True`, the outputs are encoded as given in LAPACK's ``dsytrf``
        function. This format is not intuitively interpretable, but can be
        directly used to pass as input to :func:`detkit.ldl_solve`. If `False`,
        the outputs with LAPACK's encoded format are post-processed to become
        the matrices ``lu`` and ``d`` and array ``perm``, where ``lu`` stores
        the matrix `L` (if ``lower`` is `True) or the matrix `U` (if ``lower``
        is `False`), and ``perm`` is the row/column permutations.

        .. note::
            
            When using ``return_as_lapack=False``, the operation is not
            memory-efficient as new memory will be allocated.

    Returns
    -------

    If ``return_as_lapack`` is `False`:

        lu : numpy.ndarray
            2D array of the same shape as the input matrix `A` (and not the
            shape of the sub-matrix). The upper-left :math:`m \\times m`
            sub-matrix of ``lu`` contains the lower-triangular matrix `L` (if
            ``lower=True``) or the upper-triangular matrix `U` (if
            ``lower=False``).

        d : numpy.array
            2D array of the size of ``m`` containing the diagonal blocks of the
            size 1 by 1 or 2 by 2.

        perm : numpy.array
            The row-permutation index array that brings ``lu[:m, :m]`` into
            triangular form. The size of this array is ``m``.

    If ``return_as_lapack`` is `True`:

        ldu : numpy.ndarray
            2D matrix of the same shape as the input matrix `A` (and not the
            shape of the sub-matrix), containing the LDL decomposition. This
            matrix stores both `L` (or `U`) and `D`, however, the storage
            format of this matrix is not intuitively interpretable.

        piv : numpy.array
            Row pivoting indices (zero-based indexing). The size of this array
            is ``m``.

    See Also
    --------

    detkit.lu_factor
    detkit.cho_factor
    detkit.ldl_solve

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

    **Interpreting L and U factors from the output ldu:**

    Note that the output matrix ``ldu`` is given as the same shape as ``A``,
    and only its upper-left sub-matrix should be used to extract the matrices
    :math:`\\mathbf{L}` and :math:`\\mathbf{U}` as follows.

    Let ``p, q = shape`` be the given shape of the upper-left sub-matrix, which
    may be smaller than the shape of ``A``. Also, let ``k = min(p, q)``. Then,
    ``L = ldu[:p, :k]`` (excluding the diagonals) and ``U = ldu[:k, :q]``.

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

    **Comparison with scipy.linalg.ldl:**

    To compute the LDL factorization of a sub-matrix of the input matrix using
    ``scipy.linalg.ldl`` function, you should pass a slice of the matrix to the
    function. This approach is not memory-efficient since the sliced array
    allocates new memory.

    In contrast, using ``detkit.ldl_factor`` together with the ``m`` argument,
    no memory slice is created during the inner computation, rather,
    the data from the original input matrix is accessed efficiently.

    **Implementation:**

    This function is a wrapper around LAPACK's ``ssytrf`` (for 32-bit
    precision) and ``dsytrf`` (for 64-bit precision).

    This function is internally used for :func:`detkit.memdet` for efficient
    computation of matrix determinant under memory constraint.

    Examples
    --------

    Using ``return_as_lapack=True``:

    .. code-block:: python
        :emphasize-lines: 18, 19

        >>> from detkit import ldl_factor, Memory
        >>> import numpy
        
        >>> # Create a symmetric matrix with 32-bit precision and column-major
        >>> # ordering
        >>> A = numpy.random.randn(1000, 1000)
        >>> A = A + A.T + 100 * numpy.eye(1000, 1000)
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Track memory allocation to check if LDL decomposition is not
        >>> # creating any new memory.
        >>> mem = Memory()
        >>> mem.set()

        >>> # LDL factorization of the upper-left sub-matrix of smaller shape
        >>> m = 800
        >>> ldu, piv = ldl_factor(A, m=800, overwrite=True,
        ...                       return_as_lapack=True)

        >>> # Check peak memory allocation (compared to memory of a sum-matrix)
        >>> slice_nbytes = m * m * A.dtype.itemsize
        >>> print(mem.peak() / slice_nbytes)
        0.026

        >>> # When overwrite is set to True, check if ldu is indeed a view of A
        >>> numpy.may_share_memory(ldu, A)
        True

    In the above example, the object ``mem`` of class :class:`detkit.Memory`
    tracks memory allocation. The peak of allocated memory during the matrix
    factorization is two orders of magnitude smaller than the size of one
    of the matrices slices, confirming that no new array slice was created
    during the operation.

    Repeating the above example, but using ``return_as_lapack=True``:

    .. code-block:: python
        :emphasize-lines: 17, 18

        >>> from detkit import ldl_factor
        >>> import numpy
        
        >>> # Create a symmetric matrix with 32-bit precision and column-major
        >>> # ordering
        >>> A = numpy.random.randn(1000, 1000)
        >>> A = A + A.T + 100 * numpy.eye(1000, 1000)
        >>> A = numpy.asfortranarray(A)
        >>> A = A.astype(numpy.float32)

        >>> # Get a copy of A (for the purpose of comparison) since we will
        >>> # overwrite A
        >>> A_copy = numpy.copy(A)

        >>> # LU factorization of the upper-left sub-matrix of smaller shape
        >>> m = 800
        >>> lu, d, perm = ldl_factor(A, m=m, overwrite=False,
        ...                          return_as_lapack=False)

        >>> # Check if A = LDLt holds.
        >>> atol = numpy.finfo(A.dtype).resolution
        >>> print(numpy.allclose(lu[:m, :m] @ d[:m, :m] @ lu[:m, :m].T,
        ...                      A[:m, :m], atol=10*atol))
        True
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
        ldu = A
    else:
        ldu = numpy.copy(A, order='F')

    piv = numpy.empty(m, dtype=numpy.int32)
    cdef int[:] piv_mv = piv
    cdef int* piv_p = &piv_mv[0]

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
        if ldu.flags['C_CONTIGUOUS']:
            A_fp32_c_mv = ldu
            A_fp32_p = &A_fp32_c_mv[0, 0]
            lda = A.shape[1]
        elif ldu.flags['F_CONTIGUOUS']:
            A_fp32_f_mv = ldu
            A_fp32_p = &A_fp32_f_mv[0, 0]
            lda = A.shape[0]
        else:
            raise ValueError('Array should be either "C" or "F" contiguous.')

        info = _ldl_factor_fp32(A_fp32_p, lda, piv_p, m, uplo)

    elif (A.dtype == numpy.float64):
        # Treat C and F contiguous the same as it is assumed array is symmetric
        if ldu.flags['C_CONTIGUOUS']:
            A_fp64_c_mv = ldu
            A_fp64_p = &A_fp64_c_mv[0, 0]
            lda = A.shape[1]
        elif ldu.flags['F_CONTIGUOUS']:
            A_fp64_f_mv = ldu
            A_fp64_p = &A_fp64_f_mv[0, 0]
            lda = A.shape[0]
        else:
            raise ValueError('Array should be either "C" or "F" contiguous.')

        info = _ldl_factor_fp64(A_fp64_p, lda, piv_p, m, uplo)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('LDL decomposition failed with error code: %d' % info)

    if return_as_lapack:
        # Convert from 1-based indexing (Fortran style) to zero-based indexing
        piv = piv - 1

        return ldu, piv
    else:

        swap_arr, pivot_arr = _sanitize_piv(piv, lower=lower)
        d, lu = _get_d_and_l(ldu, pivot_arr, lower=lower, hermitian=False)
        lu, perm = _construct_tri_factor(lu, swap_arr, pivot_arr, lower=lower)

        return lu, d, perm


# ===============
# ldl factor fp32
# ===============

cdef int _ldl_factor_fp32(
        float* A,
        int lda,
        int* piv,
        int m,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info
    cdef float* work = <float*> malloc(1 * sizeof(float))
    cdef int lwork = -1  # query optimal workspace size

    # Query optimal workspace
    with nogil:
        ssytrf(uplo, &m, A, &lda, piv, work, &lwork, &info)

    # Get actual size of work that is needed
    lwork = int(work[0])

    # Allocate work with actual size
    free(work)
    work = <float*> malloc(lwork * sizeof(float))

    # Perform actual decomposition
    with nogil:
        ssytrf(uplo, &m, A, &lda, piv, work, &lwork, &info)

    free(work)

    return info


# ===============
# ldl factor fp64
# ===============

cdef int _ldl_factor_fp64(
        double* A,
        int lda,
        int* piv,
        int m,
        char* uplo) noexcept nogil:
    """
    Process float64 precision.
    """

    cdef int info
    cdef double* work = <double*> malloc(1 * sizeof(double))
    cdef int lwork = -1  # query optimal workspace size

    # Query optimal workspace
    with nogil:
        dsytrf(uplo, &m, A, &lda, piv, work, &lwork, &info)

    # Get actual size of work that is needed
    if info == 0:
        lwork = int(work[0])
    else:
        return info

    # Allocate work with actual size
    free(work)
    work = <double*> malloc(lwork * sizeof(double))

    # Perform actual decomposition
    with nogil:
        dsytrf(uplo, &m, A, &lda, piv, work, &lwork, &info)

    free(work)

    return info
