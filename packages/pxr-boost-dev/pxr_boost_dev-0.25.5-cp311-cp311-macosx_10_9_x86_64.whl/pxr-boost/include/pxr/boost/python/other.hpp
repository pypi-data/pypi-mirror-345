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

#ifndef PXR_BOOST_PYTHON_OTHER_HPP
# define PXR_BOOST_PYTHON_OTHER_HPP

# include "./detail/prefix.hpp"

namespace pxr { namespace boost { namespace python {

template<class T> struct other
{ 
    typedef T type;
};

namespace detail
{
  template<typename T>
  class is_other
  {
   public:
      static constexpr bool value = false; 
  };

  template<typename T>
  class is_other<other<T> >
  {
   public:
      static constexpr bool value = true;
  };

  template<typename T>
  class unwrap_other
  {
   public:
      typedef T type;
  };

  template<typename T>
  class unwrap_other<other<T> >
  {
   public:
      typedef T type;
  };
}

}}} // namespace pxr::boost::python

#endif
