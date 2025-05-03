// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2002.
// Copyright Stefan Seefeld 2016.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_CONVERTER_SHARED_PTR_FROM_PYTHON_HPP
#define PXR_BOOST_PYTHON_CONVERTER_SHARED_PTR_FROM_PYTHON_HPP

#include "../handle.hpp"
#include "./shared_ptr_deleter.hpp"
#include "./from_python.hpp"
#include "./rvalue_from_python_data.hpp"
#include "./registered.hpp"
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
# include "./pytype_function.hpp"
#endif
#include <memory>

namespace pxr { namespace boost { namespace python { namespace converter {

template <class T, template <typename> class SP>
struct shared_ptr_from_python
{
  shared_ptr_from_python()
  {
    converter::registry::insert(&convertible, &construct, type_id<SP<T> >()
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
				, &converter::expected_from_python_type_direct<T>::get_pytype
#endif
				);
  }

 private:
  static void* convertible(PyObject* p)
  {
    if (p == Py_None)
      return p;
        
    return converter::get_lvalue_from_python(p, registered<T>::converters);
  }
    
  static void construct(PyObject* source, rvalue_from_python_stage1_data* data)
  {
    void* const storage = ((converter::rvalue_from_python_storage<SP<T> >*)data)->storage.bytes;
    // Deal with the "None" case.
    if (data->convertible == source)
      new (storage) SP<T>();
    else
    {
      void *const storage = ((converter::rvalue_from_python_storage<SP<T> >*)data)->storage.bytes;
      // Deal with the "None" case.
      if (data->convertible == source)
        new (storage) SP<T>();
      else
      {
        SP<void> hold_convertible_ref_count((void*)0, shared_ptr_deleter(handle<>(borrowed(source))) );
        // use aliasing constructor
        new (storage) SP<T>(hold_convertible_ref_count, static_cast<T*>(data->convertible));
      }
    }
    data->convertible = storage;
  }
};

}}}} // namespace pxr::boost::python::converter

#endif
