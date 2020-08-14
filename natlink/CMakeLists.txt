cmake_minimum_required(VERSION 3.12)
set(PROJECT_NAME NatlinkModule)
project(${PROJECT_NAME})
 
set(PY_SRCS
    __init__.py
    config.py
    gramparser.py
    loader.py
    redirect_output.py
    _natlink_core.pyi
    py.typed
)
foreach(pyfile ${PY_SRCS})
  add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/natlink/${pyfile}"
    COMMAND cmake -E copy "${CMAKE_CURRENT_SOURCE_DIR}/${pyfile}"
    "${CMAKE_CURRENT_BINARY_DIR}/natlink/${pyfile}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${pyfile}"
    )
   list(APPEND pyfile_dest "${CMAKE_CURRENT_BINARY_DIR}/natlink/${pyfile}")
endforeach(pyfile)

set(pyfile setup.py)
add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${pyfile}"
COMMAND cmake -E copy "${CMAKE_CURRENT_SOURCE_DIR}/${pyfile}"
"${CMAKE_CURRENT_BINARY_DIR}/${pyfile}"
DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${pyfile}"
)
list(APPEND pyfile_dest "${CMAKE_CURRENT_BINARY_DIR}/${pyfile}")


add_custom_target(${PROJECT_NAME} ALL DEPENDS ${pyfile_dest})
add_dependencies(${PROJECT_NAME} NatlinkPyd)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:NatlinkPyd> "${CMAKE_CURRENT_BINARY_DIR}/natlink"
)
