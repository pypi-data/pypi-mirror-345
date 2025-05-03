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

#ifndef PXR_BOOST_PYTHON_OBJECT_MAKE_INSTANCE_HPP
# define PXR_BOOST_PYTHON_OBJECT_MAKE_INSTANCE_HPP

# include "../ref.hpp"
# include "../detail/prefix.hpp"
# include "./instance.hpp"
# include "../converter/registered.hpp"
# include "../detail/decref_guard.hpp"
# include "../detail/type_traits.hpp"
# include "../detail/none.hpp"
# include "../detail/mpl2/or.hpp"

namespace pxr { namespace boost { namespace python { namespace objects {

template <class T, class Holder, class Derived>
struct make_instance_impl
{
    typedef objects::instance<Holder> instance_t;
        
    template <class Arg>
    static inline PyObject* execute(Arg& x)
    {
        static_assert((python::detail::mpl2::or_<pxr::boost::python::detail::is_class<T>,
                pxr::boost::python::detail::is_union<T> >::value));

        PyTypeObject* type = Derived::get_class_object(x);

        if (type == 0)
            return python::detail::none();

        PyObject* raw_result = type->tp_alloc(
            type, objects::additional_instance_size<Holder>::value);
          
        if (raw_result != 0)
        {
            python::detail::decref_guard protect(raw_result);
            
            instance_t* instance = (instance_t*)raw_result;
            
            // construct the new C++ object and install the pointer
            // in the Python object.
            Holder *holder =Derived::construct(instance->storage.bytes, (PyObject*)instance, x);
            holder->install(raw_result);
              
            // Note the position of the internally-stored Holder,
            // for the sake of destruction
            const size_t offset = reinterpret_cast<size_t>(holder) -
              reinterpret_cast<size_t>(instance->storage.bytes) + offsetof(instance_t, storage);
            Py_SET_SIZE(instance, offset);

            // Release ownership of the python object
            protect.cancel();
        }
        return raw_result;
    }
};
    

template <class T, class Holder>
struct make_instance
    : make_instance_impl<T, Holder, make_instance<T,Holder> >
{
    template <class U>
    static inline PyTypeObject* get_class_object(U&)
    {
        return converter::registered<T>::converters.get_class_object();
    }
    
    static inline Holder* construct(void* storage, PyObject* instance, std::reference_wrapper<T const> x)
    {
        size_t allocated = objects::additional_instance_size<Holder>::value;
        void* aligned_storage = std::align(pxr::boost::python::detail::alignment_of<Holder>::value,
                                           sizeof(Holder), storage, allocated);
        return new (aligned_storage) Holder(instance, x);
    }
};
  

}}}} // namespace pxr::boost::python::object

#endif // PXR_BOOST_PYTHON_OBJECT_MAKE_INSTANCE_HPP
