"""SDATA struct helpers for COM data marshaling."""

import ctypes

from ._com_helpers import cotaskmem_free


def sdata_to_bytes(sdata) -> bytes:
    """Extract raw bytes from an SDATA struct and free the COM-allocated buffer.

    Returns b"" if pData is null or dwSize is 0.
    """
    if not sdata.pData or sdata.dwSize == 0:
        return b""
    try:
        return ctypes.string_at(sdata.pData, sdata.dwSize)
    finally:
        cotaskmem_free(sdata.pData)


def build_sdata(tlb, data: bytes):
    """Build SDATA from raw bytes.

    Returns (sdata, buf) — caller MUST keep buf reference alive until the COM
    call completes.  ctypes.cast creates a raw pointer that does NOT prevent
    GC of the source buffer.
    """
    sdata = tlb.SDATA()
    if data:
        buf = (ctypes.c_ubyte * len(data))(*data)
        sdata.pData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
        sdata.dwSize = len(data)
    else:
        # C++ emptyList sets sData.pData = "\0" with dwSize = 0 — a non-NULL
        # pointer.  Dragon's ListSet may check for NULL, so match C++.
        buf = (ctypes.c_ubyte * 1)(0)
        sdata.pData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
        sdata.dwSize = 0
    return sdata, buf
