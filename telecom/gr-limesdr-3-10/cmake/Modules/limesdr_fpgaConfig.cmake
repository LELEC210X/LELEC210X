INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_LIMESDR_FPGA limesdr_fpga)

FIND_PATH(
    LIMESDR_FPGA_INCLUDE_DIRS
    NAMES limesdr_fpga/api.h
    HINTS $ENV{LIMESDR_FPGA_DIR}/include
        ${PC_LIMESDR_FPGA_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    LIMESDR_FPGA_LIBRARIES
    NAMES gnuradio-limesdr_fpga
    HINTS $ENV{LIMESDR_FPGA_DIR}/lib
        ${PC_LIMESDR_FPGA_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/limesdr_fpgaTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LIMESDR_FPGA DEFAULT_MSG LIMESDR_FPGA_LIBRARIES LIMESDR_FPGA_INCLUDE_DIRS)
MARK_AS_ADVANCED(LIMESDR_FPGA_LIBRARIES LIMESDR_FPGA_INCLUDE_DIRS)
