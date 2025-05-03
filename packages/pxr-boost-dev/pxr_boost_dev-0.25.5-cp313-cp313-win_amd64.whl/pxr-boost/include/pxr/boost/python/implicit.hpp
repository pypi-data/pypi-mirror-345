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

#ifndef PXR_BOOST_PYTHON_IMPLICIT_HPP
# define PXR_BOOST_PYTHON_IMPLICIT_HPP

# include "./detail/prefix.hpp"
# include "./type.hpp"
# include "./converter/implicit.hpp"
# include "./converter/registry.hpp"
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
# include "./converter/pytype_function.hpp"
#endif
# include "./type_id.hpp"

namespace pxr { namespace boost { namespace python {

template <class Source, class Target>
void implicitly_convertible(type<Source>* = 0, type<Target>* = 0)
{
    typedef converter::implicit<Source,Target> functions;
    
    converter::registry::push_back(
          &functions::convertible
        , &functions::construct
        , type_id<Target>()
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
        , &converter::expected_from_python_type_direct<Source>::get_pytype
#endif
        );
}

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_IMPLICIT_HPP
