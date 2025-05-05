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
from .._cy_linear_algebra import lu_factor, solve_triangular, matmul
from .._device import InstructionsCounter

__all__ = ['memdet_gen']


# =========
# lu factor
# =========

def _lu_factor(A, dtype, order, block_info, ic, verbose=False):
    """
    Performs LU factorization of an input matrix.
    """

    if verbose:
        print(f'lu decompos {ANSI.FAINT}... ', end='', flush=True)
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

    lu, perm = lu_factor(A_, A_shape, overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    # Check lu is overwritten to A.
    if not numpy.may_share_memory(lu, A_):
        raise RuntimeError('"lu" is not overwritten to "A".')

    if verbose:
        prof.print_profile(A_shape, dtype)

    return lu, perm


# ================
# solve triangular
# ================

def _solve_triangular(lu, B, dtype, order, trans, lower, unit_diagonal,
                      block_info, ic, verbose=False):
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
    B_shape, B_shape_on_mem = get_block_shape(block_info, trans=trans)

    # Get buffer from shared memory
    B_ = get_array(B, B_shape_on_mem, dtype, order)

    # Start performance counter
    if ic is not None:
        ic.start()

    x = solve_triangular(lu, B_, shape=B_shape, trans=trans, lower=lower,
                         unit_diagonal=unit_diagonal, overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    # Check x is actually overwritten to B
    if not numpy.may_share_memory(x, B_):
        raise RuntimeError('"x" is not overwritten to "B".')

    if verbose:
        prof.print_profile(B_shape, dtype)

    return x


# ================
# schur complement
# ================

def _schur_complement(L_t, U, S, dtype, order, block_info, ic, verbose=False):
    """
    Computes in-place Schur complement without allocating any intermediate
    memory. This method is parallel.

    For this function to not allocate any new memory, all matrices, L, U,
    and S should be in Fortran ordering.
    """

    if verbose:
        print(f'schur compl {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    # Find the size of block on memory
    shape, shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    L_t_ = get_array(L_t, shape_on_mem, dtype, order)
    U_ = get_array(U, shape_on_mem, dtype, order)
    S_ = get_array(S, shape_on_mem, dtype, order)

    # Check all matrices have Fortran ordering
    if not L_t_.flags['F_CONTIGUOUS']:
        raise TypeError('Matrix "L" should have column-ordering.')
    if not U_.flags['F_CONTIGUOUS']:
        raise TypeError('Matrix "U" should have column-ordering.')
    if not S_.flags['F_CONTIGUOUS']:
        raise TypeError('Matrix "S" should have column-ordering.')

    # Find the shape of matrix product
    m1, m2 = shape
    m = shape_on_mem[0]
    matmul_shape = (m1, m, m2)

    trans_a = True
    trans_b = False
    alpha = -1.0
    beta = 1.0

    # Start performance counter
    if ic is not None:
        ic.start()

    matmul(L_t_, U_, S_, matmul_shape, trans_a, trans_b, alpha, beta,
           overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    if verbose:
        prof.print_profile(shape, dtype)


# ==================
# permutation parity
# ==================

def _permutation_parity(p_inv):
    """
    Compute the parity of a permutation represented by the pivot array `piv`.

    Parameters
    ----------

    piv (array_like): The pivot array returned by `scipy.linalg.lu_factor`.

    Returns
    -------
    int: The parity of the permutation (+1 or -1).
    """

    n = len(p_inv)
    visited = numpy.zeros(n, dtype=bool)
    parity = 1

    for i in range(n):
        if not visited[i]:
            j = i
            while not visited[j]:
                visited[j] = True
                j = p_inv[j]
                if j != i:
                    parity = -parity

    return parity


# ========
# get diag
# ========

def _get_diag(A, block_info):
    """
    Get the diagonal elements of a block. If the matrix is smaller than the
    block size (such as the last diagonal block and when m is not a divider of
    n), in this case, the correct diagonal elements of the sub-matrix is
    returned.
    """

    A_shape, _ = get_block_shape(block_info, trans=False)
    md = A_shape[0]
    diag_A = numpy.diag(A)[:md].astype(numpy.float64)

    return diag_A


# ==========
# memdet gen
# ==========

def memdet_gen(io, verbose):
    """
    memdet algorithm for generic matrices (non-symmetric). This method uses
    LU decomposition.
    """

    # Unpack variables
    dtype = io['config']['dtype']
    order = io['config']['order']
    num_blocks = io['config']['num_blocks']
    n = io['config']['n']
    m = io['config']['m']
    A11 = io['arrays']['A11']
    A12 = io['arrays']['A12']
    A21_t = io['arrays']['A21_t']
    A22 = io['arrays']['A22']

    # Output, this will accumulate logdet of each diagonal block
    ld = 0
    sign = 1
    diag = []
    perm = []
    perm_base_index = 0

    # Hardware instruction counter
    if io['profile']['inst_per_flop'] is not None:
        ic = InstructionsCounter()
        ic.set_inst_per_flop(io['profile']['inst_per_flop'])
    else:
        ic = None

    # Initialize progress
    progress = Progress(num_blocks, assume='gen', verbose=verbose)

    # Diagonal iterations
    for k in range(num_blocks):

        # print task to be processed
        if verbose:
            progress.print_task(k, k, k)

        if k == 0:
            load_block(io, A11, k, k, verbose=verbose)

        # LU decomposition
        lu_11, perm_lu_11 = _lu_factor(A11, dtype, order,
                                       block_info=(k, k, num_blocks, n), ic=ic,
                                       verbose=verbose)

        # log-determinant
        diag_lu_11 = _get_diag(lu_11, (k, k, num_blocks, n))
        ld += numpy.sum(numpy.log(numpy.abs(diag_lu_11)))

        # Sign of determinant
        parity = _permutation_parity(perm_lu_11)
        sign *= numpy.prod(numpy.sign(diag_lu_11)) * parity

        # Save diagonals and permutationd
        diag.append(numpy.copy(diag_lu_11))
        perm.append(numpy.copy(perm_lu_11) + perm_base_index)
        perm_base_index += perm_lu_11.size

        # Print progress count
        progress.count()

        # Row iterations
        for i in range(num_blocks-1, k, -1):

            if (i - k) % 2 == 0:
                # Start space-filling curve in a forward direction in the
                # last row
                j_start = k+1
                j_end = num_blocks
                j_step = +1
            else:
                # start space-filling curve in a backward direction in the
                # last row
                j_start = num_blocks-1
                j_end = k
                j_step = -1

            # print task to be processed
            if verbose:
                progress.print_task(k, i, j_start)

            load_block(io, A21_t, i, k, trans=True, verbose=verbose)

            # Solve upper-triangular system
            l_21_t = _solve_triangular(lu_11, A21_t, dtype, order, trans=True,
                                       lower=False, unit_diagonal=False,
                                       block_info=(i, k, num_blocks, n), ic=ic,
                                       verbose=verbose)

            # Column iterations
            for j in range(j_start, j_end, j_step):

                # print task to be processed
                if verbose and (j != j_start):
                    progress.print_task(k, i, j)

                # When the space-filling curve changes direction, do not
                # read new A12, rather use the previous matrix already
                # loaded to memory
                if (i == num_blocks-1) or (j != j_start):
                    # load_block(io, A12, k, j, verbose=verbose)
                    if i == num_blocks-1:
                        load_block(io, A12, k, j, perm=perm_lu_11,
                                   verbose=verbose)
                    else:
                        load_block(io, A12, k, j, perm=None, verbose=verbose)

                if i == num_blocks-1:

                    # Permute A12
                    # _permute_array(A12, perm_lu_11, (m, md), dtype, order)

                    # Solve lower-triangular system
                    u_12 = _solve_triangular(
                            lu_11, A12, dtype, order, trans=False, lower=True,
                            unit_diagonal=True,
                            block_info=(k, j, num_blocks, n), ic=ic,
                            verbose=verbose)

                    # The if condition below excludes two very specific cases
                    # from storing A12 to scratch. One case is when
                    # num_blocks - k = 1 or 2 (0x0 or 1x1 remaining blocks),
                    # and the other one is then num_block - k is 3 (a 2x2
                    # remaining block) and only when j is the last j (j_end-1
                    # in forward or j_end+1 in backward) case. In the last
                    # case,A12 will be still in memory on the next row
                    # iteration where j becomes j_start, and there will be no
                    # further row iteration after that, since there are only
                    # two rows on that 2x2 remaining block. As for
                    # num_block - k > 3, A12 should always be stored, since on
                    # other row iterations, we will need A12 again, so we
                    # should store it.
                    if (num_blocks - k > 3) or (j != j_end - j_step):
                        # Store u_12, which is the same as A12 since u_12
                        # is overwritten to A12.
                        store_block(io, A12, k, j, verbose=verbose)
                else:
                    u_12 = get_array(A12, (m, m), dtype, order)

                # Compute Schur complement
                if (i == k+1) and (j == k+1):

                    # Use A11 instead of A22
                    load_block(io, A11, i, j, verbose=verbose)

                    # Overwrite A11 with Schur complement
                    _schur_complement(l_21_t, u_12, A11, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)
                else:
                    load_block(io, A22, i, j, verbose=verbose)

                    # Overwrite A22 with Schur complement
                    _schur_complement(l_21_t, u_12, A22, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)

                    # Store A22 to disk. This point reaches only when num_block
                    # is greater than 2 (hence using scratch)
                    store_block(io, A22, i, j, verbose=verbose)

                # Print progress count
                progress.count()

    # concatenate diagonals and permutartions of blocks of U
    diag = numpy.concatenate(diag)
    perm = numpy.concatenate(perm)

    # Instructions count
    if ic is not None:
        io['profile']['hw_inst_count'] = ic.get_count()
        io['profile']['flops'] = ic.get_flops()

    return ld, sign, diag, perm
