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

# ifndef PXR_BOOST_PYTHON_DETAIL_SIGNATURE_HPP
#  define PXR_BOOST_PYTHON_DETAIL_SIGNATURE_HPP

#  include "../type_id.hpp"

#  include "./preprocessor.hpp"
#  include "./indirect_traits.hpp"
#  include "../converter/pytype_function.hpp"

#  include "./mpl2/at.hpp"
#  include "./mpl2/size.hpp"

#  include <utility>

namespace pxr { namespace boost { namespace python { namespace detail {

struct signature_element
{
    char const* basename;
    converter::pytype_function pytype_f;
    bool lvalue;
};

struct py_func_sig_info
{
    signature_element const *signature;
    signature_element const *ret;
};

template <class Idxs> struct signature_arity;

// A metafunction returning the base class used for
//
//   signature<class F, class CallPolicies, class Sig>.
//
template <class Sig>
struct signature_base_select
{
    enum { arity = detail::mpl2::size<Sig>::value - 1 };
    typedef typename signature_arity<
        std::make_index_sequence<arity+1>>::template impl<Sig> type;
};

template <class Sig>
struct signature
    : signature_base_select<Sig>::type
{
};

template <size_t... N>
struct signature_arity<std::index_sequence<N...>>
{
    template <class Sig>
    struct impl
    {
        static signature_element const* elements()
        {
            static signature_element const result[sizeof...(N)+1] = {
                
#ifndef PXR_BOOST_PYTHON_NO_PY_SIGNATURES
                {
                  type_id<typename detail::mpl2::at_c<Sig,N>::type>().name()
                  , &converter::expected_pytype_for_arg<typename detail::mpl2::at_c<Sig,N>::type>::get_pytype
                  , indirect_traits::is_reference_to_non_const<typename detail::mpl2::at_c<Sig,N>::type>::value
                }...,
#else
                {
                  type_id<typename detail::mpl2::at_c<Sig,N>::type>().name()
                  , 0
                  , indirect_traits::is_reference_to_non_const<typename detail::mpl2::at_c<Sig,N>::type>::value
                }...,
#endif
                {0,0,0}
            };
            return result;
        }
    };
};

}}}} // namespace pxr::boost::python::detail

# endif // PXR_BOOST_PYTHON_DETAIL_SIGNATURE_HPP
