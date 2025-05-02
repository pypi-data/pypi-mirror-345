#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "greedyapi" for configuration "Release"
set_property(TARGET greedyapi APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(greedyapi PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgreedyapi.a"
  )

list(APPEND _cmake_import_check_targets greedyapi )
list(APPEND _cmake_import_check_files_for_greedyapi "${_IMPORT_PREFIX}/lib/libgreedyapi.a" )

# Import target "multichunkgreedyapi" for configuration "Release"
set_property(TARGET multichunkgreedyapi APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(multichunkgreedyapi PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmultichunkgreedyapi.a"
  )

list(APPEND _cmake_import_check_targets multichunkgreedyapi )
list(APPEND _cmake_import_check_files_for_multichunkgreedyapi "${_IMPORT_PREFIX}/lib/libmultichunkgreedyapi.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
