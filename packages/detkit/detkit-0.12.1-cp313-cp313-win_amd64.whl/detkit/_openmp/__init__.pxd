# SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

from detkit._openmp.openmp cimport cond_omp_lock_t, cond_omp_init_lock, \
    cond_omp_set_lock, cond_omp_unset_lock, cond_omp_get_max_threads, \
    cond_omp_get_thread_num, cond_omp_set_num_threads, use_openmp

__all__ = ['cond_omp_lock_t', 'cond_omp_init_lock', 'cond_omp_set_lock',
           'cond_omp_unset_lock', 'cond_omp_get_max_threads',
           'cond_omp_get_thread_num', 'cond_omp_set_num_threads',
           'use_openmp']
