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
from detkit import cho_factor, cho_solve

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(B_shape, sub_shape, lower=False, overwrite=False, dtype='float64',
          order='C'):
    """
    Test solving linear system based on Cholesky factorization for a given
    sub-matrix shape.
    """

    A = numpy.random.rand(B_shape[0], B_shape[0])
    A = A.T @ A + A.shape[0] * numpy.eye(A.shape[0])
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

    # Compute Cholesky using detkit
    p, q = sub_shape
    cho = cho_factor(A, p, lower=lower, overwrite=overwrite)

    # Compute Cholesky using scipy
    cho2, low2 = scipy.linalg.cho_factor(A_copy[:p, :p], lower=lower,
                                         overwrite_a=False)

    # Solve linear system with detkit
    X = cho_solve(cho, B, sub_shape, lower=lower, overwrite=overwrite)

    # Solve linear system with scipy
    X2 = scipy.linalg.cho_solve((cho2, low2), B_copy[:p, :q],
                                overwrite_b=False)

    # Check overwrite
    if overwrite and (X.base != B.base):
        raise RuntimeError('"X" and "B" do not share common base in ' +
                           'overwrite.')

    atol = numpy.finfo(dtype).resolution

    status1 = numpy.allclose(X[:p, :q], X2, atol=10*atol)
    status2 = numpy.allclose(A_copy[:p, :p] @ X[:p, :q], B_copy[:p, :q],
                             atol=10*atol)

    if status1 and status2:
        print('OK')
    else:
        print('Failed.')

    assert numpy.logical_and(status1, status2)


# ===============
# test cho factor
# ===============

def test_cho_factor():
    """
    Test for `cho_solve` function.
    """

    overwrites = [True, False]
    lowers = [False, True]
    dtypes = ['float32', 'float64']
    orders = ['C', 'F']

    for overwrite in overwrites:
        for lower in lowers:
            for dtype in dtypes:
                for order in orders:

                    # overwrite should be used only if order is 'F'
                    if (overwrite is True) and (order == 'C'):
                        continue

                    _test((9, 9), (9, 9), lower=lower, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (4, 6), lower=lower, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (6, 4), lower=lower, overwrite=overwrite,
                          dtype=dtype, order=order)
                    _test((9, 9), (4, 4), lower=lower, overwrite=overwrite,
                          dtype=dtype, order=order)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_cho_factor()
