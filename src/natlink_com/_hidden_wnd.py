"""Hidden window for COM callback dispatch — STA-thread work queue.

Sink callbacks (PhraseFinish, Paused, MimicDone, etc.) arrive on the STA
main thread.  Sinks defer Python-side work to the main message pump via
one of two primitives:

  * ``dispatch(fn, *args, channel=WM_X)`` — queue a closure on a
    per-channel deque and post a Windows message so the pump's wndproc
    drains it on the next DispatchMessage.  Used for deferring Python
    callbacks (PhraseFinish → user gotResults, Paused → Begin, etc.).

  * ``signal(msg, wparam, lparam=0, *, data=None)`` — post a sync-op
    completion with real Win32 ``wparam``/``lparam`` so the pump's
    ``message_loop`` can match waiters by client code.  Optional
    ``data`` is attached via a sidecar dict and retrieved later with
    ``take_signal_data(msg, wparam)``.

Two small registries support these:

  * ``_queues`` — per-channel ``deque`` of ``(fn, args, t_enq)`` tuples;
    wndproc drains one per DispatchMessage call.
  * ``_signal_data`` — ``(msg, wparam)`` → payload, for attaching a
    Python object to a signal (e.g. the error string on
    ``ExecutionAborted``).

Signal channels and OS-generated messages (WM_TIMER) route through
``register_message_handler(msg, fn)``; their handlers run on the STA
thread during wndproc.  Dispatch channels are auto-routed and do not
need a registration.

``_accepting`` gates ``dispatch()``: set ``False`` in ``destroy()``
before clearing the queues so new dispatches are rejected at the
source rather than being silently discarded when the queue is cleared.

— Originally Joel Gould, DragonCode.cpp (hiddenWndProc, postMessage)
"""

import ctypes
import ctypes.wintypes as wt
import logging
import threading
import time
from collections import deque
from typing import Any, Callable

log        = logging.getLogger("natlink.com.sta")
log_disp   = logging.getLogger("natlink.com.sta.dispatch")
log_drain  = logging.getLogger("natlink.com.sta.drain")
log_health = logging.getLogger("natlink.com.sta.health")
log_error  = logging.getLogger("natlink.com.sta.error")

# Private instances, not ctypes.windll.*: use_last_error is required for
# ctypes.get_last_error() below to report anything, and keeping our own
# instance means the argtypes set here cannot be clobbered by — or silently
# depended on by — another module sharing the process-wide windll cache.
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_longlong
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, ctypes.c_uint,
                              wt.WPARAM, wt.LPARAM)

user32.DefWindowProcW.argtypes = [wt.HWND, ctypes.c_uint, wt.WPARAM, wt.LPARAM]
user32.DefWindowProcW.restype = LRESULT
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


# --- Window messages (matching C++ WM_USER+345..352) ---
# "Here are the various windows messages we send ourself.  We give this
# window message some random value to avoid conflicts."
# — Joel Gould, DragonCode.cpp (line 227-228)
#
# Classification after the dispatch refactor:
#   SIGNAL channels carry real wparam/lparam used by pump.message_loop
#     to match sync-op waiters.  Posted via signal().
#   DISPATCH channels carry closures via the _queues sidecar; wparam
#     and lparam are zero at the Win32 level.  Posted via dispatch().
WM_USER = 0x0400

WM_PLAYBACK            = WM_USER + 345  # SIGNAL — playString / playEvents done
WM_EXECUTION           = WM_USER + 346  # SIGNAL — execScript done/aborted (data= on abort)
WM_ATTRIBCHANGED       = WM_USER + 347  # SIGNAL — AttribChanged2 pump completion
WM_PAUSED              = WM_USER + 348  # DISPATCH — engine sink._do_paused
WM_SENDRESULTS         = WM_USER + 349  # DISPATCH — conn._do_send_results (router)
WM_MIMICDONE           = WM_USER + 350  # SIGNAL — RecognitionMimic completion
WM_PHRASE_HYPO         = WM_USER + 351  # DISPATCH — conn._do_phrase_hypo (router)
WM_DICT_TEXTCHANGED    = WM_USER + 352  # DISPATCH — conn._do_dict_text_changed (router)
WM_DEFERRED_CALL       = WM_USER + 353  # DISPATCH — UI default channel
WM_ATTRIBCHANGED_WORK  = WM_USER + 354  # DISPATCH — engine_sink._dispatch_attrib_changed

# Channels that auto-route through the closure queue.
_DISPATCH_CHANNELS = (
    WM_PAUSED, WM_SENDRESULTS, WM_PHRASE_HYPO, WM_DICT_TEXTCHANGED,
    WM_DEFERRED_CALL, WM_ATTRIBCHANGED_WORK,
)

# Reverse lookup for log messages.
_CHANNEL_NAMES = {
    v: k for k, v in globals().items()
    if k.startswith("WM_") and k != "WM_USER" and isinstance(v, int)
}


def _ch_name(msg: int) -> str:
    return _CHANNEL_NAMES.get(msg, f"0x{msg:04X}")


# --- State ---
# _queues[channel]          : deque of (fn, args, t_enq) for DISPATCH channels.
# _signal_data[(msg, wp)]   : object attached to a signal for later consumption.
# _message_handlers[msg]    : (wparam, lparam) -> None callback for SIGNAL channels
#                             and OS-generated messages (WM_TIMER).  Dispatch
#                             channels do NOT use this — they auto-drain.
# _accepting                : gates dispatch().  Flipped to False in destroy()
#                             BEFORE queues are cleared to reject new work at
#                             the source instead of silently losing it.
_queues: "dict[int, deque]" = {}
_signal_data: "dict[tuple[int, int], Any]" = {}
_message_handlers: "dict[int, Callable[[int, int], None]]" = {}
_accepting = False

# Logged once per channel per _BACKLOG_WARN step when a channel backs up.
_BACKLOG_WARN = 16


# --- Window ---
_CLASS_NAME = "natlink_com"
_class_registered = False
_wndproc_ref = None
_hwnd = None


# C++ hiddenWndProc (line 576): "Note when a posted message comes in,
# the Python interpreter should be unlocked so we first have to
# establish a thread state and lock the interpreter."
# — Joel Gould, DragonCode.cpp (line 572-574)
# In this Python port the GIL serves the same role as CLockPython.
def _wndproc(hwnd, msg, wparam, lparam):
    # Dispatch channel → drain one closure from its queue.
    q = _queues.get(msg)
    if q is not None:
        try:
            fn, args, t_enq = q.popleft()
        except IndexError:
            # PostMessage fired for a channel with no queued work —
            # ignore rather than propagate.
            return 0
        t_start = time.perf_counter()
        try:
            fn(*args)
        except Exception:
            log_error.exception("dispatch handler error channel=%s fn=%s",
                                _ch_name(msg), getattr(fn, "__qualname__", fn))
        finally:
            if log_drain.isEnabledFor(logging.DEBUG):
                t_end = time.perf_counter()
                log_drain.debug(
                    "run channel=%s fn=%s wait=%.1fms dur=%.1fms",
                    _ch_name(msg),
                    getattr(fn, "__qualname__", str(fn)),
                    (t_start - t_enq) * 1000,
                    (t_end - t_start) * 1000,
                )
        return 0

    # Signal channel or OS message → run registered handler.
    h = _message_handlers.get(msg)
    if h is not None:
        try:
            h(wparam, lparam)
        except Exception:
            log_error.exception("message handler error channel=%s",
                                _ch_name(msg))
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def create():
    """Create hidden window on main thread. Returns HWND or None."""
    global _class_registered, _wndproc_ref, _hwnd, _accepting

    if _hwnd:
        # Assigning over a live _hwnd would drop the only reference to the
        # previous window, leaking it with no way to destroy it. Reachable
        # whenever a connect fails after create() and is retried, since the
        # failure path does not call destroy().
        _accepting = True
        return _hwnd

    hInstance = kernel32.GetModuleHandleW(None)

    # Win32 window APIs use handled SEH internally — faulthandler's
    # vectored exception handler reports these as fatal even though
    # Windows handles them.  Disable around both RegisterClassExW
    # and CreateWindowExW.
    import faulthandler as _fh
    _fh_was_enabled = _fh.is_enabled()
    if _fh_was_enabled:
        _fh.disable()

    try:
        if not _class_registered:
            _wndproc_ref = WNDPROC(_wndproc)
            cls = WNDCLASSEXW()
            cls.cbSize = ctypes.sizeof(cls)
            cls.lpfnWndProc = _wndproc_ref
            cls.hInstance = hInstance
            cls.lpszClassName = _CLASS_NAME
            atom = user32.RegisterClassExW(ctypes.byref(cls))
            if not atom:
                log.error("RegisterClassExW failed: %d", ctypes.get_last_error())
                return None
            _class_registered = True

        _hwnd = user32.CreateWindowExW(
            0, _CLASS_NAME, _CLASS_NAME, 0x80000000,  # WS_POPUP
            0, 0, 0, 0, None, None, hInstance, None)
    finally:
        if _fh_was_enabled:
            try:
                _fh.enable()
            except Exception:
                # faulthandler.enable() writes to sys.stderr and needs a real
                # file descriptor.  Hosts that replace sys.stderr with a stream
                # that has none — pytest's capture, GUI shells, natlinkcore's
                # own redirect_output — would otherwise abort hidden-window
                # creation, and with it the whole connection, over a debug aid.
                log.debug("could not re-enable faulthandler", exc_info=True)

    if not _hwnd:
        log.error("CreateWindowExW failed: %d", ctypes.get_last_error())
        return None

    # Pre-allocate one deque per dispatch channel so dispatch() can index
    # without setdefault — avoids a narrow race on free-threaded Python.
    for ch in _DISPATCH_CHANNELS:
        _queues.setdefault(ch, deque())

    _accepting = True
    log.debug("Hidden COM window created: 0x%X", _hwnd)
    return _hwnd


def hwnd():
    """Return the hidden window handle, or None if not created."""
    return _hwnd


def destroy():
    """Destroy hidden window and clear pending work.

    Flips ``_accepting`` to False *before* touching any state so new
    ``dispatch()`` calls are rejected at the source rather than being
    enqueued into a deque that is about to be cleared.
    """
    global _hwnd, _accepting
    _accepting = False
    if _hwnd:
        user32.DestroyWindow(_hwnd)
        log.debug("Hidden COM window destroyed")
        _hwnd = None
    for q in _queues.values():
        q.clear()
    _signal_data.clear()


# --- Post primitives ---

def dispatch(fn, *args, channel: int = WM_DEFERRED_CALL) -> bool:
    """Queue ``fn(*args)`` for execution on the COM (STA) thread.

    Safe to call from any thread.  Returns True if queued, False if the
    hidden window is unavailable or ``_accepting`` is False (shutdown
    in progress).  The closure runs on the STA thread during the next
    DispatchMessage that pulls the matching channel message off the
    Windows queue.

    ``channel`` is one of the ``WM_*`` constants exported by this
    module.  It is used both as the Windows message ID (for log /
    Spy++ readability and FIFO ordering guarantees within a channel)
    and as the key into ``_queues``.
    """
    if not _accepting:
        if log_health.isEnabledFor(logging.DEBUG):
            log_health.debug("dispatch rejected (not accepting) channel=%s fn=%s",
                             _ch_name(channel), getattr(fn, "__qualname__", fn))
        return False

    q = _queues.get(channel)
    if q is None:
        # Channel not in _DISPATCH_CHANNELS — caller bug.  Log and bail.
        log_error.error("dispatch: unknown channel %s fn=%s",
                        _ch_name(channel), getattr(fn, "__qualname__", fn))
        return False

    t_enq = time.perf_counter()
    q.append((fn, args, t_enq))
    depth = len(q)

    if log_disp.isEnabledFor(logging.DEBUG):
        log_disp.debug("enq channel=%s fn=%s tid=%d depth=%d",
                       _ch_name(channel),
                       getattr(fn, "__qualname__", str(fn)),
                       threading.get_ident(), depth)

    if depth >= _BACKLOG_WARN and depth % _BACKLOG_WARN == 0:
        log_health.warning("backlog channel=%s depth=%d",
                           _ch_name(channel), depth)

    hwnd_local = _hwnd
    if hwnd_local and user32.PostMessageW(hwnd_local, channel, 0, 0):
        return True

    # Delivery failed — roll back the append so every False return means
    # "not queued, caller may unwind dependent state (e.g. pause_recog)".
    # Without this rollback, a queued-but-unposted closure would later
    # drain and run its finally block, double-decrementing state the
    # caller already unwound.  That matters for Dragon: a spurious
    # pause_recog decrement lets Dragon fire Resume before the actual
    # callback runs.
    #
    # Rollback safety: STA sink channels are single-threaded (sink
    # callback → conn.defer_* → dispatch all run on STA, and the STA
    # wndproc only ever popleft()s from the left).  The UI channel
    # (WM_DEFERRED_CALL) is cross-thread but has no pause_recog
    # accounting, so an unlikely race on pop() is semantically harmless.
    try:
        q.pop()
    except IndexError:
        pass

    if not hwnd_local:
        log_health.debug("dispatch dropped (no hwnd) channel=%s fn=%s",
                         _ch_name(channel),
                         getattr(fn, "__qualname__", str(fn)))
    else:
        log_health.warning("PostMessageW failed channel=%s depth=%d",
                           _ch_name(channel), depth)
    return False


def signal(msg: int, wparam: int, lparam: int = 0,
           *, data: Any = None) -> bool:
    """Post a sync-op completion to the hidden window.

    Used for channels whose wparam/lparam are read by
    ``pump.message_loop``'s waiter-matching logic (WM_PLAYBACK,
    WM_EXECUTION, WM_MIMICDONE, WM_ATTRIBCHANGED).  ``data`` attaches
    an optional Python payload indexed by ``(msg, wparam)``; retrieve
    it with ``take_signal_data(msg, wparam)``.

    Returns True if the message was posted; False if the hidden window
    is unavailable.  Unlike dispatch(), signal() is not gated by
    ``_accepting`` — sync-op completions must get through even during
    disconnect teardown so blocked ``message_loop`` callers can
    return cleanly.
    """
    if data is not None:
        _signal_data[(msg, wparam)] = data

    hwnd_local = _hwnd
    if hwnd_local and user32.PostMessageW(hwnd_local, msg, wparam, lparam):
        return True

    # Post failed or no window — clean up the sidecar to avoid leak.
    if data is not None:
        _signal_data.pop((msg, wparam), None)
    if not hwnd_local:
        log_health.debug("signal dropped (no hwnd) channel=%s",
                         _ch_name(msg))
    else:
        log_health.warning("signal PostMessageW failed channel=%s",
                           _ch_name(msg))
    return False


def take_signal_data(msg: int, wparam: int) -> Any:
    """Pop and return data attached to a prior ``signal(msg, wparam, ...)``.

    Returns None if no data was attached.  Idempotent — a second call
    for the same key returns None.
    """
    return _signal_data.pop((msg, wparam), None)


# --- Message handler registry (for signal channels + OS messages) ---

def register_message_handler(msg: int, handler: Callable[[int, int], None]) -> None:
    """Register a ``(wparam, lparam) -> None`` handler for a message.

    Used by:
      * The pump, to route signal channels to ``trigger_message``.
      * The pump, to handle OS-generated ``WM_TIMER`` heartbeats.

    Dispatch channels (WM_PAUSED, WM_SENDRESULTS, etc.) MUST NOT be
    registered here — their closures route automatically through
    the per-channel deques.
    """
    if msg in _queues:
        raise ValueError(
            f"register_message_handler: channel {_ch_name(msg)} is a "
            "dispatch channel; use dispatch() instead.")
    _message_handlers[msg] = handler


def unregister_all_message_handlers() -> None:
    """Clear the signal/OS message handler registry.

    Called during disconnect teardown so handlers captured from the old
    connection do not persist into a fresh connect.
    """
    _message_handlers.clear()
