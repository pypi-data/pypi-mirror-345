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

#ifndef PXR_BOOST_PYTHON_DETAIL_COPY_CTOR_MUTATES_RHS_HPP
# define PXR_BOOST_PYTHON_DETAIL_COPY_CTOR_MUTATES_RHS_HPP

#include "./is_auto_ptr.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

template <class T>
struct copy_ctor_mutates_rhs
    : is_auto_ptr<T>
{
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_COPY_CTOR_MUTATES_RHS_HPP
