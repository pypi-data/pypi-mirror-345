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

#ifndef PXR_BOOST_PYTHON_OBJECT_HPP
# define PXR_BOOST_PYTHON_OBJECT_HPP

# include "./ssize_t.hpp"
# include "./object_core.hpp"
# include "./object_attributes.hpp"
# include "./object_items.hpp"
# include "./object_slices.hpp"
# include "./object_operators.hpp"
# include "./converter/arg_to_python.hpp"

namespace pxr { namespace boost { namespace python {

    inline ssize_t len(object const& obj)
    {
        ssize_t result = PyObject_Length(obj.ptr());
        if (PyErr_Occurred()) throw_error_already_set();
        return result;
    }

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_OBJECT_HPP
