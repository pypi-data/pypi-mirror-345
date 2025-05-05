#! /usr/bin/env python

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
import numpy.linalg
from detkit import lu_factor

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(A_shape, sub_shape, overwrite=False, dtype='float64', order='C'):
    """
    Test lu factorization for a given sub-matrix shape.
    """

    A = numpy.random.rand(A_shape[0], A_shape[1])
    A_copy = numpy.copy(A)

    if order == 'C':
        A = numpy.ascontiguousarray(A)
    else:
        A = numpy.asfortranarray(A)

    if dtype == 'float64':
        A = A.astype(numpy.float64)
    else:
        A = A.astype(numpy.float32)

    # Shape of sub-matrix
    lu, perm = lu_factor(A, sub_shape, overwrite=overwrite)

    # Check overwrite
    if overwrite and (A.base != lu.base):
        raise RuntimeError('A and lu do not share common base in overwrite.')

    p, q = sub_shape
    k = numpy.min(sub_shape)
    U = numpy.triu(lu[:k, :q])
    L = numpy.tril(lu[:p, :k], -1)
    for i in range(k):
        L[i, i] = 1

    atol = numpy.finfo(dtype).resolution
    status = numpy.allclose(A_copy[perm[:p], :q], L @ U, atol=10*atol)

    if status:
        print('OK')
    else:
        print('Failed.')

    assert status


# ==============
# test lu_factor
# ==============

def test_lu_factor():
    """
    Test for `lu_factor` function.
    """

    overwrites = [True, False]
    dtypes = ['float32', 'float64']
    orders = ['C', 'F']

    for overwrite in overwrites:
        for dtype in dtypes:
            for order in orders:

                # overwrite should be used only if order is 'F'
                if (overwrite is True) and (order == 'C'):
                    continue

                _test((9, 4), (9, 4), overwrite=overwrite, dtype=dtype,
                      order=order)
                _test((9, 4), (5, 3), overwrite=overwrite, dtype=dtype,
                      order=order)
                _test((4, 9), (4, 9), overwrite=overwrite, dtype=dtype,
                      order=order)
                _test((4, 9), (3, 5), overwrite=overwrite, dtype=dtype,
                      order=order)
                _test((9, 9), (9, 9), overwrite=overwrite, dtype=dtype,
                      order=order)
                _test((9, 9), (4, 4), overwrite=overwrite, dtype=dtype,
                      order=order)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_lu_factor()
