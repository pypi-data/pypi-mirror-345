#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::arch" for configuration "Release"
set_property(TARGET pxr::arch APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::arch PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/pxr-arch/lib/PxrArch.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-arch/lib/PxrArch.dll"
  )

list(APPEND _cmake_import_check_targets pxr::arch )
list(APPEND _cmake_import_check_files_for_pxr::arch "${_IMPORT_PREFIX}/pxr-arch/lib/PxrArch.lib" "${_IMPORT_PREFIX}/pxr-arch/lib/PxrArch.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
