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

from detkit.datasets import electrocardiogram
import os
import sys
import glob

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
# test electrocardiogram
# ======================

def test_electrocardiogram():
    """
    Test for `electrocardiogram` function.

    Note that this test can only be done on Python 3.8 and above.
    """

    # Find Python version
    py_major = sys.version_info.major
    py_minor = sys.version_info.minor

    # This test can only be done on Python 3.8 and above.
    if (py_major < 3) or (py_minor < 8):
        return

    electrocardiogram(start=0.0, end=10.0, bw_window=0.5, freq_cut=45,
                      plot='ecg1', plot_bw=False)
    electrocardiogram(start=0.0, end=10.0, bw_window=0.5, freq_cut=45,
                      plot='ecg2', plot_bw=True)

    _remove_saved_plot('ecg*.svg')
    _remove_saved_plot('ecg*.pdf')


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_electrocardiogram()
