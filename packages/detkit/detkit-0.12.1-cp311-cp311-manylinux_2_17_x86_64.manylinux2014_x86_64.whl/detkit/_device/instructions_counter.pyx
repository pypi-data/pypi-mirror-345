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

from libc.stdint cimport int64_t
import numpy

cdef extern from "c_instructions_counter.h":
    cdef cppclass cInstructionsCounter:
        cInstructionsCounter()
        void set_inst_per_flop(double inst_per_flop)
        void start()
        void stop()
        void reset()
        int64_t get_count()
        int64_t get_flops()

__all__ = ['InstructionCounter']


# ====================
# Instructions Counter
# ====================

cdef class InstructionsCounter:
    """
    Wrapper for Linux's Perf tool.

    Parameters
    ----------

    inst_per_flop : float, default=1.0
        Instructions per FLOP. This can also be set later using
        :func:`set_inst_per_flop`.

    Methods
    -------

    start
    stop
    reset
    get_count
    set_inst_per_flop
    get_flop

    See Also
    --------

    detkit.check_perf_support
    detkit.get_instructions_per_flop
    detkit.Profile
    detkit.memdet

    Notes
    -----

    To measure hardware instructions count, the Perf tool needs to be installed
    and necessary permissions should be granted for it to work. See
    :ref:`Perf Tool <perf_tool>`.

    To count FLOPs, multiply hardware instructions counter by flops per
    hardware instructions, which can be estimated using
    :func:`detkit.get_instructions_per_flop`.

    Examples
    --------

    .. code-block:: python

        >>> import detkit

        >>> # You may first check Perf tool is installed and supported
        >>> results = detkit.check_perf_support()
        >>> print(results)
        {
            'kernel_version': '6.8.0-51-generic',
            'perf_event_paranoid': 1,
            'perf_installed': True,
            'perf_working': True
        }

    Once you made sure Perf tool is installed and working, you can measure
    hardware instructions count. In the example below, we measure it for the
    matrix-matrix multiplication.

    .. code-block:: python
        :emphasize-lines: 3, 12, 14, 16

        >>> # Initialize
        >>> from detkit import InstructionsCounter
        >>> ic = InstructionsCounter()

        >>> # Create matrices for testing
        >>> import numpy
        >>> n = 1000
        >>> A = numpy.random.randn(n, n)
        >>> B = numpy.random.randn(n, n)

        >>> # Start counting hardware instructions
        >>> ic.start()
        >>> C = A @ B
        >>> ic.stop()

        >>> print(is.get_count())
    """

    cdef cInstructionsCounter* c_instructions_counter

    # =====
    # cinit
    # =====

    def __cinit__(self, inst_per_flop=1.0):
        """
        Initialize the C++ InstructionsCounter.
        """

        self.c_instructions_counter = new cInstructionsCounter()
        self.c_instructions_counter.set_inst_per_flop(1.0)

    # =======
    # dealloc
    # =======

    def __dealloc__(self):
        """
        Clean up the C++ object.
        """

        del self.c_instructions_counter

    # =====
    # start
    # =====

    def start(self):
        """
        Start counting instructions.
        """

        self.c_instructions_counter.start()

    # ====
    # stop
    # ====

    def stop(self):
        """
        Stop counting instructions.
        """

        self.c_instructions_counter.stop()

    # =====
    # reset
    # =====

    def reset(self):
        """
        Reset counts.
        """

        self.c_instructions_counter.reset()

    # =========
    # get count
    # =========

    def get_count(self):
        """
        Get the instruction count.
        
        Returns
        -------
    
        count : int
            Number of hardware instructions counted.
        """

        return self.c_instructions_counter.get_count()

    # =================
    # set inst per flop
    # =================

    def set_inst_per_flop(self, inst_per_flop: float):
        """
        Set retired instructions per floating-point operations.

        Parameters
        ----------

        inst_per_flop : float
            Number of hardware instruction per FLOP.
        """

        self.c_instructions_counter.set_inst_per_flop(inst_per_flop)

    # =========
    # get flops
    # =========

    def get_flops(self) -> float:
        """
        Get the adjusted floating-point operation count (FLOPs).

        Returns
        -------

        flops : float
            Number of FLOPs counted.
        """

        flops = self.c_instructions_counter.get_flops()

        if flops < 0.0:
            flops = numpy.nan

        return flops
