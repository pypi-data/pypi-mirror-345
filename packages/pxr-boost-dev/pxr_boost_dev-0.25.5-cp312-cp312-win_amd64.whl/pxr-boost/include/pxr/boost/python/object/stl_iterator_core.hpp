// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright Eric Niebler 2005.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_OBJECT_STL_ITERATOR_CORE_HPP
# define PXR_BOOST_PYTHON_OBJECT_STL_ITERATOR_CORE_HPP

# include "../object_fwd.hpp"
# include "../handle_fwd.hpp"

namespace pxr { namespace boost { namespace python { namespace objects {

struct PXR_BOOST_PYTHON_DECL stl_input_iterator_impl
{
    stl_input_iterator_impl();
    stl_input_iterator_impl(pxr::boost::python::object const &ob);
    void increment();
    bool equal(stl_input_iterator_impl const &that) const;
    pxr::boost::python::handle<> const &current() const;
private:
    pxr::boost::python::object it_;
    pxr::boost::python::handle<> ob_;
};

}}}} // namespace pxr::boost::python::object

#endif // PXR_BOOST_PYTHON_OBJECT_STL_ITERATOR_CORE_HPP
