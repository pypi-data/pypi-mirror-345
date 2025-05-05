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

import time
import numpy
import dask
from ._ansi import ANSI
from ._memdet_util import get_array, get_block_shape
from .profile import Profile
from ._parallel_io import load, store
from .._cy_linear_algebra import fill_triangle


__all__ = ['load_block', 'store_block']


# =============
# permute array
# =============

def _permute_array(array, perm_inv, shape, dtype, order):
    """
    Permutes rows of 2D array.

    This function overwrites the input array. Note that this function creates
    new memory, hence, is not memory efficient.
    """

    # Get buffer from shared memory
    array_ = get_array(array, shape, dtype, order)
    array_copy = numpy.copy(array_, order=order)
    array_[perm_inv, :] = array_copy[:, :]


# =====
# shift
# =====

def _shift(perm, shift):
    """
    Shifts a slice or permutation array.
    """

    if isinstance(perm, numpy.ndarray):
        shifted_perm = perm + shift
    elif isinstance(perm, slice):
        start = perm.start + shift
        stop = perm.stop + shift
        step = perm.step
        shifted_perm = slice(start, stop, step)
    else:
        raise ValueError('"perm" type is not recognized.')

    return shifted_perm


# ==========
# load block
# ==========

def load_block(io, array, i, j, trans=False, perm=None, verbose=False):
    """
    If triangle is 'l' or 'u', it replicates the other half of the triangle
    only if reading the original data from the input matrix. But when loading
    from the scratch space, it does not replicate the other half. This is
    because when data are stored to scratch space, all matrix is stored, not
    just a half triangle of it. Hence its loading should be full.

    perm_inv is the inverse permutation of perm. The operation of A[:, :] =
    B[perm, :] is equivalent to A[perm_inv, :] = B[:, :]. However, the latter
    creates additional memory of the same size as the original matrix, and is
    much slower. This is because numpy copies a slice and then permutes it.
    However, the first operation with perm_inv does not create any additional
    memory and is very fast.

    When scratchpad is used, the indices of j1 and j2 are shifted by -m,
    meaning we use j1-m and j2-m, since the scratchpad does not store the whole
    input matrix A of size (n, n), rather, it stores a matrix of size (n, n-m),
    where the first column A[:, :m] is not stored.
    """

    # Unpack config variables
    num_blocks = io['config']['num_blocks']
    n = io['config']['n']
    m = io['config']['m']
    triangle = io['config']['triangle']
    order = io['config']['order']
    dtype = io['config']['dtype']
    parallel_io = io['config']['parallel_io']

    # Unpack data variables
    scratch = io['data']['scratch']
    dask_scratch = io['data']['dask_scratch']
    ts_scratch = io['data']['ts_scratch']
    dask_A = io['data']['dask_A']
    ts_A = io['data']['ts_A']
    A = io['data']['A']
    cached = io['data']['cached']

    # Counter of the number of block loadings
    io['profile']['num_block_loads'] += 1

    # Initialize load times
    init_load_wall_time = time.time()
    init_load_proc_time = time.process_time()

    if verbose:
        print(f'loading blk {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    if (num_blocks > 2) and (bool(cached[i, j]) is True):
        read_from_scratch = True
    else:
        read_from_scratch = False

    if ((not read_from_scratch) and
        (((triangle == 'l') and (i < j)) or
         ((triangle == 'u') and (i > j)))):
        i_ = j
        j_ = i
        trans = numpy.logical_not(trans)
    else:
        i_ = i
        j_ = j

    i1 = m*i_
    if i_ == num_blocks-1:
        i2 = n
    else:
        i2 = m*(i_+1)

    j1 = m*j_
    if j_ == num_blocks-1:
        j2 = n
    else:
        j2 = m*(j_+1)

    # Get array shape
    block_info = (i, j, num_blocks, n)
    array_shape, array_shape_on_mem = get_block_shape(
        block_info, trans=trans)

    # Permutation of rows
    if perm is not None:

        # Row orders with permutation. perm_inv is the inverse of
        # permutation to be applied on the target array, rather than the
        # source array, while perm is applied to the source array. In the
        # case of transpose, perm is applied to the columns of the source
        # array, which is equivalent of taking the transpose first, then
        # apply perm on the rows.
        perm = numpy.array(perm)
        perm_inv = numpy.argsort(perm)

        if perm.ndim != 1:
            raise ValueError('"perm" should be a 1D array.')
        elif (((trans is False) and (perm.size != i2-i1)) or
              (trans is True) and (perm.size != j2-j1)):
            raise ValueError('"perm" size does not match the slice size')

        # When using perm on the source array, the indices should be
        # shifted to start from the beginning of the block, but this is not
        # necessary for perm_inv on target array.
        if trans:
            perm = _shift(perm, j1)
        else:
            perm = _shift(perm, i1)

    else:
        # Rows order with no permutation.
        # Note: do not use numpy.arange(0, i2-i1) as this is much slower
        # and takes much more memory than slice(0, i2-i1)
        if trans:
            perm = slice(j1, j2)
            perm_inv = slice(0, j2-j1)
        else:
            perm = slice(i1, i2)
            perm_inv = slice(0, i2-i1)

    # Perform reading
    if read_from_scratch:

        if parallel_io == 'multiproc':
            # Read using multiprocessing
            load(scratch, (i1, i2), (j1-m, j2-m), array, array_shape,
                 array_shape_on_mem, order, trans, perm_inv, num_proc=None)
        else:
            # Get buffer from shared memory
            array_ = get_array(array, array_shape_on_mem, dtype, order)

            if parallel_io == 'dask':
                # Read using dask
                if trans:
                    with dask.config.set(scheduler='threads'):
                        dask.array.store(
                                dask_scratch[i1:i2, (j1-m):(j2-m)].T,
                                array_[:(j2-j1), :(i2-i1)], lock=False)
                else:
                    with dask.config.set(scheduler='threads'):
                        dask.array.store(
                                dask_scratch[i1:i2, (j1-m):(j2-m)],
                                array_[:(i2-i1), :(j2-j1)], lock=False)

                # Dask cannot do permutation within store function. Do it
                # here manually
                if isinstance(perm, numpy.ndarray):
                    _permute_array(array_, perm_inv, array_shape_on_mem,
                                   dtype, order)

            elif parallel_io == 'tensorstore':
                # Read using tensorstore
                # For ts mode, when source is 'C' order and target is 'F'
                # order, using perm on source array is faster than
                # using perm_inv on target array. But, if source and target
                # have the same ordering, either perm or perm_inv have the
                # same performance. Here, array_ and scratch are both 'F'
                # ordering, so using either perm and perm_inv are fine.
                if trans:
                    # Using perm in columns of source when transposing.
                    array_[:(j2-j1), :(i2-i1)] = \
                        ts_scratch[i1:i2, _shift(perm, -m)].T.read(
                            order=order).result()
                else:
                    array_[:(i2-i1), :(j2-j1)] = \
                        ts_scratch[perm, (j1-m):(j2-m)].read(
                            order=order).result()

            else:
                # Read using numpy. Here, using perm_inv on target array is
                # faster.
                if trans:
                    array_[perm_inv, :(i2-i1)] = \
                        scratch[i1:i2, (j1-m):(j2-m)].T
                else:
                    array_[perm_inv, :(j2-j1)] = \
                        scratch[i1:i2, (j1-m):(j2-m)]

    else:
        # Reading from input array A (not from scratch)
        if (parallel_io == 'multiproc') and isinstance(A, numpy.memmap):
            # Read using multiprocessing
            load(A, (i1, i2), (j1, j2), array, array_shape,
                 array_shape_on_mem, order, trans, perm_inv, num_proc=None)
        else:

            # Get buffer from shared memory
            array_ = get_array(array, array_shape_on_mem, dtype, order)

            if parallel_io == 'dask':
                # Read using dask
                if trans:
                    with dask.config.set(scheduler='threads'):
                        dask.array.store(dask_A[i1:i2, j1:j2].T,
                                         array_[:(j2-j1), :(i2-i1)],
                                         lock=False)
                else:
                    with dask.config.set(scheduler='threads'):
                        dask.array.store(dask_A[i1:i2, j1:j2],
                                         array_[:(i2-i1), :(j2-j1)],
                                         lock=False)

                # Dask cannot do permutation within store function. Do it
                # here manually
                if isinstance(perm, numpy.ndarray):
                    _permute_array(array_, perm_inv, array_shape_on_mem,
                                   dtype, order)

            elif parallel_io == 'tensorstore':
                # Read using tensorstore
                # For ts mode, when source is 'C' order and target is 'F'
                # order, using perm on source array is faster than using
                # perm_inv on target array. But, if source and target have the
                # same ordering, either perm or perm_inv have the same
                # performance. Here, array_ is 'F' ordering while ts_A is 'C'
                # ordering, so using perm is preferred.
                if trans:
                    # Using perm in columns of source when transposing.
                    array_[:(j2-j1), :(i2-i1)] = \
                        ts_A[i1:i2, perm].T.read(order=order).result()
                else:
                    array_[:(i2-i1), :(j2-j1)] = ts_A[perm, j1:j2].read(
                            order=order).result()

            else:
                # Read using numpy. Here, using perm_inv on target array is
                # faster.
                if trans:
                    array_[perm_inv, :(i2-i1)] = A[i1:i2, j1:j2].T
                else:
                    array_[perm_inv, :(j2-j1)] = A[i1:i2, j1:j2]

    # Fill the other half of diagonal blocks (if input data is triangle)
    if (i == j) and (triangle is not None) and (not read_from_scratch):

        # Get buffer from shared memory
        array_ = get_array(array, array_shape_on_mem, dtype, order)

        if (triangle == 'l'):
            lower = True
        else:
            lower = False

        fill_triangle(array_, lower)

    # Forming matrix M = t*A + diag(d). Only apply to the first read of the
    # matrix from the input, not those already stored from scratch.
    if not read_from_scratch:
        t = io['data']['t']
        d = io['data']['d']

        # Get buffer from shared memory
        array_ = get_array(array, array_shape_on_mem, dtype, order)

        # Perform t A
        if t != 1.0:
            array_ *= t

        # Add diagonal diag(d)
        if (i == j) and (d is not None):
            diag_idx = numpy.arange(i2-i1)

            if numpy.isscalar(d):
                array_[diag_idx, diag_idx] += d
            else:
                array_[diag_idx, diag_idx] += d[i1:i2]

    # load times
    io['profile']['load_wall_time'] += time.time() - init_load_wall_time
    io['profile']['load_proc_time'] += time.process_time() - \
        init_load_proc_time

    if verbose:
        prof.print_profile(array_shape, dtype)


# ===========
# store block
# ===========

def store_block(io, array, i, j, verbose=False):
    """
    Store array to scratch space.

    When scratchpad is used, the indices of j1 and j2 are shifted by -m,
    meaning we use j1-m and j2-m, since the scratchpad does not store the whole
    input matrix A of size (n, n), rather, it stores a matrix of size (n, n-m),
    where the first column A[:, :m] is not stored.
    """

    # Unpack config variables
    num_blocks = io['config']['num_blocks']
    n = io['config']['n']
    m = io['config']['m']
    order = io['config']['order']
    dtype = io['config']['dtype']
    parallel_io = io['config']['parallel_io']

    # Unpack data variables
    io_chunk = io['data']['io_chunk']
    scratch = io['data']['scratch']
    ts_scratch = io['data']['ts_scratch']
    cached = io['data']['cached']

    # Counter of the number of block storing
    io['profile']['num_block_stores'] += 1

    # Initialize store times
    init_store_wall_time = time.time()
    init_store_proc_time = time.process_time()

    if verbose:
        print(f'storing blk {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    i1 = m*i
    if i == num_blocks-1:
        i2 = n
    else:
        i2 = m*(i+1)

    j1 = m*j
    if j == num_blocks-1:
        j2 = n
    else:
        j2 = m*(j+1)

    # Get array shape
    block_info = (i, j, num_blocks, n)
    array_shape, array_shape_on_mem = get_block_shape(
        block_info, trans=False)

    if parallel_io == 'multiproc':
        # Write in parallel
        trans = False
        store(scratch, (i1, i2), (j1-m, j2-m), array, array_shape,
              array_shape_on_mem, order, trans, num_proc=None)
    else:
        # Get buffer from shared memory
        array_ = get_array(array, array_shape_on_mem, dtype, order)

        if parallel_io == 'dask':
            with dask.config.set(scheduler='threads'):
                dask_array = dask.array.from_array(
                        array_[:(i2-i1), :(j2-j1)],
                        chunks=(io_chunk, io_chunk))
                scratch[i1:i2, (j1-m):(j2-m)] = dask_array.compute()
        elif parallel_io == 'tensorstore':
            ts_scratch[i1:i2, (j1-m):(j2-m)].write(
                array_[:(i2-i1), :(j2-j1)]).result()
        else:
            scratch[i1:i2, (j1-m):(j2-m)] = array_[:(i2-i1), :(j2-j1)]

    # Cache table to flag the block is now written to scratch space, so
    # next time, in order to access the block, scratch space should be
    # read, rather than the input matrix.
    cached[i, j] = True

    if isinstance(scratch, numpy.memmap):
        scratch.flush()

    # store times
    io['profile']['store_wall_time'] += time.time() - init_store_wall_time
    io['profile']['store_proc_time'] += time.process_time() - \
        init_store_proc_time

    if verbose:
        prof.print_profile(array_shape, dtype)
