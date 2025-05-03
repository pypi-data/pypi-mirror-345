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

#ifndef PXR_BOOST_PYTHON_REGISTER_PTR_TO_PYTHON_HPP
#define PXR_BOOST_PYTHON_REGISTER_PTR_TO_PYTHON_HPP

#include "./pointee.hpp"
#include "./object.hpp"
#include "./object/class_wrapper.hpp"

namespace pxr { namespace boost { namespace python {
    
template <class P>
void register_ptr_to_python()
{
    typedef typename pxr::boost::python::pointee<P>::type X;
    objects::class_value_wrapper<
        P
      , objects::make_ptr_instance<
            X
          , objects::pointer_holder<P,X>
        >
    >();
}           

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_REGISTER_PTR_TO_PYTHON_HPP


