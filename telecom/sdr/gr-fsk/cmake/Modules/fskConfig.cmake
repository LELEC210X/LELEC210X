INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_FSK fsk)

FIND_PATH(
    FSK_INCLUDE_DIRS
    NAMES fsk/api.h
    HINTS $ENV{FSK_DIR}/include
        ${PC_FSK_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    FSK_LIBRARIES
    NAMES gnuradio-fsk
    HINTS $ENV{FSK_DIR}/lib
        ${PC_FSK_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/fskTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(FSK DEFAULT_MSG FSK_LIBRARIES FSK_INCLUDE_DIRS)
MARK_AS_ADVANCED(FSK_LIBRARIES FSK_INCLUDE_DIRS)
