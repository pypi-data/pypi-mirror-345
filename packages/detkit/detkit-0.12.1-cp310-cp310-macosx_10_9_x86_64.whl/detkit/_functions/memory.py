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

import tracemalloc
import numpy
import psutil

__all__ = ['Memory']


# ======
# Memory
# ======

class Memory(object):
    """
    Trace memory allocation.

    Parameters
    ----------

    unit : int or str {``'B'``, ``'KB'``, ``'MB'``, ``'GB'``, ``'TB'``}, \
            default=``1``
        Unit of memory either as a string, such as ``'KB'``, representing
        1024 bytes, or directly specify the number of bytes as an integer.

    See Also
    --------

    detkit.Disk
    detkit.Profile

    Methods
    -------

    set
    now
    peak
    info

    Examples
    --------

    .. code-block:: python
        :emphasize-lines: 11, 21

        >>> from detkit import Memory, memdet
        >>> import numpy

        >>> # Create a random matrix
        >>> A = numpy.random.randn(10000, 10000)

        >>> # Initialize with MB unit
        >>> mem = Memory(unit='MB')

        >>> # Set the starting point of memory inquiry
        >>> mem.set()

        >>> # Perform a memory-intensive operation
        >>> ld = memdet(A)

        >>> # Inquiry current allocated memory in MB unit
        >>> print(mem.now())
        82.3

        >>> # Inquiry the peak allocated memory in MB unit
        >>> print(mem.peak())
        82.3

        >>> # Reset the memory counter and inquiry again
        >>> mem.set()
        >>> print(mem.now())
        0.0
    """

    # ====
    # init
    # ====

    def __init__(self, unit=1):
        """
        Initialization.
        """

        self._mem = 0
        self._peak = 0
        self._init_mem = 0
        self._init_peak = 0

        # Set unit size
        if isinstance(unit, str):
            if unit == 'B':
                self.unit_size = 1
            elif unit == 'KB':
                self.unit_size = 1024
            elif unit == 'MB':
                self.unit_size = 1024**2
            elif unit == 'GB':
                self.unit_size = 1024**3
            elif unit == 'TB':
                self.unit_size = 1024**4
            else:
                raise ValueError('"unit" is invalid.')

        elif isinstance(unit, (int, numpy.int8, numpy.int16, numpy.int32,
                               numpy.int64, numpy.uint8, numpy.uint16,
                               numpy.uint32, numpy.uint64)):
            self.unit_size = int(unit)

        else:
            raise ValueError('"unit" should be integer or string.')

        self.set()

    # ===
    # set
    # ===

    def set(self):
        """
        Set or reset tracing allocated memory.

        See Also
        --------

        now
        peak

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 11, 21

            >>> from detkit import Memory, memdet
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize with KB unit
            >>> mem = Memory(unit='KB')

            >>> # Set the starting point of memory inquiry
            >>> mem.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry current allocated memory in KB unit
            >>> print(mem.now())
            781489.4

            >>> # Reset the memory counter and inquiry again
            >>> mem.set()
            >>> print(mem.now())
            0.1
        """

        tracemalloc.start()
        tracemalloc.clear_traces()
        tracemalloc.reset_peak()

        mem, peak = tracemalloc.get_traced_memory()
        self._init_mem = mem
        self._init_peak = peak
        self._mem = 0
        self._peak = 0

    # ====
    # read
    # ====

    def _read(self):
        """
        Inquiries current and peak memory allocation.
        """

        mem, peak = tracemalloc.get_traced_memory()
        self._mem = mem - self._init_mem
        self._peak = peak - self._init_peak

    # ===
    # now
    # ===

    def now(self):
        """
        Inquiry current memory allocation.

        Returns
        -------

        current_mem : float
            The net memory allocation and deallocation since calling
            :func:`detkit.Memory.set` divided by the specified unit of memory.

        See Also
        --------

        set
        peak

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 17

            >>> from detkit import Memory, memdet
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize with KB unit
            >>> mem = Memory(unit='KB')

            >>> # Set the starting point of memory inquiry
            >>> mem.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry current allocated memory in KB unit
            >>> print(mem.now())
            781489.4
        """

        self._read()
        return self._mem / self.unit_size

    # ====
    # peak
    # ====

    def peak(self):
        """
        Inquiry peak memory allocation since memory is set.

        Returns
        -------

        peak_mem : float
            The peak memory allocation since calling :func:`detkit.Memory.set`
            divided by the specified unit of memory.

        See Also
        --------

        set
        now

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 17

            >>> from detkit import Memory, memdet
            >>> import numpy

            >>> # Create a random matrix
            >>> A = numpy.random.randn(10000, 10000)

            >>> # Initialize with KB unit
            >>> mem = Memory(unit='KB')

            >>> # Set the starting point of memory inquiry
            >>> mem.set()

            >>> # Perform a memory-intensive operation
            >>> ld = memdet(A)

            >>> # Inquiry the peak allocated memory in KB unit
            >>> print(mem.peak())
            781489.4
        """

        self._read()
        return self._peak / self.unit_size

    # ====
    # info
    # ====

    @staticmethod
    def info():
        """
        Inquiry memory information.

        Returns
        -------

        mem_info
            A dictionary containing the following keys:

            * ``'total'``: total memory in bytes
            * ``'used'``: used memory.
            * ``'available'``: available memory.
            * ``'allocatable'``: allocatable memory in bytes

        Notes
        -----

        Allocatable memory is obtained by the difference of total and used
        memory. Used memory is obtained as the sum of all RSS for all
        processes. This is a similar approach that ``top`` and ``htop`` report.

        See Also
        --------

        detkit.Disk.partition_info
        detkit.get_processor_name

        Examples
        --------

        .. code-block:: python

            >>> from detkit import Memory, human_readable_mem
            >>> mem_info = Memory.info()

            >>> # total memory
            >>> print(human_readable_mem(mem_info['total']))
            15.6 (GB)

            >>> # used memory
            >>> print(human_readable_mem(mem_info['used']))
            4.28 (GB)

            >>> # allocatable memory
            >>> print(human_readable_mem(mem_info['allocatable']))
            9.24 (GB)
        """

        mem_info = psutil.virtual_memory()
        total_mem = mem_info.total

        # Used memory is the sum of all RSS
        total_rss = 0
        for proc in psutil.process_iter(['memory_info']):
            try:
                proc_mem_info = proc.info['memory_info']
                if (proc_mem_info is not None) and \
                   (hasattr(proc_mem_info, 'rss')):
                    total_rss += proc_mem_info.rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sometimes total_rss is larger than total_mem, making allocatable
        # memory to be negative. So here we take max with available memory.
        allocatable_mem = max(mem_info.available, total_mem - total_rss)

        info_ = {
            'total': mem_info.total,
            'used': mem_info.used,
            'available': mem_info.available,
            'allocatable': allocatable_mem,
        }

        return info_
