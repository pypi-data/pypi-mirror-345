// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./pySingleton.h"

#include <string>

using std::string;

namespace pxr {

namespace Tf_PySingleton {

bp::object _DummyInit(bp::tuple const & /* args */,
                      bp::dict const & /* kw */) {
    return bp::object();
}
    
string _Repr(bp::object const &self, string const &prefix) {
    string name(bp::extract<string>(self.attr("__class__").attr("__name__")));
    return prefix + name + "()";
}

}

Tf_PySingleton::Visitor TfPySingleton() {
    return Tf_PySingleton::Visitor();
}

}  // namespace pxr
