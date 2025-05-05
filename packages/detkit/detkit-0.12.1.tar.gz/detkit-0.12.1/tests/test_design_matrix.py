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

from detkit.datasets import design_matrix

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ==================
# test design matrix
# ==================

def test_design_matrix():
    """
    Test for `design_matrix` function.
    """

    design_matrix(num_rows=2**9, num_cols=2**8, ortho=True)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_design_matrix()
