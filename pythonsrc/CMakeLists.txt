message("src CMakeLists.txt")
find_program(FLIT NAMES flit.exe)
if(NOT FLIT)
	message(STATUS "Flit not found")
else(FLIT)
    message(STATUS "FLIT ISCC at ${FLIT}")
endif(NOT FLIT)

set(PACKAGE "dist/natlink-1.0-py3-none-any.whl")

add_custom_target(package_in_dist ALL 
    COMMAND ${FLIT} build --format wheel 
    DEPENDS StampDriver # otherwise the stamps are not checked
        ${PROJECT_BINARY_DIR}/NatlinkSource/NatlinkSource.STAMP
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/pythonsrc 
    COMMENT "Now Building Python Package"
)