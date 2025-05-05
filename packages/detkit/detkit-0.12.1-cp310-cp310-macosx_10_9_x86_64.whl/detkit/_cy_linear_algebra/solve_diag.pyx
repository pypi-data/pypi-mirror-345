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
from cython.parallel cimport parallel, prange
from .._openmp import get_avail_num_threads
from .._openmp cimport cond_omp_set_num_threads

__all__ = ['solve_diag']



# ==========
# solve diag
# ==========

cpdef solve_diag(D, B, shape=None, overwrite=False):
    """
    """

    # Determine the sub-matrix of D and B to be referenced
    if shape is not None:

        if not isinstance(shape, tuple):
            raise ValueError('"shape" should be a tuple.')
        elif len(shape) != 2:
            raise ValueError('"shape" should be a tuple of size two.')

        # Shape of sub-matrix of D is n by 2
        n = shape[0]

        if n > D.shape[0]:
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"D".')

        if D.shape[1] != 2:
            raise ValueError('"D" should only have two columns.')

        # Shape of sub-matrix of B is n by nrhs (number of right hand sides)
        nrhs = shape[1]

        if (n > B.shape[0]) or (nrhs > B.shape[1]):
            raise ValueError('The given "shape" is larger than the shape of ' +
                             '"B".')

    else:
        if D.shape[1] != 2:
            raise ValueError('"D" should have two columns.')

        if D.shape[0] != B.shape[0]:
            raise ValueError('Number of rows of "D" and "B" should match.')

        n = D.shape[0]
        nrhs = B.shape[1]

    # Overwrite to B or create new array
    if overwrite:
        X = B
    else:
        X = numpy.copy(B, order='F')

    # Check X has column-ordering.
    if X.flags['F_CONTIGUOUS'] is not True:
        raise ValueError('"B" should be "F" contiguous. Alternatively, '
                         'set "overwrite" to True.')

    # Set number of parallel threads
    num_threads = get_avail_num_threads()
    cond_omp_set_num_threads(num_threads)

    cdef float[::1, :] D_fp32_f_mv
    cdef float[::1, :] B_fp32_f_mv
    cdef double[::1, :] D_fp64_f_mv
    cdef double[::1, :] B_fp64_f_mv

    cdef float* D_fp32_p
    cdef float* B_fp32_p
    cdef double* D_fp64_p
    cdef double* B_fp64_p

    # dispatch based on floating point precision and order
    if (D.dtype == numpy.float32):

        # Get pointer to D
        if D.flags['F_CONTIGUOUS']:
            D_fp32_f_mv = D
            D_fp32_p = &D_fp32_f_mv[0, 0]
            ldd = D.shape[0]
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

        info = _solve_diag_fp32(D_fp32_p, ldd, B_fp32_p, ldb, n, nrhs)

    elif (D.dtype == numpy.float64):

        # Get pointer to D
        if D.flags['F_CONTIGUOUS']:
            D_fp64_f_mv = D
            D_fp64_p = &D_fp64_f_mv[0, 0]
            ldd = D.shape[0]
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

        info = _solve_diag_fp64(D_fp64_p, ldd, B_fp64_p, ldb, n, nrhs)

    else:
        raise ValueError('Array should be "float32" or "float64" precision.')

    if info != 0:
        raise ValueError('LDL decomposition failed with error code: %d' % info)

    return X, info


# ===============
# solve diag fp32
# ===============

cdef int _solve_diag_fp32(
        float* D,
        int ldd,
        float* B,
        int ldb,
        int n,
        int nrhs) noexcept nogil:
    """
    Process float32 precision.
    """

    cdef int i, j
    cdef float a, b, c, det
    cdef float row_ip0, row_ip1
    cdef int[1] info
    info[0] = 0

    with nogil, parallel():

        # Assume lower triangle part is given. Fill upper triangle part
        for j in prange(nrhs, schedule='static'):
            for i in range(n):

                if D[ldd + i] == 0:

                    # Check if this was not part of a previously 2x2 block
                    if (i > 0) and (D[ldd + i-1] != 0):
                        continue
                    else:
                        # Indicates 1x1 block
                        if D[i] == 0:
                            # Encountered zero diagonal in 1x1 block
                            info[0] = 1
                            continue

                        B[j*ldb + i] = B[j*ldb + i] / D[i]

                else:
                    # Indicates 2x2 diagonal block
                    a = D[i]
                    b = D[i+1]
                    c = D[ldd + i]
                    det = a*b - c*c

                    if det == 0.0:
                        # Encountered zero diagonal in 2x2 block.
                        info[0] = 1
                        continue

                    # Multiply B[i:i+2, :] by the inverse of 2x2 block
                    row_ip0 = (b * B[j*ldb + i] - c * B[j*ldb + i+1]) / det
                    row_ip1 = (-c * B[j*ldb + i] + a * B[j*ldb + i+1]) / det

                    B[j*ldb + i] = row_ip0
                    B[j*ldb + i+1] = row_ip1

    return info[0]


# ===============
# solve diag fp64
# ===============

cdef int _solve_diag_fp64(
        double* D,
        int ldd,
        double* B,
        int ldb,
        int n,
        # int nrhs) noexcept nogil:
        int nrhs) nogil:
    """
    Process float64 precision.
    """

    cdef int i, j
    cdef double a, b, c, det
    cdef double row_ip0, row_ip1
    cdef int[1] info
    info[0] = 0

    with nogil, parallel():

        # Assume lower triangle part is given. Fill upper triangle part
        for j in prange(nrhs, schedule='static'):
            for i in range(n):

                if D[ldd + i] == 0:

                    # Check if this was not part of a previously 2x2 block
                    if (i > 0) and (D[ldd + i-1] != 0):
                        continue
                    else:
                        # Indicates 1x1 block
                        if D[i] == 0:
                            # Encountered zero diagonal in 1x1 block
                            info[0] = 1
                            continue

                        B[j*ldb + i] = B[j*ldb + i] / D[i]

                else:
                    # Indicates 2x2 diagonal block
                    a = D[i]
                    b = D[i+1]
                    c = D[ldd + i]
                    det = a*b - c*c

                    if det == 0.0:
                        # Encountered zero diagonal in 2x2 block.
                        info[0] = 1
                        continue

                    # Multiply B[i:i+2, :] by the inverse of 2x2 block
                    row_ip0 = (b * B[j*ldb + i] - c * B[j*ldb + i+1]) / det
                    row_ip1 = (-c * B[j*ldb + i] + a * B[j*ldb + i+1]) / det

                    B[j*ldb + i] = row_ip0
                    B[j*ldb + i+1] = row_ip1

    return info[0]
