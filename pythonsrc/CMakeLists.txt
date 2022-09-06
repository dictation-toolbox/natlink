message("src CMakeLists.txt")
find_program(FLIT NAMES flit.exe)
if(NOT FLIT)
	message(STATUS "Flit not found")
else(FLIT)
    message(STATUS "FLIT ISCC at ${FLIT}")
endif(NOT FLIT)

set(PACKAGE "dist/natlink-${NATLINK_VERSION}-py3-none-any.whl")

#there are few files in the python portion, list them individually.

configure_file(pyproject.toml pyproject.toml)
configure_file(src/natlink/__init__.py src/natlink/__init__.py)
configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)
configure_file(readme.md readme.md) 

#we also need the binaries from the natlink build output.

configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

set(NL_BINARY_DIR ${CMAKE_BINARY_DIR}/NatlinkSource/Debug)
set(NL_PY_DIR  ${CMAKE_BINARY_DIR}/pythonsrc/src/natlink)

set (NL_FILES ${NL_BINARY_DIR}/_natlink_core13.pyd ${NL_BINARY_DIR}/_natlink_core13.pdb ${NL_BINARY_DIR}/_natlink_core15.pyd ${NL_BINARY_DIR}/_natlink_core15.pdb
${_Python3_RUNTIME_LIBRARY_RELEASE} ) 

#natlink-${NATLINK_VERSION}-py3-none-any.whl 
add_custom_target(package_in_dist ALL
    COMMENT "Adding ${NL_FILES} to python package"
    COMMAND ${CMAKE_COMMAND} -E  copy ${NL_FILES}  ${NL_PY_DIR}
    COMMENT "Now Building Python Package" 
    COMMAND ${FLIT} build --format wheel 
    DEPENDS StampDriver # otherwise the stamps are not checked
        ${PROJECT_BINARY_DIR}/NatlinkSource/NatlinkSource.STAMP
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}/pythonsrc 
)