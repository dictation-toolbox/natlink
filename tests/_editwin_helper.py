"""Tiny Win32 Edit control window for integration testing.

Creates a classic Win32 window with an EDIT child control and prints
'HWND <main> <edit>' to stdout.  Provides a lightweight, self-contained
target for Dragon dictation, Select-and-Say, and keystroke tests.

Usage:
    proc = subprocess.Popen([sys.executable, __file__], stdout=subprocess.PIPE)
    line = proc.stdout.readline().decode().strip()
    main_hwnd, edit_hwnd = (int(x) for x in line.split()[1:])
"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Prototypes
user32.RegisterClassW.restype = wt.ATOM
user32.CreateWindowExW.argtypes = [
    wt.DWORD, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wt.HWND, wt.HMENU, wt.HINSTANCE, wt.LPVOID,
]
user32.CreateWindowExW.restype = wt.HWND
user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_long
user32.SetFocus.argtypes = [wt.HWND]
user32.SetFocus.restype = wt.HWND
user32.AllowSetForegroundWindow.argtypes = [wt.DWORD]
user32.AllowSetForegroundWindow.restype = wt.BOOL

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

WM_DESTROY = 0x0002
WM_ACTIVATE = 0x0006
WM_APP = 0x8000
WM_APP_FOCUS_EDIT = WM_APP + 1   # wParam=1: focus EDIT, wParam=0: focus main
ASFW_ANY = 0xFFFFFFFF
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
ES_MULTILINE = 0x0004
ES_AUTOVSCROLL = 0x0040


_edit_hwnd = [0]  # mutable ref for WM_ACTIVATE handler


def _wnd_proc(hwnd, msg, wp, lp):
    if msg == WM_ACTIVATE:
        if (wp & 0xFFFF) != 0 and _edit_hwnd[0]:
            user32.SetFocus(_edit_hwnd[0])
            # Grant all processes foreground rights so Dragon's
            # JournalPlayback hook (playString) can be installed.
            user32.AllowSetForegroundWindow(ASFW_ANY)
        return 0
    if msg == WM_APP_FOCUS_EDIT:
        # Toggle keyboard focus: wParam=1 → EDIT child, wParam=0 → main window
        user32.SetFocus(_edit_hwnd[0] if wp else hwnd)
        return 0
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wp, lp)


_wndproc_ref = WNDPROC(_wnd_proc)  # prevent GC


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wt.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wt.HINSTANCE),
        ("hIcon", wt.HICON),
        ("hCursor", wt.HANDLE),
        ("hbrBackground", wt.HBRUSH),
        ("lpszMenuName", wt.LPCWSTR),
        ("lpszClassName", wt.LPCWSTR),
    ]


def main():
    hInst = kernel32.GetModuleHandleW(None)

    wc = WNDCLASSW()
    wc.lpfnWndProc = _wndproc_ref
    wc.hInstance = hInst
    wc.lpszClassName = "NatlinkTestEdit"
    wc.hbrBackground = user32.GetSysColorBrush(5)  # COLOR_WINDOW
    user32.RegisterClassW(ctypes.byref(wc))

    main_hwnd = user32.CreateWindowExW(
        0, "NatlinkTestEdit", "NatlinkTestEdit",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        100, 100, 500, 400,
        None, None, hInst, None,
    )
    edit_hwnd = user32.CreateWindowExW(
        0, "EDIT", "",
        WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_AUTOVSCROLL,
        0, 0, 500, 400,
        main_hwnd, None, hInst, None,
    )
    _edit_hwnd[0] = edit_hwnd
    user32.SetFocus(edit_hwnd)

    sys.stdout.write(f"HWND {main_hwnd} {edit_hwnd}\n")
    sys.stdout.flush()

    msg = wt.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


if __name__ == "__main__":
    main()
