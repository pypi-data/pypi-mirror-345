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
from ._memdet_util import Progress, get_array, get_block_shape
from ._memdet_block import load_block, store_block
from ._ansi import ANSI
from .profile import Profile
from ._memdet_gen import _get_diag, _schur_complement, _solve_triangular
from .._cy_linear_algebra import cho_factor, cho_solve
from .._device import InstructionsCounter

__all__ = ['memdet_spd']


# ==========
# cho factor
# ==========

def _cho_factor(A, dtype, order, lower, block_info, ic, verbose=False):
    """
    Performs Cholesky factorization of an input matrix.
    """

    if verbose:
        print(f'chol decomp {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    # The location of block in the matrix
    i = block_info[0]
    j = block_info[1]
    if i != j:
        raise RuntimeError('LU factor should be done on diagonal blocks only.')

    # Find the size of block on memory
    A_shape, A_shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    A_ = get_array(A, A_shape_on_mem, dtype, order)

    # Start performance counter
    if ic is not None:
        ic.start()

    # Cholesky (Lower: A = L @ L.T or Upper: A = U.T @ U)
    cho = cho_factor(A_, A_shape[0], lower=lower, overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    # Check cho is overwritten to A.
    if not numpy.may_share_memory(cho, A_):
        raise RuntimeError('"cho" is not overwritten to "A".')

    if verbose:
        prof.print_profile(A_shape, dtype)

    return cho


# =========
# cho solve
# =========

def _cho_solve(cho, B, dtype, order, lower, block_info, ic, verbose=False):
    """
    Solve triangular system of equations.
    """

    if verbose:
        if lower:
            print(f'solve lotri {ANSI.FAINT}... ', end='', flush=True)
        else:
            print(f'solve uptri {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    # Find the size of block on memory
    B_shape, B_shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    B_ = get_array(B, B_shape_on_mem, dtype, order)

    # Start performance counter
    if ic is not None:
        ic.start()

    x = cho_solve(cho, B_, shape=B_shape, lower=lower, overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    # Check x is actually overwritten to B
    if not numpy.may_share_memory(x, B_):
        raise RuntimeError('"x" is not overwritten to "B".')

    if verbose:
        prof.print_profile(B_shape, dtype)

    return x


# ==========
# memdet spd
# ==========

def memdet_spd(io, verbose):
    """
    memdet algorithm for symmetric positive-definite matrices. This method uses
    Cholesky decomposition.
    """

    # Unpack variables
    dtype = io['config']['dtype']
    order = io['config']['order']
    num_blocks = io['config']['num_blocks']
    n = io['config']['n']
    A11 = io['arrays']['A11']
    A12 = io['arrays']['A12']
    A21_t = io['arrays']['A21_t']
    A22 = io['arrays']['A22']

    # Output, this will accumulate logdet of each diagonal block
    ld = 0
    sign = 1
    diag = []
    lower = True

    # Hardware instruction counter
    if io['profile']['inst_per_flop'] is not None:
        ic = InstructionsCounter()
        ic.set_inst_per_flop(io['profile']['inst_per_flop'])
    else:
        ic = None

    # Initialize progress
    progress = Progress(num_blocks, assume='sym', verbose=verbose)

    # Diagonal iterations
    for k in range(num_blocks):

        # print task to be processed
        if verbose:
            progress.print_task(k, k, k)

        if k == 0:
            load_block(io, A11, k, k, verbose=verbose)

        # Cholesky decomposition
        cho_11 = _cho_factor(A11, dtype, order, lower=lower,
                             block_info=(k, k, num_blocks, n), ic=ic,
                             verbose=verbose)

        # log-determinant
        diag_cho_11 = _get_diag(cho_11, (k, k, num_blocks, n))
        ld += 2.0 * numpy.sum(numpy.log(numpy.abs(diag_cho_11)))

        # Save diagonals
        diag.append(numpy.copy(diag_cho_11))

        # Print progress count
        progress.count()

        # Row iterations
        for j in range(num_blocks-1, k, -1):

            # Vertical upward movement of block, first process diagonal
            # block, then go from top downward to one block above diagonal
            i_range = numpy.r_[j, numpy.arange(k+1, j)]

            # print task to be processed
            if verbose:
                progress.print_task(k, i_range[0], j)

            if ((num_blocks-1 - j) % 2 == 0):
                B = A12
            else:
                B = A21_t

            if j == num_blocks-1:
                load_block(io, B, k, j, trans=False, verbose=verbose)
                _solve_triangular(cho_11, B, dtype, order, trans=False,
                                  lower=lower, unit_diagonal=False,
                                  block_info=(k, j, num_blocks, n), ic=ic,
                                  verbose=verbose)

            # Row iterations
            for i in i_range:

                # print task to be processed
                if verbose and (i != i_range[0]):
                    progress.print_task(k, i, j)

                # When the space-filling curve changes direction, do not
                # read new A12, rather use the previous matrix already
                # loaded to memory
                if i == j:
                    C = B

                else:
                    # Point C to the opposite choices we made for B. That is,
                    # if B points to A12, make C to point to A21_t, and vice
                    # versa.
                    if ((num_blocks-1 - j) % 2 == 0):
                        C = A21_t
                    else:
                        C = A12

                    load_block(io, C, k, i, perm=None, verbose=verbose)

                    if j == num_blocks-1:
                        _solve_triangular(cho_11, C, dtype, order, trans=False,
                                          lower=lower, unit_diagonal=False,
                                          block_info=(k, i, num_blocks, n),
                                          ic=ic, verbose=verbose)

                        if (num_blocks > 2) and (i < j-1):
                            store_block(io, C, k, i, verbose=verbose)

                # Compute Schur complement
                if j == k+1:

                    # Use A11 instead of A22
                    load_block(io, A11, i, j, verbose=verbose)

                    # Overwrite A11 with Schur complement
                    _schur_complement(C, B, A11, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)
                else:

                    load_block(io, A22, i, j, verbose=verbose)

                    # Overwrite A22 with Schur complement
                    _schur_complement(C, B, A22, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)

                    # Store A22 to disk. This point reaches only when num_block
                    # is greater than 2 (hence using scratch)
                    store_block(io, A22, i, j, verbose=verbose)

                # Print progress count
                progress.count()

    # concatenate diagonals of blocks of U
    diag = numpy.concatenate(diag)

    # Cholesky has no permutation
    perm = numpy.arange(diag.size)

    # Instructions count
    if ic is not None:
        io['profile']['hw_inst_count'] = ic.get_count()
        io['profile']['flops'] = ic.get_flops()

    return ld, sign, diag, perm
