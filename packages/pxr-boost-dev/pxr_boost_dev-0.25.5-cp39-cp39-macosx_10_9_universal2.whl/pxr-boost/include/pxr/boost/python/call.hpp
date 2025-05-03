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

# ifndef PXR_BOOST_PYTHON_CALL_HPP
#  define PXR_BOOST_PYTHON_CALL_HPP

# include "./detail/prefix.hpp"

#  include "./converter/arg_to_python.hpp"
#  include "./converter/return_from_python.hpp"
#  include "./detail/preprocessor.hpp"
#  include "./detail/void_return.hpp"

namespace pxr { namespace boost { namespace python {

template <class R, class... A>
typename detail::returnable<R>::type
call(PyObject* callable, A const&... a)
{
    PyObject* const result = 
        PyObject_CallFunctionObjArgs(
            callable
            , converter::arg_to_python<A>(a).get()...
            , NULL
            );
    
    // This conversion *must not* be done in the same expression as
    // the call, because, in the special case where the result is a
    // reference a Python object which was created by converting a C++
    // argument for passing to PyObject_CallFunction, its reference
    // count will be 2 until the end of the full expression containing
    // the conversion, and that interferes with dangling
    // pointer/reference detection.
    converter::return_from_python<R> converter;
    return converter(result);
}

}}} // namespace pxr::boost::python

# endif // PXR_BOOST_PYTHON_CALL_HPP
