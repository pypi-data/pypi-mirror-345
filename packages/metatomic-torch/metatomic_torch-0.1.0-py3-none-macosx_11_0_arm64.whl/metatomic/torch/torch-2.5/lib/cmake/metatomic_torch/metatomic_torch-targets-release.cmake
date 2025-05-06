#----------------------------------------------------------------
# Generated CMake target import file for configuration "release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "metatomic_torch" for configuration "release"
set_property(TARGET metatomic_torch APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(metatomic_torch PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmetatomic_torch.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libmetatomic_torch.dylib"
  )

list(APPEND _cmake_import_check_targets metatomic_torch )
list(APPEND _cmake_import_check_files_for_metatomic_torch "${_IMPORT_PREFIX}/lib/libmetatomic_torch.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
