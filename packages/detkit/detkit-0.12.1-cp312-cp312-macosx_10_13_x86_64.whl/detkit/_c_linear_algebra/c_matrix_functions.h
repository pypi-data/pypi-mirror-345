/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _C_LINEAR_ALGEBRA_C_MATRIX_FUNCTIONS_H_
#define _C_LINEAR_ALGEBRA_C_MATRIX_FUNCTIONS_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // IndexType, LongIndexType, FlagType


// ===========
// c Functions
// ===========

/// \class cMatrixDecompositons
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
class cMatrixFunctions
{
    public:

        // logdet
        static DataType logdet(
                DataType* A,
                const LongIndexType num_rows,
                const FlagType sym_pos,
                FlagType& sign);

        // triang logdet
        static DataType triang_logdet(
                const DataType* A,
                const LongIndexType* P,
                const LongIndexType num_rows,
                FlagType& sign);

        // det
        static DataType det(
                DataType* A,
                const LongIndexType num_rows,
                const FlagType sym_pos);

        // loggdet
        static DataType loggdet(
                const DataType* A,
                const DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType method,
                const FlagType X_orth,
                FlagType& sign,
                long long& flops);

        // loggdet legacy
        static DataType _loggdet_legacy(
                const DataType* A,
                const DataType* X,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                FlagType& sign);

        // loggdet proj
        static DataType _loggdet_proj(
                const DataType* A,
                const DataType* X,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType X_orth,
                FlagType& sign);

        // loggdet comp
        static DataType _loggdet_comp(
                const DataType* A,
                const DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType X_orth,
                FlagType& sign);

        // logpdet
        static DataType logpdet(
                const DataType* A,
                const DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType method,
                const FlagType X_orth,
                FlagType& sign,
                long long& flops);

        // logpdet legacy
        static DataType _logpdet_legacy(
                const DataType* A,
                const DataType* X,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType X_orth,
                FlagType& sign);

        // logpdet proj
        static DataType _logpdet_proj(
                const DataType* A,
                const DataType* X,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType X_orth,
                FlagType& sign);

        // logpdet comp
        static DataType _logpdet_comp(
                const DataType* A,
                const DataType* X,
                DataType* Xp,
                const FlagType use_Xp,
                const LongIndexType num_rows,
                const LongIndexType num_columns,
                const FlagType sym_pos,
                const FlagType X_orth,
                FlagType& sign);
};

#endif  // _C_LINEAR_ALGEBRA_C_MATRIX_FUNCTIONS_H_
