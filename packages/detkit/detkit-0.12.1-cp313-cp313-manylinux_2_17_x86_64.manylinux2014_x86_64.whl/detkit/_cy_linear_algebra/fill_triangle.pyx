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
# from .._openmp cimport cond_omp_set_num_threads

__all__ = ['fill_triangle']

# =============
# fill triangle
# =============

cpdef fill_triangle(array, lower=False):
    """
    Symmetrizes a triangle matrix by fills the other half of triangle part
    of the matrix.
    """

    # Get number of CPU threads
    num_threads = get_avail_num_threads()

    # Set number of parallel threads
    # cond_omp_set_num_threads(num_threads)

    n, m = array.shape

    # Check array should be square
    if n != m:
        raise ValueError('Array should be square.')

    # dispatch based on floating point precision and order
    if (array.dtype == numpy.float32) and (array.flags['C_CONTIGUOUS']):
        _fill_triangle_fp32_c(array, n, lower)
    elif (array.dtype == numpy.float32) and (array.flags['F_CONTIGUOUS']):
        _fill_triangle_fp32_f(array, n, lower)
    elif (array.dtype == numpy.float64) and (array.flags['C_CONTIGUOUS']):
        _fill_triangle_fp64_c(array, n, lower)
    elif (array.dtype == numpy.float64) and (array.flags['F_CONTIGUOUS']):
        _fill_triangle_fp64_f(array, n, lower)
    elif (array.dtype == numpy.float128) and (array.flags['C_CONTIGUOUS']):
        _fill_triangle_fp128_c(array, n, lower)
    elif (array.dtype == numpy.float128) and (array.flags['F_CONTIGUOUS']):
        _fill_triangle_fp128_f(array, n, lower)
    else:
        raise ValueError('Array should be "fp32", "fp64", or "fp128" '
                         'precision and "C" or "F" contiguous.')


# ====================
# fill triangle fp32 c
# ====================

cdef void _fill_triangle_fp32_c(
        float[:, ::1] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float32 bit precision data and C contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]


# ====================
# fill triangle fp32 f
# ====================

cdef void _fill_triangle_fp32_f(
        float[::1, :] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float32 bit precision data and F contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]


# ====================
# fill triangle fp64 c
# ====================

cdef void _fill_triangle_fp64_c(
        double[:, ::1] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float64 bit precision data and C contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]


# ====================
# fill triangle fp64 f
# ====================

cdef void _fill_triangle_fp64_f(
        double[::1, :] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float64 bit precision data and F contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]


# =====================
# fill triangle fp128 c
# =====================

cdef void _fill_triangle_fp128_c(
        long double[:, ::1] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float128 bit precision data and C contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]


# =====================
# fill triangle fp128 f
# =====================

cdef void _fill_triangle_fp128_f(
        long double[::1, :] array,
        int n,
        bint lower) noexcept nogil:
    """
    For float128 bit precision data and F contiguous ordering.
    """

    cdef int ix
    cdef int iy
    cdef int jx
    cdef int jy

    if lower:
        with nogil, parallel():

            # Assume lower triangle part is given. Fill upper triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[ix, jx] = array[jx, ix]

    else:
        with nogil, parallel():

            # Assume upper triangle part is given. Fill lower triangle part
            for ix in prange(n, schedule='static'):
                for jx in range(ix+1, n):
                    array[jx, ix] = array[ix, jx]
