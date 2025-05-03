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

#ifndef PXR_BOOST_PYTHON_DEFAULT_CALL_POLICIES_HPP
# define PXR_BOOST_PYTHON_DEFAULT_CALL_POLICIES_HPP

# include "./detail/prefix.hpp"
# include "./detail/mpl2/if.hpp"
# include "./to_python_value.hpp"
# include "./detail/type_traits.hpp"
# include "./detail/value_arg.hpp"
# include "./detail/mpl2/or.hpp"
# include "./detail/mpl2/front.hpp"

namespace pxr { namespace boost { namespace python {

template <class T> struct to_python_value;

namespace detail
{
// for "readable" error messages
  template <class T> struct specify_a_return_value_policy_to_wrap_functions_returning
# if defined(__GNUC__) || defined(__EDG__)
  {}
# endif 
  ;
}

struct default_result_converter;

struct default_call_policies
{
    // Ownership of this argument tuple will ultimately be adopted by
    // the caller.
    template <class ArgumentPackage>
    static bool precall(ArgumentPackage const&)
    {
        return true;
    }

    // Pass the result through
    template <class ArgumentPackage>
    static PyObject* postcall(ArgumentPackage const&, PyObject* result)
    {
        return result;
    }

    typedef default_result_converter result_converter;
    typedef PyObject* argument_package;

    template <class Sig> 
    struct extract_return_type : detail::mpl2::front<Sig>
    {
    };

};

struct default_result_converter
{
    template <class R>
    struct apply
    {
        typedef typename detail::mpl2::if_<
            detail::mpl2::or_<detail::is_pointer<R>, detail::is_reference<R> >
          , detail::specify_a_return_value_policy_to_wrap_functions_returning<R>
          , pxr::boost::python::to_python_value<
                typename detail::value_arg<R>::type
            >
        >::type type;
    };
};

// Exceptions for c strings an PyObject*s
template <>
struct default_result_converter::apply<char const*>
{
    typedef pxr::boost::python::to_python_value<char const*const&> type;
};

template <>
struct default_result_converter::apply<PyObject*>
{
    typedef pxr::boost::python::to_python_value<PyObject*const&> type;
};

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_DEFAULT_CALL_POLICIES_HPP
