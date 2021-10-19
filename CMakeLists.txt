cmake_minimum_required (VERSION 3.14)

project (Natlink)
set(NATLINK_VERSION 6.0)
set(PYTHON_VERSION 3.8 CACHE STRING "3.X for X >= 8")
set(MYAPP_NAME "Natlink")

# Other supported version; use CMake cache editor
set(PYTHON_VERSIONS 3.8 3.9 3.10)
set_property(CACHE PYTHON_VERSION PROPERTY STRINGS ${PYTHON_VERSIONS})

#### where to find the 32-bit installer for $(PYTHON_VERSION)
if(${PYTHON_VERSION} STREQUAL 3.10)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.10.0/python-3.10.0.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.9)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.9.7/python-3.9.7.exe")
elseif(${PYTHON_VERSION} STREQUAL 3.8)
    set(PYTHON_INSTALL_URL "https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe") 
endif()

# fish for the suffix in PYTHON_INSTALL_EXE after the last "/", something like
# "python-3.10.0.exe"
string(REGEX MATCH "[^/]*$" PYTHON_INSTALL_EXE ${PYTHON_INSTALL_URL})

# DEPRECATE
set(DRAGON_VERSION 15)

# The header files of $(PYTHON_VERSION) must be present
find_package (Python3 ${PYTHON_VERSION} EXACT REQUIRED
                      COMPONENTS Development)
if (NOT(Python3_FOUND))
    message(FATAL_ERROR "Python 3, version ${PYTHON_VERSION} not found")
endif()  
message(STATUS "Using Python installation found at: ${Python3_EXECUTABLE}")

# Now configure the project
add_subdirectory ("NatlinkSource")
add_subdirectory ("NatlinkModule")
add_subdirectory ("InstallerSource")
