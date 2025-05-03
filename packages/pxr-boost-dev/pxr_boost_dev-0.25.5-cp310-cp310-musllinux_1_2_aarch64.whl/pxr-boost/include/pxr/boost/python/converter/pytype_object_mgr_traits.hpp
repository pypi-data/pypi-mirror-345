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

#ifndef PXR_BOOST_PYTHON_CONVERTER_PYTYPE_OBJECT_MGR_TRAITS_HPP
# define PXR_BOOST_PYTHON_CONVERTER_PYTYPE_OBJECT_MGR_TRAITS_HPP

# include "../detail/prefix.hpp"
# include "../detail/raw_pyobject.hpp"
# include "../cast.hpp"
# include "./pyobject_type.hpp"
# include "../errors.hpp"

namespace pxr { namespace boost { namespace python { namespace converter {

// Provide a forward declaration as a convenience for clients, who all
// need it.
template <class T> struct object_manager_traits;

// Derive specializations of object_manager_traits from this class
// when T is an object manager for a particular Python type hierarchy.
//
template <PyTypeObject* pytype, class T>
struct pytype_object_manager_traits
    : pyobject_type<T, pytype> // provides check()
{
    static constexpr bool is_specialized = true;
    static inline python::detail::new_reference adopt(PyObject*);
};

//
// implementations
//
template <PyTypeObject* pytype, class T>
inline python::detail::new_reference pytype_object_manager_traits<pytype,T>::adopt(PyObject* x)
{
    return python::detail::new_reference(python::pytype_check(pytype, x));
}

}}}} // namespace pxr::boost::python::converter

#endif // PXR_BOOST_PYTHON_CONVERTER_PYTYPE_OBJECT_MGR_TRAITS_HPP
