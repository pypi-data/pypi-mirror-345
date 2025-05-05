/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _C_BASIC_ALGEBRA_C_MATRIX_OPERATIONS_H_
#define _C_BASIC_ALGEBRA_C_MATRIX_OPERATIONS_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // IndexType, LongIndexType, FlagType


// ===================
// c Matrix Operations
// ===================

/// \class cMatrixOperations
///
/// \brief   A static class for matrix-vector operations, which are similar to
///          the level-2 operations of the BLAS library. This class acts as a
///          templated namespace, where all member methods are *public* and
///          *static*.
///
/// \details This class implements matrix-ector multiplication for three types
///          of matrices:
///
///          * Dense matrix (both row major and column major)
///          * Compressed sparse row matrix (CSR)
///          * Compressed sparse column matrix (CSC)
///
///          For each of the above matrix types, there are four kinds of matrix
///          vector multiplications implemented.
///
///          1. \c dot : performs \f$ \boldsymbol{c} = \mathbf{A}
///             \boldsymbol{b} \f$.
///          2. \c dot_plus : performs \f$ \boldsymbol{c} = \boldsymbol{c} +
///             \alpha \mathbf{A} \boldsymbol{b} \f$.
///          3. \c transpose_dot : performs \f$ \boldsymbol{c} =
///             \mathbf{A}^{\intercal} \boldsymbol{b} \f$.
///          4. \c transpose_dot_plus : performs \f$ \boldsymbol{c} =
///             \boldsymbol{c} + \alpha \mathbf{A}^{\intercal} \boldsymbol{b}
///             \f$.
///
/// \sa      cVectorOperations

template <typename DataType>
class cMatrixOperations
{
    public:
        static void copy(
                const DataType* A,
                DataType* B,
                const LongIndexType num_rows,
                const LongIndexType num_columns);

        static void add(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType num_rows,
                const LongIndexType num_columns);
        
        // add diagonal inplace
        static void add_diagonal_inplace(
                DataType* A,
                const DataType alpha,
                const LongIndexType num_rows);

        // add inplace
        static void add_inplace(
                DataType* A,
                const DataType* B,
                const LongIndexType num_rows,
                const LongIndexType num_columns);
        
        // subtract inplace
        static void subtract_inplace(
                DataType* A,
                const DataType* B,
                const LongIndexType num_rows,
                const LongIndexType num_columns);

        // matmat
        static void matmat(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const LongIndexType p,
                const DataType c);

        // matmat transpose
        static void matmat_transpose(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const LongIndexType p,
                const DataType c);

        // gramian matmat transpose
        static void gramian_matmat_transpose(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const DataType c);

        // gramian
        static void gramian(
                const DataType* A,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const DataType c);

        // inner prod
        static void inner_prod(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const DataType c);

        // outer prod
        static void outer_prod(
                const DataType* A,
                const DataType* B,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const DataType c);

        // outer prod
        static void self_outer_prod(
                const DataType* A,
                DataType* C,
                const LongIndexType n,
                const LongIndexType m,
                const DataType c);
};

#endif  // _C_BASIC_ALGEBRA_C_MATRIX_OPERATIONS_H_
