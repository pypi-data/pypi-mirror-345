#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mimir::core" for configuration "Release"
set_property(TARGET mimir::core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mimir::core PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libmimir_core.a"
  )

list(APPEND _cmake_import_check_targets mimir::core )
list(APPEND _cmake_import_check_files_for_mimir::core "${_IMPORT_PREFIX}/lib64/libmimir_core.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
