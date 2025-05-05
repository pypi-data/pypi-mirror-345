/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _DEVICE_BENCHMARK_H_
#define _DEVICE_BENCHMARK_H_

// =======
// Headers
// =======

#include "../_definitions/types.h"  // IndexType


// =========
// Benchmark
// =========

template <typename DataType>
class Benchmark
{
    public:

        static long long matmul(
                const DataType* dummy_var,
                const IndexType n);

        static long long gramian(
                const DataType* dummy_var,
                const IndexType n);

        static long long cholesky(
                const DataType* dummy_var,
                const IndexType n);

        static long long lu(
                const DataType* dummy_var,
                const IndexType n);

        static long long plu(
                const DataType* dummy_var,
                const IndexType n);

    private:

        static void zeros(
                DataType* A,
                const LongIndexType n,
                const LongIndexType m);

        static void random(
                DataType* A,
                const LongIndexType n,
                const LongIndexType m);
};

#endif  // _DEVICE_BENCHMARK_H_
