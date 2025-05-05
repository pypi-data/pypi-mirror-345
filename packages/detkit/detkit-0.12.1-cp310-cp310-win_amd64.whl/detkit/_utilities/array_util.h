/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


#ifndef _UTILITIES_ARRAY_H_
#define _UTILITIES_ARRAY_H_

// ==========
// Array Util
// ==========

/// \class A utility class for arrays.
///

template <typename DataType>
class ArrayUtil
{
    public:

    static void del(DataType* array);
};


#endif  // _UTILITIES_ARRAY_H_
