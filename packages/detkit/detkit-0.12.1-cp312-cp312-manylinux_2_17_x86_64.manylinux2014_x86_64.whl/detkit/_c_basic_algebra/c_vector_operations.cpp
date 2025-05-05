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

#include "./c_vector_operations.h"
#include <cmath>  // sqrt
#include "../_definitions/definitions.h"


// ======================
// subtract scaled vector
// ======================

/// \brief         Subtracts the scaled column \c j of matrix \c B from the
///                column \c i of \c A and writes to \c A inplace. Both
///                matrices should have the same number of rows.
///

template <typename DataType>
void cVectorOperations<DataType>::subtract_scaled_vector(
        DataType* A,
        DataType* B,
        const LongIndexType num_rows,
        const LongIndexType num_columns_A,
        const LongIndexType num_columns_B,
        const DataType scale,
        const LongIndexType i_A,
        const LongIndexType j_B)
{
    if (scale == 0.0)
    {
        return;
    }

    for (LongIndexType k=0; k < num_rows; ++k)
    {
        A[k*num_columns_A + i_A] -= scale * B[k*num_columns_B + j_B];
    }
}


// =============
// inner product
// =============

/// \brief     Computes Euclidean inner product of two columns of a matrix.
///

template <typename DataType>
DataType cVectorOperations<DataType>::inner_product(
        const DataType* A,
        const DataType* B,
        const LongIndexType num_rows,
        const LongIndexType num_columns_A,
        const LongIndexType num_columns_B,
        const LongIndexType i_A,
        const LongIndexType j_B)
{
    long double inner_prod = 0.0;

    for (LongIndexType k=0; k < num_rows; ++k)
    {
        inner_prod += A[k*num_columns_A + i_A] * B[k*num_columns_B + j_B];
    }

    return static_cast<DataType>(inner_prod);
}


// ==============
// euclidean norm
// ==============

/// \brief     Computes the Euclidean norm of a column of a matrix.
///

template <typename DataType>
DataType cVectorOperations<DataType>::euclidean_norm(
        const DataType* A,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const LongIndexType i)
{
    // Compute norm squared
    long double norm2 = 0.0;

    for (LongIndexType k=0; k < num_rows; ++k)
    {
        norm2 += A[k*num_columns + i] * A[k*num_columns + i];
    }

    // Norm
    DataType norm = sqrt(static_cast<DataType>(norm2));

    return norm;
}


// =========================
// normalize vector in place
// =========================

/// \brief  Normalizes a column of matrix based on Euclidean 2-norm. The result
///         is written in-place.

template <typename DataType>
DataType cVectorOperations<DataType>::normalize_vector_in_place(
        DataType* A,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const LongIndexType i)
{
    // Norm of vector
    DataType norm = cVectorOperations<DataType>::euclidean_norm(
            A, num_rows, num_columns, i);

    // Normalize in place
    for (LongIndexType k=0; k < num_rows; ++k)
    {
        A[k*num_columns + i] /= norm;
    }

    return norm;
}


// ===============================
// Explicit template instantiation
// ===============================

template class cVectorOperations<float>;
template class cVectorOperations<double>;
template class cVectorOperations<long double>;
