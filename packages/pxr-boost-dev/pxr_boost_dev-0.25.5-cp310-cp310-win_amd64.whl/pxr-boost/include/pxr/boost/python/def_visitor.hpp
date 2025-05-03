// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright David Abrahams 2003.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Modified by Jeremy Retailleau.

#ifndef PXR_BOOST_PYTHON_DEF_VISITOR_HPP
# define PXR_BOOST_PYTHON_DEF_VISITOR_HPP

# include "./detail/prefix.hpp"

namespace pxr { namespace boost { namespace python {

template <class DerivedVisitor> class def_visitor;
template <class T, class X1, class X2, class X3> class class_;

class def_visitor_access
{
    template <class Derived> friend class def_visitor;
    
    // unnamed visit, c.f. init<...>, container suites
    template <class V, class classT>
    static void visit(V const& v, classT& c)
    {
        v.derived_visitor().visit(c);
    }

    // named visit, c.f. object, pure_virtual
    template <class V, class classT, class OptionalArgs>
    static void visit(
        V const& v
      , classT& c
      , char const* name
      , OptionalArgs const& options
    ) 
    {
        v.derived_visitor().visit(c, name, options);
    }
    
};


template <class DerivedVisitor>
class def_visitor
{
    friend class def_visitor_access;
    
    template <class T, class X1, class X2, class X3> friend class class_;
    
    // unnamed visit, c.f. init<...>, container suites
    template <class classT>
    void visit(classT& c) const
    {
        def_visitor_access::visit(*this, c);
    }

    // named visit, c.f. object, pure_virtual
    template <class classT, class OptionalArgs>
    void visit(classT& c, char const* name, OptionalArgs const& options) const
    {
        def_visitor_access::visit(*this, c, name, options);
    }
    
 protected:
    DerivedVisitor const& derived_visitor() const
    {
        return static_cast<DerivedVisitor const&>(*this);
    }
};

}}} // namespace pxr::boost::python

#endif // PXR_BOOST_PYTHON_DEF_VISITOR_HPP
