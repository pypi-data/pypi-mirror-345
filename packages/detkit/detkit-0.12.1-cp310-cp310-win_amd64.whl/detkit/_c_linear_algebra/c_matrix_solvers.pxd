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

cdef extern from "c_matrix_solvers.h":

    cdef cppclass cMatrixSolvers[DataType]:

        @staticmethod
        void lower_triang_solve(
                const DataType* L,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose) noexcept nogil

        @staticmethod
        void upper_triang_solve(
                const DataType* L,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose) noexcept nogil

        @staticmethod
        void lu_solve(
                const DataType* L,
                const DataType* U,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose) noexcept nogil

        @staticmethod
        void plu_solve(
                const DataType *A,
                const LongIndexType *P, 
                const DataType *B,
                DataType *X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose) noexcept nogil
