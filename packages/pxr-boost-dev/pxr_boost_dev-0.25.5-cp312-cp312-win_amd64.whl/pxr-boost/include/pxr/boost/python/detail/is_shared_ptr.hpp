// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2003.
// Copyright Stefan Seefeld 2016.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DETAIL_IS_SHARED_PTR_HPP
#define PXR_BOOST_PYTHON_DETAIL_IS_SHARED_PTR_HPP

#include "./is_xxx.hpp"
#include <memory>

namespace pxr { namespace boost { namespace python { namespace detail {

PXR_BOOST_PYTHON_IS_XXX_DEF(shared_ptr, std::shared_ptr, 1)

}}}} // namespace pxr::boost::python::detail

#endif
