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
from detkit import FitLogdet

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ===============
# test fit logdet
# ===============

def test_fit_logdet():
    """
    Test for `FitLogdet` class.
    """

    x_fit = numpy.logspace(1, 3)
    y_fit = -x_fit * numpy.log(x_fit)

    flodet = FitLogdet(m=3, n=0, scale_x=1, alpha=0, scale_y=1)
    flodet.fit(x_fit, y_fit, lam=0.0, smooth_interval=[1e3, 1e5],
               verbose=False)

    x_eval = numpy.logspace(3, 5)
    y_eval = flodet.eval(x_eval)                                   # noqa: F841


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_fit_logdet()
