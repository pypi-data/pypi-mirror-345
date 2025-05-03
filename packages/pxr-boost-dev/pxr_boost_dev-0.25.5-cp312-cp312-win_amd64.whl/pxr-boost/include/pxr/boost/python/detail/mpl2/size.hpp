// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_MPL2_SIZE_HPP
#define PXR_BOOST_PYTHON_DETAIL_MPL2_SIZE_HPP

#include "../../type_list.hpp"

namespace pxr { namespace boost { namespace python { namespace detail { namespace mpl2 {

template <typename Sequence>
struct size : size<typename Sequence::type>
{
};

template <typename... T>
struct size<python::type_list<T...>>
{
    static constexpr size_t value = sizeof...(T);
};

}}}}} // namespace pxr::boost::python::detail::mpl2

#endif
