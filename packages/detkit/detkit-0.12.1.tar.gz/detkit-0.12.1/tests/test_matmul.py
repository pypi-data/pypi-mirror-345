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
from detkit import matmul

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ===========
# test matmul
# ===========

def test_matmul():
    """
    Test for `matmul` function.
    """

    A = numpy.random.randn(10, 10)
    B = numpy.random.randn(10, 10)
    C = numpy.zeros((10, 10), order='F', dtype='float64')

    A = numpy.asfortranarray(A)
    B = numpy.asfortranarray(B)

    trans_as = [False, True]
    trans_bs = [False, True]
    alphas = [1, 2.5]
    betas = [0, 1.5]
    dtypes = ['float32', 'float64']
    overwrites = [False, True]
    shapes = ((10, 10, 10), (6, 4, 2), (6, 2, 4), (4, 6, 2), (4, 2, 6),
              (2, 6, 4), (2, 4, 6))

    for trans_a in trans_as:
        for trans_b in trans_bs:
            for alpha in alphas:
                for beta in betas:
                    for overwrite in overwrites:
                        for dtype in dtypes:
                            for shape in shapes:

                                if overwrite:
                                    C_ = numpy.copy(C)
                                    C2_ = numpy.copy(C)
                                else:
                                    C_ = C
                                    C2_ = C

                                A_ = A.astype(dtype)
                                B_ = B.astype(dtype)
                                C_ = C_.astype(dtype)
                                C2_ = C2_.astype(dtype)

                                # Using detkit
                                X = matmul(
                                    A_, B_, C_, shape=shape, trans_a=trans_a,
                                    trans_b=trans_b, alpha=alpha, beta=beta,
                                    overwrite=overwrite)

                                # Using numpy
                                m, n, k = shape

                                if trans_a:
                                    op_A = A_.T
                                else:
                                    op_A = A_

                                if trans_b:
                                    op_B = B_.T
                                else:
                                    op_B = B_

                                X2 = alpha * op_A[:m, :n] @ op_B[:n, :k] + \
                                    beta * C2_[:m, :k]

                                # Check accuracy of results
                                atol = numpy.finfo(dtype).resolution
                                status = numpy.allclose(X[:m, :k], X2,
                                                        atol=10*atol)

                                if status:
                                    print('OK')
                                else:
                                    print('Failed.')
                                    assert status


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_matmul()
