#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::boost-python" for configuration "Release"
set_property(TARGET pxr::boost-python APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::boost-python PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-boost/lib/libPxrBoostPython.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libPxrBoostPython.dylib"
  )

list(APPEND _cmake_import_check_targets pxr::boost-python )
list(APPEND _cmake_import_check_files_for_pxr::boost-python "${_IMPORT_PREFIX}/pxr-boost/lib/libPxrBoostPython.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
