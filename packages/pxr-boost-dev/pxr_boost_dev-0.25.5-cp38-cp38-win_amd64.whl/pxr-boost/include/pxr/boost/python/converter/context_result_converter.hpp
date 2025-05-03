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

#ifndef PXR_BOOST_PYTHON_CONVERTER_CONTEXT_RESULT_CONVERTER_HPP
# define PXR_BOOST_PYTHON_CONVERTER_CONTEXT_RESULT_CONVERTER_HPP

namespace pxr { namespace boost { namespace python { namespace converter {

// A ResultConverter base class used to indicate that this result
// converter should be constructed with the original Python argument
// list.
struct context_result_converter {};

}}}} // namespace pxr::boost::python::converter

#endif // PXR_BOOST_PYTHON_CONVERTER_CONTEXT_RESULT_CONVERTER_HPP
