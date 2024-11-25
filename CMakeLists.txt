cmake_minimum_required (VERSION 3.20)

project (Natlink)

#leave this line in
set (NLC_PIP_OPTIONS  "--pre")        

#Important
#when you change  NATLINK_VERSION, decide if you want a prerelease of natlinkcore

#comment this line out to only install a release version of natlinkcore. During development it will be normally commented out.

#set (NLC_PIP_OPTIONS "")             

set(NATLINK_VERSION 5.5.8.dev1) #if you are changing this to a release version, probably you want to comment out the line above.

set(PYTHON_VERSION 3.10 CACHE STRING "3.X for X >= 8") # Python to compile PYTHON_VERSION 3.X
set(MYAPP_NAME "Natlink")

# Anything later than Python 3.8 is fine for the actual Natlink binaries but 3.10 is officially supported.
# These are for the installer.
# Other supported version; use CMake cache editor
set(PYTHON_VERSIONS 3.8 3.9 3.10 3.11)
set_property(CACHE PYTHON_VERSION PROPERTY STRINGS ${PYTHON_VERSIONS})

#### where to find the 32-bit installer for $(PYTHON_VERSION)
if(${PYTHON_VERSION} STREQUAL 3.11)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.11.4/python-3.11.4.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.10)    
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.9)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.9.13/python-3.9.13.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.8)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe") 
endif()

# Fish for the suffix in PYTHON_INSTALL_EXE after the last "/", something like
# "python-3.10.0.exe"
string(REGEX MATCH "[^/]*$" PYTHON_INSTALL_EXE ${PYTHON_INSTALL_URL})

# The header files of $(PYTHON_VERSION) must be present
find_package(Python3 ${PYTHON_VERSION} EXACT REQUIRED
                      COMPONENTS Interpreter Development)
if (NOT(Python3_FOUND))
    message(FATAL_ERROR "Python 3, version ${PYTHON_VERSION} not found")
endif()  
message(STATUS "Using Python installation found at: ${Python3_EXECUTABLE}")

# Use static linking of MSVC runtime libraries, both in debug and release
# See https://cmake.org/cmake/help/git-stage/variable/CMAKE_MSVC_RUNTIME_LIBRARY.html#variable:CMAKE_MSVC_RUNTIME_LIBRARY
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

set(WHEEL_NAME "natlink-${NATLINK_VERSION}-py3-none-any.whl")
set(WHEEL_PATH "${CMAKE_BINARY_DIR}/pythonsrc/dist/${WHEEL_NAME}") 
message(STATUS "Wheel to include: ${WHEEL_PATH}")


# Build C++ code, including two versions of _natlink.pyd, the COM server running Python
add_subdirectory ("NatlinkSource") 
add_subdirectory ("pythonsrc") 
add_subdirectory ("InstallerSource")
