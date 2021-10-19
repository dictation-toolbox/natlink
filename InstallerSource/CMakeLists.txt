cmake_minimum_required (VERSION 3.8)

project ("Installer")

find_program(ISCC NAMES ISCC ISCC.exe PATH_SUFFIXES "Inno Setup 6")
if(NOT ISCC)
	message(STATUS "ISCC not found")
else()
    message(STATUS "Found ISCC at ${ISCC}")
endif()

set (INSTALLER_FILE_BASE "natlink${NATLINK_VERSION}-py${PYTHON_VERSION}-32-setup")
add_custom_target(natlink-installer 
        ALL DEPENDS "${INSTALLER_FILE_BASE}.exe")

# TODO: why all this copying when not used? add lots of dependencies:
# such as .py files (see inno-setup-natlink.iss, which uses source files directly)
string(REPLACE "." "" PYTHON_VERSION_NO_DOT ${PYTHON_VERSION})

add_custom_command(
    OUTPUT "${INSTALLER_FILE_BASE}.exe"
    DEPENDS natlink15_pyd natlink1314_pyd "inno-setup-natlink.iss" "inno-code.iss"
    COMMAND ${ISCC}
        ${CMAKE_CURRENT_SOURCE_DIR}/inno-setup-natlink.iss
        /O"${CMAKE_CURRENT_BINARY_DIR}"
        /F"${INSTALLER_FILE_BASE}"
        /D"SourceRoot=${CMAKE_SOURCE_DIR}"
        /D"BinaryRoot=${CMAKE_BINARY_DIR}"
        /D"MyAppVersion=${NATLINK_VERSION}"
        /D"PythonVersion=${PYTHON_VERSION}"
        /D"PythonVersionNoDot=${PYTHON_VERSION_NO_DOT}"
        /D"PythonInstallURL=${PYTHON_INSTALL_URL}"
        /D"PythonInstallExe=${PYTHON_INSTALL_EXE}"
        /D"MyAppName=${MYAPP_NAME}"
)

add_custom_target(natlink-installer-zip ALL DEPENDS "${INSTALLER_FILE_BASE}.zip")
add_custom_command(
    OUTPUT "${INSTALLER_FILE_BASE}.zip"
    DEPENDS natlink-installer
	COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${INSTALLER_FILE_BASE}.zip" --format=zip
       "${CMAKE_CURRENT_BINARY_DIR}/${INSTALLER_FILE_BASE}.exe")
