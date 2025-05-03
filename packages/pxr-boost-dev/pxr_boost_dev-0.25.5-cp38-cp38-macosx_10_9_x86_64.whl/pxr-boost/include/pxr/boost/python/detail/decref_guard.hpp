// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2002.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_DECREF_GUARD_HPP
# define PXR_BOOST_PYTHON_DETAIL_DECREF_GUARD_HPP

namespace pxr { namespace boost { namespace python { namespace detail {

struct decref_guard
{
    decref_guard(PyObject* o) : obj(o) {}
    ~decref_guard() { Py_XDECREF(obj); }
    void cancel() { obj = 0; }
 private:
    PyObject* obj;
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_DECREF_GUARD_HPP
