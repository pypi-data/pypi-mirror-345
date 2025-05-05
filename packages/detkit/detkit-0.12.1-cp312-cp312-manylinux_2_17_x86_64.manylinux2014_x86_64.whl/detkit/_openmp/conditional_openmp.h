/*
 *  SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef CONDITIONAL_OPENMP_H_
#define CONDITIONAL_OPENMP_H_

// =======
// Headers
// =======

// Check OPENMP exists
#if defined(_OPENMP) || (defined(__INTEL_COMPILER) && defined(__OPENMP)) \
    || (defined(__NVCOMPILER) && defined(_OPENMP))
    #define _HAS_OPENMP 1
#else
    #define _HAS_OPENMP 0
#endif

// Check user wants OPENMP
#if (_HAS_OPENMP == 1) && defined(USE_OPENMP) && (USE_OPENMP == 1)
    #include <omp.h>
    #define use_openmp 1
#else
    #define use_openmp 0
#endif

// Dummy type declarations
#if use_openmp == 1
    typedef omp_lock_t cond_omp_lock_t;
#else
    typedef int cond_omp_lock_t;
#endif

// Dummy function declarations
void cond_omp_init_lock(cond_omp_lock_t *lock);
void cond_omp_set_lock(cond_omp_lock_t *lock);
void cond_omp_unset_lock(cond_omp_lock_t *lock);
int cond_omp_get_max_threads();
int cond_omp_get_thread_num();
void cond_omp_set_num_threads(int num_threads);


#endif  // CONDITIONAL_OPENMP_H_
