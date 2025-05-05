/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _C_LINEAR_ALGEBRA_C_MATRIX_DECOMPOSITIONS_H_
#define _C_LINEAR_ALGEBRA_C_MATRIX_DECOMPOSITIONS_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // IndexType, LongIndexType, FlagType


// =======================
// c Matrix Decompositions
// =======================

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
class cMatrixDecompositions
{
    public:

        // lu
        static void lu(
                DataType* A,
                const LongIndexType num_rows,
                DataType* L);

        // plu
        static FlagType plu(
                DataType* A,
                LongIndexType* P,
                const LongIndexType num_rows,
                const DataType tol);

        // cholesky
        static FlagType cholesky(
                DataType* A,
                const LongIndexType num_rows,
                DataType* L);

        // gram schmidt
        static void gram_schmidt(
                DataType *A,
                const LongIndexType num_rows,
                const LongIndexType num_columns);

        // Orthonormal complement
        static void ortho_complement(
                DataType *Xp,
                const DataType *X,
                const LongIndexType num_rows,
                const LongIndexType num_columns_Xp,
                const LongIndexType num_columns_X,
                const FlagType X_orth);
};

#endif  // _C_LINEAR_ALGEBRA_C_MATRIX_DECOMPOSITIONS_H_
