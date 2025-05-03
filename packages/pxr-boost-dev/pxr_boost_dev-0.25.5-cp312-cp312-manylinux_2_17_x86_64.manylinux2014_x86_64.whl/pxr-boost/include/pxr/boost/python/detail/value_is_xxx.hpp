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

#ifndef PXR_BOOST_PYTHON_DETAIL_VALUE_IS_XXX_HPP
# define PXR_BOOST_PYTHON_DETAIL_VALUE_IS_XXX_HPP

# include "./mpl2/bool.hpp"

# include "./type_traits.hpp"
#  include "./is_xxx.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

#  define PXR_BOOST_PYTHON_VALUE_IS_XXX_DEF(name, qualified_name, nargs) \
template <class X_>                                                     \
struct value_is_##name                                                  \
{                                                                       \
    PXR_BOOST_PYTHON_IS_XXX_DEF(name,qualified_name,nargs)              \
    static constexpr bool value = is_##name<                            \
                               typename remove_cv<                      \
                                  typename remove_reference<X_>::type   \
                               >::type                                  \
                           >::value;                                    \
    typedef mpl2::bool_<value> type;                                    \
                                                                        \
};                                                              

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_VALUE_IS_XXX_HPP
