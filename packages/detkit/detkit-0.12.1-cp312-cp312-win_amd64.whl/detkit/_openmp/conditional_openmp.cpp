/*
 *  SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
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

#include "./conditional_openmp.h"  // use_openmp


// ==================
// cond omp init lock
// ==================

void cond_omp_init_lock(cond_omp_lock_t *lock)
{
    #if use_openmp == 1
        omp_init_lock(lock);
    #else
        // Nullify this OPENMP functions
        (void) lock;
    #endif
}

// =================
// cond omp set lock
// =================

void cond_omp_set_lock(cond_omp_lock_t *lock)
{
    #if use_openmp == 1
        omp_set_lock(lock);
    #else
        // Nullify this OPENMP functions
        (void) lock;
    #endif
}

// ===================
// cond omp unset lock
// ===================

void cond_omp_unset_lock(cond_omp_lock_t *lock)
{
    #if use_openmp == 1
        omp_unset_lock(lock);
    #else
        // Nullify this OPENMP functions
        (void) lock;
    #endif
}

// ========================
// cond omp get max threads
// ========================

int cond_omp_get_max_threads()
{
    #if use_openmp == 1
        return omp_get_max_threads();
    #else
        // Nullify this OPENMP functions
        return 1;
    #endif
}

// =======================
// cond omp get thread num
// =======================

int cond_omp_get_thread_num()
{
    #if use_openmp == 1
        return omp_get_thread_num();
    #else
        // Nullify this OPENMP functions
        return 0;
    #endif
}

// ========================
// cond omp set num threads
// ========================

void cond_omp_set_num_threads(int num_threads)
{
    #if use_openmp == 1
        omp_set_num_threads(num_threads);
    #else
        // Nullify this OPENMP functions
        (void) num_threads;
    #endif
}
