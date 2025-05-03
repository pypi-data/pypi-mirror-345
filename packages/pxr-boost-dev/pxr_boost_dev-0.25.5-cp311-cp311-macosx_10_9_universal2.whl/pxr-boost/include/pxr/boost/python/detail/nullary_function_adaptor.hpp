// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2003.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_NULLARY_FUNCTION_ADAPTOR_HPP
# define PXR_BOOST_PYTHON_DETAIL_NULLARY_FUNCTION_ADAPTOR_HPP

# include "./prefix.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

// nullary_function_adaptor -- a class template which ignores its
// arguments and calls a nullary function instead.  Used for building
// error-reporting functions, c.f. pure_virtual
template <class NullaryFunction>
struct nullary_function_adaptor
{
    nullary_function_adaptor(NullaryFunction fn)
      : m_fn(fn)
    {}

    template <class... A>
    void operator()(A const&...) const { m_fn(); }
    
 private:
    NullaryFunction m_fn;
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_NULLARY_FUNCTION_ADAPTOR_HPP
