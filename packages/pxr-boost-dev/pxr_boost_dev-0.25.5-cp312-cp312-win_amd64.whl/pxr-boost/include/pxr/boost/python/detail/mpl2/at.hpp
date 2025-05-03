// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_MPL2_AT_HPP
#define PXR_BOOST_PYTHON_DETAIL_MPL2_AT_HPP

#include "../../type_list.hpp"
#include <tuple>

namespace pxr { namespace boost { namespace python { namespace detail { namespace mpl2 {

template <typename Sequence, long n>
struct at_c : at_c<typename Sequence::type, n>
{
};

template <typename... T, long n>
struct at_c<python::type_list<T...>, n>
{
    // Cheat a little by using std::tuple and std::tuple_element to avoid
    // writing a custom implementation. Some compilers also have built-in
    // support for std::tuple_element to avoid recursive template
    // instantiations.
    using tuple_type = std::tuple<T...>;
    using type = typename std::tuple_element<n, tuple_type>::type;
};

template <typename Sequence, typename N>
using at = at_c<Sequence, N::value>;

}}}}} // namespace pxr::boost::python::detail::mpl2

#endif
