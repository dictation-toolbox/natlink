set(CMAKE_CXX_STANDARD 20)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(BUILD_SHARED_LIBS ON)

configure_file(natlink.rc.in natlink.rc)

set(SRC_FILES
        COM/appsupp.cpp DictationObject.cpp DragonCode.cpp
        Exceptions.cpp GrammarObject.cpp natlink.cpp
        pythwrap.cpp ResultObject.cpp MessageWindow.cpp
        StdAfx.cpp ${CMAKE_CURRENT_BINARY_DIR}/natlink.rc)

set(HEADERS_FILES
        COM/appsupp.h COM/comsupp.h DictationObject.h
        DragonCode.h COM/dspeech.h Exceptions.h GrammarObject.h
        ResultObject.h Resource.h MessageWindow.h
        COM/speech.h StdAfx.h)

# for Visual Studio convenience
source_group("Headers" FILES ${HEADERS_FILES}) 
source_group("Sources" FILES ${SRC_FILES})

# FIXME: this is wrong. We don't need the python interpreter, only it's name (if at all)
add_executable(python_dll IMPORTED)
set_target_properties(python_dll
        PROPERTIES
        IMPORTED_LOCATION ${_Python_RUNTIME_LIBRARY_RELEASE})

# Include CMAKE_CURRENT_SOURCE_DIR for the benefit of natlink.rc (in current_binary_dir)
include_directories(${Python_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR})
include_directories("extern")

add_compile_definitions(NATLINK_VERSION="${NATLINK_VERSION}"
        PYTHON_VERSION="${PYTHON_VERSION}" # strict discipline every
        MYAPP_NAME="${MYAPP_NAME}") # that'll likely be Natlink
                        
add_compile_options("/std:c++17")
add_compile_options("/EHsc")

# Asserts that Py_ssize_t is used in argument parsing,
# see note at top of https://docs.python.org/3/c-api/arg.html
add_compile_definitions(PY_SSIZE_T_CLEAN)

# Add two DLL libraries to build, one for 15 and one for 13 (which also works for 14).
add_library(natlink_core_pyd SHARED ${SRC_FILES})
add_library(natlink_core_legacy_pyd SHARED ${SRC_FILES})
# They share some properties
set_target_properties(natlink_core_pyd natlink_core_legacy_pyd PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"
        LINKER_LANGUAGE C
        DEPENDS python_dll)
# and they both use Python libraries
set_property(TARGET natlink_core_pyd natlink_core_legacy_pyd
             APPEND PROPERTY LINK_LIBRARIES ${Python_LIBRARIES})
# Now, define filename for Dragon 15, 16 pyd and the -D passed to the compiler
set_property(TARGET natlink_core_pyd PROPERTY OUTPUT_NAME "_natlink_core" )
target_compile_definitions(natlink_core_pyd PRIVATE LEGACY=False)
# Same for Dragon 13 and 14 legacy pyd
set_property(TARGET natlink_core_legacy_pyd PROPERTY OUTPUT_NAME "_natlink_core_legacy" )
target_compile_definitions(natlink_core_legacy_pyd PRIVATE LEGACY=True)

add_custom_target(StampDriver DEPENDS NatlinkSource.STAMP)

add_custom_command(OUTPUT NatlinkSource.STAMP
  COMMAND cmake -E touch NatlinkSource.STAMP
  DEPENDS 
  natlink_core_legacy_pyd natlink_core_pyd) # binary targets)