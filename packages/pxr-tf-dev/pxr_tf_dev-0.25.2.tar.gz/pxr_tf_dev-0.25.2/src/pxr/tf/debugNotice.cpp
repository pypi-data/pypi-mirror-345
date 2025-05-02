// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./debugNotice.h"
#include "./registryManager.h"
#include "./type.h"

namespace pxr {

TF_REGISTRY_FUNCTION(pxr::TfType)
{
    TfType::Define< TfDebugSymbolsChangedNotice,
        TfType::Bases<TfNotice> >();
    TfType::Define< TfDebugSymbolEnableChangedNotice,
        TfType::Bases<TfNotice> >();
}

TfDebugSymbolsChangedNotice::~TfDebugSymbolsChangedNotice() {}
TfDebugSymbolEnableChangedNotice::~TfDebugSymbolEnableChangedNotice() {}

}  // namespace pxr
