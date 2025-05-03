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

#ifndef PXR_BOOST_PYTHON_MANAGE_NEW_OBJECT_HPP
# define PXR_BOOST_PYTHON_MANAGE_NEW_OBJECT_HPP

# include "./detail/prefix.hpp"
# include "./detail/indirect_traits.hpp"
# include "./detail/type_traits.hpp"
# include "./detail/mpl2/if.hpp"
# include "./to_python_indirect.hpp"

namespace pxr { namespace boost { namespace python {

namespace detail
{
  template <class R>
  struct manage_new_object_requires_a_pointer_return_type
# if defined(__GNUC__) || defined(__EDG__)
  {}
# endif
  ;
}

struct manage_new_object
{
    template <class T>
    struct apply
    {
        typedef typename python::detail::mpl2::if_c<
            detail::is_pointer<T>::value
            , to_python_indirect<T, detail::make_owning_holder>
            , detail::manage_new_object_requires_a_pointer_return_type<T>
        >::type type;
    };
};

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_MANAGE_NEW_OBJECT_HPP
