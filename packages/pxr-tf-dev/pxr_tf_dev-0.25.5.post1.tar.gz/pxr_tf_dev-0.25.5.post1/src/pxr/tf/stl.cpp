// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./stl.h"

namespace pxr {

size_t
Tf_GetEmptyHashMapBucketCount()
{
    static const TfHashMap<int, int> empty(0);
    return empty.bucket_count();
}

size_t
Tf_GetEmptyHashSetBucketCount()
{
    static const TfHashSet<int> empty(0);
    return empty.bucket_count();
}

}  // namespace pxr
