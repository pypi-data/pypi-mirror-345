// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_MPL2_FRONT_HPP
#define PXR_BOOST_PYTHON_DETAIL_MPL2_FRONT_HPP

#include "../../type_list.hpp"

namespace pxr { namespace boost { namespace python { namespace detail { namespace mpl2 {

template <typename Sequence>
struct front : front<typename Sequence::type>
{
};

template <typename T0, typename... T>
struct front<python::type_list<T0, T...>>
{
    using type = T0;
};

}}}}} // namespace pxr::boost::python::detail::mpl2

#endif
