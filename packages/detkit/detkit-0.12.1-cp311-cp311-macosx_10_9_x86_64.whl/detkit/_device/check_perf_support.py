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
import subprocess

__all__ = ['check_perf_support']


# ==================
# check perf support
# ==================

def check_perf_support():
    """
    Check Perf tool is supported.

    Returns
    -------

    status : dict
        A dictionary with the following keys:

        * ``'kernel_version'``: Linux kernel version
        * ``'perf_event_paranoid'``: Permission status of kernel for using
          Perf. Values ``-1``, ``0``, and ``1`` are admissible permissions.
          Higher values prevent kernel from allowing Perf tool to work.
        * ``'perf_installed'``: Boolean, indicates if Perf tool is installed.
        * ``'perf_working'``: Boolean, indicates if Perf tool is working.

    See Also
    --------

    get_instructions_per_flop
    memdet
    loggdet
    logpdet

    Notes
    -----

    The Perf tool needs to be installed and necessary permissions should be
    granted for it to work. See :ref:`Perf Tool <perf_tool>`.

    Examples
    --------

    .. code-block:: python

        >>> import detkit
        >>> results = detkit.check_perf_support()
        >>> print(results)
        {
            'kernel_version': '6.8.0-51-generic',
            'perf_event_paranoid': 1,
            'perf_installed': True,
            'perf_working': True
        }
    """

    result = {
        "kernel_version": "",
        "perf_event_paranoid": None,
        "perf_installed": False,
        "perf_working": False,
    }

    # Check kernel version
    try:
        result["kernel_version"] = subprocess.check_output(
                ["uname", "-r"], text=True).strip()

    except subprocess.CalledProcessError:
        result["kernel_version"] = "Unknown"

    # Check /proc/sys/kernel/perf_event_paranoid
    if os.path.exists("/proc/sys/kernel/perf_event_paranoid"):
        with open("/proc/sys/kernel/perf_event_paranoid", "r") as f:
            result["perf_event_paranoid"] = int(f.read().strip())
    else:
        result["perf_event_paranoid"] = None

    # Check if 'perf' is installed
    try:
        subprocess.run(["which", "perf"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result["perf_installed"] = True

    except subprocess.CalledProcessError:
        result["perf_installed"] = False

    # Check if 'perf' is working
    if result["perf_installed"]:
        try:
            subprocess.run(
                ["perf", "stat", "-e", "cycles", "ls"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            result["perf_working"] = True
        except subprocess.CalledProcessError:
            result["perf_working"] = False

    return result
