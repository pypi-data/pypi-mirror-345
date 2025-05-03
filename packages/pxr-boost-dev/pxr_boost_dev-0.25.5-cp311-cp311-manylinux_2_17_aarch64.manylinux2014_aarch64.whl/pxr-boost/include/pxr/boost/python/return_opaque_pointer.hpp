// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright Gottfried Ganßauge 2003.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

/*
 * Generic Return value converter generator for opaque C++-pointers
 */
# ifndef PXR_BOOST_PYTHON_RETURN_OPAQUE_POINTER_HPP
# define PXR_BOOST_PYTHON_RETURN_OPAQUE_POINTER_HPP

# include "./detail/prefix.hpp"
# include "./opaque_pointer_converter.hpp"
# include "./detail/force_instantiate.hpp"
# include "./to_python_value.hpp"
# include "./detail/type_traits.hpp"
# include "./detail/value_arg.hpp"

namespace pxr { namespace boost { namespace python {

namespace detail
{
  template <class Pointee>
  static void opaque_pointee(Pointee const volatile*)
  {
      force_instantiate(opaque<Pointee>::instance);
  }
}

struct return_opaque_pointer
{
    template <class R>
    struct apply
    {
        static_assert( detail::is_pointer<R>::value, "RETURN_OPAQUE_POINTER_EXPECTS_A_POINTER_TYPE");
        
        struct type :  
          pxr::boost::python::to_python_value<
              typename detail::value_arg<R>::type
          >
        {
            type() { detail::opaque_pointee(R()); }
        };
    };
};

}}} // namespace pxr::boost::python
# endif // PXR_BOOST_PYTHON_RETURN_OPAQUE_POINTER_HPP
