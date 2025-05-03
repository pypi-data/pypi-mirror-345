// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_MPL2_IF_HPP
#define PXR_BOOST_PYTHON_DETAIL_MPL2_IF_HPP

#include <type_traits>

namespace pxr { namespace boost { namespace python { namespace detail { namespace mpl2 {

template <typename C, typename T1, typename T2>
using if_ = std::conditional<C::value, T1, T2>;

template <bool c, typename T1, typename T2>
using if_c = std::conditional<c, T1, T2>;

}}}}} // namespace pxr::boost::python::detail::mpl2

#endif
