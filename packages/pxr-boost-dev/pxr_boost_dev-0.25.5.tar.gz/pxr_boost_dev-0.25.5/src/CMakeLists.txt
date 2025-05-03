add_library(boost-python
    pxr/boost/python/converter/arg_to_python_base.cpp
    pxr/boost/python/converter/builtin_converters.cpp
    pxr/boost/python/converter/from_python.cpp
    pxr/boost/python/converter/registry.cpp
    pxr/boost/python/converter/type_id.cpp
    pxr/boost/python/dict.cpp
    pxr/boost/python/errors.cpp
    pxr/boost/python/exec.cpp
    pxr/boost/python/import.cpp
    pxr/boost/python/list.cpp
    pxr/boost/python/long.cpp
    pxr/boost/python/module.cpp
    pxr/boost/python/object/class.cpp
    pxr/boost/python/object/enum.cpp
    pxr/boost/python/object/function.cpp
    pxr/boost/python/object/function_doc_signature.cpp
    pxr/boost/python/object/inheritance.cpp
    pxr/boost/python/object/iterator.cpp
    pxr/boost/python/object/life_support.cpp
    pxr/boost/python/object/pickle_support.cpp
    pxr/boost/python/object/stl_iterator.cpp
    pxr/boost/python/object_operators.cpp
    pxr/boost/python/object_protocol.cpp
    pxr/boost/python/slice.cpp
    pxr/boost/python/str.cpp
    pxr/boost/python/tuple.cpp
    pxr/boost/python/wrapper.cpp
)

target_include_directories(boost-python
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(boost-python
    PUBLIC
        Python::Python
)

set_target_properties(boost-python
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrBoostPython"
)

# Add PXR_BOOST_PYTHON_SOURCE when building this library to ensure symbols
# decorated with PXR_BOOST_PYTHON_DECL are exported.
target_compile_definitions(boost-python
    PRIVATE
        PXR_BOOST_PYTHON_SOURCE
)

# Disable insertion of C++ signatures in docstrings. We generate this
# information separately via our Python doc build process.
target_compile_definitions(boost-python
    PUBLIC
        PXR_BOOST_PYTHON_NO_PY_SIGNATURES
)

# By default CMake defines NDEBUG in CMAKE_CXX_FLAGS_<config> for
# non-debug build configurations, which applies to all targets
# created in this directory. This disables assert calls in unit
# tests, rendering them useless in those configurations.
#
# To avoid this, we remove NDEBUG from CMAKE_CXX_FLAGS_<config>
# and reapply it only to the main library itself below.
if (MSVC)
    set(ndebug_flag "/DNDEBUG")
else()
    set(ndebug_flag "-DNDEBUG")
endif()

foreach(config RELEASE RELWITHDEBINFO MINSIZEREL)
    string(REPLACE
        ${ndebug_flag} ""
        CMAKE_CXX_FLAGS_${config} ${CMAKE_CXX_FLAGS_${config}}
    )
endforeach()

target_compile_definitions(boost-python
    PRIVATE
        $<$<NOT:$<CONFIG:Debug>>:NDEBUG>
)

install(
    TARGETS boost-python EXPORT ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    FILES
        pxr/boost/python.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost
)

install(
    FILES
        pxr/boost/python/arg_from_python.hpp
        pxr/boost/python/args.hpp
        pxr/boost/python/args_fwd.hpp
        pxr/boost/python/back_reference.hpp
        pxr/boost/python/base_type_traits.hpp
        pxr/boost/python/bases.hpp
        pxr/boost/python/borrowed.hpp
        pxr/boost/python/call.hpp
        pxr/boost/python/call_method.hpp
        pxr/boost/python/cast.hpp
        pxr/boost/python/class.hpp
        pxr/boost/python/class_fwd.hpp
        pxr/boost/python/copy_const_reference.hpp
        pxr/boost/python/copy_non_const_reference.hpp
        pxr/boost/python/data_members.hpp
        pxr/boost/python/def.hpp
        pxr/boost/python/def_visitor.hpp
        pxr/boost/python/default_call_policies.hpp
        pxr/boost/python/dict.hpp
        pxr/boost/python/docstring_options.hpp
        pxr/boost/python/enum.hpp
        pxr/boost/python/errors.hpp
        pxr/boost/python/exception_translator.hpp
        pxr/boost/python/exec.hpp
        pxr/boost/python/extract.hpp
        pxr/boost/python/handle.hpp
        pxr/boost/python/handle_fwd.hpp
        pxr/boost/python/has_back_reference.hpp
        pxr/boost/python/implicit.hpp
        pxr/boost/python/import.hpp
        pxr/boost/python/init.hpp
        pxr/boost/python/instance_holder.hpp
        pxr/boost/python/iterator.hpp
        pxr/boost/python/list.hpp
        pxr/boost/python/long.hpp
        pxr/boost/python/lvalue_from_pytype.hpp
        pxr/boost/python/make_constructor.hpp
        pxr/boost/python/make_function.hpp
        pxr/boost/python/manage_new_object.hpp
        pxr/boost/python/module.hpp
        pxr/boost/python/module_init.hpp
        pxr/boost/python/noncopyable.hpp
        pxr/boost/python/object.hpp
        pxr/boost/python/object_attributes.hpp
        pxr/boost/python/object_core.hpp
        pxr/boost/python/object_fwd.hpp
        pxr/boost/python/object_items.hpp
        pxr/boost/python/object_operators.hpp
        pxr/boost/python/object_protocol.hpp
        pxr/boost/python/object_protocol_core.hpp
        pxr/boost/python/object_slices.hpp
        pxr/boost/python/opaque_pointer_converter.hpp
        pxr/boost/python/operators.hpp
        pxr/boost/python/other.hpp
        pxr/boost/python/overloads.hpp
        pxr/boost/python/override.hpp
        pxr/boost/python/pointee.hpp
        pxr/boost/python/proxy.hpp
        pxr/boost/python/ptr.hpp
        pxr/boost/python/pure_virtual.hpp
        pxr/boost/python/raw_function.hpp
        pxr/boost/python/ref.hpp
        pxr/boost/python/refcount.hpp
        pxr/boost/python/reference_existing_object.hpp
        pxr/boost/python/register_ptr_to_python.hpp
        pxr/boost/python/return_arg.hpp
        pxr/boost/python/return_by_value.hpp
        pxr/boost/python/return_internal_reference.hpp
        pxr/boost/python/return_opaque_pointer.hpp
        pxr/boost/python/return_value_policy.hpp
        pxr/boost/python/scope.hpp
        pxr/boost/python/self.hpp
        pxr/boost/python/signature.hpp
        pxr/boost/python/slice.hpp
        pxr/boost/python/slice_nil.hpp
        pxr/boost/python/ssize_t.hpp
        pxr/boost/python/stl_iterator.hpp
        pxr/boost/python/str.hpp
        pxr/boost/python/tag.hpp
        pxr/boost/python/to_python_converter.hpp
        pxr/boost/python/to_python_indirect.hpp
        pxr/boost/python/to_python_value.hpp
        pxr/boost/python/tuple.hpp
        pxr/boost/python/type.hpp
        pxr/boost/python/type_id.hpp
        pxr/boost/python/type_list.hpp
        pxr/boost/python/with_custodian_and_ward.hpp
        pxr/boost/python/wrapper.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python
)

install(
    FILES
        pxr/boost/python/converter/arg_from_python.hpp
        pxr/boost/python/converter/arg_to_python.hpp
        pxr/boost/python/converter/arg_to_python_base.hpp
        pxr/boost/python/converter/as_to_python_function.hpp
        pxr/boost/python/converter/builtin_converters.hpp
        pxr/boost/python/converter/constructor_function.hpp
        pxr/boost/python/converter/context_result_converter.hpp
        pxr/boost/python/converter/convertible_function.hpp
        pxr/boost/python/converter/from_python.hpp
        pxr/boost/python/converter/implicit.hpp
        pxr/boost/python/converter/obj_mgr_arg_from_python.hpp
        pxr/boost/python/converter/object_manager.hpp
        pxr/boost/python/converter/pointer_type_id.hpp
        pxr/boost/python/converter/pyobject_traits.hpp
        pxr/boost/python/converter/pyobject_type.hpp
        pxr/boost/python/converter/pytype_function.hpp
        pxr/boost/python/converter/pytype_object_mgr_traits.hpp
        pxr/boost/python/converter/registered.hpp
        pxr/boost/python/converter/registered_pointee.hpp
        pxr/boost/python/converter/registrations.hpp
        pxr/boost/python/converter/registry.hpp
        pxr/boost/python/converter/return_from_python.hpp
        pxr/boost/python/converter/rvalue_from_python_data.hpp
        pxr/boost/python/converter/shared_ptr_deleter.hpp
        pxr/boost/python/converter/shared_ptr_from_python.hpp
        pxr/boost/python/converter/shared_ptr_to_python.hpp
        pxr/boost/python/converter/to_python_function_type.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python/converter
)

install(
    FILES
        pxr/boost/python/detail/aix_init_module.hpp
        pxr/boost/python/detail/api_placeholder.hpp
        pxr/boost/python/detail/borrowed_ptr.hpp
        pxr/boost/python/detail/caller.hpp
        pxr/boost/python/detail/config.hpp
        pxr/boost/python/detail/construct.hpp
        pxr/boost/python/detail/convertible.hpp
        pxr/boost/python/detail/copy_ctor_mutates_rhs.hpp
        pxr/boost/python/detail/cv_category.hpp
        pxr/boost/python/detail/dealloc.hpp
        pxr/boost/python/detail/decorated_type_id.hpp
        pxr/boost/python/detail/decref_guard.hpp
        pxr/boost/python/detail/def_helper.hpp
        pxr/boost/python/detail/def_helper_fwd.hpp
        pxr/boost/python/detail/defaults_def.hpp
        pxr/boost/python/detail/defaults_gen.hpp
        pxr/boost/python/detail/dependent.hpp
        pxr/boost/python/detail/destroy.hpp
        pxr/boost/python/detail/enable_if.hpp
        pxr/boost/python/detail/exception_handler.hpp
        pxr/boost/python/detail/force_instantiate.hpp
        pxr/boost/python/detail/get_pointer.hpp
        pxr/boost/python/detail/if_else.hpp
        pxr/boost/python/detail/indirect_traits.hpp
        pxr/boost/python/detail/integer_cast.hpp
        pxr/boost/python/detail/invoke.hpp
        pxr/boost/python/detail/is_auto_ptr.hpp
        pxr/boost/python/detail/is_shared_ptr.hpp
        pxr/boost/python/detail/is_wrapper.hpp
        pxr/boost/python/detail/is_xxx.hpp
        pxr/boost/python/detail/make_keyword_range_fn.hpp
        pxr/boost/python/detail/map_entry.hpp
        pxr/boost/python/detail/mpl_lambda.hpp
        pxr/boost/python/detail/msvc_typeinfo.hpp
        pxr/boost/python/detail/none.hpp
        pxr/boost/python/detail/not_specified.hpp
        pxr/boost/python/detail/nullary_function_adaptor.hpp
        pxr/boost/python/detail/operator_id.hpp
        pxr/boost/python/detail/overloads_fwd.hpp
        pxr/boost/python/detail/pointee.hpp
        pxr/boost/python/detail/prefix.hpp
        pxr/boost/python/detail/preprocessor.hpp
        pxr/boost/python/detail/python_type.hpp
        pxr/boost/python/detail/raw_pyobject.hpp
        pxr/boost/python/detail/referent_storage.hpp
        pxr/boost/python/detail/result.hpp
        pxr/boost/python/detail/scope.hpp
        pxr/boost/python/detail/sfinae.hpp
        pxr/boost/python/detail/signature.hpp
        pxr/boost/python/detail/string_literal.hpp
        pxr/boost/python/detail/target.hpp
        pxr/boost/python/detail/translate_exception.hpp
        pxr/boost/python/detail/type_list.hpp
        pxr/boost/python/detail/type_list_impl.hpp
        pxr/boost/python/detail/type_traits.hpp
        pxr/boost/python/detail/unwind_type.hpp
        pxr/boost/python/detail/unwrap_type_id.hpp
        pxr/boost/python/detail/unwrap_wrapper.hpp
        pxr/boost/python/detail/value_arg.hpp
        pxr/boost/python/detail/value_is_shared_ptr.hpp
        pxr/boost/python/detail/value_is_xxx.hpp
        pxr/boost/python/detail/void_ptr.hpp
        pxr/boost/python/detail/void_return.hpp
        pxr/boost/python/detail/wrap_python.hpp
        pxr/boost/python/detail/wrapper_base.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python/detail
)

install(
    FILES
        pxr/boost/python/detail/mpl2/and.hpp
        pxr/boost/python/detail/mpl2/at.hpp
        pxr/boost/python/detail/mpl2/bool.hpp
        pxr/boost/python/detail/mpl2/eval_if.hpp
        pxr/boost/python/detail/mpl2/front.hpp
        pxr/boost/python/detail/mpl2/identity.hpp
        pxr/boost/python/detail/mpl2/if.hpp
        pxr/boost/python/detail/mpl2/int.hpp
        pxr/boost/python/detail/mpl2/not.hpp
        pxr/boost/python/detail/mpl2/pop_front.hpp
        pxr/boost/python/detail/mpl2/push_front.hpp
        pxr/boost/python/detail/mpl2/or.hpp
        pxr/boost/python/detail/mpl2/size.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python/detail/mpl2
)

install(
    FILES
        pxr/boost/python/object/add_to_namespace.hpp
        pxr/boost/python/object/class.hpp
        pxr/boost/python/object/class_detail.hpp
        pxr/boost/python/object/class_metadata.hpp
        pxr/boost/python/object/class_wrapper.hpp
        pxr/boost/python/object/enum_base.hpp
        pxr/boost/python/object/find_instance.hpp
        pxr/boost/python/object/forward.hpp
        pxr/boost/python/object/function.hpp
        pxr/boost/python/object/function_doc_signature.hpp
        pxr/boost/python/object/function_handle.hpp
        pxr/boost/python/object/function_object.hpp
        pxr/boost/python/object/inheritance.hpp
        pxr/boost/python/object/inheritance_query.hpp
        pxr/boost/python/object/instance.hpp
        pxr/boost/python/object/iterator.hpp
        pxr/boost/python/object/iterator_core.hpp
        pxr/boost/python/object/life_support.hpp
        pxr/boost/python/object/make_holder.hpp
        pxr/boost/python/object/make_instance.hpp
        pxr/boost/python/object/make_ptr_instance.hpp
        pxr/boost/python/object/pickle_support.hpp
        pxr/boost/python/object/pointer_holder.hpp
        pxr/boost/python/object/py_function.hpp
        pxr/boost/python/object/stl_iterator_core.hpp
        pxr/boost/python/object/value_holder.hpp
        pxr/boost/python/object/value_holder_fwd.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python/object
)

install(
    FILES
        pxr/boost/python/suite/indexing/container_utils.hpp
        pxr/boost/python/suite/indexing/detail/indexing_suite_detail.hpp
        pxr/boost/python/suite/indexing/indexing_suite.hpp
        pxr/boost/python/suite/indexing/map_indexing_suite.hpp
        pxr/boost/python/suite/indexing/vector_indexing_suite.hpp
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/boost/python/suite
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-boost-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-boost
)