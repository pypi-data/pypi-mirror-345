// Copyright 2021 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./pyInvoke.h"

#include "./diagnostic.h"
#include "./errorMark.h"
#include "./pyInterpreter.h"
#include "./stringUtils.h"

#include <pxr/boost/python.hpp>

#include <vector>

namespace pxr {

// Convert nullptr to None.
pxr::boost::python::object Tf_ArgToPy(const std::nullptr_t &value)
{
    return pxr::boost::python::object();
}

void Tf_BuildPyInvokeKwArgs(
    pxr::boost::python::dict *kwArgsOut)
{
    // Variadic template recursion base case: all args already processed, do
    // nothing.
}

void Tf_BuildPyInvokeArgs(
    pxr::boost::python::list *posArgsOut,
    pxr::boost::python::dict *kwArgsOut)
{
    // Variadic template recursion base case: all args already processed, do
    // nothing.
}

bool Tf_PyInvokeImpl(
    const std::string &moduleName,
    const std::string &callableExpr,
    const pxr::boost::python::list &posArgs,
    const pxr::boost::python::dict &kwArgs,
    pxr::boost::python::object *resultObjOut)
{
    static const char* const listVarName = "_Tf_invokeList_";
    static const char* const dictVarName = "_Tf_invokeDict_";
    static const char* const resultVarName = "_Tf_invokeResult_";

    // Build globals dict, containing builtins and args.
    // No need for TfScriptModuleLoader; our python code performs import.
    pxr::boost::python::dict globals;
    pxr::boost::python::handle<> modHandle(
        PyImport_ImportModule("builtins"));
    globals["__builtins__"] = pxr::boost::python::object(modHandle);
    globals[listVarName] = posArgs;
    globals[dictVarName] = kwArgs;

    // Build python code for interpreter.
    // Import, look up callable, perform call, store result.
    const std::string pyStr = TfStringPrintf(
        "import %s\n"
        "%s = %s.%s(*%s, **%s)\n",
        moduleName.c_str(),
        resultVarName,
        moduleName.c_str(),
        callableExpr.c_str(),
        listVarName,
        dictVarName);

    TfErrorMark errorMark;

    // Execute code.
    TfPyRunString(pyStr, Py_file_input, globals);

    // Bail if python code raised any TfErrors.
    if (!errorMark.IsClean())
        return false;

    // Look up result.  If we got this far, it should be there.
    if (!TF_VERIFY(globals.has_key(resultVarName)))
        return false;
    *resultObjOut = globals.get(resultVarName);

    return true;
}

}  // namespace pxr
