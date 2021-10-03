cmake_minimum_required (VERSION 3.8)

project (Natlink)
set(NATLINK_VERSION 4.2)
set(PYTHON_VERSION 3.8)

add_subdirectory ("NatlinkSource")
add_subdirectory ("natlink")
add_subdirectory ("InstallerSource")
