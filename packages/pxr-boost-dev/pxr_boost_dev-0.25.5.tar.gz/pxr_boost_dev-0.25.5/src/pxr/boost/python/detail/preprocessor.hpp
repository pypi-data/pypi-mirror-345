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

#ifndef PXR_BOOST_PYTHON_DETAIL_PREPROCESSOR_HPP
# define PXR_BOOST_PYTHON_DETAIL_PREPROCESSOR_HPP

# ifndef PXR_BOOST_PYTHON_MAX_ARITY
#  define PXR_BOOST_PYTHON_MAX_ARITY 15
# endif

# ifndef PXR_BOOST_PYTHON_MAX_BASES
#  define PXR_BOOST_PYTHON_MAX_BASES 10
# endif 

// cv-qualifiers
# define PXR_BOOST_PYTHON_NIL
# define PXR_BOOST_PYTHON_APPLY_QUALIFIERS(M, ...)      \
    M(PXR_BOOST_PYTHON_NIL, __VA_ARGS__)                \
    M(const, __VA_ARGS__)                               \
    M(volatile, __VA_ARGS__)                            \
    M(const volatile, __VA_ARGS__)

#endif // PXR_BOOST_PYTHON_DETAIL_PREPROCESSOR_HPP
