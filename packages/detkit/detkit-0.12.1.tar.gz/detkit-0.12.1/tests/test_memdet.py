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

import sys
import numpy
from detkit import memdet, logdet
import zarr
import os
import shutil
import platform

# import warnings
# warnings.resetwarnings()
# warnings.filterwarnings('error')


# ==========
# remove dir
# ==========

def remove_dir(dir_name):
    """
    Removes a directory
    """

    if os.path.exists(dir_name):
        try:
            shutil.rmtree(dir_name)
            print('File %s is deleted.' % dir_name)
        except OSError:
            pass

    else:
        print('Directory %s does not exists.' % dir_name)


# ====
# test
# ====

def _test(A, assumes, dtypes, parallel_ios, triangles, num_blocks, max_mems):
    """
    Test one or multiple cases.
    """

    mixed_precision = 'float64'
    scratch_dir = None

    for assume in assumes:

        if assume == 'gen':
            B = A
            sym_pos = False
        elif assume == 'sym':
            B = A.T + A
            sym_pos = False
        elif assume == 'spd':
            B = A.T @ A
            sym_pos = True

        for dtype in dtypes:

            B = B.astype(dtype)

            # True solution
            ld0, sign0 = logdet(B, sym_pos=sym_pos, use_scipy=True)

            for parallel_io in parallel_ios:

                # Windows seem to have permission issue with .npy files
                # and npy scratch file is generated when parallel_io is set
                # to multiproc.
                if sys.platform == 'win32':
                    # Do not use tmp dir
                    scratch_dir = '.'

                for triangle in triangles:

                    if triangle == 'l':
                        B_tri = numpy.tril(B).astype(B.dtype)
                    elif triangle == 'u':
                        B_tri = numpy.triu(B).astype(B.dtype)
                    else:
                        B_tri = B

                    # tensorstore can only be used with zarr arrays
                    if parallel_io == 'tensorstore':

                        # Store matrix as a zarr array on disk (optional)
                        z_path = 'my_matrix.zarr'
                        matrix = zarr.open(z_path, mode='w', shape=A.shape,
                                           dtype=B_tri.dtype)
                        matrix[:, :] = B_tri

                    else:
                        matrix = B_tri

                    for num_block in num_blocks:
                        for max_mem in max_mems:

                            print('\nprocessing:\n' +
                                  f'num_block: {num_block}\n' +
                                  f'max_mem: {max_mem}\n' +
                                  f'dtype: {dtype}\n' +
                                  f'assume: {assume}\n' +
                                  f'triangle: {triangle}\n' +
                                  f'parallel_io: {parallel_io}\n', flush=True)

                            if sys.platform == "linux":
                                flops = True
                            else:
                                flops = False

                            # Compute log-determinant
                            ld, sign, diag, perm, info = memdet(
                                    matrix, max_mem=max_mem,
                                    num_blocks=num_block, assume=assume,
                                    mixed_precision=mixed_precision,
                                    scratch_dir=scratch_dir, triangle=triangle,
                                    parallel_io=parallel_io, flops=False,
                                    verbose=True, return_info=True)

                            # Compare error
                            sign_error = (sign == sign0)
                            ld_error = numpy.abs(1.0 - ld0/ld)

                            rtol = 100.0 * numpy.finfo('float32').resolution
                            if (sign_error is False) or (ld_error > rtol):
                                raise RuntimeError(
                                    '\nmemdet is inaccurate:\n' +
                                    f'num_block: {num_block}\n' +
                                    f'max_mem: {max_mem}\n' +
                                    f'dtype: {dtype}\n' +
                                    f'assume: {assume}\n' +
                                    f'triangle: {triangle}\n' +
                                    f'parallel_io: {parallel_io}\n' +
                                    f'sign: {sign}, true sign: {sign0}\n' +
                                    f'ld: {ld}, true ld: {ld0}, ' +
                                    f'err: {ld_error}\n' +
                                    f'rtol: {rtol}')
                            else:
                                print('OK')

    if 'z_path' in locals():
        remove_dir(z_path)


# ===========
# test memdet
# ===========

def test_memdet():
    """
    Test `memdet` function.
    """

    # Create a symmetric matrix
    n = 200
    A = numpy.random.randn(n, n) + (n/2.0) * numpy.eye(n)

    os_name = platform.system()

    if os_name in ['Linux', 'Windows']:
        parallel_ios = ['tensorstore']
    else:
        # For some reason, tensorstore causes threading issues on macos
        parallel_ios = [None]

    # Limit memory though num_blocks
    _test(A, assumes=['gen', 'sym', 'spd'], dtypes=['float64'],
          parallel_ios=parallel_ios, triangles=[None], num_blocks=[2, 3, 4],
          max_mems=[float('inf')])

    # Limit memory though max_mem
    nbytes = A.nbytes
    _test(A, assumes=['gen', 'sym', 'spd'], dtypes=['float64'],
          parallel_ios=parallel_ios, triangles=[None], num_blocks=[1],
          max_mems=[nbytes//4, '60KB', float('inf')])

    # Test data types
    _test(A, assumes=['gen', 'sym', 'spd'], dtypes=['float32', 'float64'],
          parallel_ios=parallel_ios, triangles=[None], num_blocks=[3],
          max_mems=[float('inf')])

    # Test other parallel io
    parallel_ios = [None]
    if (sys.version_info[0] >= 3) and (sys.version_info[1] < 12):
        # In Python 3.12, dask takes forever.
        parallel_ios += ['dask']

    # if sys.platform.startswith("linux"):
    #     # For some reason, multiproc does not work well in macos and windows,
    #     # causing issues in loading or storing blocks. As such, the blocks
    #     # become zero, and makes the matrix singular till LU crashes.
    #     parallel_ios += ['multiproc']

    _test(A, assumes=['gen'], dtypes=['float64'], triangles=[None],
          parallel_ios=parallel_ios, num_blocks=[4], max_mems=[float('inf')])

    # Test triangle, but only for sym matrices
    _test(A, assumes=['sym'], dtypes=['float64'],
          parallel_ios=[None], triangles=['u', 'l'], num_blocks=[4],
          max_mems=[float('inf')])


# ===========
# script main
# ===========

if __name__ == "__main__":
    test_memdet()
