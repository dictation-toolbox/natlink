"""Per-monitor DPI support for the tray UI.

Without this the process runs DPI-unaware: Windows renders it at 96 DPI and
bitmap-stretches the result, so the window and its text are blurry on any
scaled display. Worse for diagnosis, an unaware process is *lied to* —
``GetDpiForSystem`` always reports 96 and monitor enumeration returns
virtualized coordinates, so DPI bugs are invisible from inside the process.

Declaring Per-Monitor V2 turns that off: we get real pixels and must scale
ourselves, including re-scaling when the window is dragged between monitors
of different DPI (``WM_DPICHANGED``).

Awareness is process-wide and must be set before the first window exists.
"""

import ctypes
import ctypes.wintypes as wt
import logging

log = logging.getLogger("natlink.ui.dpi")

user32 = ctypes.windll.user32

# Baseline DPI: Windows expresses scaling as a ratio against this.
USER_DEFAULT_SCREEN_DPI = 96

WM_DPICHANGED = 0x02E0
SM_CXSMICON = 49

# DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2. A sentinel handle, not a count.
_CONTEXT_PER_MONITOR_AWARE_V2 = -4
_PROCESS_PER_MONITOR_DPI_AWARE = 2   # for the 8.1-era shcore API
_MONITOR_DEFAULTTONEAREST = 2
_MDT_EFFECTIVE_DPI = 0


_applied = None


def set_process_dpi_aware() -> str:
    """Declare Per-Monitor V2 awareness. Returns the mechanism that worked.

    Idempotent, so every entry point that might be first can call it without
    coordinating. Any DPI query made before this runs gets the virtualized
    96 rather than the truth, so call it before measuring anything.

    Tries newest to oldest so a modern Windows gets true per-monitor
    behaviour and older ones still avoid bitmap stretching:

      SetProcessDpiAwarenessContext  Win10 1703+  per-monitor, rescales live
      SetProcessDpiAwareness         Win8.1+      per-monitor, no WM_DPICHANGED
      SetProcessDPIAware             Vista+       system DPI only

    Call before creating any window — Windows locks awareness once one
    exists. Already-set awareness (from a manifest, or a second call) is not
    an error; it means someone got here first.
    """
    global _applied
    if _applied is not None:
        return _applied
    _applied = _set_process_dpi_aware()
    return _applied


def current_awareness() -> str:
    """What the process is right now: per-monitor / system / unaware.

    GetProcessDpiAwareness does not distinguish V2 from the original
    per-monitor mode; both report per-monitor, which is the distinction that
    matters to callers.
    """
    try:
        value = ctypes.c_int()
        if ctypes.windll.shcore.GetProcessDpiAwareness(
                None, ctypes.byref(value)) == 0:
            return {0: "unaware", 1: "system",
                    2: "per-monitor"}.get(value.value, "unaware")
    except (AttributeError, OSError):
        pass
    return "unaware"


def _set_process_dpi_aware() -> str:
    # Awareness can only be set once per process. A manifest, an embedding
    # host, or an earlier call may have set it already -- in which case every
    # Set* below fails, and reporting the last one that "succeeded" would
    # claim a weaker mode than the process actually has. SetProcessDPIAware
    # in particular returns TRUE for an already-aware process, so the naive
    # chain reports "system" for a per-monitor process. Ask instead.
    already = current_awareness()
    if already != "unaware":
        return already

    try:
        user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        if user32.SetProcessDpiAwarenessContext(
                ctypes.c_void_p(_CONTEXT_PER_MONITOR_AWARE_V2)):
            return "per-monitor-v2"
    except AttributeError:
        pass  # pre-1703

    try:
        shcore = ctypes.windll.shcore
        if shcore.SetProcessDpiAwareness(_PROCESS_PER_MONITOR_DPI_AWARE) == 0:
            return "per-monitor"
    except (AttributeError, OSError):
        pass  # pre-8.1

    try:
        if user32.SetProcessDPIAware():
            return "system"
    except AttributeError:
        pass

    return "unaware"


def dpi_for_window(hwnd) -> int:
    """Effective DPI of the monitor showing ``hwnd``, or the system DPI."""
    if hwnd:
        try:
            dpi = user32.GetDpiForWindow(hwnd)
            if dpi:
                return dpi
        except AttributeError:
            pass  # pre-1607
    return dpi_for_system()


def dpi_for_system() -> int:
    try:
        return user32.GetDpiForSystem() or USER_DEFAULT_SCREEN_DPI
    except AttributeError:
        return USER_DEFAULT_SCREEN_DPI


def dpi_for_point(x: int, y: int) -> int:
    """Effective DPI of the monitor containing a screen point.

    Used before a window exists, to size it for the display it will open on.
    """
    try:
        shcore = ctypes.windll.shcore
        user32.MonitorFromPoint.restype = ctypes.c_void_p
        point = wt.POINT(x, y)
        monitor = user32.MonitorFromPoint(point, _MONITOR_DEFAULTTONEAREST)
        if monitor:
            dpi_x, dpi_y = ctypes.c_uint(), ctypes.c_uint()
            if shcore.GetDpiForMonitor(ctypes.c_void_p(monitor),
                                       _MDT_EFFECTIVE_DPI,
                                       ctypes.byref(dpi_x),
                                       ctypes.byref(dpi_y)) == 0:
                return dpi_x.value or USER_DEFAULT_SCREEN_DPI
    except (AttributeError, OSError):
        pass
    return dpi_for_system()


def scale(value: int, dpi: int) -> int:
    """Convert a 96-DPI design measurement to physical pixels at ``dpi``."""
    return round(value * dpi / USER_DEFAULT_SCREEN_DPI)


def small_icon_size() -> int:
    """Side length Windows wants for a tray icon, in physical pixels."""
    return user32.GetSystemMetrics(SM_CXSMICON) or 16
