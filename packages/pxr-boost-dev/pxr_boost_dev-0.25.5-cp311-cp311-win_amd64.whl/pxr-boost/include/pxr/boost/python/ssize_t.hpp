// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright Ralf W. Grosse-Kunstleve & David Abrahams 2006.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_SSIZE_T_HPP
# define PXR_BOOST_PYTHON_SSIZE_T_HPP

# include "./detail/prefix.hpp"

namespace pxr { namespace boost { namespace python {

#if PY_VERSION_HEX >= 0x02050000

typedef Py_ssize_t ssize_t;
ssize_t const ssize_t_max = PY_SSIZE_T_MAX;
ssize_t const ssize_t_min = PY_SSIZE_T_MIN;

#else

typedef int ssize_t;
ssize_t const ssize_t_max = INT_MAX;
ssize_t const ssize_t_min = INT_MIN;

#endif

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_SSIZE_T_HPP
