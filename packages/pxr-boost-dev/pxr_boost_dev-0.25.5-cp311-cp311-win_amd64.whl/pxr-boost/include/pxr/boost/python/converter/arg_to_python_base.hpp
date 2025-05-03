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

#ifndef PXR_BOOST_PYTHON_CONVERTER_ARG_TO_PYTHON_BASE_HPP
# define PXR_BOOST_PYTHON_CONVERTER_ARG_TO_PYTHON_BASE_HPP

# include "../handle.hpp"

namespace pxr { namespace boost { namespace python { namespace converter {

struct registration;

namespace detail
{
  struct PXR_BOOST_PYTHON_DECL arg_to_python_base
      : handle<>
  {
      arg_to_python_base(void const volatile* source, registration const&);
  };
}

}}}} // namespace pxr::boost::python::converter

#endif // PXR_BOOST_PYTHON_CONVERTER_ARG_TO_PYTHON_BASE_HPP
