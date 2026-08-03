"""Low-level COM vtable helpers and factory utilities."""

import ctypes
import itertools
from ctypes import POINTER, byref, c_void_p, c_ulong, c_long, c_wchar

from ._guids import GUID, IID_IDgnErrorW

# Process-wide, monotonic, never reused. next() on itertools.count is atomic
# under the GIL, so no lock is needed.
_object_handles = itertools.count(1)


def next_object_handle() -> int:
    """Allocate a handle for a grammar or dictation object.

    Deliberately *not* ``id(self)``. CPython reallocates freed heap addresses
    to new objects of the same size, and these handles are not just local
    keys: they index the connection's sink registry and the compat registries,
    and they travel through the PostMessage deferral queue, where they are
    resolved only when the pump drains — potentially after the object they
    named has been freed.

    With ``id(self)`` that window is reachable in normal use: a grammar
    receives PhraseFinish and a WM_SENDRESULTS closure is queued carrying its
    handle; before the pump drains, a reload unloads that grammar and loads
    another whose object lands on the freed address; the queued closure then
    resolves the handle to the *new* grammar and delivers the old one's
    recognition to it. Grammar reload is exactly when this happens, and it is
    the most common operation in a natlink session.

    The C++ original passed real interface pointers with no post-and-drain
    gap, so it had no equivalent exposure.
    """
    return next(_object_handles)

_ole32 = ctypes.windll.ole32
_ole32.CoTaskMemFree.argtypes = [c_void_p]
_ole32.CoTaskMemFree.restype = None


def cotaskmem_free(ptr):
    """Free a COM-allocated buffer (CoTaskMemFree)."""
    _ole32.CoTaskMemFree(ptr)


def qi_raw(punk, iid):
    """Raw QueryInterface on a COM pointer."""
    vtbl = ctypes.cast(punk, POINTER(POINTER(c_void_p))).contents
    fn = ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(GUID), POINTER(c_void_p))(vtbl[0])
    ppv = c_void_p()
    hr = fn(punk, byref(iid), byref(ppv))
    return hr, ppv.value


def release_raw(punk):
    """Raw Release on a COM pointer."""
    vtbl = ctypes.cast(punk, POINTER(POINTER(c_void_p))).contents
    fn = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtbl[2])
    return fn(punk)


def call_query_service(psp, guidService, riid):
    """Raw IServiceProvider::QueryService call."""
    vtbl = ctypes.cast(psp, POINTER(POINTER(c_void_p))).contents
    fn = ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(GUID), POINTER(GUID), POINTER(c_void_p))(vtbl[3])
    ppv = c_void_p()
    hr = fn(psp, byref(guidService), byref(riid), byref(ppv))
    return hr, ppv.value


def addref_raw(ptr):
    """Extract raw COM pointer from a comtypes proxy and AddRef it.

    Returns an independently ref-counted raw pointer that survives
    even if comtypes internally releases its own reference.  The caller
    must call release_raw() on the returned value during disconnect.
    """
    if ptr is None:
        return 0
    raw = ctypes.cast(ptr, c_void_p).value
    if not raw:
        return 0
    # AddRef via vtable slot [1]
    vtbl = ctypes.cast(raw, POINTER(POINTER(c_void_p))).contents
    fn = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtbl[1])
    fn(raw)
    return raw


def get_refcount(raw):
    """Get COM refcount by doing AddRef + Release (returns current count)."""
    if not raw:
        return -1
    vtbl = ctypes.cast(raw, POINTER(POINTER(c_void_p))).contents
    addref_fn = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtbl[1])
    release_fn = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtbl[2])
    count = addref_fn(raw)  # AddRef returns new count
    release_fn(raw)         # undo AddRef
    return count - 1        # subtract the AddRef we just did


def force_release(ptr):
    """Deterministic COM Release that prevents comtypes from double-releasing.

    Extracts the raw COM pointer from a comtypes proxy, zeroes out the
    proxy's internal pointer (so comtypes' __del__ becomes a no-op), then
    calls Release via vtable.  This guarantees Dragon sees the Release
    immediately, regardless of comtypes' internal refcount state.

    Without this, setting a comtypes wrapper to None relies on Python GC
    for the actual COM Release — which may never happen if comtypes has
    already internally released the proxy (leaving Dragon's CNotify list
    with dangling entries).

    STA-only: the read-then-zero of the proxy pointer is not atomic, so this
    must run on the apartment thread that owns the proxy.  A stray cross-thread
    call racing the same proxy would double-free.
    """
    if ptr is None:
        return
    raw = ctypes.cast(ptr, c_void_p).value
    if not raw:
        return
    # Detach: zero the comtypes proxy's internal COM pointer.
    # This is the inverse of wrap_comtypes' memmove — it prevents the
    # proxy's __del__ from calling Release again (double-release).
    ctypes.memmove(byref(ptr), byref(c_void_p(0)), ctypes.sizeof(c_void_p))
    # Now send the COM Release to Dragon via vtable.
    release_raw(raw)


def wrap_comtypes(raw_ptr, interface):
    """Wrap a raw COM pointer in a comtypes interface wrapper.

    AddRef is required because memmove bypasses comtypes' normal COM pointer
    construction (which would AddRef automatically).  The caller must call
    release_raw(raw_ptr) after wrapping to release the raw reference — the
    comtypes wrapper now owns its own reference.
    """
    obj = ctypes.POINTER(interface)()
    ctypes.memmove(byref(obj), byref(c_void_p(raw_ptr)), ctypes.sizeof(c_void_p))
    obj.AddRef()
    return obj


def lazy_com_factory(builder):
    """Create a factory that lazily builds a COMObject class on first call.

    Defers the comtypes import until the first sink instance is created,
    since sys.coinit_flags must be set before comtypes is imported.
    """
    _cls_holder = [None]

    def create(*args, **kwargs):
        if _cls_holder[0] is None:
            _cls_holder[0] = builder()
        return _cls_holder[0](*args, **kwargs)

    return create


def get_dragon_error_message(punk):
    """Extract Dragon's extended error description via IDgnErrorW.

    The IUnknown passed to ErrorHappened/WarningHappened callbacks can be
    QI'd for IDgnErrorW to get a human-readable error string.  This mirrors
    the C++ pattern in Exceptions.cpp:189-229.

    Returns the error string, or None if the QI or call fails (e.g. because
    the cross-process proxy/stub for IDgnErrorW is not available).
    """
    if not punk:
        return None
    try:
        raw = ctypes.cast(punk, c_void_p).value
        if not raw:
            return None
        hr, pErr = qi_raw(raw, IID_IDgnErrorW)
        if hr < 0 or not pErr:
            return None
        try:
            return _call_error_message_get(pErr)
        finally:
            release_raw(pErr)
    except Exception:
        return None


def _call_error_message_get(pIDgnError):
    """Call IDgnErrorW::ErrorMessageGet (vtable slot 4).

    C++ signature: HRESULT ErrorMessageGet(wchar_t* pBuf, DWORD dwBufSize, DWORD* pdwNeeded)
    where dwBufSize and pdwNeeded are in wchar counts (not byte counts).
    See Exceptions.cpp:206 — the C++ uses a 512-char buffer.
    """
    vtbl = ctypes.cast(pIDgnError, POINTER(POINTER(c_void_p))).contents
    # Slot 0=QI, 1=AddRef, 2=Release, 3=LastErrorGet, 4=ErrorMessageGet
    fn = ctypes.WINFUNCTYPE(
        c_long, c_void_p,          # this
        c_void_p,                   # wchar_t* pBuf
        c_ulong,                    # DWORD dwBufSize (wchar count)
        POINTER(c_ulong),           # DWORD* pdwNeeded (wchar count)
    )(vtbl[4])

    char_count = 512
    buf = (c_wchar * char_count)()
    needed = c_ulong(0)
    hr = fn(pIDgnError, ctypes.cast(buf, c_void_p), char_count, byref(needed))

    # Retry with larger buffer if E_BUFFERTOOSMALL (0x8004020E)
    if (hr & 0xFFFFFFFF) == 0x8004020E and needed.value > char_count:
        char_count = needed.value
        buf = (c_wchar * char_count)()
        hr = fn(pIDgnError, ctypes.cast(buf, c_void_p), char_count, byref(needed))

    if hr < 0:
        return None
    return buf.value or None
