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

#ifndef PXR_BOOST_PYTHON_BACK_REFERENCE_HPP
# define PXR_BOOST_PYTHON_BACK_REFERENCE_HPP

# include "./detail/prefix.hpp"

# include "./object_fwd.hpp"
# include "./detail/dependent.hpp"
# include "./detail/raw_pyobject.hpp"

namespace pxr { namespace boost { namespace python {

template <class T>
struct back_reference
{
 private: // types
    typedef typename detail::dependent<object,T>::type source_t;
 public:
    typedef T type;
    
    back_reference(PyObject*, T);
    source_t const& source() const;
    T get() const;
 private:
    source_t m_source;
    T m_value;
};

template<typename T>
class is_back_reference
{
 public:
    static constexpr bool value = false; 
};

template<typename T>
class is_back_reference<back_reference<T> >
{
 public:
    static constexpr bool value = true;
};


//
// implementations
//
template <class T>
back_reference<T>::back_reference(PyObject* p, T x)
    : m_source(detail::borrowed_reference(p))
      , m_value(x)
{
}

template <class T>
typename back_reference<T>::source_t const& back_reference<T>::source() const
{
    return m_source;
}

template <class T>
T back_reference<T>::get() const
{
    return m_value;
}

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_BACK_REFERENCE_HPP
