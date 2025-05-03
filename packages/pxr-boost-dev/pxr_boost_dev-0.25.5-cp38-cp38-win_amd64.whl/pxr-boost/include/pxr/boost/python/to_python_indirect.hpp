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

#ifndef PXR_BOOST_PYTHON_TO_PYTHON_INDIRECT_HPP
# define PXR_BOOST_PYTHON_TO_PYTHON_INDIRECT_HPP

# include "./detail/prefix.hpp"

# include "./object/pointer_holder.hpp"
# include "./object/make_ptr_instance.hpp"

# include "./detail/none.hpp"

#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
# include "./converter/pytype_function.hpp"
#endif

# include "./refcount.hpp"

# include "./detail/type_traits.hpp"

# include <memory>

namespace pxr { namespace boost { namespace python {

template <class T, class MakeHolder>
struct to_python_indirect
{
    template <class U>
    inline PyObject*
    operator()(U const& ref) const
    {
        return this->execute(const_cast<U&>(ref), detail::is_pointer<U>());
    }
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
    inline PyTypeObject const*
    get_pytype()const
    {
        return converter::registered_pytype<T>::get_pytype();
    }
#endif
 private:
    template <class U>
    inline PyObject* execute(U* ptr, detail::true_) const
    {
        // No special NULL treatment for references
        if (ptr == 0)
            return python::detail::none();
        else
            return this->execute(*ptr, detail::false_());
    }
    
    template <class U>
    inline PyObject* execute(U const& x, detail::false_) const
    {
        U* const p = &const_cast<U&>(x);
        if (detail::is_polymorphic<U>::value)
        {
            if (PyObject* o = detail::wrapper_base_::owner(p))
                return incref(o);
        }
        return MakeHolder::execute(p);
    }
};

//
// implementations
//
namespace detail
{
  struct make_owning_holder
  {
      template <class T>
      static PyObject* execute(T* p)
      {
          typedef std::unique_ptr<T> smart_pointer;
          typedef objects::pointer_holder<smart_pointer, T> holder_t;

          smart_pointer ptr(const_cast<T*>(p));
          return objects::make_ptr_instance<T, holder_t>::execute(ptr);
      }
  };

  struct make_reference_holder
  {
      template <class T>
      static PyObject* execute(T* p)
      {
          typedef objects::pointer_holder<T*, T> holder_t;
          T* q = const_cast<T*>(p);
          return objects::make_ptr_instance<T, holder_t>::execute(q);
      }
  };
}

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_TO_PYTHON_INDIRECT_HPP
