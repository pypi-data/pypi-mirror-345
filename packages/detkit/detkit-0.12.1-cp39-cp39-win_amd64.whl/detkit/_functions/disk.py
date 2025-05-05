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

import os
import psutil
import numpy
import sys

__all__ = ['Disk']


# ====
# Disk
# ====

class Disk(object):
    """
    Measure read and write to disk.

    Parameters
    ----------

    unit : int or str {``'B'``, ``'KB'``, ``'MB'``, ``'GB'``, ``'TB'``}, \
            default=``1``
        Unit of memory either as a string, such as ``'KB'``, representing
        1024 bytes, or directly specify the number of bytes as an integer.

    See Also
    --------

    detkit.Memory
    detkit.Profile

    Methods
    -------

    set
    read
    write
    partition_info

    Notes
    -----

    **Dropping Cache:**

    You may need to drop cache to get accurate results on disk's read. To drop
    cache, execute the following:

    .. code-block:: bash

        echo 3 | sudo tee /proc/sys/vm/drop_caches

    Note that dropping cache is necessary to inquiry disk's *read*, but usually
    not needed to inquiry disk's *write*.

    Examples
    --------

    **Set and reset disk object:**

    .. code-block:: python
        :emphasize-lines: 2

        >>> from detkit import Disk, memdet, human_readable_mem
        >>> disk = Disk()

        >>> # Set the starting point of disk inquiry
        >>> disk.set()

        >>> # Perform an operation that reads from and writes to disk
        >>> import numpy
        >>> A = numpy.random.randn(1000, 1000)
        >>> ld = memdet(A, num_blocks=4)

        >>> # Inquiry read from disk during the above operation
        >>> print(human_readable_mem(disk.read()))
        1.0 MB

        >>> # Inquiry write to disk during the above operation
        >>> print(human_readable_mem(disk.write()))
        10.3 MB

        >>> # Reset the starting point of disk inquiry
        >>> disk.set()

        >>> # Inquiry read from disk again
        >>> print(human_readable_mem(disk.write()))
        0  B

    **Custom unit of memory:**

    Here we create and array and set the unit of memory as the size of whole
    array. This way, we can compare the amount of read and write to disk
    relative to the array size, rather than in the standard units of memory.

    .. code-block:: python
        :emphasize-lines: 7

        >>> # Create an array
        >>> import numpy
        >>> A = numpy.random.randn(1000, 1000)

        >>> # Create disk object with custom unit of memory
        >>> from detkit import Disk, memdet, human_readable_mem
        >>> disk = Disk(unit=A.nbytes)

        >>> # Set the starting point of disk inquiry
        >>> disk.set()

        >>> # Perform an operation that reads from and writes to disk
        >>> ld = memdet(A, num_blocks=4)

        >>> # Inquiry read from disk during the above operation
        >>> print(disk.read())
        0.14

        >>> # Inquiry write to disk during the above operation
        >>> print(disk.write())
        1.34

    In the above example, the amount of read to disk is 0.14 times the size of
    the array `A`.
    """

    # ====
    # init
    # ====

    def __init__(self, unit=1):
        """
        Initialization.
        """

        # The io_counters() is not available in macos. For macos, we will
        # instead use disk_io_counters() function.
        if sys.platform in ['linux', 'win32', 'cygwin']:
            self.process = psutil.Process(os.getpid())

        self.init_io = None
        self.final_io = None

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
            elif unit == 'PB':
                self.unit_size = 1024**5
            elif unit == 'EB':
                self.unit_size = 1024**6
            elif unit == 'ZB':
                self.unit_size = 1024**7
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
        Set or reset tracing disk read and write.

        See Also
        --------

        read
        write

        Notes
        -----

        When an object of :class:`detkit.Disk` is instantiated, the
        :func:`detkit.Disk.set` method is automatically called. So, you may not
        need to call this on a newly created disk object.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 7, 19

            >>> from detkit import Disk, memdet

            >>> # Initialize with MB unit
            >>> disk = Disk(unit='MB')

            >>> # Set the starting point of disk inquiry
            >>> disk.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry read from disk during the above operation, in MB unit
            >>> print(disk.read())
            5.72

            >>> # Reset the starting point of disk inquiry
            >>> disk.set()

            >>> # Inquiry read from disk again
            >>> print(disk.read())
            0.0
        """

        if sys.platform in ['linux', 'win32', 'cygwin']:
            self.init_io = self.process.io_counters()
        else:
            self.init_io = psutil.disk_io_counters()

    # ====
    # read
    # ====

    def read(self):
        """
        Inquiry the amount of read from disk.

        Returns
        -------

        read_size : int
            The amount of read from disk divided by the specified unit size.

        See Also
        --------

        write

        Notes
        -----

        The read amount is measured from the point where
        :func:`detkit.Disk.set` is called to the current. The reported read
        amount is divided by the give unit (see argument to
        :class:`detkit.Disk`).

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

            >>> from detkit import Disk, memdet

            >>> # Initialize with MB unit
            >>> disk = Disk(unit='MB')

            >>> # Set (or reset) the starting point of disk inquiry
            >>> disk.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry read from disk during the above operation, in MB unit
            >>> print(disk.read())
            5.72
        """

        if self.init_io is None:
            raise RuntimeError('"Disk" object has not been set.')

        # Force the OS to write its buffers to disk (note: on Windows, os.sync
        # does not exists).
        if hasattr(os, "sync"):
            os.sync()

        if sys.platform in ['linux', 'win32', 'cygwin']:
            self.final_io = self.process.io_counters()
        else:
            self.final_io = psutil.disk_io_counters()

        read_bytes = self.final_io.read_bytes - self.init_io.read_bytes

        return read_bytes / self.unit_size

    # =====
    # write
    # =====

    def write(self):
        """
        Inquiry the amount of write to disk.

        Returns
        -------

        write_size : int
            The amount of write to disk divided by the specified unit size.

        See Also
        --------

        read

        Notes
        -----

        The write amount is measured from the point where
        :func:`detkit.Disk.set` is called to the current. The reported write
        amount is divided by the give unit (see argument to
        :class:`detkit.Disk`).

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 15

            >>> from detkit import Disk, memdet

            >>> # Initialize with MB unit
            >>> disk = Disk(unit='MB')

            >>> # Set (or reset) the starting point of disk inquiry
            >>> disk.set()

            >>> # Perform an operation that reads from and writes to disk
            >>> import numpy
            >>> A = numpy.random.randn(1000, 1000)
            >>> ld = memdet(A, num_blocks=4)

            >>> # Inquiry write to disk during the above operation, in MB unit
            >>> print(disk.write())
            5.72
        """

        if self.init_io is None:
            raise RuntimeError('"Disk" object has not been set.')

        # Force the OS to write its buffers to disk (note: on Windows, os.sync
        # does not exists).
        if hasattr(os, "sync"):
            os.sync()

        if sys.platform in ['linux', 'win32', 'cygwin']:
            self.final_io = self.process.io_counters()
        else:
            self.final_io = psutil.disk_io_counters()

        write_bytes = self.final_io.write_bytes - self.init_io.write_bytes

        return write_bytes / self.unit_size

    # ==============
    # partition info
    # ==============

    @staticmethod
    def partition_info(path):
        """
        Disk partition info.

        Parameters
        ----------

        path : str
            Path of a directory or file within the disk partition.

        Returns
        -------

        part_info
            An object containing disk's partition information. If no partition
            is found, `None` is returned. The object contains the following
            attributes:

            * ``'device'``: disk device corresponding to the partition
            * ``'mountpoint'``: Mount point of the partition
            * ``'fstype'``: file system type of the partition
            * ``'opts'``: options where the partition is configured with
            * ``'maxfile'``: maxfile of partition
            * ``'maxpath'``: maxpath of partition

        See Also
        --------

        detkit.Memory.info

        Notes
        -----

        This is a static method and does not need the :class:`detkit.Disk` to
        be instantiated (see example below).

        Examples
        --------

        .. code-block:: python

            >>> from detkit import Disk
            >>> part_info = Disk.partition_info('/home')

            >>> # Get device
            >>> print(part_info.device)
            '/dev/nvme0n1p7'

            >>> # Get mount point
            >>> print(part_info.mountpoint)
            '/'

            >>> # Get file system type
            >>> print(part_info.fstype)
            'ext4'
        """

        # Convert relative to absolute path
        path = os.path.abspath(path)

        # Get partition information
        partitions = psutil.disk_partitions()
        part_info = None

        for partition in partitions:
            # On Windows, check if the path starts with the drive letter
            if sys.platform == 'win32':
                if path.lower().startswith(partition.mountpoint.lower()):
                    part_info = partition
                    break
            else:
                # For Linux and others
                if path.startswith(partition.mountpoint):
                    part_info = partition
                    break

        return part_info
