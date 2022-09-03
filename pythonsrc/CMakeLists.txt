message("src CMakeLists.txt")
find_program(FLIT NAMES flit.exe)
if(NOT FLIT)
	message(STATUS "Flit not found")
else(FLIT)
    message(STATUS "FLIT ISCC at ${FLIT}")
endif(NOT FLIT)

set(PACKAGE "dist/natlink-1.0-py3-none-any.whl")

#there are few files in the python portion, list them individually.

configure_file(pyproject.toml pyproject.toml)
#configure_file(pythonsrc/src/natlink/__init__.py src/natlink/__init__.py)
#configure_file(pythonsrc/src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

#we also need the binaries from the natlink build output.

configure_file(src/natlink/_natlink_core.pyi src/natlink/_natlink_core.pyi)

#COMMAND file(COPY, ${PROJECT_BINARY_DIR}/NatlinkSource/Debug/_natlink_core13.pdb)

add_custom_target(package_in_dist ALL 
 
    COMMAND ${FLIT} build --format wheel 
    DEPENDS StampDriver # otherwise the stamps are not checked
        ${PROJECT_BINARY_DIR}/NatlinkSource/NatlinkSource.STAMP
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/pythonsrc 
    COMMENT "Now Building Python Package"
)