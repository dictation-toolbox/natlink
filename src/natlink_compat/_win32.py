"""Shared Win32 definitions — canonical DLL handles and GUI constants.

All natlink modules should import user32/kernel32/gdi32/shell32 from here
instead of calling ctypes.windll directly.  Centralizes argtypes declarations.
"""

import ctypes
import ctypes.wintypes as wt
from ctypes import c_ulong, c_ushort, c_ubyte

user32 = ctypes.windll.user32
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
gdi32 = ctypes.windll.gdi32
shell32 = ctypes.windll.shell32

DRAGON_CLS = "DgnBarMainWindowCls"

# Common messages
WM_USER = 0x0400
WM_COMMAND = 0x0111
WM_CLOSE = 0x0010
WM_DESTROY = 0x0002
WM_MOVE = 0x0003
WM_SIZE = 0x0005
WM_TIMER = 0x0113
WM_SETTEXT = 0x000C
WM_SETFONT = 0x0030

# Window styles
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_VSCROLL = 0x00200000

# Show window
SW_SHOW = 5
SW_HIDE = 0

# LRESULT is LONG_PTR — c_longlong on 64-bit Windows
LRESULT = ctypes.c_longlong

WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, ctypes.c_uint,
                              wt.WPARAM, wt.LPARAM)

user32.DefWindowProcW.argtypes = [wt.HWND, ctypes.c_uint, wt.WPARAM, wt.LPARAM]
user32.DefWindowProcW.restype = LRESULT


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.UINT), ("style", wt.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
        ("hInstance", wt.HINSTANCE), ("hIcon", wt.HICON),
        ("hCursor", wt.HANDLE), ("hbrBackground", wt.HANDLE),
        ("lpszMenuName", wt.LPCWSTR), ("lpszClassName", wt.LPCWSTR),
        ("hIconSm", wt.HICON),
    ]


class GUID(ctypes.Structure):
    """Raw GUID struct for Win32 APIs (Shell_NotifyIconW etc.)."""
    _fields_ = [
        ("Data1", c_ulong), ("Data2", c_ushort), ("Data3", c_ushort),
        ("Data4", c_ubyte * 8),
    ]
    def __init__(self, d1=0, d2=0, d3=0, d4=None):
        super().__init__()
        self.Data1, self.Data2, self.Data3 = d1, d2, d3
        if d4:
            for i, b in enumerate(d4):
                self.Data4[i] = b
