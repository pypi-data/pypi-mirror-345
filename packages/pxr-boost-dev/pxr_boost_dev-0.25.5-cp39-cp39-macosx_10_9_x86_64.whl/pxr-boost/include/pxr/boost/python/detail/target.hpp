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

# ifndef PXR_BOOST_PYTHON_DETAIL_TARGET_HPP
#  define PXR_BOOST_PYTHON_DETAIL_TARGET_HPP

#  include "./preprocessor.hpp"

#  include "../type.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

template <class R>
void(* target(R (*)()) )()
{
    return 0;
}

template <class R, class A0, class... A>
A0(* target(R (*)(A0, A...)) )()
{
    return 0;
}

#define PXR_BOOST_PYTHON_TARGET_MEMBER_FN(Q, ...)              \
template <class R, class T, class... A>                        \
T& (* target(R (T::*)(A...) Q) )()                             \
{                                                              \
    return 0;                                                  \
}

PXR_BOOST_PYTHON_APPLY_QUALIFIERS(PXR_BOOST_PYTHON_TARGET_MEMBER_FN)

#undef PXR_BOOST_PYTHON_TARGET_MEMBER_FN

template <class R, class T>
T& (* target(R (T::*)) )() { return 0; }

}}}} // namespace pxr::boost::python::detail

# endif // PXR_BOOST_PYTHON_DETAIL_TARGET_HPP
