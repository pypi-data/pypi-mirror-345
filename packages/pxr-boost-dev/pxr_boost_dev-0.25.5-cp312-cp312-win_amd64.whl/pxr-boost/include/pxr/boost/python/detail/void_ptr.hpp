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

#ifndef PXR_BOOST_PYTHON_DETAIL_VOID_PTR_HPP
# define PXR_BOOST_PYTHON_DETAIL_VOID_PTR_HPP

# include "./type_traits.hpp"

namespace pxr { namespace boost { namespace python { namespace detail {

template <class U>
inline U& void_ptr_to_reference(void const volatile* p, U&(*)())
{
    return *(U*)p;
}

template <class T>
inline void write_void_ptr(void const volatile* storage, void* ptr, T*)
{
    *(T**)storage = (T*)ptr;
}

// writes U(ptr) into the storage
template <class U>
inline void write_void_ptr_reference(void const volatile* storage, void* ptr, U&(*)())
{
    // stripping CV qualification suppresses warnings on older EDGs
    typedef typename remove_cv<U>::type u_stripped; 
    write_void_ptr(storage, ptr, u_stripped(0));
}

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_VOID_PTR_HPP
