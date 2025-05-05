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
import psutil
import numpy
from .memory import Memory
from .disk import Disk
from .._openmp import get_avail_num_threads
from ._utilities import human_readable_time, human_readable_mem
from ._ansi import ANSI

__all__ = ['Profile']


# ================
# global variables
# ================

# Time in seconds where if a task takes longer than that, the time log in
# verbose print-outs will appear as bright bold color, hence, making attention.
time_attention = 60

# The ratio of block size in which if a memory or disk io operation in bytes
# take larger volume than that of ratio of the block size in bytes, the memory
# or disk io logs in verbose print-outs will appear in bright bold colors.
mem_attention_ratio = 0.2

# The threshold where above this threshold, the cpu utilization in percent,
# in logs in verbose print-outs will appear in bright bold color.
cpu_attention = 90


# =======
# Profile
# =======

class Profile(object):
    """
    Profile a process.

    See Also
    --------

    detkit.Memory
    detkit.Disk

    Methods
    -------

    set
    wall_time
    proc_time
    cpu_utilization
    mem_now
    mem_peak
    disk_read
    disk_write
    print_profile

    Notes
    -----

    **Dropping Cache:**

    You may need to drop cache to get accurate results on disk's read. To drop
    cache, execute the following:

    .. code-block:: bash

        echo 3 | sudo tee /proc/sys/vm/drop_caches

    While dropping cache is necessary to inquiry disk's *read*, this is not
    needed to inquiry disk's *write*.

    Examples
    --------

    .. code-block:: python

        >>> from detkit import Profile, memdet, human_readable_time, \\
        ...    human_readable_mem

        >>> # Create a random matrix
        >>> import numpy
        >>> A = numpy.random.randn(10000, 10000)

        >>> # Initialize profile
        >>> prof = Profile()

        >>> # Set the starting point of memory inquiry
        >>> prof.set()

        >>> # Perform a memory-intensive operation
        >>> ld = memdet(A)

        >>> # Inquiry wall time
        >>> print(human_readable_time(prof.wall_time()))
        5.0 sc

        >>> # Inquiry process time
        >>> print(human_readable_time(prof.proc_time()))
        19.0 sc

        >>> # Check CPU utilization (in percent)
        >>> print(prof.cpu_utilization())
        50.51

        >>> # Inquiry the current memory allocation
        >>> print(human_readable_mem(prof.mem_now()))
        88.1 KB

        >>> # Inquiry the peak memory allocation
        >>> print(human_readable_mem(prof.mem_peak()))
        763.2 MB

        >>> # Inquiry read from disk during the above operation
        >>> print(prof.disk_read())
        909312.0

        >>> # Inquiry write to disk during the above operation, in MB unit
        >>> print(prof.disk_write())
        10776576.0

        >>> # Inquiry write to disk during the above operation, in MB unit
        >>> prof.print_profile(shape=A.shape, dtype=A.dtype)
        | time:   5.0 sc | cpu:  50% | alloc:  763.2 MB | read: 888 KB |
        | write:   10.2 MB |
    """

    # ----
    # init
    # ----

    def __init__(self):
        """
        Initialization.
        """

        self.init_wall_time = None
        self.init_proc_time = None
        self.init_cpu_times = None
        self.mem = None
        self.disk = None
        self.num_threads = get_avail_num_threads()

        self.set()

    # ---
    # set
    # ---

    def set(self):
        """
        Sets or resets the start point of profiling.

        See Also
        --------

        wall_time
        proc_time
        mem_now
        mem_peak
        disk_read
        disk_write
        cpu_utilization

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 11

            >>> from detkit import Profile, memdet, human_readable_time
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set the starting point of memory inquiry
            >>> prof.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry wall time
            >>> print(human_readable_time(prof.wall_time()))
            5.0 sc
        """

        # Set time
        self.init_wall_time = time.time()
        self.init_proc_time = time.process_time()

        # Set cpu times
        self.init_cpu_times = psutil.cpu_times(percpu=True)

        # Set disk
        self.disk = Disk()
        self.disk.set()

        # Set memory (this should be set after all the above so that the above
        # objects' memory do not be count)
        self.mem = Memory()
        self.mem.set()

    # ---------
    # wall time
    # ---------

    def wall_time(self):
        """
        Measure elapsed wall time.

        Returns
        -------

        wall_time : float
            Elapsed wall time since calling :func:`detkit.Profile.set`.

        See Also
        --------

        set
        proc_time

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 8

            >>> from detkit import Profile, memdet, human_readable_time
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set the starting point of memory inquiry
            >>> prof.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry wall time
            >>> print(human_readable_time(prof.wall_time()))
            5.0 sc
        """

        if self.init_wall_time is None:
            raise RuntimeError('"profile" has not been set.')

        wall_time_ = time.time() - self.init_wall_time

        return wall_time_

    # ---------
    # proc time
    # ---------

    def proc_time(self):
        """
        Measure process time.

        Returns
        -------

        wall_time : float
            Process time since calling :func:`detkit.Profile.set`.

        See Also
        --------

        set
        wall_time

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 8

            >>> from detkit import Profile, memdet, human_readable_time
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set the starting point of memory inquiry
            >>> prof.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry process time
            >>> print(human_readable_time(prof.proc_time()))
            19.0 sc
        """

        if self.init_proc_time is None:
            raise RuntimeError('"profile" has not been set.')

        proc_time_ = time.process_time() - self.init_proc_time

        return proc_time_

    # ---------------
    # cpu utilization
    # ---------------

    def cpu_utilization(self):
        """
        Measure CPU utilization.

        Returns
        -------

        cpu_util : float
            CPu utilization in percent.

        See Also
        --------

        set
        wall_time
        proc_time

        Notes
        -----

        CPU utilization is defined as follows. Suppose there are :math:`m`
        CPU threads. For each thread :math:`i = 1, \\dots, m`, we define

        * :math:`u_i`: thread's user time
        * :math:`s_i`: thread's system time
        * :math:`d_i`: thread's idle time

        The CPU utilization :math:`\\gamma`, in percent, is defined by:

        .. math::

            \\gamma = 100 \\times \\frac{1}{m} \\sum_{i}^{m}
            \\frac{u_i + s_i}{u_i + s_i + d_i}

        Examples
        --------

        Inquiry the CPU utilization for matrix-matrix multiplication
        :math:`\\mathbf{C} \\leftarrow \\alpha \\mathbf{A} \\mathbf{B} +
        \\beta \\mathbf{C}` on a machine with 8 CPU threads:

        .. code-block:: python

            >>> from detkit import matmul, Profile

            >>> # Create random matrices
            >>> import numpy
            >>> n = 10000
            >>> A = numpy.random.randn(n, n)
            >>> B = numpy.random.randn(n, n)
            >>> C = numpy.random.randn(n, n)

            >>> # Make sure arrays have column-ordering
            >>> A = numpy.asfortranarray(A)
            >>> B = numpy.asfortranarray(B)
            >>> C = numpy.asfortranarray(C)

            >>> # Initiate profiling
            >>> prof = Profile()
            >>> prof.set()

            >>> # Perform matrix-matrix multiplication
            >>> alpha, beta = 1.0, 2.0
            >>> X = matmul(A, B, C, alpha=alpha, beta=beta, overwrite=True)

            >>> # Check CPU utilization (in percent)
            >>> print(prof.cpu_utilization())
            56.28

        The above result means 54.2 percent of all 8 CPU threads were utilized.
        """

        final_cpu_times = psutil.cpu_times(percpu=True)

        # Calculate CPU utilization for each logical CPU
        utilizations = []
        for start, end in zip(self.init_cpu_times, final_cpu_times):
            user_time = end.user - start.user
            system_time = end.system - start.system
            idle_time = end.idle - start.idle

            active_time = user_time + system_time
            total_time = active_time + idle_time

            if total_time != 0:
                utilization = 100 * active_time / total_time
            else:
                utilization = 0.0

            utilizations.append(utilization)

        # Calculate the average CPU utilization across all logical CPUs
        average_utilization = numpy.mean(utilizations)

        return average_utilization

    # -------
    # mem now
    # -------

    def mem_now(self):
        """
        Inquiry current net memory allocation since profiling is set.

        Returns
        -------

        current_mem : float
            The net memory allocation and deallocation since calling
            :func:`detkit.Profile.set`.

        See Also
        --------

        set
        mem_peak

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 17

            >>> from detkit import Profile, memdet, human_readable_mem
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set the starting point of memory inquiry
            >>> prof.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry the current memory allocation
            >>> print(human_readable_mem(prof.mem_now()))
            79.4 KB
        """

        if self.mem is None:
            raise RuntimeError('"profile" has not been set.')

        mem_now = self.mem.now()

        return mem_now

    # --------
    # mem peak
    # --------

    def mem_peak(self):
        """
        Inquiry peak memory allocation since profiling is set.

        Returns
        -------

        peak_mem : float
            The peak memory allocation since calling
            :func:`detkit.Profile.set`.

        See Also
        --------

        set
        mem_now

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 17

            >>> from detkit import Profile, memdet, human_readable_mem
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set the starting point of memory inquiry
            >>> prof.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry the peak memory allocation
            >>> print(human_readable_mem(prof.mem_peak()))
            763.2 MB
        """

        if self.mem is None:
            raise RuntimeError('"profile" has not been set.')

        mem_peak = self.mem.peak()

        return mem_peak

    # ---------
    # disk read
    # ---------

    def disk_read(self):
        """
        Inquiry the amount of read from disk.

        Returns
        -------

        write_size : int
            The amount of read from disk in bytes.

        See Also
        --------

        disk_write

        Notes
        -----

        The read amount is measured from the point where
        :func:`detkit.Profile.set` is called to the current.

        .. note::

            To properly measure the read from disk, the memory cache should be
            dropped before calling this function. To do so, execute the
            following in terminal:

            .. code-block:: bash

                echo 3 | sudo tee /proc/sys/vm/drop_caches

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 15

            >>> from detkit import Profile, memdet

            >>> # Initialize profile
            >>> prof = Profile()

            >>> # Set (or reset) the starting point of inquiry
            >>> prof.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry read from disk during the above operation
            >>> print(prof.disk_read())
            909312.0
        """

        if self.disk is None:
            raise RuntimeError('"profile" has not been set.')

        disk_read_ = self.disk.read()

        return disk_read_

    # ----------
    # disk write
    # ----------

    def disk_write(self):
        """
        Inquiry the amount of write to disk.

        Returns
        -------

        write_size : int
            The amount of write to disk in bytes.

        See Also
        --------

        disk_read

        Notes
        -----

        The write amount is measured from the point where
        :func:`detkit.Profile.set` is called to the current.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 15

            >>> from detkit import Profile, memdet

            >>> # Initialize with MB unit
            >>> prof = Profile()

            >>> # Set (or reset) the starting point of inquiry
            >>> prof.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry write to disk during the above operation, in MB unit
            >>> print(prof.disk_write())
            10776576.0
        """

        if self.disk is None:
            raise RuntimeError('"profile" has not been set.')

        disk_write_ = self.disk.write()

        return disk_write_

    # -------------
    # print profile
    # -------------

    def print_profile(self, shape=None, dtype=None):
        """
        Print profile information.

        Parameters
        ----------

        shape : tuple, default=None
            A tuple of size two representing the shape of the matrix.

        dtype : str, default=None
            The data type of the matrix.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 15

            >>> from detkit import Profile, memdet

            >>> # Initialize with MB unit
            >>> prof = Profile()

            >>> # Set (or reset) the starting point of inquiry
            >>> prof.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry write to disk during the above operation, in MB unit
            >>> prof.print_profile(shape=A.shape, dtype=A.dtype)
            | time:  661 ms | cpu:  20% | alloc:    5.4 MB | read:      0  B |
            | write:   10.2 MB |
        """

        # Time and memory inquiries before computing CPU utilization
        wall_time = self.wall_time()
        mem_peak = self.mem_peak()
        disk_read = self.disk_read()
        disk_write = self.disk_write()

        if (shape is not None) or (dtype is not None):
            mem_attention = mem_attention_ratio * shape[0] * shape[1] * \
                numpy.dtype(dtype).itemsize
        else:
            mem_attention = None

        string = f'{ANSI.BLINK_OFF}{ANSI.RESET}'

        # Wall time
        hr_wall_time = human_readable_time(wall_time, pad=True)
        string += f'| {ANSI.MAGENTA}{ANSI.FAINT}time: ' + \
            f'{ANSI.RESET}{ANSI.MAGENTA}'
        if wall_time >= time_attention:
            string += f'{ANSI.BOLD}{ANSI.BR_MAGENTA}'
        string += f'{hr_wall_time}{ANSI.RESET} | '

        # CPU utilization
        cpu_utilization = self.cpu_utilization()
        string += f'{ANSI.CYAN}{ANSI.FAINT}cpu: {ANSI.RESET}{ANSI.CYAN}'
        if cpu_utilization >= cpu_attention:
            string += f'{ANSI.BOLD}{ANSI.BR_CYAN}'
        string += f'{cpu_utilization:>3.0f}%{ANSI.RESET} | '

        # Peak memory allocation
        hr_mem_peak = human_readable_mem(mem_peak, pad=True)
        string += f'{ANSI.GREEN}{ANSI.FAINT}alloc: {ANSI.RESET}{ANSI.GREEN}'
        if (mem_attention is not None) and (mem_peak >= mem_attention):
            string += f'{ANSI.BOLD}{ANSI.BR_GREEN}'
        string += f'{hr_mem_peak}{ANSI.RESET} | '

        # Disk read
        hr_disk_read = human_readable_mem(disk_read, pad=True)
        string += f'{ANSI.YELLOW}{ANSI.FAINT}read: {ANSI.RESET}{ANSI.YELLOW}'
        if (mem_attention is not None) and (disk_read >= mem_attention):
            string += f'{ANSI.BOLD}{ANSI.BR_YELLOW}'
        string += f'{hr_disk_read}{ANSI.RESET} | '

        # Disk write
        hr_disk_write = human_readable_mem(disk_write, pad=True)
        string += f'{ANSI.RED}{ANSI.FAINT}write: {ANSI.RESET}{ANSI.RED}'
        if (mem_attention is not None) and (disk_write >= mem_attention):
            string += f'{ANSI.BOLD}{ANSI.BR_RED}'
        string += f'{hr_disk_write}{ANSI.RESET} |'

        print(string, flush=True)
