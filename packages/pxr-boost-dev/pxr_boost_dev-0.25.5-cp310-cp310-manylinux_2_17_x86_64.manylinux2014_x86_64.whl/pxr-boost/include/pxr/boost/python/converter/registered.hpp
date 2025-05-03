// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2002.
// Copyright Stefan Seefeld 2016.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_CONVERTER_REGISTERED_HPP
#define PXR_BOOST_PYTHON_CONVERTER_REGISTERED_HPP

#include "../type_id.hpp"
#include "./registry.hpp"
#include "./registrations.hpp"
#include "../detail/type_traits.hpp"
#include "../type.hpp"
#include <memory>
#if defined(PXR_BOOST_PYTHON_TRACE_REGISTRY) \
 || defined(PXR_BOOST_PYTHON_CONVERTER_REGISTRY_APPLE_MACH_WORKAROUND)
# include <iostream>
#endif

namespace pxr { namespace boost {

namespace python { namespace converter { 

struct registration;

namespace detail
{
  template <class T>
  struct registered_base
  {
      static registration const& converters;
  };
}

template <class T>
struct registered
  : detail::registered_base<
        typename pxr::boost::python::detail::add_lvalue_reference<
            typename pxr::boost::python::detail::add_cv<T>::type
        >::type
    >
{
};

// collapses a few more types to the same static instance.  MSVC7.1
// fails to strip cv-qualification from array types in typeid.  For
// some reason we can't use this collapse there or array converters
// will not be found.
template <class T>
struct registered<T&>
  : registered<T> {};

//
// implementations
//
namespace detail
{
  inline void
  register_shared_ptr0(...)
  {
  }

  template <class T>
  inline void
  register_shared_ptr0(std::shared_ptr<T>*)
  {
      registry::lookup_shared_ptr(type_id<std::shared_ptr<T> >());
  }

  template <class T>
  inline void
  register_shared_ptr1(T const volatile*)
  {
      detail::register_shared_ptr0((T*)0);
  }
  
  template <class T>
  inline registration const& 
  registry_lookup2(T&(*)())
  {
      detail::register_shared_ptr1((T*)0);
      return registry::lookup(type_id<T&>());
  }

  template <class T>
  inline registration const& 
  registry_lookup1(type<T>)
  {
      return registry_lookup2((T(*)())0);
  }

  inline registration const& 
  registry_lookup1(type<const volatile void>)
  {
      detail::register_shared_ptr1((void*)0);
      return registry::lookup(type_id<void>());
  }

  template <class T>
  registration const& registered_base<T>::converters = detail::registry_lookup1(type<T>());

}

}}}} // namespace pxr::boost::python::converter

#endif
