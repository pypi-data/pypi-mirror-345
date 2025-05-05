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

from detkit import ortho_complement, orthogonalize
import numpy

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# =====================
# test ortho complement
# =====================

def test_ortho_complement():
    """
    Test for `get_config.py` function.
    """

    # n, m, p = 2**9, 2**8, 2**4
    n, m, p = 2**9, 2**2, 2**1
    Zero = numpy.zeros((m, p))
    I = numpy.eye(p, p)                                            # noqa: E741

    X = numpy.random.rand(n, m)
    Xp = numpy.random.rand(n, p)
    ortho_complement(Xp, X, X_orth=False)
    atol = 1e-7

    # Check orthonormal
    status_1 = numpy.allclose(X.T @ Xp, Zero, atol=atol)
    status_2 = numpy.allclose(Xp.T @ Xp, I, atol=atol)
    print(status_1)
    print(status_2)

    # Assume X is already orthonormalized
    X = numpy.random.rand(n, m)
    Xp = numpy.random.rand(n, p)
    orthogonalize(X)
    ortho_complement(Xp, X, X_orth=True)

    # Check orthonormal
    status_1 = numpy.allclose(X.T @ Xp, Zero, atol=atol)
    status_2 = numpy.allclose(Xp.T @ Xp, I, atol=atol)
    print(status_1)
    print(status_2)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_ortho_complement()
