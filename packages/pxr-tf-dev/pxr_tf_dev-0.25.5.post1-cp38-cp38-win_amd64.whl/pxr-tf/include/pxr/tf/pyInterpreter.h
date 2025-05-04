// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_PY_INTERPRETER_H
#define PXR_TF_PY_INTERPRETER_H

/// \file tf/pyInterpreter.h
/// Python runtime utilities.

#include "./api.h"
#include <pxr/boost/python/handle.hpp>
#include <pxr/boost/python/object.hpp>
#include <string>

namespace pxr {

/// Starts up the python runtime.
/// IMPORTANT: The GIL will NOT be held when this returns.
/// (If Python is already initialized, the GIL will be unchanged)
///
/// The program name and arguments are set automatically. sys.argv has no
/// arguments other than an argv[0] matching the program name.
TF_API
extern void TfPyInitialize();

/// Runs the given string using PyRun_SimpleString().
///
/// Starts the interpreter if necessary. Deals with necessary thread state
/// setup.
///
/// Callers are not required to hold the GIL, though of course they may.
///
/// Returns zero on success, nonzero on failure.
TF_API
extern int TfPyRunSimpleString(const std::string & cmd);

/// Runs the given string using PyRun_String().
///
/// \a start is Py_eval_input, Py_single_input or Py_file_input.
/// \a globals and locals can be dictionaries to use when evaluating the 
///    string in python. Defaults to reusing globals from main module. If
///    only the globals are provided, they will also be used as locals.
///
/// Starts the interpreter if necessary. Deals with necessary thread state
/// setup.
///
/// Callers must hold the GIL before calling; see TfPyLock.  This is true for
/// any pxr::boost::python call, including constructing and destroying the default
/// values of \p globals and \p locals.  Holding the GIL will also make it safe
/// to inspect the returned pxr::boost::python::handle.
TF_API
extern pxr::boost::python::handle<>
TfPyRunString(const std::string & cmd, int start,
              pxr::boost::python::object const &globals = pxr::boost::python::object(),
              pxr::boost::python::object const &locals = pxr::boost::python::object()
              );

/// Runs the given file using PyRun_File().
///
/// \a start is Py_eval_input, Py_single_input or Py_file_input.
/// \a globals and locals can be dictionaries to use when evaluating the 
///    string in python. Defaults to reusing globals from main module. If
///    only the globals are provided, they will also be used as locals.
///
/// Starts the interpreter if necessary. Deals with necessary thread state
/// setup.
///
/// Callers must hold the GIL before calling; see TfPyLock.  This is true for
/// any pxr::boost::python call, including constructing and destroying the default
/// values of \p globals and \p locals.  Holding the GIL will also make it safe
/// to inspect the returned pxr::boost::python::handle.
TF_API
extern pxr::boost::python::handle<>
TfPyRunFile(const std::string &filename, int start,
            pxr::boost::python::object const &globals = pxr::boost::python::object(),
            pxr::boost::python::object const &locals = pxr::boost::python::object()
            );

}  // namespace pxr

#endif // PXR_TF_PY_INTERPRETER_H
