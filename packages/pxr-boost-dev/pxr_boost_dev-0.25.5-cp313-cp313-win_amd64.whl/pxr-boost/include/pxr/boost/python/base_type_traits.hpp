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

#ifndef PXR_BOOST_PYTHON_BASE_TYPE_TRAITS_HPP
# define PXR_BOOST_PYTHON_BASE_TYPE_TRAITS_HPP

# include "./detail/prefix.hpp"

namespace pxr { namespace boost { namespace python {

namespace detail
{
  struct unspecialized {};
}

// Derive from unspecialized so we can detect whether traits are
// specialized
template <class T> struct base_type_traits
  : detail::unspecialized
{};

template <>
struct base_type_traits<PyObject>
{
    typedef PyObject type;
};

template <>
struct base_type_traits<PyTypeObject>
{
    typedef PyObject type;
};

template <>
struct base_type_traits<PyMethodObject>
{
    typedef PyObject type;
};

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_BASE_TYPE_TRAITS_HPP
