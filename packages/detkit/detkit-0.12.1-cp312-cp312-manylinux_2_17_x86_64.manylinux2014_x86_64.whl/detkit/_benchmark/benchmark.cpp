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

#include "./benchmark.h"
#include <cstdlib>  // rand, RAND_MAX
#include <cassert>  // assert
#include "../_definitions/definitions.h"  // COUNT_PERF
#include "../_device/c_instructions_counter.h"  // cInstructionsCounter
#include "../_c_basic_algebra/c_matrix_operations.h"  // cMatrixOperations
#include "../_c_linear_algebra/c_matrix_decompositions.h"  // cMatrixDecompo...


// ======
// matmul
// ======

/// \brief  Computes the number of hardware instructions for a matrix-martrix
///         multiplication. This number is used to find on a certain device,
///         how many insrtrucitons is needed to compute a single task in
///         mat-mat multiplication, that is, a multiplication of two scalars
///         and one addition.

template <typename DataType>
long long Benchmark<DataType>::matmul(
        const DataType* dummy_var,
        const LongIndexType n)
{
    long long hw_instructions = -1;

    // Mark unused variables to avoid compiler warnings
    // (-Wno-unused-parameter)
    (void) dummy_var;

    #if COUNT_PERF

        DataType* A = new DataType[n*n];
        DataType* B = new DataType[n*n];
        DataType* C = new DataType[n*n];

        // Initialize A and B with random numbers
        Benchmark<DataType>::random(A, n, n);
        Benchmark<DataType>::random(B, n, n);

        // Start measure flops
        cInstructionsCounter instructions_counter = cInstructionsCounter();
        instructions_counter.start();

        // Matrix-matrix multiplications
        cMatrixOperations<DataType>::matmat(A, B, C, n, n, n, 0.0);

        // Terminate measuring flops
        instructions_counter.stop();
        hw_instructions = instructions_counter.get_count();

        delete[] A;
        delete[] B;
        delete[] C;

    #endif

    return hw_instructions;
}


// =======
// gramian
// =======

/// \brief  Computes the number of hardware instructions for a matrix-martrix
///         multiplication. This number is used to find on a certain device,
///         how many insrtrucitons is needed to compute a single task in
///         mat-mat multiplication, that is, a multiplication of two scalars
///         and one addition.

template <typename DataType>
long long Benchmark<DataType>::gramian(
        const DataType* dummy_var,
        const LongIndexType n)
{
    long long hw_instructions = -1;

    // Mark unused variables to avoid compiler warnings
    // (-Wno-unused-parameter)
    (void) dummy_var;

    #if COUNT_PERF

        DataType* A = new DataType[n*n];
        DataType* B = new DataType[n*n];

        // Initialize A and B with random numbers
        Benchmark<DataType>::random(A, n, n);

        // Start measure flops
        cInstructionsCounter instructions_counter = cInstructionsCounter();
        instructions_counter.start();

        // Gramian matrix-matrix multiplications
        cMatrixOperations<DataType>::gramian(A, B, n,n, 0.0);

        // Terminate measuring flops
        instructions_counter.stop();
        hw_instructions = instructions_counter.get_count();

        delete[] A;
        delete[] B;

    #endif

    return hw_instructions;
}


// ========
// cholesky
// ========

/// \brief  Computes the number of hardware instructions for a matrix-martrix
///         multiplication. This number is used to find on a certain device,
///         how many insrtrucitons is needed to compute a single task in
///         mat-mat multiplication, that is, a multiplication of two scalars
///         and one addition.

template <typename DataType>
long long Benchmark<DataType>::cholesky(
        const DataType* dummy_var,
        const LongIndexType n)
{
    long long hw_instructions = -1;

    // Mark unused variables to avoid compiler warnings
    // (-Wno-unused-parameter)
    (void) dummy_var;

    #if COUNT_PERF

        DataType* A = new DataType[n*n];
        DataType* B = new DataType[n*n];
        DataType* L = new DataType[n*n];

        // Initialize A with random numbers
        Benchmark<DataType>::random(A, n, n);

        // Make A to be symmetric positive-definite, outputs to B
        cMatrixOperations<DataType>::gramian(A, B, n, n, 0.0);

        // Start measure flops
        cInstructionsCounter instructions_counter = cInstructionsCounter();
        instructions_counter.start();

        // Cholesky decomposition
        cMatrixDecompositions<DataType>::cholesky(B, n, L);

        // Terminate measuring flops
        instructions_counter.stop();
        hw_instructions = instructions_counter.get_count();

        delete[] A;
        delete[] B;
        delete[] L;

    #endif

    return hw_instructions;
}


// ==
// lu
// ==

/// \brief  Computes the number of hardware instructions for a matrix-martrix
///         multiplication. This number is used to find on a certain device,
///         how many insrtrucitons is needed to compute a single task in
///         mat-mat multiplication, that is, a multiplication of two scalars
///         and one addition.

template <typename DataType>
long long Benchmark<DataType>::lu(
        const DataType* dummy_var,
        const LongIndexType n)
{
    long long hw_instructions = -1;

    // Mark unused variables to avoid compiler warnings
    // (-Wno-unused-parameter)
    (void) dummy_var;

    #if COUNT_PERF

        DataType* A = new DataType[n*n];
        DataType* L = new DataType[n*n];

        // Initialize A with random numbers
        Benchmark<DataType>::random(A, n, n);

        // Start measure flops
        cInstructionsCounter instructions_counter = cInstructionsCounter();
        instructions_counter.start();

        // LU decomposition
        cMatrixDecompositions<DataType>::lu(A, n, L);

        // Terminate measuring flops
        instructions_counter.stop();
        hw_instructions = instructions_counter.get_count();

        delete[] A;
        delete[] L;

    #endif

    return hw_instructions;
}


// ===
// plu
// ===

/// \brief  Computes the number of hardware instructions for a matrix-martrix
///         multiplication. This number is used to find on a certain device,
///         how many insrtrucitons is needed to compute a single task in
///         mat-mat multiplication, that is, a multiplication of two scalars
///         and one addition.

template <typename DataType>
long long Benchmark<DataType>::plu(
        const DataType* dummy_var,
        const LongIndexType n)
{
    long long hw_instructions = -1;

    // Mark unused variables to avoid compiler warnings
    // (-Wno-unused-parameter)
    (void) dummy_var;

    #if COUNT_PERF

        DataType* A = new DataType[n*n];
        LongIndexType* P = new LongIndexType[n+1];

        // Initialize A with random numbers
        Benchmark<DataType>::random(A, n, n);

        // Start measure flops
        cInstructionsCounter instructions_counter = cInstructionsCounter();
        instructions_counter.start();

        // PLU decomposition
        DataType tol = 1e-8;
        FlagType status = cMatrixDecompositions<DataType>::plu(A, P, n, tol);

        // With the if condition, avoid -Wunused-value warning
        if (status == 0)
        {
            assert(status != 0);
        }

        // Terminate measuring flops
        instructions_counter.stop();
        hw_instructions = instructions_counter.get_count();

        delete[] A;
        delete[] P;

    #endif

    return hw_instructions;
}


// =====
// zeros
// =====

/// \brief Initializes a matrix with zeros.
///

template<typename DataType>
void Benchmark<DataType>::zeros(
        DataType* A,
        const LongIndexType n,
        const LongIndexType m)
{
    for (LongIndexType i=0; i < n; ++i)
    {
        for (LongIndexType j=0; j < m; ++j)
        {
            A[i*n + j] = 0.0;
        }
    }
}


// ======
// random
// ======

/// \brief Initializes a matrix with random numbers between 0 and 1.
///

template<typename DataType>
void Benchmark<DataType>::random(
        DataType* A,
        const LongIndexType n,
        const LongIndexType m)
{
    for (LongIndexType i=0; i < n; ++i)
    {
        for (LongIndexType j=0; j < m; ++j)
        {
            A[i*n + j] = rand() / static_cast<DataType>(RAND_MAX);
        }
    }
}


// ===============================
// Explicit template instantiation
// ===============================

template class Benchmark<float>;
template class Benchmark<double>;
template class Benchmark<long double>;
