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
import scipy
from detkit import lu_factor, lu_solve

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(B_shape, sub_shape, trans=False, overwrite=False, dtype='float64',
          order='C'):
    """
    Test solving linear system based on LU factorization for a given
    sub-matrix shape.
    """

    A = numpy.random.rand(B_shape[0], B_shape[0])
    A = A + sub_shape[0] * numpy.eye(A.shape[0])
    A_copy = numpy.copy(A)

    B = numpy.random.randn(B_shape[0], B_shape[1])
    B_copy = numpy.copy(B)

    if order == 'C':
        A = numpy.ascontiguousarray(A)
        B = numpy.ascontiguousarray(B)
    else:
        A = numpy.asfortranarray(A)
        B = numpy.asfortranarray(B)

    if dtype == 'float64':
        A = A.astype(numpy.float64)
        B = B.astype(numpy.float64)
    else:
        A = A.astype(numpy.float32)
        B = B.astype(numpy.float32)

    # Compute LU using detkit
    p, q = sub_shape
    lu, perm = lu_factor(A, (p, p), overwrite=overwrite)

    # Compute lu using scipy
    lu2, piv2 = scipy.linalg.lu_factor(A_copy[:p, :p], overwrite_a=False)

    # Solve linear system with detkit
    X = lu_solve(lu, perm, B, sub_shape, trans=trans, overwrite=overwrite)

    # Solve linear system with scipy
    if trans:
        trans_ = 1
    else:
        trans_ = 0
    X2 = scipy.linalg.lu_solve((lu2, piv2), B_copy[:p, :q], trans=trans_,
                               overwrite_b=False)

    # Check overwrite
    if overwrite and (X.base != B.base):
        raise RuntimeError('"X" and "B" do not share common base in ' +
                           'overwrite.')

    atol = numpy.finfo(dtype).resolution
    status1 = numpy.allclose(X[:p, :q], X2, atol=10*atol)

    if trans:
        op = A_copy[:p, :p].T
    else:
        op = A_copy[:p, :p]
    status2 = numpy.allclose(op @ X[:p, :q], B_copy[:p, :q], atol=10*atol)

    if status1 and status2:
        print('OK')
    else:
        print('Failed.')

    assert numpy.logical_and(status1, status2)


# ==============
# test lu factor
# ==============

def test_lu_factor():
    """
    Test for `lu_solve` function.
    """

    overwrites = [True, False]
    transs = [False, True]
    dtypes = ['float32', 'float64']
    orders = ['C', 'F']

    for overwrite in overwrites:
        for trans in transs:
            for dtype in dtypes:
                for order in orders:

                    # overwrite should be used only if order is 'F'
                    if (overwrite is True) and (order == 'C'):
                        continue

                    _test((9, 9), (9, 9), trans=trans, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (4, 6), trans=trans, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (6, 4), trans=trans, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (4, 4), trans=trans, overwrite=overwrite,
                          dtype=dtype, order=order)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_lu_factor()
