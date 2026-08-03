"""Unified natlink window — tray icon + output surface in one HWND.

One window owns:
  - Shell tray icon (status + context menu)
  - RichEdit child control (displayText output)
  - Geometry persistence
  - Its own UI thread (message pump for the HWND)

Click tray → toggle window visibility.
Right-click tray → context menu.
Close button → hide (not destroy). Tray stays.
"""

import collections
import concurrent.futures
import ctypes
import ctypes.wintypes as wt
import logging
import queue
import threading

from ._win32 import (
    GUID,
    user32, kernel32, gdi32, shell32,
    WNDPROC, WNDCLASSEXW,
    WM_USER, WM_COMMAND, WM_SETTEXT, WM_CLOSE, WM_DESTROY,
    WM_MOVE, WM_SIZE, WM_TIMER, WM_SETFONT,
    WS_OVERLAPPEDWINDOW, WS_CHILD, WS_VISIBLE, WS_VSCROLL,
    SW_SHOW, SW_HIDE,
)
from . import _dpi

log = logging.getLogger("natlink.ui.window")


# ---------------------------------------------------------------------------
# UI thread — owns the HWND message pump
# ---------------------------------------------------------------------------

WM_UI_CREATE = WM_USER + 500
WM_UI_SHUTDOWN = WM_USER + 501

_thread = None
_thread_id = 0
_ready = threading.Event()
_create_queue = queue.SimpleQueue()

_worker_pool = concurrent.futures.ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="natlink-ui-worker")

import atexit as _atexit
_atexit.register(_worker_pool.shutdown, wait=False)


def _ensure_ui_thread():
    """Start the UI thread if not already running."""
    global _thread, _thread_id
    if _thread is not None and _thread.is_alive():
        return _thread_id
    _thread_id = 0
    _ready.clear()
    _thread = threading.Thread(target=_ui_thread_run, daemon=True, name="natlink-ui")
    _thread.start()
    if not _ready.wait(timeout=5):
        log.error("UI thread did not become ready within 5s")
        raise RuntimeError("UI thread failed to start")
    if not _thread_id:
        raise RuntimeError("UI thread started but _thread_id is still 0")
    return _thread_id


def _run_on_ui_thread(fn, *args):
    """Schedule fn(*args) on the UI thread. Blocks until complete."""
    if threading.current_thread() is _thread:
        return fn(*args)
    done = threading.Event()
    result = [None, None]

    def _wrapper():
        try:
            result[0] = fn(*args)
        except Exception as e:
            result[1] = e
        finally:
            done.set()

    _create_queue.put(_wrapper)
    user32.PostThreadMessageW(_thread_id, WM_UI_CREATE, 0, 0)
    done.wait(timeout=10)
    if not done.is_set():
        log.error("_run_on_ui_thread: UI thread did not respond within 10s")
        raise TimeoutError("UI thread did not respond within 10s")
    if result[1] is not None:
        raise result[1]
    return result[0]


def _post_to_ui(msg, hwnd, wparam=0, lparam=0):
    """Post a message to a window on the UI thread (non-blocking)."""
    if hwnd:
        user32.PostMessageW(hwnd, msg, wparam, lparam)


def _dispatch_async(fn, *args):
    """Run fn(*args) on a worker thread (for blocking menu callbacks)."""
    _worker_pool.submit(_safe_call, fn, args)


def _safe_call(fn, args):
    try:
        fn(*args)
    except Exception:
        log.debug("UI worker callback error", exc_info=True)


def _ui_thread_run():
    global _thread_id
    _thread_id = kernel32.GetCurrentThreadId()

    # Before the first window: Windows locks process awareness once one exists.
    log.debug("DPI awareness: %s", _dpi.set_process_dpi_aware())

    import faulthandler as _fh
    try:
        _fh.disable()
    except Exception:
        pass

    _ole32 = ctypes.windll.ole32
    hr = _ole32.OleInitialize(None)
    if hr < 0:
        log.debug("OleInitialize returned 0x%08X", hr & 0xFFFFFFFF)

    msg = wt.MSG()
    user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
    _ready.set()

    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == WM_UI_CREATE:
            while not _create_queue.empty():
                try:
                    _create_queue.get_nowait()()
                except queue.Empty:
                    break
        elif msg.message == WM_UI_SHUTDOWN:
            user32.PostQuitMessage(0)
            continue
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    _ole32.OleUninitialize()
    _thread_id = 0


# ---------------------------------------------------------------------------
# Tray icon constants
# ---------------------------------------------------------------------------

WM_TRAYICON = WM_USER + 100
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205
NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIF_MESSAGE = 1
NIF_ICON = 2
NIF_TIP = 4
NIF_GUID = 0x20
NIF_SHOWTIP = 0x80
NOTIFYICON_VERSION_4 = 4
NIM_SETVERSION = 4
MF_STRING = 0
MF_SEPARATOR = 0x800
MF_POPUP = 0x10
MF_CHECKED = 0x08
MF_UNCHECKED = 0

_NATLINK_TRAY_GUID = GUID(
    0xA1B2C3D4, 0xE5F6, 0x7890,
    [0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90])


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.DWORD), ("hWnd", wt.HWND), ("uID", wt.UINT),
        ("uFlags", wt.UINT), ("uCallbackMessage", wt.UINT),
        ("hIcon", wt.HICON), ("szTip", wt.WCHAR * 128),
        ("dwState", wt.DWORD), ("dwStateMask", wt.DWORD),
        ("szInfo", wt.WCHAR * 256), ("uVersion", wt.UINT),
        ("szInfoTitle", wt.WCHAR * 64), ("dwInfoFlags", wt.DWORD),
        ("guidItem", GUID),
    ]


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", wt.BOOL), ("xHotspot", wt.DWORD), ("yHotspot", wt.DWORD),
        ("hbmMask", wt.HANDLE), ("hbmColor", wt.HANDLE),
    ]


# ---------------------------------------------------------------------------
# RichEdit constants
# ---------------------------------------------------------------------------

_RICHEDIT_CLASS = "RICHEDIT50W"
_richedit_loaded = False
_richedit_lock = threading.Lock()

ES_MULTILINE = 0x0004
ES_AUTOVSCROLL = 0x0040
ES_READONLY = 0x0800
ES_NOHIDESEL = 0x0100
WM_APPENDTEXT = WM_USER + 200
WM_CLEARTEXT = WM_USER + 201
WM_SHOWWINDOW = WM_USER + 202
WM_HIDEWINDOW = WM_USER + 203
WM_SETTOPMOST = WM_USER + 204
WM_UPDATE_TRAY = WM_USER + 205
WM_DESTROY_SAFE = WM_USER + 206
EM_SETSEL = 0x00B1
EM_REPLACESEL = 0x00C2
EM_SCROLLCARET = 0x00B7
EM_SETCHARFORMAT = WM_USER + 68
EM_SETBKGNDCOLOR = WM_USER + 67
SCF_SELECTION = 0x0001
CFM_COLOR = 0x40000000
CFM_BOLD = 0x00000001
CFE_BOLD = 0x00000001

_CLR_NORMAL = 0x00404040
_CLR_ERROR = 0x000000CC
_CLR_BACKGROUND = 0x00FFFFFF


class _CHARFORMAT2W(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.UINT), ("dwMask", wt.DWORD), ("dwEffects", wt.DWORD),
        ("yHeight", ctypes.c_long), ("yOffset", ctypes.c_long),
        ("crTextColor", wt.COLORREF), ("bCharSet", wt.BYTE),
        ("bPitchAndFamily", wt.BYTE), ("szFaceName", ctypes.c_wchar * 32),
        ("wWeight", wt.WORD), ("sSpacing", ctypes.c_short),
        ("crBackColor", wt.COLORREF), ("lcid", wt.DWORD),
        ("dwReserved", wt.DWORD), ("sStyle", ctypes.c_short),
        ("wKerning", wt.WORD), ("bUnderlineType", wt.BYTE),
        ("bAnimation", wt.BYTE), ("bRevAuthor", wt.BYTE),
        ("bUnderlineColor", wt.BYTE),
    ]


_proto_send_str = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, wt.HWND, ctypes.c_uint, wt.WPARAM, ctypes.c_wchar_p)
_send_msg_str = _proto_send_str(("SendMessageW", user32))

_proto_send_ptr = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, wt.HWND, ctypes.c_uint, wt.WPARAM, ctypes.c_void_p)
_send_msg_ptr = _proto_send_ptr(("SendMessageW", user32))


# ---------------------------------------------------------------------------
# Icon helpers
# ---------------------------------------------------------------------------

def _create_circle_icon(r, g, b, size=16):
    color = r | (g << 8) | (b << 16)
    hdc = user32.GetDC(None)
    hbmColor = gdi32.CreateCompatibleBitmap(hdc, size, size)
    hdcMem = gdi32.CreateCompatibleDC(hdc)
    hbmMask = None
    hdcMask = None
    try:
        oldBmpMem = gdi32.SelectObject(hdcMem, hbmColor)
        rect = wt.RECT(0, 0, size, size)
        bg = gdi32.CreateSolidBrush(0xF0F0F0)
        user32.FillRect(hdcMem, ctypes.byref(rect), bg)
        gdi32.DeleteObject(bg)
        brush = gdi32.CreateSolidBrush(color)
        pen = gdi32.CreatePen(0, 1, color >> 1 & 0x7F7F7F)
        oldBrush = gdi32.SelectObject(hdcMem, brush)
        oldPen = gdi32.SelectObject(hdcMem, pen)
        inset = max(1, round(size / 8))  # 2px at 16px, proportional above
        gdi32.Ellipse(hdcMem, inset, inset, size - inset, size - inset)
        gdi32.SelectObject(hdcMem, oldBrush)
        gdi32.SelectObject(hdcMem, oldPen)
        gdi32.DeleteObject(brush)
        gdi32.DeleteObject(pen)
        hbmMask = gdi32.CreateBitmap(size, size, 1, 1, None)
        hdcMask = gdi32.CreateCompatibleDC(hdc)
        oldBmpMask = gdi32.SelectObject(hdcMask, hbmMask)
        white = gdi32.CreateSolidBrush(0xFFFFFF)
        user32.FillRect(hdcMask, ctypes.byref(rect), white)
        gdi32.DeleteObject(white)
        black = gdi32.CreateSolidBrush(0)
        oldBrushMask = gdi32.SelectObject(hdcMask, black)
        gdi32.Ellipse(hdcMask, inset, inset, size - inset, size - inset)
        gdi32.SelectObject(hdcMask, oldBrushMask)
        gdi32.DeleteObject(black)
        gdi32.SelectObject(hdcMem, oldBmpMem)
        gdi32.SelectObject(hdcMask, oldBmpMask)
        gdi32.DeleteDC(hdcMem)
        hdcMem = None
        gdi32.DeleteDC(hdcMask)
        hdcMask = None
        user32.ReleaseDC(None, hdc)
        hdc = None
        ii = ICONINFO()
        ii.fIcon = True
        ii.hbmMask = hbmMask
        ii.hbmColor = hbmColor
        hIcon = user32.CreateIconIndirect(ctypes.byref(ii))
        if not hIcon:
            log.warning("CreateIconIndirect failed")
        return hIcon
    except Exception:
        log.warning("_create_circle_icon failed", exc_info=True)
        return 0
    finally:
        if hdcMem:
            gdi32.DeleteDC(hdcMem)
        if hdcMask:
            gdi32.DeleteDC(hdcMask)
        if hdc:
            user32.ReleaseDC(None, hdc)
        gdi32.DeleteObject(hbmColor)
        if hbmMask:
            gdi32.DeleteObject(hbmMask)


_ICON_CACHE = {}

def _get_icon(name):
    """Tray icon at the size Windows asks for, not a fixed 16px.

    SM_CXSMICON scales with DPI (24px at 150%), and the shell stretches
    anything smaller. Keyed by size too, so a DPI change builds a new icon
    rather than reusing the blurry one.
    """
    size = _dpi.small_icon_size()
    key = (name, size)
    if key not in _ICON_CACHE:
        colors = {"connected": (0, 180, 0), "disconnected": (180, 0, 0),
                  "error": (220, 180, 0)}
        rgb = colors.get(name, (128, 128, 128))
        _ICON_CACHE[key] = _create_circle_icon(*rgb, size=size)
    return _ICON_CACHE[key]


def _destroy_icon_cache():
    for hIcon in _ICON_CACHE.values():
        if hIcon:
            user32.DestroyIcon(hIcon)
    _ICON_CACHE.clear()


# ---------------------------------------------------------------------------
# Menu constants
# ---------------------------------------------------------------------------

_IDM_BASE = 2000


# ---------------------------------------------------------------------------
# NatlinkWindow — unified tray + output
# ---------------------------------------------------------------------------

class NatlinkWindow:
    """Single window combining tray icon and RichEdit output surface.

    Tray icon:
      - Shell_NotifyIconW bound to this HWND
      - Left-click toggles window visibility
      - Right-click shows context menu

    Output:
      - RichEdit50W child control fills the client area
      - Colored text (normal=gray, error=red)

    Geometry and topmost state are persisted to natlink_ui.ini.
    """

    _SAVE_TIMER_ID = 1

    def __init__(self, title="Natlink Messages", width=800, height=500,
                 load_config=None, save_config=None):
        # Must precede the geometry maths below: an unaware process is told
        # every monitor is 96 DPI, so scaling computed first would be a no-op.
        _dpi.set_process_dpi_aware()

        # Window state
        self._hwnd = None
        self._edit = None
        self._font = None
        self._cls_name = None
        self._hinstance = None
        self._wndproc_ref = None
        self._visible = False
        self._created = False
        self._save_pending = False
        self._load_config = load_config
        self._save_config = save_config
        self._title = title
        self._text_queue = collections.deque(maxlen=1000)
        self._charfmt = _CHARFORMAT2W()
        self._charfmt.cbSize = ctypes.sizeof(self._charfmt)

        # Tray state
        self._icon_added = False
        self._use_guid = True
        self._last_tray = (None, None)  # (tooltip, icon_name) for change detection
        # Latest-wins payload for WM_UPDATE_TRAY; writes are atomic in CPython.
        self._pending_tray = None
        self._menu_items = []
        self._menu_lock = threading.Lock()
        self._menu_callbacks = {}
        self._menu_id_max = _IDM_BASE

        # Load saved geometry / topmost (single config read).
        # Defaults are 96-DPI design sizes, so scale them for the display they
        # will open on. Saved values are already physical pixels and carry the
        # position that picks the monitor — rescaling those would compound.
        cfg = load_config() if load_config else None
        def_dpi = _dpi.dpi_for_point(100, 100)
        x, y, w, h = self._load_geometry(
            100, 100, _dpi.scale(width, def_dpi), _dpi.scale(height, def_dpi), cfg)
        self._x = x
        self._y = y
        self._width = w
        self._height = h
        self._topmost = self._load_topmost(cfg)

        # Create on UI thread
        _ensure_ui_thread()
        _run_on_ui_thread(self._create_window)

    # ------------------------------------------------------------------
    # Tray icon
    # ------------------------------------------------------------------

    def show_tray_icon(self, tooltip="Natlink", icon_name="disconnected"):
        if not self._hwnd:
            return
        # Latest-wins: coalesces bursty state changes. Dedup and Shell_NotifyIconW
        # run on the UI thread where the tray HWND lives.
        self._pending_tray = (tooltip, icon_name)
        _post_to_ui(WM_UPDATE_TRAY, self._hwnd)

    def _apply_pending_tray(self):
        pending = self._pending_tray
        if pending is None:
            return
        tooltip, icon_name = pending
        key = (tooltip, icon_name)
        if self._icon_added and key == self._last_tray:
            return
        if not self._icon_added:
            self._tray_notify(NIM_ADD, tooltip, icon_name)
        else:
            self._tray_notify(NIM_MODIFY, tooltip, icon_name)
        self._last_tray = key

    def update_tray_icon(self, tooltip=None, icon_name=None):
        if self._hwnd and self._icon_added:
            self._tray_notify(NIM_MODIFY, tooltip, icon_name)

    def hide_tray_icon(self):
        if self._hwnd and self._icon_added:
            nid = NOTIFYICONDATAW()
            nid.cbSize = ctypes.sizeof(nid)
            nid.hWnd = self._hwnd
            nid.uID = 1
            if self._use_guid:
                nid.uFlags = NIF_GUID
                nid.guidItem = _NATLINK_TRAY_GUID
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
            self._icon_added = False

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def add_menu_item(self, label, callback, check_fn=None):
        with self._menu_lock:
            self._menu_items.append((label, callback, check_fn))

    def add_separator(self):
        with self._menu_lock:
            self._menu_items.append(None)

    def add_submenu(self, label, items):
        with self._menu_lock:
            self._menu_items.append(("submenu", label, items))

    # ------------------------------------------------------------------
    # Output surface
    # ------------------------------------------------------------------

    def write(self, text: str, is_error: bool = False) -> None:
        hwnd = self._hwnd
        if not hwnd or not self._edit:
            return
        self._text_queue.append((text, is_error))
        _post_to_ui(WM_APPENDTEXT, hwnd)

    def clear(self) -> None:
        if self._hwnd:
            _post_to_ui(WM_CLEARTEXT, self._hwnd)

    # ------------------------------------------------------------------
    # Window visibility
    # ------------------------------------------------------------------

    @property
    def is_visible(self) -> bool:
        return self._visible

    def show(self) -> None:
        if self._hwnd:
            _post_to_ui(WM_SHOWWINDOW, self._hwnd)

    def hide(self) -> None:
        if self._hwnd:
            _post_to_ui(WM_HIDEWINDOW, self._hwnd)

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    @property
    def is_topmost(self) -> bool:
        return self._topmost

    def set_topmost(self, topmost: bool) -> None:
        self._topmost = topmost
        if self._hwnd:
            _post_to_ui(WM_SETTOPMOST, self._hwnd, int(topmost))
        if self._load_config and self._save_config:
            try:
                cfg = self._load_config()
                if not cfg.has_section("window"):
                    cfg.add_section("window")
                cfg.set("window", "always_on_top", str(topmost).lower())
                self._save_config(cfg)
            except Exception:
                log.debug("Failed to save topmost state", exc_info=True)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def destroy_safe(self):
        """Destroy from any thread — best-effort, non-blocking.

        If called off the UI thread, posts to the UI thread and returns
        immediately so main-thread shutdown is never blocked by a wedged
        UI thread. The UI thread is a daemon and dies with the process;
        destruction is best-effort.
        """
        if _thread is not None and threading.current_thread() is not _thread:
            if self._hwnd:
                _post_to_ui(WM_DESTROY_SAFE, self._hwnd)
            return
        self.destroy()

    def destroy(self):
        """Remove tray icon and destroy window. Must be called on UI thread."""
        self.hide_tray_icon()
        if self._hwnd:
            if self._save_pending:
                user32.KillTimer(self._hwnd, self._SAVE_TIMER_ID)
                self._save_pending = False
            self._save_geometry()
            user32.DestroyWindow(self._hwnd)
            self._hwnd = None
            self._edit = None
        if self._cls_name and self._hinstance:
            user32.UnregisterClassW(self._cls_name, self._hinstance)
            self._cls_name = None
        if self._font:
            gdi32.DeleteObject(self._font)
            self._font = None
        _destroy_icon_cache()

    # ------------------------------------------------------------------
    # Internals — tray
    # ------------------------------------------------------------------

    def _tray_notify(self, action, tooltip=None, icon_name=None):
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(nid)
        nid.hWnd = self._hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE
        nid.uCallbackMessage = WM_TRAYICON
        if self._use_guid:
            nid.uFlags |= NIF_GUID
            nid.guidItem = _NATLINK_TRAY_GUID
        if tooltip:
            nid.uFlags |= NIF_TIP | NIF_SHOWTIP
            nid.szTip = tooltip[:127]
        if icon_name:
            nid.uFlags |= NIF_ICON
            nid.hIcon = _get_icon(icon_name)
        ok = shell32.Shell_NotifyIconW(action, ctypes.byref(nid))
        if action == NIM_ADD:
            if not ok and self._use_guid:
                log.debug("Shell_NotifyIconW(NIM_ADD) with GUID failed, clearing stale entry")
                del_nid = NOTIFYICONDATAW()
                del_nid.cbSize = ctypes.sizeof(del_nid)
                del_nid.uFlags = NIF_GUID
                del_nid.guidItem = _NATLINK_TRAY_GUID
                shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(del_nid))
                ok = shell32.Shell_NotifyIconW(action, ctypes.byref(nid))
            if not ok and self._use_guid:
                log.debug("Shell_NotifyIconW(NIM_ADD) GUID retry failed, falling back")
                self._use_guid = False
                nid.uFlags &= ~NIF_GUID
                nid.guidItem = GUID()
                ok = shell32.Shell_NotifyIconW(action, ctypes.byref(nid))
            self._icon_added = bool(ok)
            if ok:
                ver = NOTIFYICONDATAW()
                ver.cbSize = ctypes.sizeof(ver)
                ver.hWnd = self._hwnd
                ver.uID = 1
                if self._use_guid:
                    ver.uFlags = NIF_GUID
                    ver.guidItem = _NATLINK_TRAY_GUID
                ver.uVersion = NOTIFYICON_VERSION_4
                shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(ver))
            else:
                log.error("Shell_NotifyIconW(NIM_ADD) failed")

    def _build_menu(self, items, callbacks, idm):
        menu = user32.CreatePopupMenu()
        for item in items:
            if item is None:
                user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            elif isinstance(item, tuple) and item[0] == "submenu":
                _, label, subitems = item
                # subitems may be a callable so dynamic submenus (loaders,
                # log categories) reflect current state on each right-click.
                if callable(subitems):
                    subitems = subitems()
                sub, idm = self._build_menu(subitems, callbacks, idm)
                user32.AppendMenuW(menu, MF_POPUP, sub, label)
            else:
                label, cb, check_fn = item
                display = label() if callable(label) else label
                flags = MF_CHECKED if check_fn and check_fn() else MF_STRING
                user32.AppendMenuW(menu, flags, idm, display)
                callbacks[idm] = cb
                idm += 1
        return menu, idm

    def _show_menu(self):
        callbacks = {}
        with self._menu_lock:
            items = list(self._menu_items)
        # ID counter resets to _IDM_BASE on every build so the command-ID
        # space stays bounded regardless of menu size.
        menu, next_id = self._build_menu(items, callbacks, _IDM_BASE)
        self._menu_id_max = next_id
        self._menu_callbacks = callbacks
        pt = wt.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        user32.SetForegroundWindow(self._hwnd)
        user32.TrackPopupMenu(menu, 0, pt.x, pt.y, 0, self._hwnd, None)
        # Canonical Win32 fix: post WM_NULL so the menu dismisses on the
        # first outside-click (see KB135788).
        user32.PostMessageW(self._hwnd, 0x0000, 0, 0)  # WM_NULL
        user32.DestroyMenu(menu)

    # ------------------------------------------------------------------
    # Internals — output
    # ------------------------------------------------------------------

    def _set_text_color(self, color, bold=False):
        cf = self._charfmt
        cf.dwMask = CFM_COLOR | CFM_BOLD
        cf.crTextColor = color
        cf.dwEffects = CFE_BOLD if bold else 0
        _send_msg_ptr(self._edit, EM_SETCHARFORMAT, SCF_SELECTION, ctypes.byref(cf))

    def _append_text(self, text, is_error=False):
        if not self._edit:
            return
        if not is_error and "Traceback (most recent" in text:
            is_error = True
        user32.SendMessageW(self._edit, EM_SETSEL, -1, -1)
        color = _CLR_ERROR if is_error else _CLR_NORMAL
        self._set_text_color(color, bold=is_error)
        if not text.endswith("\n"):
            text += "\n"
        _send_msg_str(self._edit, EM_REPLACESEL, 0, text)
        user32.SendMessageW(self._edit, EM_SCROLLCARET, 0, 0)

    def _apply_topmost(self):
        if self._hwnd:
            user32.SetWindowPos(
                self._hwnd, wt.HWND(-1 if self._topmost else -2),
                0, 0, 0, 0, 0x0003)  # SWP_NOSIZE | SWP_NOMOVE

    def _apply_font(self):
        """(Re)create the RichEdit font at the current monitor's DPI.

        Called on creation and again on WM_DPICHANGED — the font is sized in
        physical pixels, so it does not follow the window across monitors on
        its own. The old handle is freed after the control has switched to
        the new one; deleting a font still selected into a control leaks it.
        """
        if not self._edit:
            return
        font_size = self._load_font_size()
        dpi = _dpi.dpi_for_window(self._hwnd)
        previous = self._font
        self._font = gdi32.CreateFontW(
            _dpi.scale(font_size, dpi), 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0,
            0x31, "Consolas")
        if not self._font:
            self._font = previous
            return
        user32.SendMessageW(self._edit, WM_SETFONT, self._font, 1)
        if previous:
            gdi32.DeleteObject(previous)

    # ------------------------------------------------------------------
    # Internals — geometry persistence
    # ------------------------------------------------------------------

    def _load_topmost(self, cfg=None):
        if cfg is None and self._load_config is not None:
            try:
                cfg = self._load_config()
            except Exception:
                return False
        if cfg is None:
            return False
        try:
            return cfg.getboolean("window", "always_on_top", fallback=False)
        except Exception:
            return False

    def _load_font_size(self, default=18, cfg=None):
        if cfg is None and self._load_config is not None:
            try:
                cfg = self._load_config()
            except Exception:
                return default
        if cfg is None:
            return default
        try:
            return cfg.getint("window", "font_size", fallback=default)
        except Exception:
            return default

    def _load_geometry(self, def_x, def_y, def_w, def_h, cfg=None):
        if cfg is None and self._load_config is not None:
            try:
                cfg = self._load_config()
            except Exception:
                return def_x, def_y, def_w, def_h
        if cfg is None:
            return def_x, def_y, def_w, def_h
        try:
            x = cfg.getint("window", "x", fallback=def_x)
            y = cfg.getint("window", "y", fallback=def_y)
            w = cfg.getint("window", "width", fallback=def_w)
            h = cfg.getint("window", "height", fallback=def_h)
            if x < -10000 or y < -10000 or x > 30000 or y > 30000 or w < 100 or h < 50:
                return def_x, def_y, def_w, def_h
            return x, y, max(w, 200), max(h, 100)
        except Exception:
            return def_x, def_y, def_w, def_h

    def _schedule_save(self):
        if self._hwnd:
            user32.SetTimer(self._hwnd, self._SAVE_TIMER_ID, 500, None)
            self._save_pending = True

    def _save_geometry(self):
        if not self._hwnd or self._load_config is None or self._save_config is None:
            return
        if user32.IsIconic(self._hwnd):
            return
        try:
            rect = wt.RECT()
            user32.GetWindowRect(self._hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            if w < 100 or h < 50 or rect.left < -10000:
                return
            cfg = self._load_config()
            if not cfg.has_section("window"):
                cfg.add_section("window")
            cfg.set("window", "x", str(rect.left))
            cfg.set("window", "y", str(rect.top))
            cfg.set("window", "width", str(w))
            cfg.set("window", "height", str(h))
            self._save_config(cfg)
        except Exception:
            log.debug("Failed to save window geometry", exc_info=True)

    # ------------------------------------------------------------------
    # Window procedure — handles both tray and output messages
    # ------------------------------------------------------------------

    def _wndproc(self, hwnd, msg, wparam, lparam):
        # --- Tray icon messages ---
        if msg == WM_TRAYICON:
            mouse_msg = lparam & 0xFFFF
            if mouse_msg == WM_LBUTTONUP:
                self.toggle()
            elif mouse_msg == WM_RBUTTONUP:
                self._show_menu()
            return 0
        if msg == WM_COMMAND:
            cmd_id = wparam & 0xFFFF
            if _IDM_BASE <= cmd_id < self._menu_id_max:
                cb = self._menu_callbacks.get(cmd_id)
                if cb:
                    _dispatch_async(cb)
            return 0

        # --- DPI ---
        if msg == _dpi.WM_DPICHANGED:
            # The window moved to a monitor with a different scale factor.
            # lParam is Windows' suggested rect for the new DPI; using it
            # verbatim is what keeps the window the same *apparent* size and
            # stops it drifting under the cursor mid-drag. Ignoring this
            # message is what makes a per-monitor-aware app misbehave on
            # mixed-DPI setups — worse than staying unaware.
            suggested = ctypes.cast(ctypes.c_void_p(lparam),
                                    ctypes.POINTER(wt.RECT)).contents
            user32.SetWindowPos(
                hwnd, None, suggested.left, suggested.top,
                suggested.right - suggested.left,
                suggested.bottom - suggested.top,
                0x0004 | 0x0010)  # SWP_NOZORDER | SWP_NOACTIVATE
            self._apply_font()
            return 0

        # --- Output messages ---
        if msg == WM_SIZE:
            if self._edit:
                rect = wt.RECT()
                user32.GetClientRect(hwnd, ctypes.byref(rect))
                user32.MoveWindow(self._edit, 0, 0, rect.right, rect.bottom, True)
            if wparam == 0 and self._created:
                self._schedule_save()
            return 0
        if msg == WM_MOVE:
            if self._created:
                self._schedule_save()
            return 0
        if msg == WM_APPENDTEXT:
            while self._text_queue:
                try:
                    text, is_error = self._text_queue.popleft()
                    self._append_text(text, is_error)
                except IndexError:
                    break
            return 0
        if msg == WM_SETTOPMOST:
            self._topmost = bool(wparam)
            self._apply_topmost()
            return 0
        if msg == WM_UPDATE_TRAY:
            self._apply_pending_tray()
            return 0
        if msg == WM_DESTROY_SAFE:
            self.destroy()
            return 0
        if msg == WM_CLEARTEXT:
            if self._edit:
                _send_msg_str(self._edit, WM_SETTEXT, 0, "")
            return 0
        if msg == WM_SHOWWINDOW:
            user32.ShowWindow(hwnd, SW_SHOW)
            self._visible = True
            return 0
        if msg == WM_HIDEWINDOW:
            user32.ShowWindow(hwnd, SW_HIDE)
            self._visible = False
            return 0
        if msg == WM_TIMER and wparam == self._SAVE_TIMER_ID:
            user32.KillTimer(hwnd, self._SAVE_TIMER_ID)
            self._save_pending = False
            self._save_geometry()
            return 0
        if msg == WM_CLOSE:
            if self._save_pending:
                user32.KillTimer(hwnd, self._SAVE_TIMER_ID)
            self._save_geometry()
            user32.ShowWindow(hwnd, SW_HIDE)
            self._visible = False
            return 0  # don't destroy — tray stays
        if msg == WM_DESTROY:
            self._hwnd = None
            self._edit = None
            return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, wt.LPARAM(lparam))

    # ------------------------------------------------------------------
    # Window creation
    # ------------------------------------------------------------------

    def _create_window(self):
        """Create window + RichEdit + tray icon. Must be called on UI thread."""
        global _richedit_loaded
        with _richedit_lock:
            if not _richedit_loaded:
                try:
                    ctypes.windll.LoadLibrary("Msftedit.dll")
                except OSError:
                    pass
                _richedit_loaded = True

        self._cls_name = f"natlink_window_{id(self)}"
        self._hinstance = kernel32.GetModuleHandleW(None)

        self._wndproc_ref = WNDPROC(self._wndproc)
        wc = WNDCLASSEXW()
        ctypes.memset(ctypes.byref(wc), 0, ctypes.sizeof(wc))
        wc.cbSize = ctypes.sizeof(wc)
        wc.lpfnWndProc = self._wndproc_ref
        wc.hInstance = self._hinstance
        wc.hbrBackground = ctypes.cast(6, wt.HANDLE)  # COLOR_WINDOW + 1
        wc.lpszClassName = self._cls_name
        user32.RegisterClassExW(ctypes.byref(wc))

        self._hwnd = user32.CreateWindowExW(
            0, self._cls_name, self._title, WS_OVERLAPPEDWINDOW,
            self._x, self._y, self._width, self._height,
            None, None, self._hinstance, None)

        if not self._hwnd:
            log.error("CreateWindowExW failed — window will not be available")
            return

        # RichEdit child
        self._edit = user32.CreateWindowExW(
            0, _RICHEDIT_CLASS, "",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL |
            ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY | ES_NOHIDESEL,
            0, 0, self._width, self._height,
            self._hwnd, None, self._hinstance, None)
        if self._edit:
            user32.SendMessageW(self._edit, EM_SETBKGNDCOLOR, 0, _CLR_BACKGROUND)
            self._apply_font()
        self._created = True
        if self._topmost:
            self._apply_topmost()
