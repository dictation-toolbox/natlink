"""User Interface Privilege Isolation checks for keystroke injection.

Windows refuses input from a process at a lower integrity level to a window
owned by a higher one. Dragon makes this a live concern rather than a corner
case: it splits itself across integrity levels, running the engine at medium
but DragonBar and the UIA servers elevated. Measured on Dragon 13:

    dragonbar.exe        HIGH
    dgnuiasvr.exe        HIGH
    dgnuiasvr_x64.exe    HIGH
    natspeak.exe         MEDIUM     <- the COM server, so COM itself is fine
    python.exe (natlink) MEDIUM

The failure is silent from the caller's side. With DragonBar foreground,
SendInput reported all four events accepted and GetLastError zero while the
intended window received nothing -- so checking the return value alone does
not detect it. Comparing integrity levels before injecting does.

Nothing here can make the injection work; a medium-integrity process cannot
direct input at an elevated window. Running natlink elevated is the only
remedy, and that is the user's decision. This exists so the situation is
diagnosable instead of looking like keystrokes that vanished.
"""

import ctypes
import ctypes.wintypes as wt
import logging

log = logging.getLogger("natlink.com.uipi")

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_TOKEN_QUERY = 0x0008
_TokenIntegrityLevel = 25

# Mandatory label RIDs, ordered. Higher wins.
UNTRUSTED = 0x0000
LOW = 0x1000
MEDIUM = 0x2000
HIGH = 0x3000
SYSTEM = 0x4000

_NAMES = {UNTRUSTED: "UNTRUSTED", LOW: "LOW", MEDIUM: "MEDIUM",
          HIGH: "HIGH", SYSTEM: "SYSTEM"}

_own_level = None
_warned_for = set()   # foreground hwnds already reported, to bound log volume


def level_name(rid):
    return _NAMES.get(rid, f"0x{rid:04X}" if rid is not None else "unknown")


def _level_from_token(handle):
    """Integrity RID from an already-open process handle, or None."""
    token = wt.HANDLE()
    if not advapi32.OpenProcessToken(wt.HANDLE(handle), _TOKEN_QUERY,
                                     ctypes.byref(token)):
        return None
    try:
        size = wt.DWORD()
        advapi32.GetTokenInformation(token, _TokenIntegrityLevel, None, 0,
                                     ctypes.byref(size))
        if not size.value:
            return None
        buf = ctypes.create_string_buffer(size.value)
        if not advapi32.GetTokenInformation(token, _TokenIntegrityLevel, buf,
                                            size, ctypes.byref(size)):
            return None
        # TOKEN_MANDATORY_LABEL starts with SID_AND_ATTRIBUTES.Sid.
        psid = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
        advapi32.GetSidSubAuthorityCount.restype = ctypes.POINTER(ctypes.c_ubyte)
        count = advapi32.GetSidSubAuthorityCount(ctypes.c_void_p(psid))[0]
        advapi32.GetSidSubAuthority.restype = ctypes.POINTER(wt.DWORD)
        return advapi32.GetSidSubAuthority(ctypes.c_void_p(psid), count - 1)[0]
    finally:
        kernel32.CloseHandle(token)


def process_level(pid=None):
    """Integrity RID of ``pid``, or of this process when pid is None."""
    try:
        if pid is None:
            return _level_from_token(kernel32.GetCurrentProcess())
        kernel32.OpenProcess.restype = wt.HANDLE
        handle = kernel32.OpenProcess(
            _PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            return _level_from_token(handle)
        finally:
            kernel32.CloseHandle(wt.HANDLE(handle))
    except OSError:
        return None


def own_level():
    """This process's integrity level. Cached: it cannot change at runtime."""
    global _own_level
    if _own_level is None:
        _own_level = process_level()
    return _own_level


def foreground_blocks_input():
    """Describe the foreground window if it outranks us, else None.

    Returns (title, level_rid) so callers can report which window is
    intercepting, rather than reporting only that something went wrong.
    """
    try:
        user32.GetForegroundWindow.restype = wt.HWND
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return None

        theirs = process_level(pid.value)
        ours = own_level()
        # A level we cannot read is not evidence of a problem: querying a
        # higher-integrity process can itself be denied, but so can querying
        # for other reasons. Only report a comparison we actually made.
        if theirs is None or ours is None or theirs <= ours:
            return None

        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title, 256)
        return title.value or "<untitled>", theirs
    except OSError:
        return None


def warn_if_foreground_outranks_us(operation):
    """Log once per foreground window that will swallow injected input.

    Returns True if a mismatch was found, so callers can record that the
    keystrokes they were asked to send may not have arrived.
    """
    found = foreground_blocks_input()
    if found is None:
        return False
    title, theirs = found
    key = (title, theirs)
    if key not in _warned_for:
        _warned_for.add(key)
        log.warning(
            "%s: foreground window %r runs at %s integrity but natlink runs "
            "at %s. Windows blocks input across that boundary, so these "
            "keystrokes may not reach it. SendInput still reports success. "
            "Run natlink elevated if you need to send keys to elevated "
            "applications.",
            operation, title, level_name(theirs), level_name(own_level()))
    return True
