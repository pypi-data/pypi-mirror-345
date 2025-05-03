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

#ifndef PXR_BOOST_PYTHON_DETAIL_VOID_RETURN_HPP
# define PXR_BOOST_PYTHON_DETAIL_VOID_RETURN_HPP

namespace pxr { namespace boost { namespace python { namespace detail {

struct void_return
{
    void_return() {}
 private: 
    void operator=(void_return const&);
};

template <class T>
struct returnable
{
    typedef T type;
};

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_VOID_RETURN_HPP
