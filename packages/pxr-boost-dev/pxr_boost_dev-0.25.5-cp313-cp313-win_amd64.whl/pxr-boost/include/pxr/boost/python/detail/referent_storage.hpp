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

#ifndef PXR_BOOST_PYTHON_DETAIL_REFERENT_STORAGE_HPP
# define PXR_BOOST_PYTHON_DETAIL_REFERENT_STORAGE_HPP

# include "./type_traits.hpp"
# include "./mpl2/if.hpp"
# include <cstddef>

namespace pxr { namespace boost { namespace python { namespace detail {

// This is equivalent to std::aligned_storage from C++11, but that's
// deprecated in C++23 so we just roll our own here.
template <std::size_t size, std::size_t alignment>
struct aligned_storage
{
  union type
  {
    alignas(alignment) char bytes[size];
  };
};
      
  // Compute the size of T's referent. We wouldn't need this at all,
  // but sizeof() is broken in CodeWarriors <= 8.0
  template <class T> struct referent_size;
  
  
  template <class T>
  struct referent_size<T&>
  {
      static constexpr 
          std::size_t value = sizeof(T);
  };

// A metafunction returning a POD type which can store U, where T ==
// U&. If T is not a reference type, returns a POD which can store T.
template <class T>
struct referent_storage
{
    typedef typename aligned_storage<
        ::pxr::boost::python::detail::referent_size<T>::value,
        alignment_of<T>::value
    >::type type;
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_REFERENT_STORAGE_HPP
