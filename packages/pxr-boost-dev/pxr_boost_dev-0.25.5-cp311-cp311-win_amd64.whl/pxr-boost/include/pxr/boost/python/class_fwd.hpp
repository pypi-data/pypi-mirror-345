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

#ifndef PXR_BOOST_PYTHON_CLASS_FWD_HPP
# define PXR_BOOST_PYTHON_CLASS_FWD_HPP

# include "./detail/prefix.hpp"
# include "./detail/not_specified.hpp"

namespace pxr { namespace boost { namespace python {

template <
    class T // class being wrapped
    // arbitrarily-ordered optional arguments. Full qualification needed for MSVC6
    , class X1 = ::pxr::boost::python::detail::not_specified
    , class X2 = ::pxr::boost::python::detail::not_specified
    , class X3 = ::pxr::boost::python::detail::not_specified
    >
class class_;

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_CLASS_FWD_HPP
