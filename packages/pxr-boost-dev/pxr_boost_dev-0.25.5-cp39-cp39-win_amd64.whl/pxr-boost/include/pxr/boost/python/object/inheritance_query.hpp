// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2003.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_OBJECT_INHERITANCE_QUERY_HPP
# define PXR_BOOST_PYTHON_OBJECT_INHERITANCE_QUERY_HPP

# include "../type_id.hpp"

namespace pxr { namespace boost { namespace python { namespace objects {

PXR_BOOST_PYTHON_DECL void* find_static_type(void* p, type_info src, type_info dst);
PXR_BOOST_PYTHON_DECL void* find_dynamic_type(void* p, type_info src, type_info dst);

}}}} // namespace pxr::boost::python::object

#endif // PXR_BOOST_PYTHON_OBJECT_INHERITANCE_QUERY_HPP
