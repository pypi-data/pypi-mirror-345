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

#ifndef PXR_BOOST_PYTHON_DETAIL_EXCEPTION_HANDLER_HPP
# define PXR_BOOST_PYTHON_DETAIL_EXCEPTION_HANDLER_HPP

# include "./config.hpp"
#include <functional>

namespace pxr { namespace boost { namespace python { namespace detail {

struct exception_handler;

typedef std::function<bool(exception_handler const&, std::function<void()> const&)> handler_function;

struct PXR_BOOST_PYTHON_DECL exception_handler
{
 private: // types
    
 public:
    explicit exception_handler(handler_function const& impl);

    inline bool handle(std::function<void()> const& f) const;
    
    bool operator()(std::function<void()> const& f) const;
 
    static exception_handler* chain;
    
 private:
    static exception_handler* tail;
    
    handler_function m_impl;
    exception_handler* m_next;
};


inline bool exception_handler::handle(std::function<void()> const& f) const
{
    return this->m_impl(*this, f);
}

PXR_BOOST_PYTHON_DECL void register_exception_handler(handler_function const& f);

}}}} // namespace pxr::boost::python::detail

#endif // PXR_BOOST_PYTHON_DETAIL_EXCEPTION_HANDLER_HPP
