/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./c_matrix_solvers.h"
#include "../_definitions/definitions.h"
#include "../_utilities/array_util.h"  // ArrayUtil


// ==================
// lower triang solve
// ==================

/// \brief Solves lower-triangular system of equations $L X = B$, where the
///        lower triangular matrix \c L is \c (n,n), and the matrices \c B and
///        \c X are \c (n,m). If \c B_transpose is \c, 1, the it is assumed
///        that \B is of the size \c (m,n), and the transpose of \c B is used
///        in the system $L X = B.T$.
///
///        Matrix \c L should have its diagonals. That is, \c L should have
///        been computed from lu function, but not plu function.

template <typename DataType>
void cMatrixSolvers<DataType>::lower_triang_solve(
        const DataType* L,
        const DataType* B,
        DataType* X,
        const LongIndexType n,
        const LongIndexType m,
        const FlagType B_transpose,
        const FlagType X_transpose)
{
    DataType x;

    for (LongIndexType k=0; k < m; ++k)
    {
        for (LongIndexType i=0; i < n; ++i)
        {
            if (B_transpose == 1)
            {
                x = B[k*n + i];
            }
            else
            {
                x = B[i*m + k];
            }

            if (X_transpose == 1)
            {
                for (LongIndexType j=0; j < i; ++j)
                {
                    x -= L[i*n + j] * X[k*n + j];
                }
            }
            else
            {
                for (LongIndexType j=0; j < i; ++j)
                {
                    x -= L[i*n + j] * X[j*m + k];
                }
            }

            x /= L[i*n + i];

            if (X_transpose == 1)
            {
                X[k*n + i] = x;
            }
            else
            {
                X[i*m + k] = x;
            }
        }
    }
}


// ==================
// upper triang solve
// ==================

/// \brief Solves upper-triangular system of equations $U X = B$, where the
///        upper triangular matrix \c U is \c (n,n), and the matrices \c B and
///        \c X are \c (n,m). If \c B_transpose is \c, 1, the it is assumed
///        that \B is of the size \c (m,n), and the transpose of \c B is used
///        in the system $L X = B.T$.

template <typename DataType>
void cMatrixSolvers<DataType>::upper_triang_solve(
        const DataType* U,
        const DataType* B,
        DataType* X,
        const LongIndexType n,
        const LongIndexType m,
        const FlagType B_transpose,
        const FlagType X_transpose)
{
    DataType x;

    for (LongIndexType k=0; k < m; ++k)
    {
        for (LongIndexType i=n-1; i >= 0; --i)
        {
            if (B_transpose == 1)
            {
                x = B[k*n + i];
            }
            else
            {
                x = B[i*m + k];
            }

            if (X_transpose == 1)
            {
                for (LongIndexType j=i+1; j < n; ++j)
                {
                    x -= U[i*n + j] * X[k*n + j];
                }
            }
            else
            {
            
                for (LongIndexType j=i+1; j < n; ++j)
                {
                    x -= U[i*n + j] * X[j*m + k];
                }
            }

            x /= U[i*n + i];

            if (X_transpose == 1)
            {
                X[k*n + i] = x;
            }
            else
            {
                X[i*m + k] = x;
            }
        }
    }
}


// ========
// lu solve
// ========

/// \brief Solves system of equations $LU X = B$, where the lower and upper
///        triangular matrices \c L and \c U is \c (n,n), and the matrices \c B
///        \c X are \c (n,m). If \c B_transpose is \c, 1, the it is assumed
///        that \B is of the size \c (m,n), and the transpose of \c B is used
///        in the system $L X = B.T$.
///
///        Matrices L and U should have been computed from LU decomposition,
///        bit not from PLU decomposition.

template <typename DataType>
void cMatrixSolvers<DataType>::lu_solve(
        const DataType* L,
        const DataType* U,
        const DataType* B,
        DataType* X,
        const LongIndexType n,
        const LongIndexType m,
        const FlagType B_transpose,
        const FlagType X_transpose)
{
    // Solving L * Y = B
    DataType* Y = new DataType[n*m];
    cMatrixSolvers<DataType>::lower_triang_solve(L, B, Y, n, m, B_transpose,
                                                 X_transpose);

    // Solving U * X = Y
    cMatrixSolvers<DataType>::upper_triang_solve(U, Y, X, n, m, B_transpose,
                                                 X_transpose);

    // Free memory
    ArrayUtil<DataType>::del(Y);
}


// =========
// plu solve
// =========

/// \brief Solves linear system. A should be the LU factor from PLU
///        decomposition, not from LU decomposition.

template <typename DataType>
void cMatrixSolvers<DataType>::plu_solve(
        const DataType *A,
        const LongIndexType *P, 
        const DataType *B,
        DataType *X,
        const LongIndexType n,
        const LongIndexType m,
        const FlagType B_transpose,
        const FlagType X_transpose)
{
    DataType x;

    for (LongIndexType l=0; l < m; ++l)
    {
        // Forward iteration
        for (int i=0; i < n; ++i)
        {
            // Get B[i][l]
            if (B_transpose == 1)
            {
                x = B[l*n + P[i]];
            }
            else
            {
                x = B[P[i]*m + l];
            }

            if (X_transpose == 1)
            {
                for (int k=0; k < i; ++k)
                {
                    x -= A[P[i]*n + k] * X[l*n + k];
                }
            }
            else
            {
                for (int k=0; k < i; ++k)
                {
                    x -= A[P[i]*n + k] * X[k*m + l];
                }
            }

            // Set X[i][l] from x
            if (X_transpose == 1)
            {
                X[l*n + i] = x;
            }
            else
            {
                X[i*m + l] = x;
            }
        }

        // Backward iteration
        for (int i=n-1; i >= 0; i--)
        {
            // Get X[i][l]
            if (X_transpose == 1)
            {
                x = X[l*n + i];
            }
            else
            {
                x = X[i*m + l];
            }

            if (X_transpose == 1)
            {
                for (int k=i+1; k < n; ++k)
                {
                    x -= A[P[i]*n + k] * X[l*n + k];
                }
            }
            else
            {
                for (int k=i+1; k < n; ++k)
                {
                    x -= A[P[i]*n + k] * X[k*m + l];
                }
            }

            x /= A[P[i]*n + i];

            // Set X[i][l]
            if (X_transpose == 1)
            {
                X[l*n + i] = x;
            }
            else
            {
                X[i*m + l] = x;
            }
        }
    }
}


// ===============================
// Explicit template instantiation
// ===============================

template class cMatrixSolvers<float>;
template class cMatrixSolvers<double>;
template class cMatrixSolvers<long double>;
