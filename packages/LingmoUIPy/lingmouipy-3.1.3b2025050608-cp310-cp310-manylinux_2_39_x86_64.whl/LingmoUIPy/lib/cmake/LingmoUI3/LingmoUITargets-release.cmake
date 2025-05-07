#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "LingmoUI3.GraphicalEffects" for configuration "Release"
set_property(TARGET LingmoUI3.GraphicalEffects APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LingmoUI3.GraphicalEffects PROPERTIES
  IMPORTED_LOCATION_RELEASE "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/GraphicalEffects/libLingmoUI3.GraphicalEffects.so.3.1.1"
  IMPORTED_SONAME_RELEASE "libLingmoUI3.GraphicalEffects.so.3"
  )

list(APPEND _cmake_import_check_targets LingmoUI3.GraphicalEffects )
list(APPEND _cmake_import_check_files_for_LingmoUI3.GraphicalEffects "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/GraphicalEffects/libLingmoUI3.GraphicalEffects.so.3.1.1" )

# Import target "LingmoUI3" for configuration "Release"
set_property(TARGET LingmoUI3 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LingmoUI3 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "Qt6::Qml;Qt6::Quick;Qt6::QuickControls2;Qt6::Core5Compat;KF6::WindowSystem"
  IMPORTED_LOCATION_RELEASE "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/libLingmoUI3.so.3.1.1"
  IMPORTED_SONAME_RELEASE "libLingmoUI3.so.3"
  )

list(APPEND _cmake_import_check_targets LingmoUI3 )
list(APPEND _cmake_import_check_files_for_LingmoUI3 "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/libLingmoUI3.so.3.1.1" )

# Import target "LingmoUI3CompatibleModule" for configuration "Release"
set_property(TARGET LingmoUI3CompatibleModule APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LingmoUI3CompatibleModule PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "Qt6::Qml;Qt6::Quick;Qt6::QuickControls2;Qt6::Core5Compat;KF6::WindowSystem"
  IMPORTED_LOCATION_RELEASE "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/CompatibleModule/libLingmoUI3CompatibleModule.so.3.1.1"
  IMPORTED_SONAME_RELEASE "libLingmoUI3CompatibleModule.so.3"
  )

list(APPEND _cmake_import_check_targets LingmoUI3CompatibleModule )
list(APPEND _cmake_import_check_files_for_LingmoUI3CompatibleModule "/home/runner/work/LingmoUI/LingmoUI/build/lib.linux-x86_64-cpython-310/LingmoUIPy/qml/LingmoUI/CompatibleModule/libLingmoUI3CompatibleModule.so.3.1.1" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
