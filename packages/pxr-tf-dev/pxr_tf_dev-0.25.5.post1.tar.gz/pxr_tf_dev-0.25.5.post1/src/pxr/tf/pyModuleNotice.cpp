// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./pyModuleNotice.h"

namespace pxr {

TF_REGISTRY_FUNCTION(pxr::TfType) {
    TfType::Define<TfPyModuleWasLoaded, TfType::Bases<TfNotice> >();
}

TfPyModuleWasLoaded::~TfPyModuleWasLoaded() {
}

}  // namespace pxr
