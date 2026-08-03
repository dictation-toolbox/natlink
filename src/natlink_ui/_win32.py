"""Win32 definitions for natlink_ui — DLL handles and GUI constants."""

import ctypes
import ctypes.wintypes as wt
from ctypes import c_ulong, c_ushort, c_ubyte

user32 = ctypes.windll.user32
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
gdi32 = ctypes.windll.gdi32
shell32 = ctypes.windll.shell32

WM_USER = 0x0400
WM_COMMAND = 0x0111
WM_CLOSE = 0x0010
WM_DESTROY = 0x0002
WM_MOVE = 0x0003
WM_SIZE = 0x0005
WM_TIMER = 0x0113
WM_SETTEXT = 0x000C
WM_SETFONT = 0x0030

WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_VSCROLL = 0x00200000

SW_SHOW = 5
SW_HIDE = 0

LRESULT = ctypes.c_ssize_t

WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, ctypes.c_uint,
                              wt.WPARAM, wt.LPARAM)

user32.DefWindowProcW.argtypes = [wt.HWND, ctypes.c_uint, wt.WPARAM, wt.LPARAM]
user32.DefWindowProcW.restype = LRESULT

# Declare every signature natlink_ui relies on. Without these, ctypes marshals
# handles as C int: CreateWindowExW truncates the returned HWND and
# PostMessageW truncates hwnd/wparam/lparam on 64-bit. Declaring them here
# rather than inheriting whatever another package left in the shared
# ctypes.windll cache keeps correctness independent of import order.
user32.RegisterClassExW.restype = wt.ATOM
user32.CreateWindowExW.restype = wt.HWND
user32.DestroyWindow.argtypes = [wt.HWND]
user32.PostMessageW.argtypes = [wt.HWND, ctypes.c_uint, wt.WPARAM, wt.LPARAM]
user32.PostMessageW.restype = wt.BOOL


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


from natlink_compat import msgbox, MB_ICONERROR  # noqa: F401
