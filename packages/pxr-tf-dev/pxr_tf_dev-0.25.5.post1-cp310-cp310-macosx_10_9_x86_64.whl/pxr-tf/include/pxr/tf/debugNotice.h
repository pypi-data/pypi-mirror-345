// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_DEBUG_NOTICE_H
#define PXR_TF_DEBUG_NOTICE_H

/// \file tf/debugNotice.h

#include "./notice.h"

namespace pxr {

/// \class TfDebugSymbolsChangedNotice
///
/// Sent when the list of available debug symbol names has changed.
class TfDebugSymbolsChangedNotice : public TfNotice
{
public:
    TfDebugSymbolsChangedNotice() {}
    virtual ~TfDebugSymbolsChangedNotice();
};

/// \class TfDebugSymbolEnableChangedNotice
///
/// Sent when a debug symbol has been enabled or disabled.
class TfDebugSymbolEnableChangedNotice : public TfNotice
{
public:
    TfDebugSymbolEnableChangedNotice() {}
    virtual ~TfDebugSymbolEnableChangedNotice();
};

}  // namespace pxr

#endif
