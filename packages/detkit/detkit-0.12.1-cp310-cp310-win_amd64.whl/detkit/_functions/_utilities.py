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
import platform
import subprocess
import re

__all__ = ['get_processor_name', 'get_data_type_name', 'human_readable_time',
           'human_readable_mem']


# ==================
# get processor name
# ==================

def get_processor_name():
    """
    Returns name of processor.

    Returns
    -------

    string : str
        Processor name.

    See Also
    --------

    detkit.Profile

    Examples
    --------

    .. code-block:: python

        >>> from detkit import get_procssor_name
        >>> print(get_processor_name())
        Intel(R) Core(TM) i7-4770K CPU @ 3.50GHz
    """

    if platform.system() == "Windows":
        return platform.processor()

    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = ["sysctl", "-n", "machdep.cpu.brand_string"]
        return subprocess.check_output(command).strip()

    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(
                command, shell=True).decode().strip()

        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line, count=1)

    return ""


# ==================
# get data type name
# ==================

def get_data_type_name(data):
    """
    Returns the typename of data as string.

    Returns
    -------

    string : str
        Data type, such as ``'float16'``, ``'float32'``, ``'float64'``,
        ``'float128'``, ``'int16'``, ``'int32'``, and ``'int64'``.
    """

    if data.dtype in [b'float16', 'float16']:
        data_type_name = b'float16'
    elif data.dtype in [b'float32', 'float32']:
        data_type_name = b'float32'
    elif data.dtype in [b'float64', 'float64']:
        data_type_name = b'float64'
    elif data.dtype in [b'float128', 'float128']:
        data_type_name = b'float128'
    elif data.dtype in [b'int16', 'int16']:
        data_type_name = b'int16'
    elif data.dtype in [b'int32', 'int32']:
        data_type_name = b'int32'
    elif data.dtype in [b'int64', 'int64']:
        data_type_name = b'int64'
    else:
        raise TypeError('Data type should be "float16", "float32", ' +
                        '"float64", "float128", "int16", "int32", or "int64".')

    return data_type_name


# ===================
# human readable time
# ===================

def human_readable_time(t, pad=False):
    """
    Converts time (in seconds) as float to string with time unit.

    Parameters
    ----------

    t : float
        Time in seconds

    pad : boolean, default=False
        Is `True`, the output string is padded from left so that it always
        have fixed and consistent length. This is useful to print in columns.

    Returns
    -------

    string : str
        A string containing time and the unit of time as follows:

        * ``'ps'``: pico-second (:math:`10^{-12}` second)
        * ``'ns'``: nano-second (:math:`10^{-9}` second)
        * ``'us'``: micro-second (:math:`10^{-6}` second)
        * ``'ms'``: milli-second (:math:`10^{-3}` second)
        * ``'se'``: second
        * ``'mn'``: minute
        * ``'hr'``: hour
        * ``'dy'``: day
        * ``'mo'``: month

    See Also
    --------

    detkit.human_readable_mem

    Examples
    --------

    .. code-block:: python

        >>> from detkit import human_readable_time

        >>> print(human_readable_time(0.01))
        10 ms

        >>> print(human_readable_time(0.01, pad=True))
         10 ms
    """

    if t < 1e-9:
        # Pico-second
        ht = t * 1e+12
        unit = 'ps'

    elif t < 1e-6:
        # Nano-second
        ht = t * 1e+9
        unit = 'ns'

    elif t < 1e-3:
        # Micro-second
        ht = t * 1e+6
        unit = 'us'

    elif t < 1e-0:
        # Milli-second
        ht = t * 1e+3
        unit = 'ms'

    elif t < 60.0:
        # second
        ht = t
        unit = 'sc'

    elif t < 60.0 * 60.0:
        # Mints
        ht = t / 60.0
        unit = 'mn'

    elif t < 60.0 * 60.0 * 24.0:
        # Hours
        ht = t / (60.0 * 60.0)
        unit = 'hr'

    elif t < 60.0 * 60.0 * 24.0 * 30.0:
        # Days
        ht = t / (60.0 * 60.0 * 24.0)
        unit = 'dy'

    else:
        # Month
        ht = t / (60.0 * 60.0 * 24.0 * 30.0)
        unit = 'mo'

    # Make sure the total length of digits and unit are 8 characters
    if unit in ['ps', 'ns', 'us', 'ms']:
        # three int digits and four unit characters
        string = f'{ht:>4.0f} {unit}'
    else:
        # four digits and three unit characters
        string = f'{ht:>4.1f} {unit}'

    if pad:
        return string
    else:
        return string.lstrip()


# ==================
# human readable mem
# ==================

def human_readable_mem(m, pad=False):
    """
    Converts memory (in bytes) as float to string with memory unit.

    Parameters
    ----------

    pad : boolean, default=False
        If `True`, adds empty string padding to the left so that the output
        string always have a consistent and fixed length. This is useful to
        print the results on a column of fixed length. If `False`, the padding
        on the left of the string is removed.

    Returns
    -------

    string : str
        A string containing the memory and its unit. The unit can be

        * ``'B'``: Byte
        * ``'KB'``: Kilo-Byte (:math:`2^{10}` bytes)
        * ``'MB'``: Mega-Byte
        * ``'GB'``: Gga-Byte
        * ``'TB'``: Tiga-Byte
        * ``'TB'``: Tera-Byte
        * ``'PB'``: Peta-Byte
        * ``'EB'``: Exa-Byte

    See Also
    --------

    detkit.human_readable_time

    Examples
    --------

    .. code-block:: python

        >>> from detkit import human_readable_mem

        >>> print(human_readable_mem(2048))
        2 KB

        >>> print(human_readable_mem(2048, pad=True))
           2 KB
    """

    if m < 1024:
        hm = m
        unit = ' B'

    elif m < 1024**2:
        hm = m / (1024)
        unit = 'KB'

    elif m < 1024**3:
        hm = m / (1024**2)
        unit = 'MB'

    elif m < 1024**4:
        hm = m / (1024**3)
        unit = 'GB'

    elif m < 1024**5:
        hm = m / (1024**4)
        unit = 'TB'

    elif m < 1024**6:
        hm = m / (1024**5)
        unit = 'PB'

    elif m < 1024**7:
        hm = m / (1024**6)
        unit = 'EB'

    else:
        raise RuntimeError('memory size is invalid.')

    # Make sure the total length of digits and unit are 9 characters
    if unit == ' B':
        # four int digits and two unit characters
        string = f'{hm:>6.0f} {unit}'
    elif len(unit) == 2:
        # six float digits and two unit characters
        string = f'{hm:>6.1f} {unit}'
    else:
        raise RuntimeError('memory unit length is invalid.')

    if pad:
        return string
    else:
        return string.lstrip()
