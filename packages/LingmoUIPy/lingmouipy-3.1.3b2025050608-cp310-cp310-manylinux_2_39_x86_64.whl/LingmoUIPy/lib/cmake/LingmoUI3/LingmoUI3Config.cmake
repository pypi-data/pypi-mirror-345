
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was LingmoUIConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

include(CMakeFindDependencyMacro)
find_dependency(Qt6Core 6.5.0)
find_dependency(Qt6DBus 6.5.0)
find_dependency(Qt6Gui 6.5.0)
find_dependency(Qt6Widgets 6.5.0)
find_dependency(Qt6Quick 6.5.0)
find_dependency(Qt6QuickControls2 6.5.0)

include("${CMAKE_CURRENT_LIST_DIR}/LingmoUI3ConfigVersion.cmake")

# Any changes in this ".cmake" file will be overwritten by CMake, the source is the ".cmake.in" file.

include("${CMAKE_CURRENT_LIST_DIR}/LingmoUITargets.cmake")

set(LingmoUI_INSTALL_PREFIX "${PACKAGE_PREFIX_DIR}")


