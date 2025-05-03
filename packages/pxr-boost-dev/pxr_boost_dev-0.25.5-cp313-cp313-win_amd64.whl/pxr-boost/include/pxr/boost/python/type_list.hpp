// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_TYPE_LIST_HPP
#define PXR_BOOST_PYTHON_TYPE_LIST_HPP

#include "./detail/type_list.hpp"

namespace pxr { namespace boost { namespace python {

template <class ...T>
using type_list = detail::type_list<T...>;

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_TYPE_LIST_HPP
