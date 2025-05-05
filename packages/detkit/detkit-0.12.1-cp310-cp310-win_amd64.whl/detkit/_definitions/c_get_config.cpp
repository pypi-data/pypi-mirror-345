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

#include "./c_get_config.h"


// ===============
// is use symmetry 
// ===============

/// \brief Returns USE_SYMMETRY.
///

bool is_use_symmetry()
{
    #if defined(USE_SYMMETRY) && (USE_SYMMETRY == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =============
// is use openmp
// =============

/// \brief Returns USE_OPENMP.
///

bool is_use_openmp()
{
    #if defined(USE_OPENMP) && (USE_OPENMP == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =============
// is count perf
// =============

/// \brief Returns COUNT_PERF.
///

bool is_count_perf()
{
    #if defined(COUNT_PERF) && (COUNT_PERF == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =====================
// is use loop unrolling
// =====================

/// \brief Returns USE_LOOP_UNROLLING.
///

bool is_use_loop_unrolling()
{
    #if defined(USE_LOOP_UNROLLING) && (USE_LOOP_UNROLLING == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =============
// is debug mode
// =============

/// \brief Returns DEBUG_MODE.
///

bool is_debug_mode()
{
    #if defined(DEBUG_MODE) && (DEBUG_MODE == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =========================
// is cython build in source
// =========================

/// \brief Returns CYTHON_BUILD_IN_SOURCE.
///

bool is_cython_build_in_source()
{
    #if defined(CYTHON_BUILD_IN_SOURCE) && (CYTHON_BUILD_IN_SOURCE == 1)
        return 1;
    #else
        return 0;
    #endif
}


// =======================
// is cython build for doc
// =======================

/// \brief Returns CYTHON_BUILD_FOR_DOC.
///

bool is_cython_build_for_doc()
{
    #if defined(CYTHON_BUILD_FOR_DOC) && (CYTHON_BUILD_FOR_DOC == 1)
        return 1;
    #else
        return 0;
    #endif
}


// ===============
// is use long int
// ===============

/// \brief Returns USE_LONG_INT.
///

bool is_use_long_int()
{
    #if defined(USE_LONG_INT) && (USE_LONG_INT == 1)
        return 1;
    #else
        return 0;
    #endif
}


// ========================
// is use unsigned long int
// ========================

/// \brief Returns USE_UNSIGNED_LONG_INT.
///

bool is_use_unsigned_long_int()
{
    #if defined(USE_UNSIGNED_LONG_INT) && (USE_UNSIGNED_LONG_INT == 1)
        return 1;
    #else
        return 0;
    #endif
}
