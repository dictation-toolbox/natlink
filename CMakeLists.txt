# CMakeLists.txt — Build natlink 64-bit marshal DLLs
#
# Produces two marshal DLLs:
#   marshal64_v13_v14.dll   (Dragon 13 / DPI 14)
#   marshal64_v15_v16.dll   (DPI 15 / 16)
#
# Both use a unique CLSID ({A1B2C3D4-...}) to avoid colliding with
# Dragon's own dd10midl PSFactory in the registry.
#
# Build:
#   cmake --preset vs2022 && cmake --build build --config Release
#
# Or use scripts/build_dll.ps1 (stops Dragon/launcher automatically):
#   .\scripts\build_dll.ps1

cmake_minimum_required(VERSION 3.20)
project(natlink_marshal C)

set(PKG_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src/natlink_com)

# Find MIDL in the Windows SDK (not always on PATH outside VS prompt).
#
# Search order:
#   1. VS-set env var + platform version  (inside VS prompt, any version)
#   2. Standard SDK path + platform version (outside VS prompt, version known)
#   3. Standard SDK path, any 10.0.* version (fallback for older VS / no env)
set(_SDK_ROOT "C:/Program Files (x86)/Windows Kits/10/bin")
file(GLOB _SDK_VERS LIST_DIRECTORIES true "${_SDK_ROOT}/10.0.*")
# Sort descending so the newest SDK is tried first
list(SORT _SDK_VERS ORDER DESCENDING)
set(_SDK_MIDL_HINTS)
foreach(_ver IN LISTS _SDK_VERS)
    list(APPEND _SDK_MIDL_HINTS "${_ver}/x64")
endforeach()

find_program(MIDL_COMPILER midl
    HINTS
        "$ENV{WindowsSdkDir}/bin/${CMAKE_VS_WINDOWS_TARGET_PLATFORM_VERSION}/x64"
        "${_SDK_ROOT}/${CMAKE_VS_WINDOWS_TARGET_PLATFORM_VERSION}/x64"
        ${_SDK_MIDL_HINTS}
    REQUIRED
)

# ===================================================================
# Helper function: build one marshal DLL from an IDL file
# ===================================================================
function(add_marshal_dll VARIANT IDL_FILE)
    set(DLL_NAME "marshal64_${VARIANT}")
    set(GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/midl_gen_${VARIANT})
    file(MAKE_DIRECTORY ${GEN_DIR})

    # --- Copy IDL as dragon_interfaces.idl so MIDL generates
    #     dragon_interfaces_ProxyFileInfo regardless of source filename ---
    set(IDL_COPY ${GEN_DIR}/dragon_interfaces.idl)
    add_custom_command(
        OUTPUT ${IDL_COPY}
        COMMAND ${CMAKE_COMMAND} -E copy ${IDL_FILE} ${IDL_COPY}
        DEPENDS ${IDL_FILE}
    )

    # --- MIDL compile ---
    add_custom_command(
        OUTPUT
            ${GEN_DIR}/dragon_interfaces_p.c
            ${GEN_DIR}/dragon_interfaces_i.c
            ${GEN_DIR}/dragon_interfaces.h
            ${GEN_DIR}/dragon_interfaces.tlb
        COMMAND ${MIDL_COMPILER} /Oicf /target NT51
            /out ${GEN_DIR}
            ${IDL_COPY}
        DEPENDS ${IDL_COPY}
    )

    set(PROXY_C ${GEN_DIR}/dragon_interfaces_p.c)

    # --- Compile and link ---
    add_library(${DLL_NAME} SHARED
        ${CMAKE_CURRENT_SOURCE_DIR}/dlldata_natlink.c
        ${PROXY_C}
        ${GEN_DIR}/dragon_interfaces_i.c
    )

    target_compile_definitions(${DLL_NAME} PRIVATE
        WIN32
        _WIN32_WINNT=0x0601
        REGISTER_PROXY_DLL
    )

    target_link_libraries(${DLL_NAME} PRIVATE
        rpcrt4 oleaut32 ole32 kernel32
    )

    # Module definition file
    set(DEF_FILE ${CMAKE_CURRENT_BINARY_DIR}/${DLL_NAME}.def)
    file(WRITE ${DEF_FILE}
"LIBRARY \"${DLL_NAME}\"
EXPORTS
    DllGetClassObject   PRIVATE
    DllCanUnloadNow     PRIVATE
    DllRegisterServer   PRIVATE
    DllUnregisterServer PRIVATE
    GetProxyDllInfo     PRIVATE
")
    set_target_properties(${DLL_NAME} PROPERTIES
        LINK_FLAGS "/DEF:\"${DEF_FILE}\""
    )

    # --- Copy outputs to package directory ---
    add_custom_command(TARGET ${DLL_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:${DLL_NAME}>
            ${PKG_DIR}/${DLL_NAME}.dll
        COMMAND ${CMAKE_COMMAND} -E echo "Copied ${DLL_NAME}.dll"
    )

    # Copy version-specific TLB for comtypes (loaded based on Dragon version)
    add_custom_command(TARGET ${DLL_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${GEN_DIR}/dragon_interfaces.tlb
            ${PKG_DIR}/dragon_interfaces_${VARIANT}.tlb
        COMMAND ${CMAKE_COMMAND} -E echo "Copied dragon_interfaces_${VARIANT}.tlb"
    )
endfunction()

# ===================================================================
# Build both variants (64-bit only)
# ===================================================================

add_marshal_dll(v15_v16 ${PKG_DIR}/dragon_interfaces_v15_v16.idl)
add_marshal_dll(v13_v14 ${PKG_DIR}/dragon_interfaces_v13_v14.idl)
