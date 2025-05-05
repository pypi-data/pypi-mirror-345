# Find MLX Data
#
# Defines the following variables:
#
#   MLX_DATA_FOUND            : True if MLX Data is found
#   MLX_DATA_INCLUDE_DIRS     : Include directory
#   MLX_DATA_LIBRARIES        : Libraries to link against
#   MLX_DATA_CXX_FLAGS        : Additional compiler flags


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was mlx-data.pc.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

####################################################################################

include(${PACKAGE_PREFIX_DIR}/share/cmake/MLXData/MLXDataTargets.cmake)

set_and_check(MLX_DATA_LIBRARY_DIRS ${PACKAGE_PREFIX_DIR}/lib)
set_and_check(MLX_DATA_INCLUDE_DIRS ${PACKAGE_PREFIX_DIR}/include)
set(MLX_DATA_LIBRARIES mlxdata)

find_library(MLX_DATA_LIBRARY mlxdata PATHS ${MLX_DATA_LIBRARY_DIRS})

set_target_properties(mlx PROPERTIES
    CXX_STANDARD 17
    INTERFACE_COMPILE_OPTIONS "${MLX_DATA_CXX_FLAGS}"
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(MLX_DATA DEFAULT_MSG MLX_DATA_LIBRARY MLX_DATA_INCLUDE_DIRS)
