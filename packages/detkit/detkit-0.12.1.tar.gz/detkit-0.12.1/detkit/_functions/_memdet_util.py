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

import signal
import os
import sys
from ._ansi import ANSI
from .profile import Profile
import numpy
from multiprocessing import shared_memory


__all__ = ['Progress', 'signal_handler', 'get_array', 'get_block_shape',
           'deep_copy']


# ==============
# signal handler
# ==============

def signal_handler(sig, frame):
    """
    Function to handle signals. When Ctrl+Z is pressed, the terminal colors
    still use the ANSI colors that was set during the execution of the code.
    To properly reset the ANSI codes, this function handles the resetting in
    the event of any termination signal.
    """

    if sig == signal.SIGINT:
        print(f'{ANSI.RESET}', flush=True)
        sys.exit(0)

    elif sig == signal.SIGTSTP:
        print(f'{ANSI.RESET}', flush=True)
        os.kill(os.getpid(), signal.SIGSTOP)  # Suspend the process


# ========
# Progress
# ========

class Progress(object):
    """
    Prints memdet progress.
    """

    # ----
    # init
    # ----

    def __init__(self, num_blocks, assume, verbose=False):
        """
        Initialize counter.
        """

        self.verbose = verbose
        self.counter = 0

        if assume == 'gen':

            # Sum of integer squares from 1 to num_blocks-1
            S1 = (num_blocks-1) * num_blocks * (2*num_blocks-1) // 6

            # Total count
            self.total_count = S1 + num_blocks

        elif assume in ['sym', 'spd']:

            # Sum of integer squares from 1 to num_blocks-1
            S1 = (num_blocks-1) * num_blocks * (2*num_blocks-1) // 6

            # Sum of integers from 1 to num_blocks-1
            S2 = (num_blocks-1) * num_blocks // 2

            # Total count
            self.total_count = (S1 + S2) // 2 + num_blocks

        else:
            raise ValueError('"assume" should be either "gen", "sym", or ' +
                             '"spd".')

        self.tot_width = len(str(self.total_count))
        self.row_width = len(str(num_blocks))

    # ----------
    # print task
    # ----------

    def print_task(self, k, i, j):
        """
        Prints the task that is going to be processed.
        """

        if self.verbose:

            if (k == 0) and (i == 0) and (j == 0):
                print('', flush=True)

            print(f'{ANSI.FAINT}' +
                  f'processing diag blk: {k+1:>0{self.row_width}d} ' +
                  f'(row blk: {i+1:>0{self.row_width}d}, ' +
                  f'col blk: {j+1:>0{self.row_width}d})' +
                  f'{ANSI.RESET}',
                  flush=True)

    # -----
    # count
    # -----

    def count(self):
        """
        Counts the progress and prints if verbose.
        """

        self.counter += 1
        if self.verbose:
            # print(f'{ANSI.INVERSE}{ANSI.BR_GREEN}{ANSI.BOLD}{ANSI.FAINT}' +
            print(f'{ANSI.BR_BG_GREEN}{ANSI.BOLD}{ANSI.BLACK}' +
                  f'progress: {ANSI.RESET}' +
                  f'{ANSI.BR_BG_GREEN}{ANSI.BOLD}{ANSI.BLACK}' +
                  f'{self.counter:>0{self.tot_width}d}/' +
                  f'{self.total_count:>{self.tot_width}d}{ANSI.RESET}\n',
                  flush=True)


# =========
# get array
# =========

def get_array(shared_mem, shape, dtype, order):
    """
    Get numpy array from shared memory buffer.
    """

    if len(shape) != 2:
        raise ValueError('"shape" should have length of two.')

    if isinstance(shared_mem, shared_memory.SharedMemory):
        # This is shared memory. Return its buffer.
        return numpy.ndarray(shape=shape, dtype=dtype, order=order,
                             buffer=shared_mem.buf)

    else:
        # This is already numpy array. Return itself.
        return shared_mem


# ===============
# get block shape
# ===============

def get_block_shape(block_info, trans=False):
    """
    When m is not a divider of n, the block matrix might not be square, and it
    its shape will depend on the indices i and j of the block.

    Note that the shape of matrix might be smaller than its shape as stored on
    memory, meaning that the intended matrix that we want to work with might be
    a sub-matrix within the block. This function returns the shape of the
    matrix.
    """

    # i and j are the indices of the position of the block within the matrix
    i, j, num_blocks, n = block_info

    # Size of all blocks except the last block
    m = (n + num_blocks - 1) // num_blocks

    # Size of last block
    md = (n-1) % m + 1

    # Shape of block on memory
    block_shape_on_mem = (m, m)

    # Number of rows of the block
    if i == num_blocks - 1:
        m1 = md
    else:
        m1 = m

    # Number of columns of the block
    if j == num_blocks - 1:
        m2 = md
    else:
        m2 = m

    if trans:
        block_shape = (m2, m1)
    else:
        block_shape = (m1, m2)

    return block_shape, block_shape_on_mem


# =========
# deep copy
# =========

def deep_copy(source, dest, dtype, order, block_info, verbose=False):
    """
    Deep copy from source array to destination array.

    This function is called on blocks that are not on the last row/column.
    As such, in case when num_blocks is not a divider of matrix size n, and
    hence, when the shape of the last row/column blocks are smaller, this
    function is not called. Rather, this function is called on the inner
    blocks, where the shape of the array is the same as their shape on memory.
    Hence, the shape of source and destination arrays are similar.
    """

    if verbose:
        print(f'copy memory {ANSI.FAINT}... ', end='', flush=True)
        prof = Profile()

    # Find the size of block on memory
    shape, shape_on_mem = get_block_shape(block_info, trans=False)

    # Get buffer from shared memory
    source_ = get_array(source, shape_on_mem, dtype, order)
    dest_ = get_array(dest, shape_on_mem, dtype, order)

    # Deep copying
    dest_[:shape[0], :shape[1]] = source_[:shape[0], :shape[1]]

    if verbose:
        prof.print_profile(shape, dtype)
