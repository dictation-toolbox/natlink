cmake_minimum_required (VERSION 3.20)

project (Natlink)
set(NATLINK_VERSION 5.5.7)
# Anything Python v3.8-3.10 is fine for the actual Natlink binaries but 3.10 is officially supported.
# Any of the python versions above 3.10 are exparimental and may not be stable
set(PYTHON_VERSION 3.10 CACHE STRING "3.X for X >= 8") # Python to compile PYTHON_VERSION 3.X setup by PythonEnv
set(MYAPP_NAME "Natlink")

add_subdirectory("PythonEnv") # setup Python environment based on PYTHON_VERSION

# Use static linking of MSVC runtime libraries, both in debug and release
# See https://cmake.org/cmake/help/git-stage/variable/CMAKE_MSVC_RUNTIME_LIBRARY.html#variable:CMAKE_MSVC_RUNTIME_LIBRARY
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

set(WHEEL_NAME "natlink-${NATLINK_VERSION}-py3-none-any.whl")
set(WHEEL_PATH "${CMAKE_BINARY_DIR}/pythonsrc/dist/${WHEEL_NAME}") 
message(STATUS "Wheel to include: ${WHEEL_PATH}")

# Build C++ code, including two versions of _natlink.pyd, the COM server running Python
add_subdirectory ("NatlinkSource")
# builds the wheel
add_subdirectory ("PythonSrc")
