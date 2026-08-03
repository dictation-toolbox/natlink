"""_helpers.py - Shared Win32 helpers for natlink tests.

Consolidated from conftest.py and test_integration.py to avoid
duplication and work around conftest import shadowing issues.

natlink_com connects directly to Dragon via COM (no proxy32.exe).
"""

import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time


# ---------------------------------------------------------------------------
# Win32 user32 setup
# ---------------------------------------------------------------------------

_user32 = ctypes.windll.user32

# 64-bit Python needs explicit argtypes/restype for HANDLE-returning APIs
_user32.FindWindowW.argtypes = [wt.LPCWSTR, wt.LPCWSTR]
_user32.FindWindowW.restype = wt.HWND
_user32.FindWindowExW.argtypes = [wt.HWND, wt.HWND, wt.LPCWSTR, wt.LPCWSTR]
_user32.FindWindowExW.restype = wt.HWND
_user32.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
_user32.SendMessageW.restype = ctypes.c_ssize_t
_user32.SetForegroundWindow.argtypes = [wt.HWND]
_user32.SetForegroundWindow.restype = wt.BOOL
_user32.GetForegroundWindow.argtypes = []
_user32.GetForegroundWindow.restype = wt.HWND
_user32.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
_user32.PostMessageW.restype = wt.BOOL
_user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
_user32.ShowWindow.restype = wt.BOOL
_user32.keybd_event.argtypes = [wt.BYTE, wt.BYTE, wt.DWORD,
                                ctypes.POINTER(wt.ULONG)]
_user32.keybd_event.restype = None

# SendInput types
class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wt.LONG),
        ("dy", wt.LONG),
        ("mouseData", wt.DWORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wt.ULONG)),
    ]

class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wt.WORD),
        ("wScan", wt.WORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wt.ULONG)),
    ]

class _INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]
    _fields_ = [("type", wt.DWORD), ("u", _U)]

# SendInput argtypes set per-call to avoid ctypes type-identity issues
_INPUT_KEYBOARD = 1
_KEYEVENTF_UNICODE = 0x0004
_KEYEVENTF_KEYUP = 0x0002


# ---------------------------------------------------------------------------
# Win32 constants
# ---------------------------------------------------------------------------

WM_APP_FOCUS_EDIT = 0x8001  # matches _editwin_helper.py


# ---------------------------------------------------------------------------
# Edit-window helpers
# ---------------------------------------------------------------------------

_EDITWIN_HELPER = os.path.join(os.path.dirname(__file__), "_editwin_helper.py")


def launch_editwin():
    """Launch the EDIT-window helper process, return (proc, main_hwnd, edit_hwnd)."""
    proc = subprocess.Popen(
        [sys.executable, _EDITWIN_HELPER],
        stdout=subprocess.PIPE,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    line = proc.stdout.readline().decode().strip()
    assert line.startswith("HWND "), f"Unexpected helper output: {line!r}"
    parts = line.split()
    return proc, int(parts[1]), int(parts[2])


def dismiss_dictation_box():
    """Close Dragon's Dictation Box if it's open (steals focus from tests).

    Dragon opens a Dictation Box when it doesn't recognize the foreground
    window as a supported text control.  We search by window title since
    the class name varies between Dragon versions.
    """
    _user32.EnumWindows.argtypes = [
        ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM), wt.LPARAM]
    _user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
    _user32.GetWindowTextW.restype = ctypes.c_int
    _user32.IsWindowVisible.argtypes = [wt.HWND]
    _user32.IsWindowVisible.restype = wt.BOOL

    found = []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def _cb(hwnd, lp):
        if _user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            _user32.GetWindowTextW(hwnd, buf, 256)
            if "dictation box" in buf.value.lower():
                found.append(hwnd)
        return True
    _user32.EnumWindows(_cb, 0)
    for hwnd in found:
        _user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    if found:
        time.sleep(0.3)


def focus_window(hwnd, timeout=3.0):
    """Bring *hwnd* to the foreground.  Raises on failure.

    Uses a brief ALT keypress to bypass Win11's foreground lock —
    Windows allows SetForegroundWindow from any process that has
    recently received keyboard input.
    """
    VK_MENU = 0x12
    KEYEVENTF_KEYUP = 0x0002
    _k32 = ctypes.windll.kernel32
    our_tid = _k32.GetCurrentThreadId()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        fg = _user32.GetForegroundWindow()
        if fg == hwnd:
            return
        # Simulate ALT press/release — unlocks SetForegroundWindow.
        _user32.keybd_event(VK_MENU, 0, 0, None)
        _user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, None)
        # Attach to the foreground thread's input queue so
        # SetForegroundWindow is allowed by Windows.
        fg_tid = _user32.GetWindowThreadProcessId(fg, None)
        attached = False
        if fg_tid and fg_tid != our_tid:
            attached = bool(_user32.AttachThreadInput(our_tid, fg_tid, True))
        _user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        _user32.BringWindowToTop(hwnd)
        _user32.SetForegroundWindow(hwnd)
        if attached:
            _user32.AttachThreadInput(our_tid, fg_tid, False)
        if _user32.GetForegroundWindow() == hwnd:
            return
        time.sleep(0.05)
    raise RuntimeError(
        f"Could not bring window {hwnd} to foreground within {timeout}s")


def get_edit_text(edit_hwnd):
    """Read all text from an EDIT control via WM_GETTEXT."""
    length = _user32.SendMessageW(edit_hwnd, 0x000E, 0, 0)  # WM_GETTEXTLENGTH
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    _user32.SendMessageW(edit_hwnd, 0x000D, length + 1,  # WM_GETTEXT
                         ctypes.addressof(buf))
    return buf.value


def wait_for_edit_text(edit_hwnd, predicate, timeout=2.0):
    """Poll the Edit control until *predicate(text)* is true or timeout.

    SendInput is async — the target thread may not have processed all
    input-queue messages by the time the calling thread reads back.
    There is no Win32 API to wait on another thread's input queue, so
    polling is the only deterministic approach.
    """
    deadline = time.monotonic() + timeout
    text = ""
    while time.monotonic() < deadline:
        text = get_edit_text(edit_hwnd)
        if predicate(text):
            return text
        time.sleep(0.05)
    return text  # return last value so the caller can use it in assertions


def clear_edit(edit_hwnd):
    """Clear an EDIT control via WM_SETTEXT."""
    empty = ctypes.create_unicode_buffer(1)
    _user32.SendMessageW(edit_hwnd, 0x000C, 0,  # WM_SETTEXT
                         ctypes.addressof(empty))


def get_edit_selection(edit_hwnd):
    """Return (start, end) character indices of current selection in Edit."""
    start = wt.DWORD()
    end = wt.DWORD()
    _user32.SendMessageW(edit_hwnd, 0x00B0,  # EM_GETSEL
                         ctypes.addressof(start), ctypes.addressof(end))
    return start.value, end.value


def send_keys(text):
    """Type *text* into the focused window via SendInput (Unicode)."""
    inputs = []
    for ch in text:
        for flags in (0, _KEYEVENTF_KEYUP):
            inp = _INPUT(type=_INPUT_KEYBOARD)
            inp.u.ki.wScan = ord(ch)
            inp.u.ki.dwFlags = _KEYEVENTF_UNICODE | flags
            inputs.append(inp)
    arr = (_INPUT * len(inputs))(*inputs)
    _fn = _user32.SendInput
    _fn.restype = wt.UINT
    sent = _fn(len(inputs), ctypes.cast(arr, ctypes.c_void_p), ctypes.sizeof(_INPUT))
    assert sent == len(inputs), \
        f"SendInput: expected {len(inputs)} events, sent {sent}"


def compile_grammar(spec):
    """Compile a grammar spec string to binary."""
    from natlink_com.grammar_compiler import compile_grammar as _compile
    return _compile(spec)


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def disconnect_session_client():
    """Disconnect the session-scoped natlink_compat client.

    After these tests finish, the ``_ensure_connected`` autouse fixture
    in conftest.py will reconnect for subsequent online tests.
    """
    from natlink_compat._state import _state
    if _state.connected:
        import natlink_compat as natlink
        try:
            natlink.natDisconnect()
        except Exception:
            _state.reset()


def do_mimic(words, retries=None, pause=None):
    """Mimic *words* via recognitionMimic.

    recognitionMimic works regardless of mic state — no need to
    toggle the mic on first.
    """
    import natlink_compat as natlink
    natlink.recognitionMimic(words)


def compile_select_grammar(select_words=None, through_word="through"):
    """Build a select grammar binary (DGNSRHDRTYPE_SELECT = 10).

    Select grammars recognize "<verb> <text> [through <text>]" where
    <verb> is one of *select_words* and <text> is drawn from the buffer
    set via GramObj.setSelectText.
    """
    import struct

    def pack_chunk(chunk_type, words):
        entries = []
        total = 0
        for word in words:
            encoded = word.encode("latin-1")
            padded = (len(encoded) + 4) & 0xFFFC
            entries.append(struct.pack("LL%ds" % padded, padded + 8, 0, encoded))
            total += padded + 8
        return struct.pack("LL", chunk_type, total) + b"".join(entries)

    if select_words is None:
        select_words = ["select"]
    parts = [struct.pack("LL", 10, 0)]  # SRHEADER: type=10, flags=0
    parts.append(pack_chunk(0x1017, select_words))
    if through_word:
        parts.append(pack_chunk(0x1018, [through_word]))
    return b"".join(parts)


def extract_words(callback_words):
    """Normalize callback word data to a list of lowercase strings.

    The results callback receives either a list of strings or a list of
    (word, ruleNumber) tuples depending on the grammar type.
    """
    return [
        w[0].lower() if isinstance(w, tuple) else w.lower()
        for w in callback_words
    ]
