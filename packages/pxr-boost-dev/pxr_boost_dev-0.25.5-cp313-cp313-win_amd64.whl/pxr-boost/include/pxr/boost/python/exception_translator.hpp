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

#ifndef PXR_BOOST_PYTHON_EXCEPTION_TRANSLATOR_HPP
# define PXR_BOOST_PYTHON_EXCEPTION_TRANSLATOR_HPP

# include "./detail/prefix.hpp"

# include "./type.hpp"
# include "./detail/translate_exception.hpp"
# include "./detail/exception_handler.hpp"

namespace pxr { namespace boost { namespace python {

template <class ExceptionType, class Translate>
void register_exception_translator(Translate translate, type<ExceptionType>* = 0)
{
    // XXX:
    // Avoid ambiguity between std::placeholders and boost.
    // Can be replaced with "using namespace std::placeholders" once
    // boost dependency has been removed.
    using std::placeholders::_1;
    using std::placeholders::_2;
    detail::register_exception_handler(
        std::bind<bool>(detail::translate_exception<ExceptionType,Translate>(), _1, _2, translate)
        );
}

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_EXCEPTION_TRANSLATOR_HPP
