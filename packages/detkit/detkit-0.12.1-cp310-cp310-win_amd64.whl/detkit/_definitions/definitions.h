/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _DEFINITIONS_DEFINITIONS_H_
#define _DEFINITIONS_DEFINITIONS_H_


// ===========
// Definitions
// ===========

// To suppress warning: __STDC_VERSION__" is not defined, evaluates to 0
// #ifndef __STDC_VERSION__
//     #define __STDC_VERSION__ 0
// #endif

// If set to 0, the LongIndexType is declared as 32-bit integer. Whereas if set
// to 1, the LongIndexType is declared as 64-bit integer. The long integer will
// slow down the performance on reading array if integers. Note that in C++,
// there is no difference between "int" and "long int". That is, both are 32
// bit. To see the real effect of long type, define the integer by "long long"
// rather than "long int". The "long long" is indeed 64-bit. Currently, the
// long type in "./types.h" is defined as "long int". Hence, setting LONG_INT
// to 1 will not make any difference unless "long long" is used.
//
// Note: The malloc and cudaMalloc can only allocate at maximum, an array of
// the limit size of "size_t" (unsigned int). So, using "long long int" is
// not indeed practical for malloc. Thus, it is better to set the type of array
// indices as just "signed int".
#ifndef LONG_INT
    #define LONG_INT 0
#endif

// If set to 0, the LongIndexType is declared as signed integer, whereas if set
// to 1, the LongIndexType is declared as unsigned integer. The unsigned type
// will double the limit of the largest integer index, while keeps the same
// speed for index operations. Note that the indices and index pointers of
// scipy sparse arrays are defined by "signed int". Hence, by setting
// UNSIGNED_LONG_INT to 1, there is a one-time overhead of convening the numpy
// int arrays (two matrices of scipy.sparse.csr_matrix.indices and
// scipy.sparse.csr_matrix.indptr) from "int" to "unsigned int". This overhead
// is only one-time and should be around half a second for moderate to large
// arrays. But, on the positive side, the unsigned int can handle arrays of
// up to twice the index size.
//
// Note: The malloc and cudaMalloc can only allocate at maximum, an array of
// the limit size of "size_t" (unsigned int). So, using "unsigned int" for
// index is not indeed practical since the array size in bytes is the size of
// array times sizeof(DataType). That is, if DataType is double for instance,
// the maximum array size could potentially be 8 times the size of maximum
// of "size_t" (unsigned int) which is not possible for malloc. Thus, it is
// better to set the type of array indices as just "signed int".
#ifndef UNSIGNED_LONG_INT
    #define UNSIGNED_LONG_INT 0
#endif

// If USE_LOOP_UNROLLING is set to 1, the for loops in dense matrix-vector
// multiplications and vector-vector multiplications use loop unrolling.
// Otherwise set to 0. Default is 1.
#ifndef USE_LOOP_UNROLLING
    #define USE_LOOP_UNROLLING 1
#endif

// If set to 1, the InstructionCounter class will count the hardware
// instructions used to compute a task. This functionality is only available on
// Linux and requires perf_tool to be installed.
#ifndef COUNT_PERF
    #define COUNT_PERF 1
#endif

// If USE_OPENMP is set to 1, the OpenMP for shared-memory parallelization will
// be enabled. Otherwise, set this to 0. You can also set this as an
// environment variable, or in setup.py script.
#ifndef USE_OPENMP
    #define USE_OPENMP 0
#endif

// If enabled, to compute Gramian matrices as transpose of matrix multiplied
// by itself, only half of the matrix multiplication is computed and the other
// half is obtained by Gramian matrix symmetry.
#ifndef USE_SYMMETRY
    #define USE_SYMMETRY 1
#endif

#endif  // _DEFINITIONS_DEFINITIONS_H_
