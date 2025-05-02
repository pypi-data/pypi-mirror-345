// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/arch/env.h>
#include "./setenv.h"
#include "./diagnostic.h"
#include <pxr/arch/errno.h>

#ifdef PXR_PYTHON_SUPPORT_ENABLED
#include "./pyUtils.h"
#endif // PXR_PYTHON_SUPPORT_ENABLED

namespace pxr {

bool
TfSetenv(const std::string & name, const std::string & value)
{
#ifdef PXR_PYTHON_SUPPORT_ENABLED
    if (TfPyIsInitialized()) {
        return TfPySetenv(name, value);
    }
#endif // PXR_PYTHON_SUPPORT_ENABLED

    if (ArchSetEnv(name.c_str(), value.c_str(), /* overwrite */ true)) {
        return true;
    }

    TF_WARN("Error setting '%s': %s", name.c_str(), ArchStrerror().c_str());
    return false;
}

bool
TfUnsetenv(const std::string & name)
{
#ifdef PXR_PYTHON_SUPPORT_ENABLED
    if (TfPyIsInitialized()) {
        return TfPyUnsetenv(name);
    }
#endif // PXR_PYTHON_SUPPORT_ENABLED

    if (ArchRemoveEnv(name.c_str())) {
        return true;
    }

    TF_WARN("Error unsetting '%s': %s", name.c_str(), ArchStrerror().c_str());
    return false;
}

}  // namespace pxr
