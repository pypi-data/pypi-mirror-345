# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'detkit.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

# ============
# check import
# ============

def _check_import():
    """
    The following two issues (see if conditions below) only happen in a cython
    package and if the package is build without --inplace option. This is
    because without the --inplace option, the *.so files will be built inside
    the /build directory (not in the same directory of the source code where
    *.pyx files are). On the other hand, when the user's directory is in the
    parent directory of the package, this path will be the first path on the
    sys.path. Thus, it looks for the package in the source-code directory, not
    where it was built or installed. But, because the built is outside of the
    source (recall no --inplace), it cannot find the *.so files.

    To resolve this issue:
    1. Either build the package with --inplace option.
    2. Change the current directory, or the directory of the script that you
       are running out of the source code.
    """

    import sys
    import os

    # Find the current directory of user (where the user calls an executable)
    _user_current_dir = os.getcwd()

    # Find executable directory (this is where the *.py executable is)
    _executable_file = os.path.abspath(sys.argv[0])
    _executable_dir = os.path.dirname(_executable_file)

    # Find the project directory (second parent directory of this script)
    _package_dir = os.path.dirname(os.path.realpath(__file__))  # It is: ../
    _project_dir = os.path.dirname(_package_dir)                # It is: ../../

    if (_user_current_dir == _project_dir):
        msg = 'You are in the source-code directory of this package. ' + \
               'Importing the package will fail. To resolve this issue, ' + \
               'consider changing the current directory outside of the ' + \
               'directory of the source-code of this package. Your ' + \
               'current directory is: %s.' % _user_current_dir

        sys.stderr.write(msg)

    elif (_executable_dir == _project_dir):
        msg = 'You are running a script in the source-code directory of ' + \
               'this package. Importing the package will fail. To ' + \
               'resolve this issue, consider changing the script ' + \
               'directory outside of the directory of the source-code of ' + \
               'this package. Your current directory is: ' + \
               '%s.' % _executable_dir

        sys.stderr.write(msg)


# =======
# Imports
# =======

try:
    # Import sub-packages
    from ._functions import logdet, loggdet, logpdet, memdet       # noqa: E402
    from ._functions import FitLogdet                              # noqa: E402
    from ._functions import orthogonalize, ortho_complement        # noqa: E402
    from ._functions import Memory, Disk, Profile                  # noqa: E402
    from ._functions import human_readable_mem                     # noqa: E402
    from ._functions import human_readable_time                    # noqa: E402
    from ._functions import get_processor_name                     # noqa: E402
    from ._cy_linear_algebra import lu_factor, lu_solve            # noqa: E402
    from ._cy_linear_algebra import ldl_factor, ldl_solve          # noqa: E402
    from ._cy_linear_algebra import cho_factor, cho_solve          # noqa: E402
    from ._cy_linear_algebra import solve_triangular, matmul       # noqa: E402
    from ._benchmark import get_instructions_per_flop              # noqa: E402
    from ._definitions import get_config                           # noqa: E402
    from ._device import InstructionsCounter, check_perf_support   # noqa: E402
    from .datasets import electrocardiogram                        # noqa: E402
    from .datasets import covariance_matrix, design_matrix         # noqa: E402

except Exception as e:
    # Before printing the exception, check if the exception is raised due to
    # being on the wrong directory.
    _check_import()

    # If the error was not due to being in the source directory, raise previous
    # error.
    raise e

__all__ = ['logdet', 'loggdet', 'logpdet', 'memdet', 'FitLogdet', 'load',
           'store', 'Memory', 'Disk', 'Profile', 'human_readable_time',
           'human_readable_mem', 'get_processor_name', 'orthogonalize',
           'ortho_complement', 'lu_factor', 'lu_solve', 'ldl_factor',
           'ldl_solve', 'cho_factor', 'cho_solve', 'matmul',
           'solve_triangular', 'get_config', 'InstructionsCounter',
           'check_perf_support', 'get_instructions_per_flop',
           'electrocardiogram', 'covariance_matrix', 'design_matrix']

from .__version__ import __version__                          # noqa: F401 E402
