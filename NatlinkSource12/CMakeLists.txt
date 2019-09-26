cmake_minimum_required(VERSION 3.12)
# Project
get_filename_component(PROJECT_DIR "${CMAKE_CURRENT_SOURCE_DIR}" ABSOLUTE)
set(DEPENDENCIES_DIR ${PROJECT_DIR}/dependencies)
set(PROJECT_NAME natlink)

# make binary python callable
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(BUILD_SHARED_LIBS  ON)

project(${PROJECT_NAME})

# Source Files
set(SRC_FILES
        ./appsupp.cpp
        ./dictobj.cpp
        ./DragCode.cpp
        ./excepts.cpp
        ./GramObj.cpp
        ./natlink.cpp
        ./pythwrap.cpp
        ./ResObj.cpp
        ./SecdThrd.cpp
        StdAfx.cpp
        natlink.rc
        )
source_group("Sources" FILES ${SRC_FILES})

# Header Files
set(HEADERS_FILES
        appsupp.h
        comsupp.h
        dictobj.h
        DragCode.h
        dspeech.h
        excepts.h
        GramObj.h
        resobj.h
        resource.h
        SecdThrd.h
        SPEECH.H
        StdAfx.h
        )
source_group("Headers" FILES ${HEADERS_FILES})

# TODO This should not be hard coded...
include_directories("C:\\Python27_32bit\\include")
link_directories("C:\\Python27_32bit\\libs")


add_compile_definitions(UNICODE)

# Add library to build.
add_library(${PROJECT_NAME} SHARED
        ${SRC_FILES} #${HEADERS_FILES}
        )
set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES
        PREFIX ""
        OUTPUT_NAME "natlink"
        LINKER_LANGUAGE C
)
SET_TARGET_PROPERTIES(${PROJECT_NAME}   PROPERTIES SUFFIX .pyd)