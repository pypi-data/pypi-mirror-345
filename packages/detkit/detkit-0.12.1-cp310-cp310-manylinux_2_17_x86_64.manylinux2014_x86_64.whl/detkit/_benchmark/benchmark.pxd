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

from .._definitions.types cimport LongIndexType


# =======
# Externs
# =======

cdef extern from "benchmark.h":

    cdef cppclass Benchmark[DataType]:

        @staticmethod
        long long matmul(
                const DataType* dummy_var,
                const LongIndexType n) noexcept nogil

        @staticmethod
        long long gramian(
                const DataType* dummy_var,
                const LongIndexType n) noexcept nogil

        @staticmethod
        long long cholesky(
                const DataType* dummy_var,
                const LongIndexType n) noexcept nogil

        @staticmethod
        long long lu(
                const DataType* dummy_var,
                const LongIndexType n) noexcept nogil

        @staticmethod
        long long plu(
                const DataType* dummy_var,
                const LongIndexType n) noexcept nogil
