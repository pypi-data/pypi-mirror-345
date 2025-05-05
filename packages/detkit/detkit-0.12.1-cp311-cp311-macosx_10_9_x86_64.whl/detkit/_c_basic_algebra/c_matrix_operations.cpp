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

#include "./c_matrix_operations.h"
#include "../_definitions/definitions.h"  // USE_SYMMETRY, USE_OPENMP
                                          // USE_LOOP_UNROLLING
#if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #include <omp.h>
#endif


// ====
// copy
// ====

/// \brief Copies A to B.
///

template <typename DataType>
void cMatrixOperations<DataType>::copy(
        const DataType* A,
        DataType* B,
        const LongIndexType num_rows,
        const LongIndexType num_columns)
{
    LongIndexType j;

    for (LongIndexType i=0; i < num_rows; ++i)
    {
        for (j=0; j < num_columns; ++j)
        {
            B[i*num_columns + j] = A[i*num_columns + j];
        }
    }
}


// ===
// add
// ===

/// \brief Adds two matrices \c A+B and relaces the result in \c C.
///

template <typename DataType>
void cMatrixOperations<DataType>::add(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType num_rows,
        const LongIndexType num_columns)
{
    LongIndexType j;

    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType num_columns_chunked = num_columns - (num_columns % chunk);
    #endif

    for (LongIndexType i=0; i < num_rows; ++i)
    {
        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j=0; j < num_columns_chunked; j+=chunk)
        {
            C[i*num_columns + j] = \
                A[i*num_columns + j] + B[i*num_columns + j];
            C[i*num_columns + j+1] = \
                A[i*num_columns + j+1] + B[i*num_columns + j+1];
            C[i*num_columns + j+2] = \
                A[i*num_columns + j+2] + B[i*num_columns + j+2];
            C[i*num_columns + j+3] = \
                A[i*num_columns + j+3] + B[i*num_columns + j+3];
            C[i*num_columns + j+4] = \
                A[i*num_columns + j+4] + B[i*num_columns + j+4];
        }
        #endif

        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j= num_columns_chunked; j < num_columns; ++j)
        #else
        for (j=0; j < num_columns; ++j)
        #endif
        {
            C[i*num_columns + j] = A[i*num_columns + j] + B[i*num_columns + j];
        }
    }
}


// ====================
// add diagonal inplace
// ====================

/// \brief Computes A + alpha*I, where I is the identity. The result is written
///        onto A, inplace.

template <typename DataType>
void cMatrixOperations<DataType>::add_diagonal_inplace(
        DataType* A,
        const DataType alpha,
        const LongIndexType num_rows)
{
    for (LongIndexType i=0; i < num_rows; ++i)
    {
        A[i*num_rows + i] += alpha;
    }
}


// ===========
// add inplace
// ===========

/// \brief Adds two matrices \c A+B and relaces the result in \c A.
///

template <typename DataType>
void cMatrixOperations<DataType>::add_inplace(
        DataType* A,
        const DataType* B,
        const LongIndexType num_rows,
        const LongIndexType num_columns)
{
    LongIndexType j;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType num_columns_chunked = num_columns - (num_columns % chunk);
    #endif

    for (LongIndexType i=0; i < num_rows; ++i)
    {
        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j=0; j < num_columns_chunked; j+=chunk)
        {
            A[i*num_columns + j] += B[i*num_columns + j];
            A[i*num_columns + j+1] += B[i*num_columns + j+1];
            A[i*num_columns + j+2] += B[i*num_columns + j+2];
            A[i*num_columns + j+3] += B[i*num_columns + j+3];
            A[i*num_columns + j+4] += B[i*num_columns + j+4];
        }
        #endif

        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j=num_columns_chunked; j < num_columns; ++j)
        #else
        for (j=0; j < num_columns; ++j)
        #endif
        {
            A[i*num_columns + j] += B[i*num_columns + j];
        }
    }
}


// ================
// subtract inplace
// ================

/// \brief Subtracts two matrices \c A+B and relaces the result in \c A.
///

template <typename DataType>
void cMatrixOperations<DataType>::subtract_inplace(
        DataType* A,
        const DataType* B,
        const LongIndexType num_rows,
        const LongIndexType num_columns)
{
    LongIndexType j;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType num_columns_chunked = num_columns - (num_columns % chunk);
    #endif

    for (LongIndexType i=0; i < num_rows; ++i)
    {
        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j=0; j < num_columns_chunked; j+=chunk)
        {
            A[i*num_columns + j] -= B[i*num_columns + j];
            A[i*num_columns + j+1] -= B[i*num_columns + j+1];
            A[i*num_columns + j+2] -= B[i*num_columns + j+2];
            A[i*num_columns + j+3] -= B[i*num_columns + j+3];
            A[i*num_columns + j+4] -= B[i*num_columns + j+4];
        }
        #endif

        #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        for (j=num_columns_chunked; j < num_columns; ++j)
        #else
        for (j=0; j < num_columns; ++j)
        #endif
        {
            A[i*num_columns + j] -= B[i*num_columns + j];
        }
    }
}


// ======
// matmat
// ======

/// \brief matrix-matrix multiplication C = c*C + A*B, where A is (n, m),
///        and B is (m , p), and C is (n , p).

template <typename DataType>
void cMatrixOperations<DataType>::matmat(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const LongIndexType p,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType m_chunked = m - (m % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < n; ++i)
    {
        for (j=0; j < p; ++j)
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < m_chunked; k+= chunk)
            {
                sum += A[i*m + k] * B[k*p + j] +
                       A[i*m + k+1] * B[(k+1)*p + j] +
                       A[i*m + k+2] * B[(k+2)*p + j] +
                       A[i*m + k+3] * B[(k+3)*p + j] +
                       A[i*m + k+4] * B[(k+4)*p + j];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=m_chunked; k < m; ++k)
            #else
            for (k=0; k < m; ++k)
            #endif
            {
                sum += A[i*m + k] * B[k*p + j];
            }

            if (c == 0)
            {
                C[i*p + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*p + j] += c * static_cast<DataType>(sum);
            }
        }
    }
}


// ================
// matmat transpose
// ================

/// \brief matrix-matrix multiplication C = c*C + A.T * B, where A is (n, m),
///        and B is (n , p), and C is (m , p).

template <typename DataType>
void cMatrixOperations<DataType>::matmat_transpose(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const LongIndexType p,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType n_chunked = n - (n % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < m; ++i)
    {
        for (j=0; j < p; ++j)
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < n_chunked; k+= chunk)
            {
                sum += A[k*m + i] * B[k*p + j] +
                       A[(k+1)*m + i] * B[(k+1)*p + j] +
                       A[(k+2)*m + i] * B[(k+2)*p + j] +
                       A[(k+3)*m + i] * B[(k+3)*p + j] +
                       A[(k+4)*m + i] * B[(k+4)*p + j];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=n_chunked; k < n; ++k)
            #else
            for (k=0; k < n; ++k)
            #endif
            {
                sum += A[k*m + i] * B[k*p + j];
            }

            if (c == 0)
            {
                C[i*p + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*p + j] += c * static_cast<DataType>(sum);
            }
        }
    }
}


// ========================
// gramian matmat transpose
// ========================

/// \brief matrix-matrix multiplication C = c*C + A.T * B, where A is (n, m),
///        and B is (n , m), and C is (m , m). It is assumed the matrix
///        product is a symmetric matrix. So, here, we only compute half of the
///        matrix product.

template <typename DataType>
void cMatrixOperations<DataType>::gramian_matmat_transpose(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType n_chunked = n - (n % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < m; ++i)
    {
        #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
        for (j=0; j <= i; ++j)
        #else
        for (j=0; j < m; ++j)
        #endif
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < n_chunked; k+= chunk)
            {
                sum += A[k*m + i] * B[k*m + j] +
                       A[(k+1)*m + i] * B[(k+1)*m + j] +
                       A[(k+2)*m + i] * B[(k+2)*m + j] +
                       A[(k+3)*m + i] * B[(k+3)*m + j] +
                       A[(k+4)*m + i] * B[(k+4)*m + j];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=n_chunked; k < n; ++k)
            #else
            for (k=0; k < n; ++k)
            #endif
            {
                sum += A[k*m + i] * B[k*m + j];
            }

            if (c == 0)
            {
                C[i*m + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*m + j] += c * static_cast<DataType>(sum);
            }

            #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
            // Symmetric matrix
            if (i != j)
            {
                C[j*m + i] = C[i*m + j];
            }
            #endif
        }
    }
}


// =======
// gramian
// =======

/// \brief matrix-matrix multiplication C = c*C + A.T * A, where A is (n, m),
///        and the output C is (m , m) matrix.

template <typename DataType>
void cMatrixOperations<DataType>::gramian(
        const DataType* A,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType n_chunked = n - (n % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < m; ++i)
    {
        #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
        for (j=i; j < m; ++j)
        #else
        for (j=0; j < m; ++j)
        #endif
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < n_chunked; k+= chunk)
            {
                sum += A[k*m + i] * A[k*m + j] +
                       A[(k+1)*m + i] * A[(k+1)*m + j] +
                       A[(k+2)*m + i] * A[(k+2)*m + j] +
                       A[(k+3)*m + i] * A[(k+3)*m + j] +
                       A[(k+4)*m + i] * A[(k+4)*m + j];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=n_chunked; k < n; ++k)
            #else
            for (k=0; k < n; ++k)
            #endif
            {
                sum += A[k*m + i] * A[k*m + j];
            }

            if (c == 0)
            {
                C[i*m + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*m + j] += c * static_cast<DataType>(sum);
            }

            // Symmetry of Gramian matrix
            #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
            if (i != j)
            {
                if (c == 0)
                {
                    C[j*m + i] = static_cast<DataType>(sum);
                }
                else
                {
                    C[j*m + i] += c * static_cast<DataType>(sum);
                }
            }
            #endif
        }
    }
}


// ==========
// inner prod
// ==========

/// \brief matrix-matrix multiplication C = c*C + A.T * B, where A and B are
///        (n, m), and the output C is (m , m) matrix.

template <typename DataType>
void cMatrixOperations<DataType>::inner_prod(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType n_chunked = n - (n % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < m; ++i)
    {
        for (j=0; j < m; ++j)
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < n_chunked; k+= chunk)
            {
                sum += A[k*m + i] * B[k*m + j] +
                       A[(k+1)*m + i] * B[(k+1)*m + j] +
                       A[(k+2)*m + i] * B[(k+2)*m + j] +
                       A[(k+3)*m + i] * B[(k+3)*m + j] +
                       A[(k+4)*m + i] * B[(k+4)*m + j];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=n_chunked; k < n; ++k)
            #else
            for (k=0; k < n; ++k)
            #endif
            {
                sum += A[k*m + i] * B[k*m + j];
            }

            if (c == 0)
            {
                C[i*m + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*m + j] += c * static_cast<DataType>(sum);
            }
        }
    }
}


// ==========
// outer prod
// ==========

/// \brief matrix-matrix multiplication C = c*C + A * B.T, where A is (n, m),
///        matrix B is (n, m), and the output C is (n, n) matrix.

template <typename DataType>
void cMatrixOperations<DataType>::outer_prod(
        const DataType* A,
        const DataType* B,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType m_chunked = m - (m % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < n; ++i)
    {
        for (j=0; j < n; ++j)
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < m_chunked; k+= chunk)
            {
                sum += A[i*m + k] * B[j*m + k] +
                       A[i*m + k+1] * B[j*m + k+1] +
                       A[i*m + k+2] * B[j*m + k+2] +
                       A[i*m + k+3] * B[j*m + k+3] +
                       A[i*m + k+4] * B[j*m + k+4];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=m_chunked; k < m; ++k)
            #else
            for (k=0; k < m; ++k)
            #endif
            {
                sum += A[i*m + k] * B[j*m + k];
            }

            if (c == 0)
            {
                C[i*n + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*n + j] += c * static_cast<DataType>(sum);
            }
        }
    }
}


// ===============
// self outer prod
// ===============

/// \brief matrix-matrix multiplication C = c*C + A * A.T, where A is (n, m),
///        and the output C is (n, n) matrix.

template <typename DataType>
void cMatrixOperations<DataType>::self_outer_prod(
        const DataType* A,
        DataType* C,
        const LongIndexType n,
        const LongIndexType m,
        const DataType c)
{
    LongIndexType j;
    LongIndexType k;
    long double sum;
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
    LongIndexType chunk = 5;
    LongIndexType m_chunked = m - (m % chunk);
    #endif

    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
    #pragma omp parallel for private(j, k, sum)
    #endif
    for (LongIndexType i=0; i < n; ++i)
    {
        #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
        for (j=i; j < n; ++j)
        #else
        for (j=0; j < n; ++j)
        #endif
        {
            sum = 0.0;
            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=0; k < m_chunked; k+= chunk)
            {
                sum += A[i*m + k] * A[j*m + k] +
                       A[i*m + k+1] * A[j*m + k+1] +
                       A[i*m + k+2] * A[j*m + k+2] +
                       A[i*m + k+3] * A[j*m + k+3] +
                       A[i*m + k+4] * A[j*m + k+4];
            }
            #endif

            #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
            for (k=m_chunked; k < m; ++k)
            #else
            for (k=0; k < m; ++k)
            #endif
            {
                sum += A[i*m + k] * A[j*m + k];
            }

            if (c == 0)
            {
                C[i*n + j] = static_cast<DataType>(sum);
            }
            else
            {
                C[i*n + j] += c * static_cast<DataType>(sum);
            }

            // Symmetry of outer product
            #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
            if (i != j)
            {
                if (c == 0)
                {
                    C[j*n + i] = static_cast<DataType>(sum);
                }
                else
                {
                    C[j*n + i] += c * static_cast<DataType>(sum);
                }
            }
            #endif
        }
    }
}


// ===============================
// Explicit template instantiation
// ===============================

template class cMatrixOperations<float>;
template class cMatrixOperations<double>;
template class cMatrixOperations<long double>;
