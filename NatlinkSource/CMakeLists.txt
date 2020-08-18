cmake_minimum_required(VERSION 3.12)
set(PROJECT_NAME NatlinkPyd)
set(CMAKE_CXX_STANDARD 20)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(BUILD_SHARED_LIBS  ON)

project(${PROJECT_NAME})

set(SRC_FILES
        COM/appsupp.cpp
        DictationObject.cpp
        DragonCode.cpp
        Exceptions.cpp
        GrammarObject.cpp
        natlink.cpp
        pythwrap.cpp
        ResultObject.cpp
        MessageWindow.cpp
        StdAfx.cpp
        natlink.rc
        )
source_group("Sources" FILES ${SRC_FILES})

set(HEADERS_FILES
        COM/appsupp.h
        COM/comsupp.h
        DictationObject.h
        DragonCode.h
        COM/dspeech.h
        Exceptions.h
        GrammarObject.h
        ResultObject.h
        Resource.h
        MessageWindow.h
        COM/speech.h
        StdAfx.h
        )
source_group("Headers" FILES ${HEADERS_FILES})

if (NOT DEFINED PYTHON_INCLUDE_DIRS)
    find_package(PythonLibs ${PYTHON_VERSION} EXACT REQUIRED)
endif (NOT DEFINED PYTHON_INCLUDE_DIRS)
message(STATUS "Using Python libraries: ${PYTHON_LIBRARIES}")
message(STATUS "Using Python include: ${PYTHON_INCLUDE_DIRS}")
include_directories(${PYTHON_INCLUDE_DIRS})
include_directories("extern")

add_compile_definitions(DRAGON_VERSION=15)
add_compile_definitions(NATLINK_VERSION="${NATLINK_VERSION}")
# Asserts that Py_ssize_t is used in argument parsing,
# see note at top of https://docs.python.org/3/c-api/arg.html
add_compile_definitions(PY_SSIZE_T_CLEAN)

# Ensures a Stable Application Binary Interface forpython 3.2+
#add_compile_definitions(Py_LIMITED_API)

# ensures that both the stdlib and vc runtime are statically linked into
# the DLL -> fewer dependencies for the user
foreach(flag_var
        CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)

    message(STATUS "${flag_var} ${${flag_var}}")
    if(${flag_var} MATCHES "/MD")
        string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
    endif(${flag_var} MATCHES "/MD")
endforeach(flag_var)

# Add library to build.
add_library(${PROJECT_NAME} SHARED
        ${SRC_FILES} #${HEADERS_FILES}
        )
set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"
        OUTPUT_NAME "_natlink_core"
        LINKER_LANGUAGE C
)
TARGET_LINK_LIBRARIES(${PROJECT_NAME} ${PYTHON_LIBRARIES})