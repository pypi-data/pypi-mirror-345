/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _C_BASIC_ALGEBRA_C_VECTOR_OPERATIONS_H_
#define _C_BASIC_ALGEBRA_C_VECTOR_OPERATIONS_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // LongIndexType


// =================
// Vector Operations
// =================

/// \class cVectorOperations
///
/// \brief A static class for vector operations, similar to level-1 operations
///        of the BLAS library. This class acts as a templated namespace, where
///        all member methods are *public* and *static*.
///
/// \sa    MatrixOperations

template <typename DataType>
class cVectorOperations
{
    public:

        // subtract scaled vector
        static void subtract_scaled_vector(
                DataType* A,
                DataType* B,
                const LongIndexType num_rows,
                const LongIndexType num_columns_A,
                const LongIndexType num_columns_B,
                const DataType scale,
                const LongIndexType i_A,
                const LongIndexType j_B);

        // inner product
        static DataType inner_product(
                const DataType* A,
                const DataType* B,
                const LongIndexType num_rows,
                const LongIndexType num_columns_A,
                const LongIndexType num_columns_B,
                const LongIndexType i_A,
                const LongIndexType j_B);

        // euclidean norm
        static DataType euclidean_norm(
                const DataType* A,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const LongIndexType i);

        // normalize vector in place
        static DataType normalize_vector_in_place(
                DataType* A,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const LongIndexType i);
};

#endif  // _C_BASIC_ALGEBRA_C_VECTOR_OPERATIONS_H_
