#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::arch" for configuration "Release"
set_property(TARGET pxr::arch APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::arch PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-arch/lib/libPxrArch.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libPxrArch.dylib"
  )

list(APPEND _cmake_import_check_targets pxr::arch )
list(APPEND _cmake_import_check_files_for_pxr::arch "${_IMPORT_PREFIX}/pxr-arch/lib/libPxrArch.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
