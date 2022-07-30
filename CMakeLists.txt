cmake_minimum_required (VERSION 3.20)

project (Natlink)
set(NATLINK_VERSION 5.3.2)
set(PYTHON_VERSION 3.9 CACHE STRING "3.X for X >= 9")
set(MYAPP_NAME "Natlink")

# Other supported version; use CMake cache editor
set(PYTHON_VERSIONS 3.9 3.10)
set_property(CACHE PYTHON_VERSION PROPERTY STRINGS ${PYTHON_VERSIONS})

#### where to find the 32-bit installer for $(PYTHON_VERSION)
if(${PYTHON_VERSION} STREQUAL 3.10)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.10.4/python-3.10.4.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.9)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.9.12/python-3.9.12.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.8)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe") 
endif()

# Fish for the suffix in PYTHON_INSTALL_EXE after the last "/", something like
# "python-3.10.0.exe"
string(REGEX MATCH "[^/]*$" PYTHON_INSTALL_EXE ${PYTHON_INSTALL_URL})

# The header files of $(PYTHON_VERSION) must be present
find_package (Python3 ${PYTHON_VERSION} EXACT REQUIRED
                      COMPONENTS Development)
if (NOT(Python3_FOUND))
    message(FATAL_ERROR "Python 3, version ${PYTHON_VERSION} not found")
endif()  
message(STATUS "Using Python installation found at: ${Python3_EXECUTABLE}")

# Use static linking of MSVC runtime libraries, both in debug and release
# See https://cmake.org/cmake/help/git-stage/variable/CMAKE_MSVC_RUNTIME_LIBRARY.html#variable:CMAKE_MSVC_RUNTIME_LIBRARY
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# Build C++ code, including two versions of _natlink.pyd, the COM server running Python
add_subdirectory ("NatlinkSource") 

# Outdated NatlinkModule is in src as nalinkcore as python package and no longer packaged by cmake in to the installer 
# add_subdirectory ("NatlinkModule")
    # The links demonstrate how timestamps with StampDriver can be used can propagate file dependencies of targets across directories and records the files for the installer. 
    # https://github.com/dictation-toolbox/natlink/blob/00a56c64f964112f3956ebbc3b79d1e9fdc3dafd/CMakeLists.txt#L39
    # https://github.com/dictation-toolbox/natlink/blob/00a56c64f964112f3956ebbc3b79d1e9fdc3dafd/src/natlinkcore/CMakeLists.txt#L1

add_subdirectory ("InstallerSource")