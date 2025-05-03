// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2004. Distributed under the Boost
// Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_OVERRIDE_HPP
# define PXR_BOOST_PYTHON_OVERRIDE_HPP

# include "./detail/prefix.hpp"

# include "./converter/return_from_python.hpp"

# include "./extract.hpp"
# include "./handle.hpp"

#  include "./type.hpp"

namespace pxr { namespace boost { namespace python {

class override;

namespace detail
{
  class wrapper_base;
  
  // The result of calling a method.
  class method_result
  {
   private:
      friend class pxr::boost::python::override;
      explicit method_result(PyObject* x)
        : m_obj(x)
      {}

   public:
      template <class T>
      operator T()
      {
          converter::return_from_python<T> converter;
          return converter(m_obj.release());
      }

#  if defined(_MSC_VER)
      // No operator T&
      // This workaround was noted as required for VC 8 (_MSC_VER == 1400).
      // It is still required as of Visual Studio 2019 (_MSC_VER == 1929).
      // Without it, the unit test "exec" fails.
#  else
      
      template <class T>
      operator T&() const
      {
          converter::return_from_python<T&> converter;
          return converter(const_cast<handle<>&>(m_obj).release());
      }
#  endif 

      template <class T>
      T as(type<T>* = 0)
      {
          converter::return_from_python<T> converter;
          return converter(m_obj.release());
      }

      template <class T>
      T unchecked(type<T>* = 0)
      {
          return extract<T>(m_obj.get())();
      }
   private:
      mutable handle<> m_obj;
  };
}

class override : public object
{
 private:
    friend class detail::wrapper_base;
    override(handle<> x)
      : object(x)
    {}
    
 public:
    template <class... A>
    detail::method_result
    operator()(A const&... a) const
    {
        detail::method_result x(
            PyObject_CallFunctionObjArgs(
                this->ptr()
                , converter::arg_to_python<A>(a).get()...
                , NULL
            ));
        return x;
    }

};

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_OVERRIDE_HPP
