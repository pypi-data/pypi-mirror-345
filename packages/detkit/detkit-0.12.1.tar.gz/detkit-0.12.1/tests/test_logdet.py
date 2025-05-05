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
from detkit import logdet

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ===========
# test logdet
# ===========

def test_logdet():
    """
    Test for `logdet` function.
    """

    n = 500
    A = numpy.random.rand(n, n)

    sym_pos = True

    if sym_pos:
        A = A.T @ A

    print(numpy.linalg.slogdet(A))
    logdet_1, sign_1 = logdet(A, sym_pos=True, use_scipy=False)
    logdet_2, sign_2 = logdet(A, sym_pos=False, use_scipy=False)
    logdet_3, sign_3 = logdet(A, sym_pos=True, use_scipy=True)
    logdet_4, sign_4 = logdet(A, sym_pos=False, use_scipy=True)

    print("%16.8f, %+d" % (logdet_1, sign_1))
    print("%16.8f, %+d" % (logdet_2, sign_2))
    print("%16.8f, %+d" % (logdet_3, sign_3))
    print("%16.8f, %+d" % (logdet_4, sign_4))


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_logdet()
