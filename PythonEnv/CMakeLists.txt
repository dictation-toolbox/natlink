message("src CMakeLists.txt")

set(PYTHON_VERSIONS 3.8 3.9 3.10 3.11, 3.12)
set_property(CACHE PYTHON_VERSION PROPERTY STRINGS ${PYTHON_VERSIONS})

#### where to find the 32-bit standalone python for $(PYTHON_VERSION)
# TODO: https://discourse.cmake.org/t/possible-to-create-a-python-virtual-env-from-cmake-and-then-find-it-with-findpython3/1132
if(${PYTHON_VERSION} STREQUAL 3.12)
    set(PYTHON_URL "https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.12.2+20240224-i686-pc-windows-msvc-shared-install_only.tar.gz")
elseif(${PYTHON_VERSION} STREQUAL 3.11)
    set(PYTHON_URL "https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-i686-pc-windows-msvc-shared-install_only.tar.gz")
elseif(${PYTHON_VERSION} STREQUAL 3.10)    
    set(PYTHON_URL "https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-i686-pc-windows-msvc-shared-install_only.tar.gz")
elseif(${PYTHON_VERSION} STREQUAL 3.9)
    set(PYTHON_URL "https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.9.18+20240224-i686-pc-windows-msvc-shared-install_only.tar.gz")
elseif(${PYTHON_VERSION} STREQUAL 3.8)
    set(PYTHON_URL "https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.8.18+20240224-i686-pc-windows-msvc-shared-install_only.tar.gz") 
endif()

set(PYTHON_ZIP Python_${PYTHON_VERSION}.zip)

# Download standalone python package
set(PYTHON_ENV_PATH "${CMAKE_BINARY_DIR}/pythonenv")
if(NOT EXISTS ${PYTHON_ZIP})
    file(MAKE_DIRECTORY ${PYTHON_ENV_PATH})
    message(STATUS "Downloading Python ${PYTHON_VERSION} standalone from ${PYTHON_URL}")
    file(DOWNLOAD ${PYTHON_URL} ${PYTHON_ZIP} STATUS ERROR)
    if(NOT ERROR EQUAL 0)
        message(FATAL_ERROR "Failed to download Python: ${ERROR}")
    endif()
endif()

# Extract python standalone package as zip file to pythonenv directory
if(NOT EXISTS ${PYTHON_ENV_PATH}/python/python.exe)
    message(STATUS "Extracting python ${PYTHON_VERSION} standalone to ${PYTHON_ENV_PATH}")
    file(ARCHIVE_EXTRACT INPUT ${PYTHON_ZIP} DESTINATION ${PYTHON_ENV_PATH} PATTERNS "python/*")
    if(NOT EXISTS ${PYTHON_ENV_PATH}/python/python.exe)
        message(FATAL_ERROR "Python ${PYTHON_VERSION} standalone not found in ${PYTHON_ENV_PATH}")
    endif()   
endif()

# Python_FIND_STRATEGY LOCATION is needed to find the Python interpreter in the Python_ROOT_DIR path
set(Python_FIND_STRATEGY LOCATION)
set(Python_ROOT_DIR ${PYTHON_ENV_PATH}/python)
find_package(Python ${PYTHON_VERSION} EXACT COMPONENTS Interpreter Development REQUIRED)
message(STATUS " Python EXE Found: ${Python_EXECUTABLE}")

# TODO: is there a better way to to share these variables with the NatlinkSource and PythonSrc CMakeLists.txt files?
set(Python_LIBRARIES ${Python_LIBRARIES} CACHE INTERNAL "Python libraries")
set(Python_INCLUDE_DIRS ${Python_INCLUDE_DIRS} CACHE INTERNAL "Python include directories") 
set(_Python_RUNTIME_LIBRARY_RELEASE ${_Python_RUNTIME_LIBRARY_RELEASE} CACHE INTERNAL "Python runtime library release")

# Find Flit executable if not install package
find_program(FLIT NAMES "${Python_ROOT_DIR}/Scripts/flit.exe" CACHE INTERNAL) # flit path used to build Wheel in PythonSrc
if (FLIT)
    message(STATUS " Flit exe found at: ${FLIT}")
else()
    # assuming fresh python environment upgrade pip
    message(STATUS " Flit exe not found at: ${Python_ROOT_DIR}/Scripts/flit.exe")
    message(STATUS " Upgrading pip and installing flit\n")
    execute_process(COMMAND ${Python_EXECUTABLE} -m pip install --upgrade pip --no-warn-script-location COMMAND_ERROR_IS_FATAL ANY)
    execute_process(COMMAND ${Python_EXECUTABLE} -m pip install flit --no-warn-script-location COMMAND_ERROR_IS_FATAL ANY)
    find_program(FLIT NAMES "${Python_ROOT_DIR}/Scripts/flit.exe")
endif()