message("src CMakeLists.txt")

#there are few files in the python portion, list them individually.

configure_file(pyproject.toml pyproject.toml)
configure_file(src/natlink/__init__.py src/natlink/__init__.py)
configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

#we also need the binaries from the natlink build output.

configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

set(NL_BINARY_DIR ${CMAKE_BINARY_DIR}/NatlinkSource/Debug)
set(NL_PY_DIR  ${CMAKE_BINARY_DIR}/pythonsrc/src/natlink)

set (NL_FILES ${NL_BINARY_DIR}/_natlink_core_legacy.pyd ${NL_BINARY_DIR}/_natlink_core_legacy.pdb 
${NL_BINARY_DIR}/_natlink_core.pyd ${NL_BINARY_DIR}/_natlink_core.pdb
${_Python_RUNTIME_LIBRARY_RELEASE} ) 

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

