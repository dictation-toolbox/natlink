message("src CMakeLists.txt")

# Find Flit executable path
get_filename_component(python_root "${Python3_EXECUTABLE}" PATH)
find_program(FLIT NAMES "${python_root}/Scripts/flit.exe")

if(NOT FLIT)
    message(FATAL_ERROR " Flit exe not found at: ${python_root}/Scripts/flit.exe\n "
    "Install Flit with: ${Python3_EXECUTABLE} -m pip install flit")
else(FLIT)
    message(STATUS "FLIT exe found at ${FLIT}")
endif(NOT FLIT)

set(PACKAGE "dist/natlink-${NATLINK_VERSION}-py3-none-any.whl")

#there are few files in the python portion, list them individually.

configure_file(pyproject.toml pyproject.toml)
configure_file(src/natlink/__init__.py src/natlink/__init__.py)
configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

#we also need the binaries from the natlink build output.

configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

set(NL_BINARY_DIR ${CMAKE_BINARY_DIR}/NatlinkSource/Debug)
set(NL_PY_DIR  ${CMAKE_BINARY_DIR}/pythonsrc/src/natlink)

set (NL_FILES ${NL_BINARY_DIR}/_natlink_core13.pyd ${NL_BINARY_DIR}/_natlink_core13.pdb 
${NL_BINARY_DIR}/_natlink_core15.pyd ${NL_BINARY_DIR}/_natlink_core15.pdb
${_Python3_RUNTIME_LIBRARY_RELEASE} ) 

add_custom_target(natlink-package ALL DEPENDS "${WHEEL_PATH}")

add_custom_command(
    OUTPUT "${WHEEL_PATH}"
    COMMENT "Adding ${NL_FILES} to python package"
    COMMAND ${CMAKE_COMMAND} -E  copy ${NL_FILES}  ${NL_PY_DIR}
    COMMENT "Now Building Python Package" 
    COMMAND ${FLIT} build --format wheel 
    DEPENDS StampDriver # otherwise the stamps are not checked
        ${PROJECT_BINARY_DIR}/NatlinkSource/NatlinkSource.STAMP
        ${NL_FILES}
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}/pythonsrc 
)

