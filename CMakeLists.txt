cmake_minimum_required (VERSION 3.8)

project (Natlink)
set(NATLINK_VERSION 6.0)
set(PYTHON_VERSION 3.8)
set(DRAGON_VERSION 15)
set(MYAPP_NAME "Natlink")

find_package (Python3 ${PYTHON_VERSION} EXACT REQUIRED
                      COMPONENTS Interpreter Development)

if (NOT(Python3_FOUND))
    message(FATAL_ERROR "Python 3, version ${PYTHON_VERSION} not found")
endif()  

message(STATUS "Using Python installation found at: ${Python3_EXECUTABLE}")

add_subdirectory ("NatlinkSource")
add_subdirectory ("natlink")

add_subdirectory ("InstallerSource")
