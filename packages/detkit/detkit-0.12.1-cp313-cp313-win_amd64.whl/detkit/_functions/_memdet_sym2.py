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
from ._memdet_gen import _schur_complement
from .._cy_linear_algebra import ldl_factor, ldl_solve
from .._cy_linear_algebra.ldl_factor import _sanitize_piv
from .._device import InstructionsCounter

__all__ = ['memdet_sym2']


# ========
# get diag
# ========

def _get_diag(ldu, pivs, block_info, lower=True):
    """
    Originally taken from scipy.linalg.decomp_ldl.py:_get_d_and_l() function.
    This function is modified version of the _get_d_and_l() function in the
    ../_cy_linear_algebra/ldl_factor.pyx:_get_d_and_l().

    Parameters
    ----------
    ldu : ndarray
        The compact output returned by the LAPACK routing
    pivs : ndarray
        The sanitized array of {0, 1, 2} denoting the sizes of the pivots. For
        every 2 there is a succeeding 0.
    lower : bool, optional
        If set to False, upper triangular part is considered.
    hermitian : bool, optional
        If set to False a symmetric complex array is assumed.

    Returns
    -------
    diag : numpy.ndarray
        Array of the diagonals

    Notes
    -----

    Helper function to extract the diagonal of the LDL.T factorization.
    However, the matrix D in the LDL decomposition is not necessarily diagonal,
    rather, block diagonal where the blocks are of the size 1 or 2. This
    function converts the diagonal blocks of size 2 by 2 to a diagonal matrix
    of size 2 by 2 as follows.

    If the 2 by 2 symmetric block is D = [[a, b], [b, c]], we compute its
    determinant det = a*c - b**2. Let s = numpy.sqrt(det). Then, we store D as
    D = [[s, 0], [0, s]]. This matrix has the same determinant as the original
    block, but it is diagonal.
    """

    A_shape, _ = get_block_shape(block_info, trans=False)
    md = A_shape[0]

    diag = numpy.empty((md, ), dtype=numpy.float64)
    diag[:] = numpy.diag(ldu)[:md]
    blk_i = 0  # block index

    for blk in pivs[pivs != 0]:
        # increment the block index and check for 2s
        # if 2 then copy the off diagonals depending on uplo
        inc = blk_i + blk

        if blk == 2:

            if lower:
                off_diag = ldu[blk_i+1, blk_i]
            else:
                off_diag = ldu[blk_i, blk_i+1]

            # Determinant of the 2 by 2 block
            det = ldu[blk_i, blk_i] * ldu[blk_i+1, blk_i+1] - off_diag**2

            # Set the next diagonal such that the determinant of the 2x2 block
            # is preserved.
            diag[blk_i+1] = det / diag[blk_i]

        blk_i = inc

    return diag


# ====================
# pivot to permutation
# ====================

def _pivot_to_permutation(swap_vec, pivs, lower=True):
    """
    This function is taken from
    scipy.linalg.decomp_ldl.py:_construct_tri_factor(). This function also
    exists in ../_cy_linear_algebra/ldl_factor.pyx:_construct_tri_factor(), but
    modified.

    Helper function to obtain permutation from pivots.

    If lower is True the permuted factors are multiplied as L(1)*L(2)*...*L(k).
    Otherwise, the permuted factors are multiplied as L(k)*...*L(2)*L(1). See
    LAPACK documentation for more details.

    Parameters
    ----------
    swap_vec : ndarray
        The array that defines the row swapping indices. If the kth entry is m
        then rows k,m are swapped. Notice that the mth entry is not necessarily
        k to avoid undoing the swapping.
    pivs : ndarray
        The array that defines the block diagonal structure returned by
        _ldl_sanitize_ipiv().
    lower : bool, optional
        The boolean to switch between lower and upper triangular structure.

    Returns
    -------
    perm : ndarray
        The permutation vector that brings the lu to the triangular form
    """

    n = len(pivs)
    perm = numpy.arange(n)
    # Setup the reading order of the permutation matrix for upper/lower
    rs, re, ri = (n-1, -1, -1) if lower else (0, n, 1)

    for ind in range(rs, re, ri):
        s_ind = swap_vec[ind]
        if s_ind != ind:
            # Column start and end positions
            col_s = ind if lower else 0
            col_e = n if lower else ind+1

            # If we stumble upon a 2x2 block include both cols in the perm.
            if pivs[ind] == (0 if lower else 2):
                col_s += -1 if lower else 0
                col_e += 0 if lower else 1
            perm[[s_ind, ind]] = perm[[ind, s_ind]]

    perm = numpy.argsort(perm)

    return perm


# ==========
# ldl factor
# ==========

def _ldl_factor(A, dtype, order, lower, block_info, ic, verbose=False):
    """
    Performs LDL factorization of an input matrix.
    """

    if verbose:
        print(f'ldl decompo {ANSI.FAINT}... ', end='', flush=True)
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

    # Upper-triangular LDL factorization where A = U.T @ D @ U
    ldu, piv = ldl_factor(A_, A_shape[0], lower=lower, overwrite=True,
                          return_as_lapack=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    # Check ldu is overwritten to A.
    if not numpy.may_share_memory(ldu, A_):
        raise RuntimeError('"ldu" is not overwritten to "A".')

    if verbose:
        prof.print_profile(A_shape, dtype)

    return ldu, piv


# =========
# ldl solve
# =========

def _ldl_solve(ldu, piv, B, dtype, order, lower, block_info, ic,
               verbose=False):
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

    x = ldl_solve(ldu, piv, B_, shape=B_shape, lower=lower, overwrite=True)

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
# memdet sym
# ==========

def memdet_sym2(io, verbose):
    """
    memdet algorithm for symmetric matrices. This method uses LDL
    decomposition.
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
    perm = []
    perm_base_index = 0
    lower = True  # using LDL.T instead UDU.T decomposition

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

        # Upper-triangular LDL decomposition
        ldu_11, piv = _ldl_factor(A11, dtype, order, lower,
                                  block_info=(k, k, num_blocks, n), ic=ic,
                                  verbose=verbose)

        # Get diagonal and permutations. The next couple of lines are taken
        # from ../_cy_linear_algebra/ldl_factor.pyx:ldl_factor() function.
        piv_ = piv + 1  # convert from 0-indexing to 1-indexing (Fortran style)
        swap_arr, pivot_arr = _sanitize_piv(piv_, lower=lower)
        diag_ldu_11 = _get_diag(ldu_11, pivot_arr, (k, k, num_blocks, n),
                                lower=lower)
        perm_ldu_11 = _pivot_to_permutation(swap_arr, pivot_arr, lower=lower)

        # log-determinant
        ld += numpy.sum(numpy.log(numpy.abs(diag_ldu_11)))

        # Sign of determinant
        sign *= numpy.prod(numpy.sign(diag_ldu_11))

        # Save diagonals and permutations
        diag.append(numpy.copy(diag_ldu_11))
        perm.append(numpy.copy(perm_ldu_11) + perm_base_index)
        perm_base_index += perm_ldu_11.size

        # Print progress count
        progress.count()

        # Row iterations
        for j in range(num_blocks-1, k, -1):

            # Vertical upward movement of block from diagonal block to top
            i_start = j
            i_end = k
            i_step = -1
            i_range = numpy.arange(i_start, i_end, i_step)

            # Push the second iterator index to the last of sequence. This
            # makes the path of blocks Hamiltonian in the line-graph.
            if len(i_range) > 2:
                i_second_element = i_range[1]
                i_range = numpy.delete(i_range, 1)
                i_range = numpy.append(i_range, i_second_element)

            # print task to be processed
            if verbose:
                progress.print_task(k, i_start, j)

            load_block(io, A12, k, j, trans=False, verbose=verbose)

            # Row iterations
            for i in i_range:

                # print task to be processed
                if verbose and (i != i_start):
                    progress.print_task(k, i, j)

                # When the space-filling curve changes direction, do not
                # read new A12, rather use the previous matrix already
                # loaded to memory
                if (j == num_blocks-1) or (i != i_start):
                    load_block(io, A21_t, k, i, perm=None, verbose=verbose)

                if i == i_start:
                    # Solving X = A11^{-1} A12. This overwrites X to A12
                    X = _ldl_solve(ldu_11, piv, A12, dtype, order,
                                   lower=lower,
                                   block_info=(k, j, num_blocks, n), ic=ic,
                                   verbose=verbose)

                # Compute Schur complement
                if (i == k+1) and (j == k+1):

                    # Use A11 instead of A22
                    load_block(io, A11, i, j, verbose=verbose)

                    # Overwrite A11 with Schur complement
                    _schur_complement(A21_t, X, A11, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)
                else:

                    load_block(io, A22, i, j, verbose=verbose)

                    # Overwrite A22 with Schur complement
                    _schur_complement(A21_t, X, A22, dtype, order,
                                      block_info=(i, j, num_blocks, n), ic=ic,
                                      verbose=verbose)

                    # Store A22 to disk. This point reaches only when num_block
                    # is greater than 2 (hence using scratch)
                    store_block(io, A22, i, j, verbose=verbose)

                # Print progress count
                progress.count()

    # concatenate diagonals and permutations of blocks of U
    diag = numpy.concatenate(diag)
    perm = numpy.concatenate(perm)

    # Instructions count
    if ic is not None:
        io['profile']['hw_inst_count'] = ic.get_count()
        io['profile']['flops'] = ic.get_flops()

    return ld, sign, diag, perm
