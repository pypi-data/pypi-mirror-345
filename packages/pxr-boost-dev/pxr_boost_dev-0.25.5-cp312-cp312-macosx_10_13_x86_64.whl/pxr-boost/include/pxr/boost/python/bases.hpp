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

#ifndef PXR_BOOST_PYTHON_BASES_HPP
# define PXR_BOOST_PYTHON_BASES_HPP

# include "./detail/prefix.hpp"
# include "./detail/type_list.hpp"
# include "./detail/type_traits.hpp"
# include "./detail/mpl2/if.hpp"
# include "./detail/mpl2/bool.hpp"

namespace pxr { namespace boost { namespace python {

  // A type list for specifying bases
  template <typename... Base>
  struct bases : detail::type_list<Base...>::type
  {};

  namespace detail
  {
    template <class T> struct specifies_bases
        : detail::mpl2::false_
    {
    };
    
    template <class... Base>
    struct specifies_bases< bases< Base... > >
        : detail::mpl2::true_
    {
    };
    template <class T, class Prev = bases<> >
    struct select_bases
        : detail::mpl2::if_<
                specifies_bases<T>
                , T
                , Prev
          >
    {
    };
  }
}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_BASES_HPP
