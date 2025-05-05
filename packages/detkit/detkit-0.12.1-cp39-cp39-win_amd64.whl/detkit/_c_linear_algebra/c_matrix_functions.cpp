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

#include "./c_matrix_functions.h"
#include <cmath>  // log, abs, exp
#include <cstddef>  // NULL
#include "../_c_basic_algebra/c_matrix_operations.h"  // cMatrixOperations
#include "./c_matrix_decompositions.h"  // cMatrixDecompositions
#include "./c_matrix_solvers.h"  // cMatrixSolvers
#include "../_device/c_instructions_counter.h"  // cInstructionsCounter
#include "../_utilities/array_util.h"  // ArrayUtil
#include "../_definitions/definitions.h"


// ======
// logdet
// ======

/// \brief      Computes the matrix vector multiplication \f$ \boldsymbol{c} =
///             \mathbf{A} \boldsymbol{b} \f$ where \f$ \mathbf{A} \f$ is a
///             dense matrix.
///
/// \details    The reduction variable (here, \c sum ) is of the type
///             \c{long double}. This is becase when \c DataType is \c float,
///             the summation loses the precision, especially when the vector
///             size is large. It seems that using \c{long double} is slightly
///             faster than using \c double. The advantage of using a type
///             with larger bits for the reduction variable is only sensible
///             if the compiler is optimized with \c -O2 or \c -O3 flags.
///
/// \param[in]  A
///             1D array that represents a 2D dense array with either C (row)
///             major ordering or Fortran (column) major ordering. The major
///             ordering should de defined by \c A_is_row_major flag.
/// \param[in]  b
///             Column vector
/// \param[in]  num_rows
///             Number of rows of \c A
/// \param[in]  num_columns
///             Number of columns of \c A
/// \param[in]  A_is_row_major
///             Boolean, can be \c 0 or \c 1 as follows:
///             * If \c A is row major (C ordering where the last index is
///               contiguous) this value should be \c 1.
///             * If \c A is column major (Fortran ordering where the first
///               index is contiguous), this value should be set to \c 0.
/// \param[out] c
///             The output column vector (written in-place).

template <typename DataType>
DataType cMatrixFunctions<DataType>::logdet(
        DataType* A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType& sign)
{
    DataType logdet_;

    // Allocate matrices
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;
    DataType status = 0;

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        status = cMatrixDecompositions<DataType>::cholesky(A, num_rows, L);

        // Check if the Cholesky decomposition was successful.
        if (status != 0)
        {
            // Matrix is not positive-definite.
            sign = -3;

            // Free memory
            ArrayUtil<DataType>::del(L);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_ = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to LU.
        P = new LongIndexType[num_rows+1];
        status = cMatrixDecompositions<DataType>::plu(A, P, num_rows, tol);
        
        // Check if the plu decomposition was successful.
        if (status != 0)
        {
            // Matrix is degenerate.
            sign = -4;

            // Free memory
            ArrayUtil<DataType>::del(L);
            ArrayUtil<LongIndexType>::del(P);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_ = cMatrixFunctions<DataType>::triang_logdet(
                A, P, num_rows, sign);
    }

    // Free array
    ArrayUtil<DataType>::del(L);
    ArrayUtil<LongIndexType>::del(P);
    
    return logdet_;
}


// =============
// triang logdet
// =============

/// \brief Computes logdet for triangular matrices.
///

template <typename DataType>
DataType cMatrixFunctions<DataType>::triang_logdet(
        const DataType* A,
        const LongIndexType* P,
        const LongIndexType num_rows,
        FlagType& sign)
{
    DataType logdet_ = 0.0;
    DataType diag;
    sign = 1;
    
    for (LongIndexType i=0; i < num_rows; ++i)
    {
        // Get the i-th element of the diagonal of A
        if (P == NULL)
        {
            diag = A[i*num_rows + i];
        }
        else
        {
            // When permutation is given, use the i-th permuted row of A.
            diag = A[P[i]*num_rows + i];
        }

        if (diag == 0.0)
        {
            // Logdet is -inf, however, here we set it to zero and flag sign to
            // negative two to identify this special case later.
            logdet_ = 0.0;
            sign = -2;
            break;
        }
        else if (diag < 0.0)
        {
            sign = -sign;
            logdet_ += log(fabs(diag));
        }
        else
        {
            logdet_ += log(diag);
        }
    }

    // Adjust sign due to permutations of the rows of A
    if ((P != NULL) & (sign != -2))
    {
        // Change sign if the number of permutations is an odd number
        if ((P[num_rows] - num_rows) % 2 == 1)
        {
            sign = -sign;
        }
    }

    return logdet_;
}


// ===
// det
// ===

/// \brief  Computes the determinant of a matrix.
///

template <typename DataType>
DataType cMatrixFunctions<DataType>::det(
        DataType* A,
        const LongIndexType num_rows,
        const FlagType sym_pos)
{
    // Compute logdet
    FlagType sign;
    DataType logdet_ = cMatrixFunctions<DataType>::logdet(
            A, num_rows, sym_pos, sign);

    // Convert logdet to det
    DataType det;
    if (sign == -2)
    {
        det = 0.0;
    }
    else
    {
        det = exp(logdet_) * static_cast<DataType>(sign);
    }
    
    return det;
}


// =======
// loggdet
// =======

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::loggdet(
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
        long long& flops)
{
    DataType loggdet_;

    #if COUNT_PERF
    // Measure flops
    cInstructionsCounter* instructions_counter = NULL;
    if (flops == 1)
    {
        instructions_counter = new cInstructionsCounter();
        instructions_counter->start();
    }
    #endif

    if (method == 0)
    {
        // Using legacy method
        loggdet_ = cMatrixFunctions<DataType>::_loggdet_legacy(
                A, X, num_rows, num_columns, sym_pos, sign);
    }
    else if (method == 1)
    {
        // Using projection method
        loggdet_ = cMatrixFunctions<DataType>::_loggdet_proj(
                A, X, num_rows, num_columns, X_orth, sign);
    }
    else
    {
        // Using compression method (method=2)
        loggdet_ = cMatrixFunctions<DataType>::_loggdet_comp(
                A, X, Xp, use_Xp, num_rows, num_columns, sym_pos, X_orth,
                sign);
    }

    #if COUNT_PERF
    if (flops == 1)
    {
        instructions_counter->stop();
        flops = instructions_counter->get_count();

        if (instructions_counter != NULL)
        {
            delete instructions_counter;
            instructions_counter = NULL;
        }
    }
    #endif

    return loggdet_;
}


// ==============
// loggdet legacy
// ==============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_loggdet_legacy(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        FlagType& sign)
{
    DataType loggdet_;
    DataType logdet_A;
    DataType logdet_W;
    DataType coeff = 0;
    FlagType sign_A;
    FlagType sign_W;

    // Allocate matrix L
    DataType* A_copy = new DataType[num_rows*num_rows];
    DataType* Y = new DataType[num_rows*num_rows];
    DataType* W = new DataType[num_rows*num_rows];
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;
    DataType status = 0;

    // Copy A to A_copy since A_copy will be overwritten during decompositions
    cMatrixOperations<DataType>::copy(A, A_copy, num_rows, num_rows);

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        status = cMatrixDecompositions<DataType>::cholesky(
            A_copy, num_rows, L);

        // Check if the Cholesky decomposition was successful.
        if (status != 0)
        {
            // Matrix is not positive-definite.
            sign = -3;

            // Free array
            ArrayUtil<DataType>::del(A_copy);
            ArrayUtil<DataType>::del(Y);
            ArrayUtil<DataType>::del(W);
            ArrayUtil<DataType>::del(L);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_A = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign_A);

        // Solve Y = Linv * X
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = Y.T * Y
        cMatrixOperations<DataType>::gramian(
                Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to U.
        P = new LongIndexType[num_rows+1];
        status = cMatrixDecompositions<DataType>::plu(
            A_copy, P, num_rows, tol);

        // Check if the plu decomposition was successful.
        if (status != 0)
        {
            // Matrix is degenerate.
            sign = -4;

            // Free memory
            ArrayUtil<DataType>::del(A_copy);
            ArrayUtil<DataType>::del(Y);
            ArrayUtil<DataType>::del(W);
            ArrayUtil<LongIndexType>::del(P);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_A = cMatrixFunctions<DataType>::triang_logdet(
                A_copy, P, num_rows, sign_A);

        // Solve Y = Ainv * X using LU decomposition of A_copy. A_copy is U.
        cMatrixSolvers<DataType>::plu_solve(
                A_copy, P, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = X.T * Y
        cMatrixOperations<DataType>::inner_prod(
                X, Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }

    // Compute loggdet
    loggdet_ = logdet_A + logdet_W;

    // Sign
    if ((sign_A == -2) || (sign_W == -2))
    {
        // Indicates that det of one of A or W is zero.
        sign = -2;
    }
    else
    {
        sign = sign_A * sign_W;
    }

    // Free array
    ArrayUtil<DataType>::del(A_copy);
    ArrayUtil<DataType>::del(Y);
    ArrayUtil<DataType>::del(W);
    ArrayUtil<DataType>::del(L);
    ArrayUtil<LongIndexType>::del(P);

    return loggdet_;
}


// ============
// loggdet proj
// ============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_loggdet_proj(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType loggdet_;
    DataType logdet_N;
    DataType logdet_XtX = 0.0;
    FlagType sign_XtX = 1;
    FlagType sign_N;

    // Allocate matrix L
    DataType* N = new DataType[num_rows*num_rows];
    DataType* A_I = new DataType[num_rows*num_rows];
    DataType* M = new DataType[num_rows*num_columns];
    DataType* S = new DataType[num_rows*num_rows];
    DataType* Y = NULL;
    DataType* XtX = NULL;
    DataType* L = NULL;
    LongIndexType* P = NULL;  // will not be used

    // Initialize N with A
    cMatrixOperations<DataType>::copy(A, N, num_rows, num_rows);

    // Initialize A_I with A
    cMatrixOperations<DataType>::copy(A, A_I, num_rows, num_rows);

    // Subtract identity from A_I, so at this point, A_I becomes A-I
    cMatrixOperations<DataType>::add_diagonal_inplace(A_I, -1.0, num_rows);

    // Compute S = (A-I)*X or S=(A-I)*Y
    if (X_orth == 1)
    {
        // Perform M = (A-I)*X
        cMatrixOperations<DataType>::matmat(
                A_I, X, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*X.T
        cMatrixOperations<DataType>::outer_prod(
                M, X, S, num_rows, num_columns, 0);
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::gramian(
                X, XtX, num_rows, num_columns, 0);

        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_columns*num_columns];
        cMatrixDecompositions<DataType>::cholesky(XtX, num_columns, L);

        // Compute logdet of XtX. Note XtX_sign is always 1, will not be used.
        logdet_XtX = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_columns, sign_XtX);

        // Compute Y.T = Linv * X.T
        Y = new DataType[num_rows*num_columns];
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_columns, num_rows, 1, 1);

        // Perform M = (A-I)*Y
        cMatrixOperations<DataType>::matmat(
                A_I, Y, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*Y.T
        cMatrixOperations<DataType>::outer_prod(
                M, Y, S, num_rows, num_columns, 0);
    }

    // Perform N = A - S (N is subtracted from A since N is initialized as A)
    cMatrixOperations<DataType>::subtract_inplace(
            N, S, num_rows, num_rows);

    // Compute logdet of N
    logdet_N = cMatrixFunctions<DataType>::logdet(N, num_rows, 0, sign_N);

    // Compute loggdet
    loggdet_ = logdet_N + logdet_XtX;

    // Sign
    if (sign_N == -4)
    {
        // Matrix is degenerate
        sign = -4;
    }
    else if ((sign_N == -2) || (sign_XtX == -2))
    {
        sign = -2;
    }
    else
    {
        sign = sign_N * sign_XtX;
    }

    // Free array
    ArrayUtil<DataType>::del(N);
    ArrayUtil<DataType>::del(A_I);
    ArrayUtil<DataType>::del(M);
    ArrayUtil<DataType>::del(S);
    ArrayUtil<DataType>::del(XtX);
    ArrayUtil<DataType>::del(L);
    ArrayUtil<DataType>::del(Y);
    ArrayUtil<LongIndexType>::del(P);

    return loggdet_;
}


// ============
// loggdet comp
// ============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_loggdet_comp(
        const DataType* A,
        const DataType* X,
        DataType* Xp,
        const FlagType use_Xp,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType loggdet_;
    DataType logdet_Ap;
    DataType logdet_XtX = 0.0;
    FlagType sign_XtX = 1;
    FlagType sign_Ap;
    LongIndexType num_columns_xp = num_rows - num_columns;
    FlagType Xp_allocated = 0;

    // Allocate matrices
    DataType* Y = new DataType[num_rows*num_columns_xp];
    DataType* Ap = new DataType[num_columns_xp*num_columns_xp];
    DataType* XtX = NULL;
    DataType* Xp_;

    // Compute Xp, the orthonormal complement of X. If Xp is not null, it means
    // it is already created.
    if (use_Xp == 0)
    {
        Xp_ = new DataType[num_rows*num_columns_xp];

        // Indicate Xp is allocated so to deallocate it. If not allocated, keep
        // it as is because it may be used in the future function calls.
        Xp_allocated = 1;

        // Compute Xp, the orthonormal complement of X
        cMatrixDecompositions<DataType>::ortho_complement(
                Xp_, X, num_rows, num_columns_xp, num_columns, X_orth);
    }
    else
    {
        // If Xp is not NULL, it is assumed that Xp is orthogonal complement of
        // X, and already pre-computed.
        Xp_ = Xp;
    }

    // Compute Y = A * Xp
    cMatrixOperations<DataType>::matmat(
            A, Xp_, Y, num_rows, num_rows, num_columns_xp, 0.0);

    // Compute Ap = Xp.T * Y
    if (sym_pos == 1)
    {
        cMatrixOperations<DataType>::gramian_matmat_transpose(
                Xp_, Y, Ap, num_rows, num_columns_xp, 0.0);
    }
    else
    {
        cMatrixOperations<DataType>::matmat_transpose(
                Xp_, Y, Ap, num_rows, num_columns_xp, num_columns_xp, 0.0);
    }

    // Compute logdet of Ap
    logdet_Ap = cMatrixFunctions<DataType>::logdet(
            Ap, num_columns_xp, sym_pos, sign_Ap);

    // Compute logdet of XtX
    if (X_orth == 1)
    {
        logdet_XtX = 0.0;
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::gramian(
                X, XtX, num_rows, num_columns, 0);

        // Compute logdet of XtX. Note XtX_sign is always 1, will not be used.
        logdet_XtX = cMatrixFunctions<DataType>::logdet(
                XtX, num_columns, 1, sign_XtX);
    }

    // Compute loggdet
    loggdet_ = logdet_Ap + logdet_XtX;

    // Sign
    if (sign_Ap == -4)
    {
        // Matrix is degenerate
        sign = -4;
    }
    else if ((sign_Ap == -2) || (sign_XtX == -2))
    {
        sign = -2;
    }
    else
    {
        sign = sign_Ap * sign_XtX;
    }

    // Free array
    if (Xp_allocated == 1)
    {
        ArrayUtil<DataType>::del(Xp_);
    }
    ArrayUtil<DataType>::del(Y);
    ArrayUtil<DataType>::del(Ap);
    ArrayUtil<DataType>::del(XtX);

    return loggdet_;
}


// =======
// logpdet
// =======

/// \brief Computes the pseudo logdet of M.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::logpdet(
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
        long long& flops)
{
    DataType logpdet_;
    
    #if COUNT_PERF
    // Measure flops
    cInstructionsCounter* instructions_counter = NULL;
    if (flops == 1)
    {
        instructions_counter = new cInstructionsCounter();
        instructions_counter->start();
    }
    #endif

    if (method == 0)
    {
        // Using legacy method
        logpdet_ = cMatrixFunctions<DataType>::_logpdet_legacy(
                A, X, num_rows, num_columns, sym_pos, X_orth, sign);
    }
    else if (method == 1)
    {
        // Using projection method
        logpdet_ = cMatrixFunctions<DataType>::_logpdet_proj(
                A, X, num_rows, num_columns, X_orth, sign);
    }
    else
    {
        // Using compression method (method=2)
        logpdet_ = cMatrixFunctions<DataType>::_logpdet_comp(
                A, X, Xp, use_Xp, num_rows, num_columns, sym_pos, X_orth,
                sign);
    }

    #if COUNT_PERF
    if (flops == 1)
    {
        instructions_counter->stop();
        flops = instructions_counter->get_count();

        if (instructions_counter != NULL)
        {
            delete instructions_counter;
            instructions_counter = NULL;
        }
    }
    #endif

    return logpdet_;
}


// ==============
// logpdet legacy
// ==============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_logpdet_legacy(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType logpdet_;
    DataType logdet_A;
    DataType logdet_W;
    DataType logdet_XtX;
    FlagType XtX_sign;
    DataType coeff = 0;
    FlagType sign_A;
    FlagType sign_W;
    FlagType sign_XtX;

    // Allocate matrix L
    DataType* A_copy = new DataType[num_rows*num_rows];
    DataType* Y = new DataType[num_rows*num_rows];
    DataType* W = new DataType[num_rows*num_rows];
    DataType* XtX = NULL;
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;
    DataType status = 0;

    // Copy A to A_copy since A_copy will be overwritten during decompositions
    cMatrixOperations<DataType>::copy(A, A_copy, num_rows, num_rows);

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        status = cMatrixDecompositions<DataType>::cholesky(
            A_copy, num_rows, L);

        // Check if the Cholesky decomposition was successful.
        if (status != 0)
        {
            // Matrix is not positive-definite.
            sign = -3;
    
            ArrayUtil<DataType>::del(A_copy);
            ArrayUtil<DataType>::del(Y);
            ArrayUtil<DataType>::del(W);
            ArrayUtil<DataType>::del(L);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_A = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign_A);

        // Solve Y = Linv * X
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = Y.T * Y
        cMatrixOperations<DataType>::gramian(
                Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to U.
        P = new LongIndexType[num_rows+1];
        status = cMatrixDecompositions<DataType>::plu(
            A_copy, P, num_rows, tol);

        // Check if the plu decomposition was successful.
        if (status != 0)
        {
            // Matrix is degenerate.
            sign = -4;

            // Free memory
            ArrayUtil<DataType>::del(A_copy);
            ArrayUtil<DataType>::del(Y);
            ArrayUtil<DataType>::del(W);
            ArrayUtil<LongIndexType>::del(P);

            return NAN;
        }

        // Compute logdet based on the diagonals of A
        logdet_A = cMatrixFunctions<DataType>::triang_logdet(
                A_copy, P, num_rows, sign_A);

        // Solve Y = Ainv * X using LU decomposition of A_copy. A_copy is U.
        cMatrixSolvers<DataType>::plu_solve(
                A_copy, P, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = X.T * Y
        cMatrixOperations<DataType>::inner_prod(
                X, Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }

    if (X_orth == 1)
    {
        logdet_XtX = 0.0;
        sign_XtX = 1;
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::gramian(
                X, XtX, num_rows, num_columns, 0);

        logdet_XtX = cMatrixFunctions<DataType>::logdet(
                XtX, num_columns, 1, XtX_sign);
    }

    // Compute logpdet
    logpdet_ = logdet_XtX - logdet_A - logdet_W;

    // Sign
    if (sign_XtX == -2)
    {
        // This indicates logdet_XtX is -inf.
        sign = -2;
    }
    else if ((sign_A == -2) || (sign_W == -2))
    {
        // This indicates that logdet of A or W is -inf.
        sign = 2;
    }
    else
    {
        sign = sign_XtX * sign_A * sign_W;
    }

    // Free array
    ArrayUtil<DataType>::del(A_copy);
    ArrayUtil<DataType>::del(Y);
    ArrayUtil<DataType>::del(W);
    ArrayUtil<DataType>::del(L);
    ArrayUtil<DataType>::del(XtX);
    ArrayUtil<LongIndexType>::del(P);

    return logpdet_;
}


// ============
// logpdet proj
// ============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_logpdet_proj(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType logpdet_;
    DataType logdet_N;
    FlagType sign_N;

    // Allocate matrix L
    DataType* N = new DataType[num_rows*num_rows];
    DataType* A_I = new DataType[num_rows*num_rows];
    DataType* M = new DataType[num_rows*num_columns];
    DataType* S = new DataType[num_rows*num_rows];
    DataType* Y = NULL;
    DataType* XtX = NULL;
    DataType* L = NULL;

    // Initialize N with A
    cMatrixOperations<DataType>::copy(A, N, num_rows, num_rows);

    // Initialize A_I with A
    cMatrixOperations<DataType>::copy(A, A_I, num_rows, num_rows);

    // Subtract identity from A_I, so at this point, A_I becomes A-I
    cMatrixOperations<DataType>::add_diagonal_inplace(A_I, -1.0, num_rows);

    // Compute S = (A-I)*X or S=(A-I)*Y
    if (X_orth == 1)
    {
        // Perform M = (A-I)*X
        cMatrixOperations<DataType>::matmat(
                A_I, X, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*X.T
        cMatrixOperations<DataType>::outer_prod(
                M, X, S, num_rows, num_columns, 0);
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::gramian(
                X, XtX, num_rows, num_columns, 0);

        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_columns*num_columns];
        cMatrixDecompositions<DataType>::cholesky(XtX, num_columns, L);

        // Compute Y.T = Linv * X.T
        Y = new DataType[num_rows*num_columns];
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_columns, num_rows, 1, 1);

        // Perform M = (A-I)*Y
        cMatrixOperations<DataType>::matmat(
                A_I, Y, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*Y.T
        cMatrixOperations<DataType>::outer_prod(
                M, Y, S, num_rows, num_columns, 0);
    }

    // Perform N = A - S (N is subtracted from A since N is initialized as A)
    cMatrixOperations<DataType>::subtract_inplace(
            N, S, num_rows, num_rows);

    // Compute logdet of N
    logdet_N = cMatrixFunctions<DataType>::logdet(N, num_rows, 0, sign_N);

    // Compute logpdet
    logpdet_ = -logdet_N;

    if (sign_N == -4)
    {
        // Matrix is degenerate
        sign = -4;
    }
    else if (sign_N == -2)
    {
        // Indicates that det of N is 0, so logdet of 1/N is +inf.
        sign = 2;
    }
    else
    {
        sign = sign_N;
    }

    // Free array
    ArrayUtil<DataType>::del(N);
    ArrayUtil<DataType>::del(A_I);
    ArrayUtil<DataType>::del(M);
    ArrayUtil<DataType>::del(S);
    ArrayUtil<DataType>::del(XtX);
    ArrayUtil<DataType>::del(L);
    ArrayUtil<DataType>::del(Y);

    return logpdet_;
}


// ============
// logpdet comp
// ============

/// \brief Computes the logpdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_logpdet_comp(
        const DataType* A,
        const DataType* X,
        DataType* Xp,
        const FlagType use_Xp,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType logpdet_;
    DataType logdet_Ap;
    FlagType sign_Ap;
    LongIndexType num_columns_xp = num_rows - num_columns;
    FlagType Xp_allocated = 0;

    // Allocate matrices
    DataType* Y = new DataType[num_rows*num_columns_xp];
    DataType* Ap = new DataType[num_columns_xp*num_columns_xp];
    DataType* XtX = NULL;
    DataType* Xp_;

    // Compute Xp, the orthonormal complement of X. If Xp is not null, it means
    // it is already created.
    if (use_Xp == 0)
    {
        Xp_ = new DataType[num_rows*num_columns_xp];

        // Indicate Xp is allocated so to deallocate it. If not allocated, keep
        // it as is because it may be used in the future function calls.
        Xp_allocated = 1;

        // Compute Xp, the orthonormal complement of X
        cMatrixDecompositions<DataType>::ortho_complement(
                Xp_, X, num_rows, num_columns_xp, num_columns, X_orth);
    }
    else
    {
        // If Xp is not NULL, it is assumed that Xp is orthogonal complement of
        // X, and already pre-computed.
        Xp_ = Xp;
    }

    // Compute Y = A * Xp
    cMatrixOperations<DataType>::matmat(
            A, Xp_, Y, num_rows, num_rows, num_columns_xp, 0.0);

    // Compute Ap = Xp.T * Y
    cMatrixOperations<DataType>::matmat_transpose(
            Xp_, Y, Ap, num_rows, num_columns_xp, num_columns_xp, 0.0);

    // Compute logdet of Ap
    logdet_Ap = cMatrixFunctions<DataType>::logdet(
            Ap, num_columns_xp, sym_pos, sign_Ap);

    // Compute loggdet
    logpdet_ = -logdet_Ap;

    // Sign
    if (sign_Ap == -4)
    {
        // Matrix is degenerate
        sign = -4;
    }
    else if (sign_Ap == -2)
    {
        sign = -2;
    }
    else
    {
        sign = sign_Ap;
    }

    // Free array
    if (Xp_allocated == 1)
    {
        ArrayUtil<DataType>::del(Xp_);
    }
    ArrayUtil<DataType>::del(Y);
    ArrayUtil<DataType>::del(Ap);
    ArrayUtil<DataType>::del(XtX);

    return logpdet_;
}


// ===============================
// Explicit template instantiation
// ===============================

template class cMatrixFunctions<float>;
template class cMatrixFunctions<double>;
template class cMatrixFunctions<long double>;
