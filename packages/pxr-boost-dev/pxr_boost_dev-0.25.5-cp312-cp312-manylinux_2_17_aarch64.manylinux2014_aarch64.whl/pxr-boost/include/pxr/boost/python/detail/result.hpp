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

# ifndef PXR_BOOST_PYTHON_DETAIL_RESULT_HPP
#  define PXR_BOOST_PYTHON_DETAIL_RESULT_HPP

#  include "../type.hpp"

#  include "./preprocessor.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

// Defines a family of overloaded function which, given x, a function
// pointer, member [function] pointer, or an AdaptableFunction object,
// returns a pointer to type<R>*, where R is the result type of
// invoking the result of bind(x).
//
// In order to work around bugs in deficient compilers, if x might be
// an AdaptableFunction object, you must pass OL as a second argument
// to get this to work portably.

template <class R, class... A>
type<R>* result(R (*)(A...), int = 0)
{
    return 0;
}

#define PXR_BOOST_PYTHON_RESULT_MEMBER_FN(Q, ...)       \
template <class R, class T, class... A>                 \
type<R>* result(R (T::*)(A...) Q, int = 0)              \
{                                                       \
    return 0;                                           \
}

PXR_BOOST_PYTHON_APPLY_QUALIFIERS(PXR_BOOST_PYTHON_RESULT_MEMBER_FN)

#undef PXR_BOOST_PYTHON_RESULT_MEMBER_FN

template <class R, class T>
type<R>* result(R (T::*), int = 0) { return 0; }

template <class X>
type<typename X::result_type>*
result(X const&, short = 0) { return 0; }

}}}} // namespace pxr::boost::python::detail

# endif // PXR_BOOST_PYTHON_DETAIL_RESULT_HPP
