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
from detkit import ldl_factor, ldl_solve

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(B_shape, sub_shape, lower=False, overwrite=False, dtype='float64',
          order='C'):
    """
    Test solving linear system based on LDL factorization for a given
    sub-matrix shape.
    """

    A = numpy.random.rand(B_shape[0], B_shape[0])
    A = A + A.T + sub_shape[0] * numpy.eye(A.shape[0])
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

    # Compute LDL using detkit
    p, q = sub_shape
    ldl, piv = ldl_factor(A, p, lower=lower, overwrite=overwrite,
                          return_as_lapack=True)

    # Solve linear system with detkit
    X = ldl_solve(ldl, piv, B, sub_shape, lower=lower, overwrite=overwrite)

    # Check overwrite
    if overwrite and (X.base != B.base):
        raise RuntimeError('"X" and "B" do not share common base in ' +
                           'overwrite.')

    atol = numpy.finfo(dtype).resolution
    status = numpy.allclose(A_copy[:p, :p] @ X[:p, :q], B_copy[:p, :q],
                            atol=10*atol)

    if status:
        print('OK')
    else:
        print('Failed.')

    assert status


# ===============
# test ldl factor
# ===============

def test_ldl_factor():
    """
    Test for `ldl_solve` function.
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
    test_ldl_factor()
