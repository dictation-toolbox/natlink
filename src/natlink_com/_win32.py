"""Pure Python Win32 utility functions (no COM needed)."""

import ctypes
import ctypes.wintypes
import logging
from typing import Tuple

log = logging.getLogger("natlink.com")

user32 = ctypes.windll.user32
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

DRAGON_CLS = "DgnBarMainWindowCls"

# Set argtypes/restype once at module level for clipboard functions
user32.OpenClipboard.argtypes = [ctypes.c_void_p]
user32.OpenClipboard.restype = ctypes.c_int
user32.GetClipboardData.argtypes = [ctypes.c_uint]
user32.GetClipboardData.restype = ctypes.c_void_p
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = ctypes.c_int
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.restype = ctypes.c_int

# Event/wait argtypes (64-bit handle safety)
kernel32.CreateEventW.restype = ctypes.wintypes.HANDLE
kernel32.OpenEventW.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.c_wchar_p]
kernel32.OpenEventW.restype = ctypes.wintypes.HANDLE
kernel32.WaitForSingleObject.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD]
kernel32.WaitForSingleObject.restype = ctypes.wintypes.DWORD
user32.MsgWaitForMultipleObjects.argtypes = [
    ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.HANDLE),
    ctypes.wintypes.BOOL, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
user32.MsgWaitForMultipleObjects.restype = ctypes.wintypes.DWORD


MB_OK = 0x0
MB_YESNO = 0x4
MB_ICONERROR = 0x10
MB_ICONQUESTION = 0x20
MB_ICONWARNING = 0x30

# MessageBox return values (button IDs)
IDOK = 1
IDYES = 6
IDNO = 7


def msgbox(text: str, title: str = "Natlink", flags: int = MB_OK) -> int:
    """Show a Windows message box. Returns the button ID (e.g. IDYES/IDNO)."""
    return user32.MessageBoxW(None, text, title, flags)


def is_dragon_running() -> bool:
    """Check if Dragon NaturallySpeaking is running.

    Uses FindWindowW for Dragon's main window class — ~0.01ms vs 49ms
    for the old subprocess-based tasklist approach.
    """
    return bool(user32.FindWindowW(DRAGON_CLS, None))


def get_clipboard() -> str:
    """Get clipboard text content."""
    CF_UNICODETEXT = 13
    if not user32.OpenClipboard(None):
        log.debug("get_clipboard: OpenClipboard failed")
        return ""
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            return ""
        try:
            # Read as null-terminated wchar_t string — ctypes.wstring_at
            # stops at the first null terminator, safe even if GlobalSize
            # returns 0 (some clipboard implementations don't support it).
            result = ctypes.wstring_at(ptr)
        except Exception:
            result = ""
        finally:
            kernel32.GlobalUnlock(handle)
        return result
    finally:
        user32.CloseClipboard()


def get_cursor_pos() -> Tuple[int, int]:
    """Get mouse cursor position.

    Matches C++ CDragonCode::getCursorPos — raises on failure.
    """
    pt = ctypes.wintypes.POINT()
    if not user32.GetCursorPos(ctypes.byref(pt)):
        raise OSError("Windows' GetCursorPos call failed "
                       "(calling getCursorPos)")
    return (pt.x, pt.y)


def get_screen_size() -> Tuple[int, int]:
    """Get usable screen dimensions (excluding taskbar).

    Matches C++ CDragonCode::getScreenSize which uses
    SM_CXFULLSCREEN / SM_CYFULLSCREEN (work area size).
    """
    SM_CXFULLSCREEN = 16
    SM_CYFULLSCREEN = 17
    w = user32.GetSystemMetrics(SM_CXFULLSCREEN)
    h = user32.GetSystemMetrics(SM_CYFULLSCREEN)
    return (w, h)


def get_current_module() -> Tuple[str, str, int]:
    """Get foreground window info: (module_path, window_title, hwnd)."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ("", "", 0)

    # Window title
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buf, 512)
    title = buf.value

    # Process ID -> module path
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    module_path = ""
    if pid.value:
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        hproc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                     False, pid.value)
        if hproc:
            try:
                psapi = ctypes.windll.psapi
                path_buf = ctypes.create_unicode_buffer(512)
                psapi.GetModuleFileNameExW(hproc, None, path_buf, 512)
                module_path = path_buf.value
            except Exception:
                log.debug("get_current_module: failed to get module path "
                          "for pid %d", pid.value, exc_info=True)
            finally:
                kernel32.CloseHandle(hproc)

    return (module_path, title, hwnd)
