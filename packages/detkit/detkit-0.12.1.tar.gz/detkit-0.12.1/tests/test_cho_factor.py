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
from detkit import cho_factor

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ====
# test
# ====

def _test(A_size, sub_size, lower=False, overwrite=False, dtype='float64',
          order='C'):
    """
    Test Cholesky factorization for a given sub-matrix shape.
    """

    A = numpy.random.rand(A_size, A_size)
    A = A.T @ A + numpy.eye(A_size)
    A_copy = numpy.copy(A)

    if order == 'C':
        A = numpy.ascontiguousarray(A)
    else:
        A = numpy.asfortranarray(A)

    if dtype == 'float64':
        A = A.astype(numpy.float64)
    else:
        A = A.astype(numpy.float32)

    # Compute Cholesky using detkit
    cho = cho_factor(A, sub_size, lower=lower, overwrite=overwrite)

    # Compute Cholesky using scipy
    cho2, _ = scipy.linalg.cho_factor(A_copy[:sub_size, :sub_size],
                                      lower=lower, overwrite_a=False)

    # Check overwrite
    if overwrite and (A.base != cho.base):
        raise RuntimeError('"A" and "cho" do not share common base in ' +
                           'overwrite.')

    atol = numpy.finfo(dtype).resolution

    if lower:
        L = numpy.tril(cho[:sub_size, :sub_size])
        L2 = numpy.tril(cho2)

        status1 = numpy.allclose(L, L2, atol=10*atol)
        status2 = numpy.allclose(L @ L.T, A_copy[:sub_size, :sub_size],
                                 atol=10*atol)

    else:
        U = numpy.triu(cho[:sub_size, :sub_size])
        U2 = numpy.triu(cho2)

        status1 = numpy.allclose(U, U2, atol=atol)
        status2 = numpy.allclose(U.T @ U, A_copy[:sub_size, :sub_size],
                                 atol=atol)

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
    Test for `cho_factor` function.
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
                    _test(9, 5, lower=lower, overwrite=overwrite, dtype=dtype,
                          order=order)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_cho_factor()
