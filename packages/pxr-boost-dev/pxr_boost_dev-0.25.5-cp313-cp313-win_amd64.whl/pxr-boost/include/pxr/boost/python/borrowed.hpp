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

#ifndef PXR_BOOST_PYTHON_BORROWED_HPP
# define PXR_BOOST_PYTHON_BORROWED_HPP

# include "./detail/prefix.hpp"
# include "./detail/borrowed_ptr.hpp"

namespace pxr { namespace boost { namespace python {

template <class T>
inline python::detail::borrowed<T>* borrowed(T* p)
{
    return (detail::borrowed<T>*)p;
}
    
}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_BORROWED_HPP
