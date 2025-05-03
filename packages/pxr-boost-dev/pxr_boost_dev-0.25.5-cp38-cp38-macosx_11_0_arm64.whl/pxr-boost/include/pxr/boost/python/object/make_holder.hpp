// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2001.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

# ifndef PXR_BOOST_PYTHON_OBJECT_MAKE_HOLDER_HPP
#  define PXR_BOOST_PYTHON_OBJECT_MAKE_HOLDER_HPP

#  include "../detail/prefix.hpp"

#  include "./instance.hpp"
#  include "../converter/registry.hpp"
#if !defined( PXR_BOOST_PYTHON_NO_PY_SIGNATURES) && defined( PXR_BOOST_PYTHON_PY_SIGNATURES_PROPER_INIT_SELF_TYPE)
#  include "../detail/python_type.hpp"
#endif

#  include "./forward.hpp"
#  include "../detail/preprocessor.hpp"

#  include "../detail/mpl2/at.hpp"

#  include <cstddef>

namespace pxr { namespace boost { namespace python { namespace objects {

template <class Idxs>
struct make_holder_impl;

template <size_t... N>
struct make_holder_impl<std::index_sequence<N...>>
{
    template <class Holder, class ArgList>
    struct apply
    {
        static void execute(
#if !defined( PXR_BOOST_PYTHON_NO_PY_SIGNATURES) && defined( PXR_BOOST_PYTHON_PY_SIGNATURES_PROPER_INIT_SELF_TYPE)
            pxr::boost::python::detail::python_class<typename Holder::value_type> *p
#else
            PyObject *p
#endif
            , typename python::detail::mpl2::at_c<ArgList, N>::type... a)
        {
            typedef instance<Holder> instance_t;

            void* memory = Holder::allocate(p, offsetof(instance_t, storage), sizeof(Holder),
                                            pxr::boost::python::detail::alignment_of<Holder>::value);
            try {
                (new (memory) Holder(
                    p, typename forward<decltype(a)>::type(a)...))->install(p);
            }
            catch(...) {
                Holder::deallocate(p, memory);
                throw;
            }
        }
    };
};

template <int N>
using make_holder = make_holder_impl<std::make_index_sequence<N>>;

}}}} // namespace pxr::boost::python::objects

# endif // PXR_BOOST_PYTHON_OBJECT_MAKE_HOLDER_HPP
