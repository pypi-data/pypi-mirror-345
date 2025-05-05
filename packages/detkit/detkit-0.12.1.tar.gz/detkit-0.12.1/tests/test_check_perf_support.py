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

from detkit import check_perf_support

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# =======================
# test check perf support
# =======================

def test_check_perf_support():
    """
    Test for `check_perf_support` function.
    """

    results = check_perf_support()
    print(results)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_check_perf_support()
