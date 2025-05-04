// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_PY_MODULE_NOTICE_H
#define PXR_TF_PY_MODULE_NOTICE_H

#include "./api.h"
#include "./notice.h"

#include <string>

namespace pxr {

/// \class TfPyModuleWasLoaded
///
/// A \a TfNotice that is sent when a script module is loaded.  Since many
/// modules may be loaded at once, listeners are encouraged to defer work
/// triggered by this notice to the end of an application iteration.  This, of
/// course, is good practice in general.
///
class TfPyModuleWasLoaded : public TfNotice {
public:
    explicit TfPyModuleWasLoaded(std::string const &name) : _name(name) {}

    TF_API
    virtual ~TfPyModuleWasLoaded();
    
    /// Return the name of the module that was loaded.
    std::string const &GetName() { return _name; }

private:
    std::string _name;
};

}  // namespace pxr

#endif // PXR_TF_PY_MODULE_NOTICE_H
