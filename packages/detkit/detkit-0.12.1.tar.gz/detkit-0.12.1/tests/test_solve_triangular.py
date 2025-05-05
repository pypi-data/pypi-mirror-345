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
from detkit import solve_triangular

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# =====================
# test solve triangular
# =====================

def test_solve_triangular():
    """
    Test for `solve_triangular` function.
    """

    n = 8
    nrhs = 6
    A = numpy.random.randn(n, n)
    B = numpy.random.randn(n, nrhs)

    A = numpy.asfortranarray(A)
    B = numpy.asfortranarray(B)

    transs = [False, True]
    lowers = [False, True]
    unit_diagonals = [False, True]
    dtypes = ['float32', 'float64']
    overwrites = [False, True]
    shapes = ((8, 6), (6, 6), (4, 6), (4, 4), (3, 4))

    for trans in transs:
        for lower in lowers:
            for unit_diagonal in unit_diagonals:
                for overwrite in overwrites:
                    for dtype in dtypes:
                        for shape in shapes:

                            if overwrite:
                                B_ = numpy.copy(B)
                                B2_ = numpy.copy(B)
                            else:
                                B_ = B
                                B2_ = B

                            A_ = A.astype(dtype)
                            B_ = B_.astype(dtype)
                            B2_ = B2_.astype(dtype)

                            # Solve using detkit
                            X = solve_triangular(
                                A_, B_, shape=shape, trans=trans, lower=lower,
                                unit_diagonal=unit_diagonal,
                                overwrite=overwrite)

                            # Solve using scipy
                            X2 = scipy.linalg.solve_triangular(
                                    A_[:shape[0], :shape[0]],
                                    B2_[:shape[0], :shape[1]], trans=trans,
                                    lower=lower, unit_diagonal=unit_diagonal,
                                    overwrite_b=overwrite)

                            # Check accuracy of results
                            atol = numpy.finfo(dtype).resolution
                            status = numpy.allclose(X[:shape[0], :shape[1]],
                                                    X2, atol=10*atol)

                            if status:
                                print('OK')
                            else:
                                print('Failed.')
                                assert status


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_solve_triangular()
