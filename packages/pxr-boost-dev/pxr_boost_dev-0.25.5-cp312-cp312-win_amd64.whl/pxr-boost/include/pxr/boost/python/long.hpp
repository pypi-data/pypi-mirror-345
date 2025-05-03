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

#ifndef PXR_BOOST_PYTHON_LONG_HPP
# define PXR_BOOST_PYTHON_LONG_HPP

# include "./detail/prefix.hpp"

# include "./object.hpp"
# include "./converter/pytype_object_mgr_traits.hpp"

namespace pxr { namespace boost { namespace python {

namespace detail
{
  struct PXR_BOOST_PYTHON_DECL long_base : object
  {
   protected:
      long_base(); // new long_
      explicit long_base(object_cref rhs);
      explicit long_base(object_cref rhs, object_cref base);
      
      PXR_BOOST_PYTHON_FORWARD_OBJECT_CONSTRUCTORS(long_base, object)
          
   private:
      static detail::new_reference call(object const&);
      static detail::new_reference call(object const&, object const&);
  };
}

class long_ : public detail::long_base
{
    typedef detail::long_base base;
 public:
    long_() {} // new long_

    template <class T>
    explicit long_(T const& rhs)
        : detail::long_base(object(rhs))
    {
    }

    template <class T, class U>
    explicit long_(T const& rhs, U const& base)
        : detail::long_base(object(rhs), object(base))
    {
    }
    
 public: // implementation detail -- for internal use only
    PXR_BOOST_PYTHON_FORWARD_OBJECT_CONSTRUCTORS(long_, base)
};

//
// Converter Specializations
//
namespace converter
{
  template <>
  struct object_manager_traits<long_>
      : pytype_object_manager_traits<&PyLong_Type,long_>
  {
  };
}

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_LONG_HPP
