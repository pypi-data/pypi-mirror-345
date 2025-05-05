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
from ._memdet_util import Progress, get_array, get_block_shape, deep_copy
from ._memdet_block import load_block, store_block
from ._memdet_gen import _solve_triangular
from ._ansi import ANSI
from .profile import Profile
from ._memdet_gen import _schur_complement
from .._cy_linear_algebra import ldl_factor, ldl_solve, solve_diag
from .._cy_linear_algebra.ldl_factor import _sanitize_piv, \
    _construct_tri_factor
from .._device import InstructionsCounter

__all__ = ['memdet_sym']


# ===========
# extract ldu
# ===========

def _extract_ldu(ldu, pivs, dtype, order, block_info, lower=True):
    """
    Originally taken from ``scipy.linalg.decomp_ldl.py:_get_d_and_l()``
    function. This function is modified version of the ``_get_d_and_l()``
    function in ``../_cy_linear_algebra/ldl_factor.pyx:_get_d_and_l()``.

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

    # Diagonals (1D array of size md). Din LDU has diagonal blocks of size 1x1
    # or 2x2. For those 2x2 blocks, this array stores only diagonals of 2x2,
    # but modifies the second diagonal so that it preserves the determinant.
    # Note: this array should be float64 (as higher precision) as its elements
    # will be summed for computing log-det.
    diag = numpy.empty((md, ), dtype=numpy.float64)
    diag[:] = numpy.diag(ldu)[:md].astype(numpy.float64)

    # Bock diagonals (2D array of size md by 2). First column are diagonals of
    # D in LDU, and the second column are the one-off diagonals of D if LDU.
    # D is mixed-diagonal, some meaning its diagonals are either blocks of size
    # 1x1 or 2x2.
    block_diag = numpy.zeros((md, 2), dtype=dtype, order=order)
    block_diag[:, 0] = diag[:]

    # Block index
    blk_i = 0

    for blk in pivs[pivs != 0]:
        # increment the block index and check for 2s
        # if 2 then copy the off diagonals depending on uplo
        inc = blk_i + blk

        if blk == 2:

            if lower:
                off_diag = ldu[blk_i+1, blk_i]
                ldu[blk_i+1, blk_i] = 0.0
            else:
                off_diag = ldu[blk_i, blk_i+1]
                ldu[blk_i, blk_i+1] = 0.0

            # Store off diagonal in the second column of block_diag array
            block_diag[blk_i, 1] = off_diag

            # Determinant of the 2 by 2 block
            det = ldu[blk_i, blk_i] * ldu[blk_i+1, blk_i+1] - off_diag**2

            # Set the next diagonal such that the determinant of the 2x2 block
            # is preserved.
            diag[blk_i+1] = det / diag[blk_i]

        # Make diagonals to be 1
        ldu[blk_i, blk_i] = 1.0
        if blk == 2:
            ldu[blk_i+1, blk_i+1] = 1.0

        blk_i = inc

    return diag, block_diag


# ====================
# unpermute tri factor
# ====================

def _unpermute_tri_factor(A, perm, dtype, order, block_info):
    """
    In-place equivalent of A = A[perm,:].
    Uses cycle-decomposition to avoid a new array.
    """

    # Find the size of block on memory
    A_shape, A_shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    A_ = get_array(A, A_shape_on_mem, dtype, order)

    n = A_shape[0]
    visited = numpy.zeros(n, dtype=bool)

    for start in range(n):

        if visited[start]:
            continue

        cycle = []
        i = start

        while not visited[i]:

            cycle.append(i)
            visited[i] = True
            i = perm[i]

        if len(cycle) <= 1:
            continue

        # forward-rotate each cycle
        tmp = A_[cycle[0]].copy()

        for k in range(len(cycle)-1):
            A_[cycle[k]] = A_[cycle[k+1]]

        A_[cycle[-1]] = tmp


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

    # LDL factorization (Lower: A = L @ D @ L.T, or Upper: A = U.T @ D @ U)
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

    This function solves X = A^{-1} B (and not X = L^{-1} B) using the
    LDL factor A = P L D L P.T.

    Note: this function is no longer used in memdet_sym, as it is up to orders
    of magnitude slower. The culprit is ?sytrs from LAPACK.
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
# solve diag
# ==========

def _solve_diag(block_diag, B, dtype, order, block_info, ic, verbose=False):
    """
    Solve by a block-diagonal matrix.

    The block_diag input is a 2D array with two columns, representing D, where
    diagonals of D are either 1x1 or 2x2 blocks.

    This function performs B <-- D^{-1} @ B.
    """

    if verbose:
        print(f'solve bdiag {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    # Find the size of block on memory
    B_shape, B_shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    B_ = get_array(B, B_shape_on_mem, dtype, order)

    # Shape of D and B
    md = block_diag.shape[0]
    nrhs = B_shape_on_mem[1]

    # Start performance counter
    if ic is not None:
        ic.start()

    X, info = solve_diag(block_diag, B_, shape=(md, nrhs), overwrite=True)

    # Stop performance counter
    if ic is not None:
        ic.stop()

    if info != 0:
        raise RuntimeError('Diagonal solved encountered zero diagonal in ' +
                           'LDL decomposition.')

    if verbose:
        prof.print_profile(B_shape, dtype)

    return X


# ==========
# memdet sym
# ==========

def memdet_sym(io, verbose):
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

        # Lower-triangular LDL decomposition
        ldu_11, piv = _ldl_factor(A11, dtype, order, lower=lower,
                                  block_info=(k, k, num_blocks, n), ic=ic,
                                  verbose=verbose)

        # Get diagonal and permutations. The next couple of lines are taken
        # from ../_cy_linear_algebra/ldl_factor.pyx:ldl_factor() function.
        piv_ = piv + 1  # convert from 0-indexing to 1-indexing (Fortran style)
        swap_arr, pivot_arr = _sanitize_piv(piv_, lower=lower)

        # Extract diagonals in two forms: The block_diag_ldu_11 is an array of
        # two columns, where the first column contains diagonals of ldu, while
        # the second column contains 1-off diagonals of ldu, since d in ldu
        # also has 2x2 diagonal blocks. In contrast, diag_ldu_11 is a 1D array
        # of diagonals. In other 2x2 blocks, the second diagonal element in
        # those blocks is modified so they have the same determinant.
        # This function also modifies ldu_11 in-place: in those 2x2 diagonal
        # blocks, the ldu_11 element right below diagonal is set to zero.
        diag_ldu_11, block_diag_ldu_11 = _extract_ldu(
                ldu_11, pivot_arr, dtype, order,
                block_info=(k, k, num_blocks, n), lower=lower)

        # The ldu_11 at this point is still not the actual L. The function
        # below makes some necessary permutations, but it converts ldu_11 to
        # P times L instead (not L itself). After this function, ldu_11
        # becomes exactly what scipy.linag.ldl outputs. However, all
        # computations here are performed in-place (as opposed to scipy).
        _, perm_ldu_11 = _construct_tri_factor(ldu_11, swap_arr, pivot_arr,
                                               lower=lower)

        # Un-permute P*L so L becomes the actual L. This is done in-place.
        _unpermute_tri_factor(ldu_11, perm_ldu_11, dtype, order,
                              block_info=(k, k, num_blocks, n))

        # log-determinant
        ld += numpy.sum(numpy.log(numpy.abs(diag_ldu_11)))

        # Sign of determinant. Note: unlike _memdet_gen for generic matrices
        # where sign was the product of the sign of diagonals and permutation
        # P, here in LDL method, we have two permutations in A = P L D L.T P.T,
        # and the product of parity of P and P.T is sign(P)**2, which is always
        # +1, so we do not need to compute the parity of P at all.
        sign *= numpy.prod(numpy.sign(diag_ldu_11))

        # Save diagonals and permutations
        diag.append(numpy.copy(diag_ldu_11))
        perm.append(numpy.copy(perm_ldu_11) + perm_base_index)
        perm_base_index += perm_ldu_11.size

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

            # Swap pointers B and C to alternate on memory blocks A12 and A21t
            if ((num_blocks-1 - j) % 2 == 0):
                B = A12
                C = A21_t
            else:
                B = A21_t
                C = A12

            if j == num_blocks-1:
                # Load P.T @ A12 (P.T is applied using perm)
                load_block(io, B, k, j, perm=perm_ldu_11, verbose=verbose)

                # Perform B <-- L^{-1} B
                _solve_triangular(ldu_11, B, dtype, order, trans=False,
                                  lower=lower, unit_diagonal=True,
                                  block_info=(k, j, num_blocks, n), ic=ic,
                                  verbose=verbose)

            # Copy B (source) to C (destination) before B is modified next.
            deep_copy(B, C, dtype, order, block_info=(k, j, num_blocks, n),
                      verbose=verbose)

            # Perform B <-- D^{-1} @ B in-place where D is block diagonal
            _solve_diag(block_diag_ldu_11, B, dtype, order,
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
                    # Do nothing as C is already copied from B before B was
                    # pre-multiplied with D^{-1}.
                    pass

                else:
                    # Load C and perform C <-- L^{-1} @ P.T @ C and store it.
                    if j == num_blocks-1:
                        # First time loading C from input array, so, load the
                        # permuted matrix P.T @ A12. This is load from
                        # input array not scratch.
                        load_block(io, C, k, i, perm=perm_ldu_11,
                                   verbose=verbose)
                    else:
                        # Here, C was loaded before from input array, and
                        # L^{-1} was pre-multiplied and its transpose was
                        # stored to disk. Hence, no need to load permutation
                        # anymore. This is loaded from scratch (if
                        # num_block > 2).
                        load_block(io, C, k, i, perm=None, verbose=verbose)

                    if j == num_blocks-1:
                        # Here, first time C is loaded and has not been
                        # pre-multiplied by L^{-1} yet. Here we do so.
                        _solve_triangular(ldu_11, C, dtype, order, trans=False,
                                          lower=lower, unit_diagonal=True,
                                          block_info=(k, i, num_blocks, n),
                                          ic=ic, verbose=verbose)

                        # Only need to store C back to scratch if we know it is
                        # needed to be loaded in the future. For the case of
                        # i=j and i=j-1, C will never be loaded again, so no
                        # need to store C for those two cases.
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

    # concatenate diagonals and permutations of blocks of U
    diag = numpy.concatenate(diag)
    perm = numpy.concatenate(perm)

    # Instructions count
    if ic is not None:
        io['profile']['hw_inst_count'] = ic.get_count()
        io['profile']['flops'] = ic.get_flops()

    return ld, sign, diag, perm
