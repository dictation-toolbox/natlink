cmake_minimum_required (VERSION 3.8)

project ("Installer")
find_program(ISCC iscc)
if(NOT ISCC)
	message(FATAL_ERROR "ISCC not found")
else()
    message(STATUS "Found ISCC at ${ISCC}")
endif()

set (INSTALLER_FILE_BASE "natlink${NATLINK_VERSION}-py${PYTHON_VERSION}-setup")
add_custom_target(natlink-installer ALL DEPENDS "${INSTALLER_FILE_BASE}.exe")
add_custom_command(
    OUTPUT "${INSTALLER_FILE_BASE}.exe"
    DEPENDS NatlinkPyd
    COMMAND ISCC
        ${CMAKE_CURRENT_SOURCE_DIR}/inno-setup-natlink.iss
        /O"${CMAKE_CURRENT_BINARY_DIR}"
        /F"natlink${NATLINK_VERSION}-py${PYTHON_VERSION}-setup"
        /D"SourceRoot=${CMAKE_SOURCE_DIR}"
        /D"BinaryRoot=${CMAKE_BINARY_DIR}"
        /D"MyAppVersion=${NATLINK_VERSION}"
        /D"PythonVersion=${PYTHON_VERSION}"
)
