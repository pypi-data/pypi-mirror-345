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

from detkit import orthogonalize
import numpy

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ==================
# test orthogonalize
# ==================

def test_orthogonalize():
    """
    Test for `get_config.py` function.
    """

    n, m = 2**9, 2**8

    X = numpy.random.randn(n, m).astype(numpy.float32)
    orthogonalize(X)

    X = numpy.random.randn(n, m).astype(numpy.float64)
    orthogonalize(X)

    X = numpy.random.randn(n, m).astype(numpy.longdouble)
    orthogonalize(X)

    # Check orthonormal
    I = numpy.eye(m, m)                                            # noqa: E741
    status = numpy.allclose(X.T @ X, I)
    print(status)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_orthogonalize()
