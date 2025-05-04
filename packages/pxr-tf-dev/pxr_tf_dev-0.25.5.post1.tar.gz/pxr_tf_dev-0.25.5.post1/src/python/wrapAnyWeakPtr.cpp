// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/anyWeakPtr.h>
#include <pxr/tf/pyUtils.h>
#include <pxr/tf/pyContainerConversions.h>

#include <pxr/boost/python/to_python_converter.hpp>

using namespace pxr;

using namespace pxr::boost::python;

namespace pxr {

// Put this in the pxr namespace so that we can declare it a friend in
// anyWeakPtr.h

object Tf_GetPythonObjectFromAnyWeakPtr(TfAnyWeakPtr const &self) {
    return self._GetPythonObject();
}

}  // namespace pxr

namespace {

struct Tf_AnyWeakPtrToPython {

    Tf_AnyWeakPtrToPython() {
        to_python_converter<TfAnyWeakPtr, Tf_AnyWeakPtrToPython>();
    }

    static PyObject *convert(TfAnyWeakPtr const &any) {
        return incref(Tf_GetPythonObjectFromAnyWeakPtr(any).ptr());
    }
};

} // anonymous namespace

void wrapAnyWeakPtr()
{
    to_python_converter<TfAnyWeakPtr, Tf_AnyWeakPtrToPython>();

    TfPyContainerConversions::from_python_sequence<
        std::set<TfAnyWeakPtr>,
        TfPyContainerConversions::set_policy>();
}
