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

#ifndef PXR_BOOST_PYTHON_OBJECT_ADD_TO_NAMESPACE_HPP
# define PXR_BOOST_PYTHON_OBJECT_ADD_TO_NAMESPACE_HPP

# include "../object_fwd.hpp"

namespace pxr { namespace boost { namespace python { namespace objects {

//
// A setattr that's "smart" about function overloading (and docstrings).
//
PXR_BOOST_PYTHON_DECL void add_to_namespace(
    object const& name_space, char const* name, object const& attribute);

PXR_BOOST_PYTHON_DECL void add_to_namespace(
    object const& name_space, char const* name, object const& attribute, char const* doc);

}}}} // namespace pxr::boost::python::objects

#endif // PXR_BOOST_PYTHON_OBJECT_ADD_TO_NAMESPACE_HPP
