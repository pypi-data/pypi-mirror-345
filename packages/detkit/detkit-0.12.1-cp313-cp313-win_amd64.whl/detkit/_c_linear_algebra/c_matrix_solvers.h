/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _C_LINEAR_ALGEBRA_C_MATRIX_SOLVERS_H_
#define _C_LINEAR_ALGEBRA_C_MATRIX_SOLVERS_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // IndexType, LongIndexType, FlagType


// ================
// c Matrix Solvers
// ================

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
class cMatrixSolvers
{
    public:

        // lower triang solve
        static void lower_triang_solve(
                const DataType* L,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose);

        // upper triang solve
        static void upper_triang_solve(
                const DataType* L,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose);

        // solve
        static void lu_solve(
                const DataType* L,
                const DataType* U,
                const DataType* B,
                DataType* X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose);

        static void plu_solve(
                const DataType *A,
                const LongIndexType *P, 
                const DataType *B,
                DataType *X,
                const LongIndexType n,
                const LongIndexType m,
                const FlagType B_transpose,
                const FlagType X_transpose);
};

#endif  // _C_LINEAR_ALGEBRA_C_MATRIX_SOLVERS_H_
