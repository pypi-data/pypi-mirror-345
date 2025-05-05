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

from .._definitions.types cimport LongIndexType, FlagType


# =======
# Externs
# =======

cdef extern from "c_matrix_functions.h":

    cdef cppclass cMatrixFunctions[DataType]:

        @staticmethod
        DataType logdet(
                DataType* A,
                const LongIndexType num_rows,
                const FlagType sym_pos,
                FlagType& sign) noexcept nogil

        @staticmethod
        DataType det(
                DataType* A,
                const LongIndexType num_rows,
                const FlagType sym_pos) noexcept nogil

        @staticmethod
        DataType loggdet(
                DataType* A,
                DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType method,
                const FlagType X_orth,
                FlagType& sign,
                long long& flops) noexcept nogil

        @staticmethod
        DataType logpdet(
                DataType* A,
                DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType method,
                const FlagType X_orth,
                FlagType& sign,
                long long& flops) noexcept nogil
