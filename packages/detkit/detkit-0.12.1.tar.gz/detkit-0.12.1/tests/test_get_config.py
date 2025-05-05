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

from detkit import get_config
from pprint import pprint

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ===============
# test get config
# ===============

def test_get_config():
    """
    Test for `get_config.py` function.
    """

    conf = get_config()
    pprint(conf)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_get_config()
