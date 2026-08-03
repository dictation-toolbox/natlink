"""Runtime marshal DLL registration for the 64-bit Python process."""

import ctypes
import logging
import os
from ctypes import POINTER, byref, c_void_p, c_ulong, c_long
from typing import Tuple

from ._com_helpers import release_raw as _release_factory
from ._guids import GUID, CLSID_MARSHAL, IID_IPSFactoryBuffer

log = logging.getLogger("natlink.com.marshal")

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.LoadLibraryW.argtypes = [ctypes.c_wchar_p]
kernel32.LoadLibraryW.restype = c_void_p
kernel32.GetProcAddress.argtypes = [c_void_p, ctypes.c_char_p]
kernel32.GetProcAddress.restype = c_void_p
kernel32.FreeLibrary.argtypes = [c_void_p]
kernel32.FreeLibrary.restype = ctypes.c_int

ole32 = ctypes.windll.ole32
ole32.CoRegisterClassObject.argtypes = [POINTER(GUID), c_void_p, c_ulong, c_ulong, POINTER(c_ulong)]
ole32.CoRegisterClassObject.restype = c_long
ole32.CoRevokeClassObject.argtypes = [c_ulong]
ole32.CoRevokeClassObject.restype = c_long
ole32.CoRegisterPSClsid.argtypes = [POINTER(GUID), POINTER(GUID)]
ole32.CoRegisterPSClsid.restype = c_long

CLSCTX_INPROC_SERVER = 0x1
REGCLS_MULTI_SEPARATE = 0x2


def _require_64bit_python() -> None:
    """Fail early on unsupported 32-bit Python installs."""
    if ctypes.sizeof(c_void_p) != 8:
        raise OSError(
            "Natlink requires 64-bit Python. Install a 64-bit CPython build "
            "to use the shipped marshal DLLs."
        )


def _parse_guid_str(s):
    """Parse '{...}' GUID string into a GUID struct."""
    from comtypes import GUID as ComGUID
    g = ComGUID(s)
    return GUID(g.Data1, g.Data2, g.Data3, (ctypes.c_ubyte * 8)(*g.Data4))


def _find_dll(bits, dragon_major=0):
    """Locate marshal DLL in the package directory.

    Picks the version-specific DLL:
      marshal{bits}_v13_v14.dll  for DNS 13/14
      marshal{bits}_v15_v16.dll  for DPI 15/16
    Falls back to marshal{bits}.dll if version-specific not found.
    """
    variant = "v13_v14" if 0 < dragon_major < 15 else "v15_v16"
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    name = f"marshal{bits}_{variant}.dll"
    path = os.path.join(pkg_dir, name)
    if os.path.isfile(path):
        log.debug("Using %s marshal DLL: %s", variant, name)
        return path
    # Fallback to unversioned name
    fallback = os.path.join(pkg_dir, f"marshal{bits}.dll")
    if os.path.isfile(fallback):
        log.warning("Version-specific %s not found, using fallback: marshal%s.dll",
                    name, bits)
        return fallback
    raise FileNotFoundError(f"Marshal DLL not found: {path}")


# All interfaces registered via CoRegisterPSClsid (64-bit Python side).
# Dragon's 32-bit side uses vcmshl (SAPI 4.0) and dd10midl (Dragon extensions).
# Our IDL matches their parameter IIDs so the wire format is compatible.
MARSHAL_INTERFACES = {
    # Sole provider — Dragon has no stubs for these
    "ISRCentralW":              "{B9BD3860-44DB-101B-90A8-00AA003E4B50}",
    "ISRGramNotifySinkW":       "{F106BFA0-C743-11CD-80E5-00AA003E4B50}",
    "ISRResAudio":              "{090CD9A7-DA1A-11CD-B3CA-00AA0047BA4F}",
    "ISRResMemory":             "{090CD9AB-DA1A-11CD-B3CA-00AA0047BA4F}",
    "IDgnSRTrainingA":          "{DD108014-6205-11CF-AE61-0000E8A28647}",
    # Shared — Dragon also has stubs (wire format matches)
    "ISRNotifySink":            "{090CD9B0-DA1A-11CD-B3CA-00AA0047BA4F}",
    "IDgnSREngineNotifySinkW":  "{DD109001-6205-11CF-AE61-0000E8A28647}",
    "IDgnSREngineControlW":     "{DD109000-6205-11CF-AE61-0000E8A28647}",
    "ISRSpeakerW":              "{090CD9AE-DA1A-11CD-B3CA-00AA0047BA4F}",
    "IDgnSRSpeakerW":           "{DD10901C-6205-11CF-AE61-0000E8A28647}",
    "IDgnSSvcOutputEventW":     "{DD109201-6205-11CF-AE61-0000E8A28647}",
    "IDgnSSvcInterpreterW":     "{DD109203-6205-11CF-AE61-0000E8A28647}",
    "IDgnSSvcActionNotifySink": "{DD108202-6205-11CF-AE61-0000E8A28647}",
    "ISRGramCommonW":           "{E8C3E160-C743-11CD-80E5-00AA003E4B50}",
    "ISRGramCFGW":              "{ECC0B180-C743-11CD-80E5-00AA003E4B50}",
    "ISRGramDictationW":        "{090CD9A3-DA1A-11CD-B3CA-00AA0047BA4F}",
    "IDgnSRGramSelectW":        "{DD10901A-6205-11CF-AE61-0000E8A28647}",
    "IDgnSRLexiconW":           "{DD109011-6205-11CF-AE61-0000E8A28647}",
    # ILexPronounceW is intentionally omitted for now. Cross-process
    # pronunciation retrieval still fails in practice, and current evidence
    # points to the Get() return-buffer path rather than a simple missing
    # registration on our side. Use IDgnLexWordW as the reliable fallback.
    "IDgnLexWordW":             "{DD109501-6205-11CF-AE61-0000E8A28647}",
    "IDgnErrorW":               "{DD109005-6205-11CF-AE61-0000E8A28647}",
    "IDgnSRAudioFileSourceW":   "{DD109008-6205-11CF-AE61-0000E8A28647}",
    "ISRResBasicW":             "{090CD9A5-DA1A-11CD-B3CA-00AA0047BA4F}",
    "ISRResGraphW":             "{090CD9AA-DA1A-11CD-B3CA-00AA0047BA4F}",
    "ISRResCorrectionW":        "{090CD9A8-DA1A-11CD-B3CA-00AA0047BA4F}",
    "IDgnSRResGraphW":          "{DD109020-6205-11CF-AE61-0000E8A28647}",
    "IDgnSRResSelect":          "{DD10801B-6205-11CF-AE61-0000E8A28647}",
    "IVoiceDictation0W":        "{DD109400-6205-11CF-AE61-0000E8A28647}",
    "IVDct0TextW":              "{DD10940A-6205-11CF-AE61-0000E8A28647}",
    "IVDct0NotifySinkW":        "{DD109401-6205-11CF-AE61-0000E8A28647}",
    "IDgnVDctTextW":            "{DD10940B-6205-11CF-AE61-0000E8A28647}",
}


def register_marshaling(dragon_major: int = 0,
                        dll_path: str = None) -> Tuple[int, int]:
    """Load 64-bit marshal DLL and register PSFactory + all interface IIDs.

    Args:
        dragon_major: Detected Dragon version (0 = unknown, uses DNS 15+ default)
        dll_path: Override DLL path (for testing)

    Returns (hmod, cookie).
    """
    _require_64bit_python()

    log.info("Registering marshal DLLs for Dragon v%d", dragon_major)

    if dll_path is None:
        dll_path = _find_dll(64, dragon_major)

    log.info("Loading marshal DLL: %s", dll_path)
    hmod = kernel32.LoadLibraryW(dll_path)
    if not hmod:
        raise OSError(f"LoadLibrary failed for {dll_path}: error {ctypes.get_last_error()}")

    try:
        pfn = kernel32.GetProcAddress(hmod, b"DllGetClassObject")
        if not pfn:
            raise OSError(f"DllGetClassObject not found in {dll_path}")

        DllGetClassObject = ctypes.WINFUNCTYPE(c_long, POINTER(GUID), POINTER(GUID), POINTER(c_void_p))(pfn)
        pFactory = c_void_p()
        hr = DllGetClassObject(byref(CLSID_MARSHAL), byref(IID_IPSFactoryBuffer), byref(pFactory))
        if hr < 0:
            raise OSError(f"DllGetClassObject failed: 0x{hr & 0xFFFFFFFF:08X}")

        cookie = c_ulong()
        try:
            hr = ole32.CoRegisterClassObject(
                byref(CLSID_MARSHAL), pFactory.value,
                CLSCTX_INPROC_SERVER, REGCLS_MULTI_SEPARATE, byref(cookie)
            )
            if hr < 0:
                raise OSError(f"CoRegisterClassObject failed: 0x{hr & 0xFFFFFFFF:08X}")
        finally:
            _release_factory(pFactory.value)
    except Exception:
        kernel32.FreeLibrary(hmod)
        raise

    # Register per-process proxy/stub for all interfaces
    registered = 0
    failed = []
    for name, iid_str in MARSHAL_INTERFACES.items():
        iid = _parse_guid_str(iid_str)
        hr = ole32.CoRegisterPSClsid(byref(iid), byref(CLSID_MARSHAL))
        if hr >= 0:
            registered += 1
        else:
            failed.append(name)
    log.info("Registered %d/%d marshal interfaces (64-bit, per-process)",
             registered, len(MARSHAL_INTERFACES))
    if failed:
        log.warning("Marshal registration failed for: %s", ", ".join(failed))

    return hmod, cookie.value
