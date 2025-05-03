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

#ifndef PXR_BOOST_PYTHON_DETAIL_TRANSLATE_EXCEPTION_HPP
# define PXR_BOOST_PYTHON_DETAIL_TRANSLATE_EXCEPTION_HPP

# include "./exception_handler.hpp"
# include "./type_traits.hpp"

#include <functional>

namespace pxr { namespace boost { namespace python { namespace detail {

// A ternary function object used to translate C++ exceptions of type
// ExceptionType into Python exceptions by invoking an object of type
// Translate. Typically the translate function will be curried with
// boost::bind().
template <class ExceptionType, class Translate>
struct translate_exception
{
    typedef typename add_lvalue_reference<
        typename add_const<ExceptionType>::type
    >::type exception_cref;
    
    inline bool operator()(
        exception_handler const& handler
      , std::function<void()> const& f
      , typename param_type<Translate>::type translate) const
    {
        try
        {
            return handler(f);
        }
        catch(exception_cref e)
        {
            translate(e);
            return true;
        }
    }
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_TRANSLATE_EXCEPTION_HPP
