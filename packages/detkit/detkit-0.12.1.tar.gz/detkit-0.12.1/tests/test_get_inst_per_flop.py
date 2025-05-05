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

import os
import glob
from detkit import get_instructions_per_flop

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# =================
# remove saved plot
# =================

def _remove_saved_plot(filenames):
    """
    Deletes image files produced during the test.
    """

    directory = os.getcwd()
    fullpath_filenames = os.path.join(directory, filenames)

    # Get a list of all files matching wildcard
    files_list = glob.glob(fullpath_filenames)

    # Iterate over files
    for file in files_list:
        try:
            os.remove(file)
            print('File %s is deleted.' % file)
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            print("Error while removing file : ", file)


# ======================
# test get inst per flop
# ======================

def test_get_inst_per_flop():
    """
    Test for `get_inst_per_flop` function.
    """

    tasks = ['matmul', 'gramian', 'cholesky', 'lu', 'plu']
    impls = ['native', 'lapack', 'blas']

    # Instructions for each task
    for impl in impls:
        for task in tasks:
            inst_per_flop = get_instructions_per_flop(
                    task=task, impl=impl, dtype='float64', min_n=100,
                    max_n=500, num_n=6, plot=False)

            print(f'impl: {impl:<7s}, task: {task:<8s}, ' +
                  f'inst_per_flop: {inst_per_flop:>5.2f}')

    # Check plot
    _ = get_instructions_per_flop(task='matmul', impl='lapack',
                                  dtype='float32', min_n=100, max_n=500,
                                  num_n=10, plot=True)

    _remove_saved_plot('simd.svg')
    _remove_saved_plot('simd.pdf')


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_get_inst_per_flop()
