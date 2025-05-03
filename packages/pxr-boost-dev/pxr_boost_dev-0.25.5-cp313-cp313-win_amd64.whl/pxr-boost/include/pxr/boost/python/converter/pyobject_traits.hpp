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

#ifndef PXR_BOOST_PYTHON_CONVERTER_PYOBJECT_TRAITS_HPP
# define PXR_BOOST_PYTHON_CONVERTER_PYOBJECT_TRAITS_HPP

# include "../detail/prefix.hpp"
# include "./pyobject_type.hpp"

namespace pxr { namespace boost { namespace python { namespace converter {

template <class> struct pyobject_traits;

template <>
struct pyobject_traits<PyObject>
{
    // All objects are convertible to PyObject
    static bool check(PyObject*) { return true; }
    static PyObject* checked_downcast(PyObject* x) { return x; }
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
    static PyTypeObject const* get_pytype() { return 0; }
#endif
};

//
// Specializations
//

# define PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(T)                  \
    template <> struct pyobject_traits<Py##T##Object>           \
        : pyobject_type<Py##T##Object, &Py##T##_Type> {}

// This is not an exhaustive list; should be expanded.
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(Type);
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(List);
#if PY_VERSION_HEX < 0x03000000
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(Int);
#endif
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(Long);
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(Dict);
PXR_BOOST_PYTHON_BUILTIN_OBJECT_TRAITS(Tuple);

}}}} // namespace pxr::boost::python::converter

#endif // PXR_BOOST_PYTHON_CONVERTER_PYOBJECT_TRAITS_HPP
