// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./hash.h"
#include "./enum.h"
#include "./stringUtils.h"
#include "./token.h"
#include "./type.h"
#include <pxr/arch/hash.h>

#include <cstring>

namespace pxr {

void
Tf_HashState::_AppendBytes(char const *bytes, size_t numBytes)
{
    _state = ArchHash64(bytes, numBytes, _state);
    _didOne = true;
}

size_t
TfHashCharPtr::operator()(const char* ptr) const
{
    return TfHash()(static_cast<const void*>(ptr));
}

size_t
TfHashCString::operator()(const char* ptr) const
{
    return ptr ? ArchHash(ptr, std::strlen(ptr)) : 0;
}

bool
TfEqualCString::operator()(const char* lhs, const char* rhs) const
{
    return std::strcmp(lhs, rhs) == 0;
}

}  // namespace pxr
