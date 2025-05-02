
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was Config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

####################################################################################

include(CMakeFindDependencyMacro)


##############################################################
# Debug prints
##############################################################

message("CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}")


##############################################################
# CMake modules and macro files
##############################################################

list(APPEND CMAKE_MODULE_PATH
  "${CMAKE_CURRENT_LIST_DIR}/cmake"
)
include("configure_boost")
include("configure_loki")

##############################################################
# Dependency Handling
##############################################################

# -----
# Boost
# -----

# Find Boost headers only according to https://cmake.org/cmake/help/latest/module/FindBoost.html
configure_boost()
find_dependency(Boost ${BOOST_MIN_VERSION} REQUIRED COMPONENTS iostreams PATHS ${CMAKE_PREFIX_PATH} NO_DEFAULT_PATH)
if(Boost_FOUND)
  message(STATUS "Found Boost: ${Boost_DIR} (found version ${Boost_VERSION})")
endif()


# -----
# Fmt
# -----

find_dependency(fmt REQUIRED)
if(fmt_FOUND)
  message(STATUS "Found fmt: ${fmt_DIR} (found version ${fmt_VERSION})")
endif()


# ----
# Loki
# ----

find_dependency(loki ${LOKI_MIN_VERSION} COMPONENTS parsers REQUIRED PATHS ${CMAKE_PREFIX_PATH} NO_DEFAULT_PATH)


# -----------
# Nauty
# -----------

find_dependency(Nauty REQUIRED)
if(Nauty_FOUND)
  message(STATUS "Found Nauty: ${NAUTY_LIBRARY} ${NAUTY_INCLUDE_DIR}")
endif()


# -----------
# abseil
# -----------

find_dependency(absl CONFIG REQUIRED PATHS ${CMAKE_PREFIX_PATH} NO_DEFAULT_PATH)
if(absl_FOUND)
  message(STATUS "Found absl: ${absl_DIR} (found version ${absl_VERSION})")
endif()


############
# Components
############

set(_mimir_supported_components core)

foreach(_comp ${mimir_FIND_COMPONENTS})
  if (NOT _comp IN_LIST _mimir_supported_components)
    set(mimir_FOUND False)
    set(mimir_NOT_FOUND_MESSAGE "Unsupported component: ${_comp}")
  endif()
  include("${CMAKE_CURRENT_LIST_DIR}/mimir${_comp}Targets.cmake")
endforeach()

get_filename_component(MIMIR_CONFIG_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
message(STATUS "Found mimir: ${MIMIR_CONFIG_DIR} (found version ${mimir_VERSION})")
