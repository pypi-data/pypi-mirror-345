// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2003.
// Copyright Stefan Seefeld 2016.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_VALUE_IS_SHARED_PTR_HPP
#define PXR_BOOST_PYTHON_DETAIL_VALUE_IS_SHARED_PTR_HPP

#include "./value_is_xxx.hpp"
#include "./is_shared_ptr.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

template <class X_>
struct value_is_shared_ptr
{
  static bool const value = is_shared_ptr<typename detail::remove_cv<
					    typename detail::remove_reference<X_>
					      ::type>
					    ::type>
    ::value;
  typedef mpl2::bool_<value> type;
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_VALUE_IS_SHARED_PTR_HPP
