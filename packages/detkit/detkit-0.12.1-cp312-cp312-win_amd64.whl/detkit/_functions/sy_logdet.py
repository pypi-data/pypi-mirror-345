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
import scipy

__all__ = ['sy_logdet']


# ====================
# pivot to permutation
# ====================

def pivot_to_permutation(piv):
    """
    Convert pivot of indices to permutation of indices.
    """

    perm = numpy.arange(len(piv))
    for i in range(len(piv)):
        perm[i], perm[piv[i]] = perm[piv[i]], perm[i]

    return perm


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


# =========
# sy logdet
# =========

def sy_logdet(
        A,
        sym_pos=False,
        overwrite_A=False):
    """
    Implementation of `logdet` function using scipy.
    """

    if sym_pos:
        L = scipy.linalg.cholesky(A, lower=True, overwrite_a=overwrite_A,
                                  check_finite=False)
        diag_L = numpy.diag(L).astype(numpy.complex128)
        logdet_L = numpy.real(numpy.sum(numpy.log(diag_L)))
        ld = 2.0*logdet_L
        sign = 1

    else:
        lu, piv = scipy.linalg.lu_factor(A, overwrite_a=overwrite_A,
                                         check_finite=False)
        diag_lu = numpy.diag(lu)
        ld = numpy.sum(numpy.log(numpy.abs(diag_lu)))

        perm = pivot_to_permutation(piv)
        parity = _permutation_parity(perm)
        sign = numpy.prod(numpy.sign(diag_lu)) * parity

    return ld, sign
