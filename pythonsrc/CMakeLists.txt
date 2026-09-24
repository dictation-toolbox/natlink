message("src CMakeLists.txt")

cmake_path(GET Python3_EXECUTABLE PARENT_PATH python_root)


#in theory any python should work, not necessarily the python used to run natlink.  Maybe not even a windows python.
#that could be useful in something like a github build action.  


set(PACKAGE "dist/natlink-${NATLINK_VERSION}-py3-none-any.whl")

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
${_Python3_RUNTIME_LIBRARY_RELEASE} ) 

add_custom_target(natlink-package ALL DEPENDS "${WHEEL_PATH}")

#    If it is ever desired to use a different Python for building the wheel, than the natlink python,
#   change this to use the desired python in the custom command below:  COMMAND ${Python3_EXECUTABLE} -m build

add_custom_command(
    OUTPUT "${WHEEL_PATH}"
    COMMENT "Building python wheel package in ${WHEEL_PATH}"
    COMMAND ${CMAKE_COMMAND} -E  copy ${NL_FILES}  ${NL_PY_DIR}
    #COMMAND ${Python3_EXECUTABLE} -m build
    COMMAND pyproject-build

    DEPENDS StampDriver # otherwise the stamps are not checked
        ${PROJECT_BINARY_DIR}/NatlinkSource/NatlinkSource.STAMP
        ${NL_FILES}
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}/pythonsrc 
)

