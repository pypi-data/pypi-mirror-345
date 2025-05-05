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
from detkit import ldl_factor

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(A_size, sub_size, lower=False, overwrite=False, dtype='float64',
          order='C'):
    """
    Test ldl factorization for a given sub-matrix shape.
    """

    A = numpy.random.rand(A_size, A_size)
    A = 0.5 * (A + A.T)
    A_copy = numpy.copy(A)

    if order == 'C':
        A = numpy.ascontiguousarray(A)
    else:
        A = numpy.asfortranarray(A)

    if dtype == 'float64':
        A = A.astype(numpy.float64)
    else:
        A = A.astype(numpy.float32)

    # Compute ldl using detkit
    lu, d, perm = ldl_factor(A, sub_size, lower=lower, overwrite=overwrite,
                             return_as_lapack=False)

    # Compute ldl using scipy
    p = sub_size
    lu2, d2, perm2 = scipy.linalg.ldl(A_copy[:p, :p], lower=lower,
                                      overwrite_a=False)

    # Check overwrite
    if overwrite and (A.base != lu.base):
        raise RuntimeError('A and ldu do not share common base in overwrite.')

    atol = numpy.finfo(dtype).resolution

    # Compare with scipy
    status1 = numpy.allclose(lu[:p, :p], lu2, atol=10*atol)
    status2 = numpy.allclose(d[:p, :p], d2, atol=10*atol)
    status3 = numpy.allclose(perm[:p], perm2)

    # Check A = LDL holds
    df = lu[:p, :p] @ d[:p, :p] @ lu[:p, :p].T - A_copy[:p, :p]
    status4 = numpy.allclose(df, numpy.zeros((p, p)), atol=10*atol)

    status = numpy.all([status1, status2, status3, status4])
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
    Test for `ldl_factor` function.
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

                    _test(9, 9, lower=lower, overwrite=overwrite, dtype=dtype,
                          order=order)
                    _test(9, 6, lower=lower, overwrite=overwrite, dtype=dtype,
                          order=order)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_ldl_factor()
