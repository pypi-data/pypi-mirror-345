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

#ifndef PXR_BOOST_PYTHON_CONVERTER_SHARED_PTR_TO_PYTHON_HPP
#define PXR_BOOST_PYTHON_CONVERTER_SHARED_PTR_TO_PYTHON_HPP

#include "../refcount.hpp"
#include "./shared_ptr_deleter.hpp"
#include <memory>

namespace pxr { namespace boost { namespace python { namespace converter {

template <class T>
PyObject* shared_ptr_to_python(std::shared_ptr<T> const& x)
{
  if (!x)
    return python::detail::none();
  else if (shared_ptr_deleter* d = std::get_deleter<shared_ptr_deleter>(x))
    return incref(d->owner.get());
  else
    return converter::registered<std::shared_ptr<T> const&>::converters.to_python(&x);
}

}}}} // namespace pxr::boost::python::converter

#endif
