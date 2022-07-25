cmake_minimum_required (VERSION 3.20)

project (Natlink)
set(NATLINK_VERSION 5.2.0)
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
#  Build the NatlinkModule, that is, depend on the previous step and 
#  make sure that the Python sources and such are fresh. Mark this
#  situation as a file NatlinkModule/NatlinkModule.STAMP. Similarly, mark
#  mark the up-to-dateness of the tests as NatlinkModule/DefaultConfig.STAMP
# Now, using dependcy on the stamps, start the inno installation generator
add_subdirectory ("InstallerSource")
