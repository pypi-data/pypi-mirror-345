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

#include "./array_util.h"
#include <cstddef>  // NULL


// ===
// del
// ===

/// \brief Deletes 1D arrays
///

template <typename DataType>
void ArrayUtil<DataType>::del(DataType* array)
{
    if (array != NULL)
    {
        delete[] array;
        array = NULL;
    }
}


// ===============================
// Explicit template instantiation
// ===============================

template class ArrayUtil<int>;
template class ArrayUtil<long int>;
template class ArrayUtil<float>;
template class ArrayUtil<double>;
template class ArrayUtil<long double>;
