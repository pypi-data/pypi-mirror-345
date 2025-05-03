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

#ifndef PXR_BOOST_PYTHON_OBJECT_CLASS_DETAIL_HPP
# define PXR_BOOST_PYTHON_OBJECT_CLASS_DETAIL_HPP

# include "../handle.hpp"
# include "../type_id.hpp"

namespace pxr { namespace boost { namespace python { namespace objects {

PXR_BOOST_PYTHON_DECL type_handle registered_class_object(type_info id);
PXR_BOOST_PYTHON_DECL type_handle class_metatype();
PXR_BOOST_PYTHON_DECL type_handle class_type();

}}}} // namespace pxr::boost::python::object

#endif // PXR_BOOST_PYTHON_OBJECT_CLASS_DETAIL_HPP
