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

#ifndef PXR_BOOST_PYTHON_COPY_CONST_REFERENCE_HPP
# define PXR_BOOST_PYTHON_COPY_CONST_REFERENCE_HPP

# include "./detail/prefix.hpp"
# include "./detail/indirect_traits.hpp"
# include "./detail/mpl2/if.hpp"
# include "./to_python_value.hpp"

namespace pxr { namespace boost { namespace python {

namespace detail
{
  template <class R>
  struct copy_const_reference_expects_a_const_reference_return_type
# if defined(__GNUC__) || defined(__EDG__)
  {}
# endif
  ;
}

template <class T> struct to_python_value;

struct copy_const_reference
{
    template <class T>
    struct apply
    {
        typedef typename detail::mpl2::if_c<
            indirect_traits::is_reference_to_const<T>::value
          , to_python_value<T>
          , detail::copy_const_reference_expects_a_const_reference_return_type<T>
        >::type type;
    };
};


}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_COPY_CONST_REFERENCE_HPP
