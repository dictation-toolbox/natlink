/*
 * dlldata_natlink.c — Standard proxy/stub DLL data.
 *
 * Uses a unique CLSID to avoid colliding with Dragon's own dd10midl
 * PSFactory registered in HKLM. Python registers this per-process via
 * CoRegisterClassObject + CoRegisterPSClsid, so no admin or registry
 * entries are needed.
 *
 * CLSID: {A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D}
 */

#define PROXY_CLSID_IS  {0xA1B2C3D4, 0xE5F6, 0x4A7B, {0x8C, 0x9D, 0x0E, 0x1F, 0x2A, 0x3B, 0x4C, 0x5D}}

#include <rpcproxy.h>

#ifdef __cplusplus
extern "C" {
#endif

EXTERN_PROXY_FILE( dragon_interfaces )

PROXYFILE_LIST_START
  REFERENCE_PROXY_FILE( dragon_interfaces ),
PROXYFILE_LIST_END

DLLDATA_ROUTINES( aProxyFileList, GET_DLL_CLSID )

#ifdef __cplusplus
}
#endif
