"""Win32 message pump for COM callback delivery.

Messaging model
~~~~~~~~~~~~~~~~
There is one messaging mechanism: PostMessage to the hidden window.

Sink callbacks (PhraseFinish, Paused, MimicDone, etc.) arrive on the
STA main thread — COM serializes Dragon's cross-process calls via the
marshal DLLs and the STA message queue.  Sinks call PostMessage to the
hidden window and return immediately, so the COM call returns quickly
to Dragon.  When the pump calls DispatchMessage, the message reaches
the hidden window's wndproc, which looks up the registered handler and
runs it.

Complex payloads travel inside closures queued on per-channel deques
in _hidden_wnd.py (dispatch).  Sync-op completions carry real
wparam/lparam via signal(); optional string payloads attach via
signal(data=...) and get retrieved with take_signal_data().

Completion tracking (C++ CMessageStack)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sync operations (recognitionMimic, playString, execScript) need to
know when their operation completes.  push_message_entry(WM_xxx, code)
registers "I'm waiting for this message."  trigger_message() scans the
stack when any message arrives and marks the matching entry as
triggered.  message_loop() pumps messages and checks entry.triggered
to know when to stop.

Three pump paths
~~~~~~~~~~~~~~~~~
  1. Launcher main loop (_launcher.py) — pump(h_events=[...]) with
     shutdown/restart/dragon events + 2s heartbeat.  Dispatches pending
     messages on every wake.  Runs continuously while the tray is active.

  2. Sync operations (this module) — message_loop() pumps messages
     until a specific completion entry is triggered.  Used by
     recognitionMimic, execScript, playString, playEvents.
     pump(h_event) waits on a single Win32 event (inputFromFile).

  pump() serves both paths: pump(h_events=[...]) for the launcher,
  pump(h_event) for single-event waits, pump() with no args to
  dispatch pending messages inline.

  3. UI thread (_ui_thread.py) — GetMessageW loop on a separate thread,
     owns tray icon and output window HWNDs.  Independent of the above.

The two main-thread paths (1 and 2) never run simultaneously.  When a
sync operation fires during a callback, the launcher's pump() is
suspended mid-DispatchMessage while message_loop() takes over.

Re-entrancy
~~~~~~~~~~~~
Dragon is free to call back into this code whenever we are pumping
messages.  We pump during playString, execScript, recognitionMimic,
playEvents, and inputFromFile.  During any of these, another COM
callback from Dragon can arrive, causing re-entrant calls into
Python.  For example:

  1. Dragon sends PhraseFinish -> sink posts WM_SENDRESULTS, returns
  2. Pumping dispatches WM_SENDRESULTS -> Python gotResults runs
  3. gotResults calls recognitionMimic -> message_loop() pumps again
  4. Dragon sends Paused -> sink posts WM_PAUSED -> Begin fires

At this point there are two nested calls into the Python interpreter
on the stack.  "The user needs to be aware that when they do a
playString, execScript or recognitionMimic, another Python callback
is possible." — Joel Gould, DragonCode.cpp

To simplify, Change callbacks (mic/user) are not fired while already
inside another callback — they are deferred until callback depth
returns to zero.  This prevents switching users mid-recognition.

PhraseFinish synchronization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dragon pauses the recognition loop in two places:

  1. JIT Pause — before recognition starts, Dragon calls Paused on all
     clients.  Recognition does not resume until every client calls
     Resume.  We translate this into Begin callbacks.

  2. Results processing — Dragon will not start a new recognition until
     all PhraseFinish callbacks complete.  If Python code calls
     recognitionMimic from inside a results callback, it blocks waiting
     for the mimic to finish, but the mimic cannot start because
     recognition is paused — deadlock (actually a timeout).

To avoid this, PhraseFinish does not call Python directly.  Instead it
posts WM_SENDRESULTS to the hidden window, returning to Dragon
immediately so the recognition loop can proceed.
— Joel Gould, DragonCode.cpp (lines 52-87)
"""

import ctypes
import ctypes.wintypes as wt
import logging
import time

from ._win32 import user32 as _user32, kernel32 as _kernel32

log = logging.getLogger("natlink.com.pump")
_timer_log = logging.getLogger("natlink.com.timer")

_QS_ALLINPUT = 0x04FF
_PM_REMOVE = 0x0001
_WAIT_OBJECT_0 = 0
_WAIT_TIMEOUT = 0x102

# Dialog handling — C++ messageLoop checks for #32770 dialog class
# and routes messages through IsDialogMessage so playString works
# with dialog controls (tab, enter, escape, etc.).
_user32.GetActiveWindow.restype = wt.HWND
_user32.GetActiveWindow.argtypes = []
_user32.IsDialogMessageW.restype = wt.BOOL
_user32.IsDialogMessageW.argtypes = [wt.HWND, ctypes.POINTER(wt.MSG)]
_GetClassNameW = _user32.GetClassNameW
_GetClassNameW.restype = ctypes.c_int
_GetClassNameW.argtypes = [wt.HWND, ctypes.c_wchar_p, ctypes.c_int]


def _dispatch_pending():
    """Dispatch all pending Win32 messages via PeekMessage/DispatchMessage.

    Uses a local MSG buffer for re-entrancy safety — message_loop or
    COM modal loops may call back into code that dispatches pending messages.
    """
    msg = wt.MSG()
    while _user32.PeekMessageW(
        ctypes.byref(msg), None, 0, 0, _PM_REMOVE
    ):
        _user32.TranslateMessage(ctypes.byref(msg))
        _user32.DispatchMessageW(ctypes.byref(msg))


# ---------------------------------------------------------------------------
# CMessageStack — matches C++ CDragonCode::TriggerMessage / IsMessageTriggered
#
# "I introduced thsi class to fix a bug in the messageLoop where we were in
# nested message loops but got the exit message out of order.  To fix that
# we remember every exit message we get."
# — Joel Gould, DragonCode.cpp (CMessageStack, line 506)
# ---------------------------------------------------------------------------

class _MessageEntry:
    """One level of the nested message_loop stack."""
    __slots__ = ('message', 'wparam', 'lparam', 'triggered')

    def __init__(self, message, wparam):
        self.message = message
        self.wparam = wparam
        self.lparam = 0
        self.triggered = False


_message_stack: list = []  # STA-thread-only — all callers run on the main thread


def trigger_message(message, wparam, lparam):
    """Mark the first matching untriggered stack entry.

    Called from two places (both on the STA main thread):
      1. message_loop — on each message from PeekMessage, BEFORE dispatch.
      2. Hidden wndproc handler — during DispatchMessage from ANY pump
         (our message_loop, COM's outgoing-call modal loop, etc.).

    Both paths can match the same message — the ``not entry.triggered``
    guard prevents double-triggering.

    (2) handles the STA pre-consumed case: a COM outgoing call
    (RecognitionMimic, get_current_module, Resume) enters a modal loop
    that dispatches our posted WM_MIMICDONE before message_loop runs.
    """
    for entry in reversed(_message_stack):
        if (entry.message == message
                and entry.wparam == wparam
                and not entry.triggered):
            entry.triggered = True
            entry.lparam = lparam
            return


def push_message_entry(target_msg, target_wparam):
    """Push a CMessageStack entry.  Returns the entry for message_loop.

    Must be called BEFORE the COM call that may trigger the completion
    message — the "pre-consumed" case from proxy32.
    """
    entry = _MessageEntry(target_msg, target_wparam)
    _message_stack.append(entry)
    return entry


def message_loop(entry, timeout_ms=60000, label="", start=None):
    """Pump messages until *entry* is triggered.

    Port of C++ CDragonCode::messageLoop with STA extensions:

    - **Pre-consumed check**: if entry was triggered during a prior COM
      modal loop, returns immediately.
    - **start callback**: if provided, dispatch pending messages first
      (dispatching any leftover WM_PAUSED → Resume from a previous
      cycle), then call *start* to issue the COM request.  This matches
      proxy32's continuous pump where the pipe request arrives INSIDE
      the message loop, after pending messages have been dispatched.

    Returns lParam on success, None on timeout.
    """
    msg = wt.MSG()  # local buffer for re-entrancy safety
    cls_buf = ctypes.create_unicode_buffer(128)  # local for re-entrancy
    t_start_t = time.monotonic()
    deadline = t_start_t + timeout_ms / 1000.0

    try:
        # Pre-consumed check
        if entry.triggered:
            if label:
                log.debug("message_loop(%s): pre-consumed, %.0fms",
                          label, (time.monotonic() - t_start_t) * 1000)
            return entry.lparam

        # Drain pending messages (e.g. WM_PAUSED from previous cycle),
        # then issue the COM call.  Dragon sees Resume before
        # RecognitionMimic — no "mimic found after pause" race.
        if start is not None:
            _dispatch_pending()
            start()
            # Check again — the COM call's modal loop may have
            # dispatched WM_MIMICDONE already (pre-consumed).
            if entry.triggered:
                if label:
                    log.debug("message_loop(%s): pre-consumed after start, "
                              "%.0fms", label,
                              (time.monotonic() - t_start_t) * 1000)
                return entry.lparam

        while True:
            if entry.triggered:
                if label:
                    log.debug("message_loop(%s): triggered, %.0fms",
                              label, (time.monotonic() - t_start_t) * 1000)
                return entry.lparam

            remaining_ms = int((deadline - time.monotonic()) * 1000)
            if remaining_ms <= 0:
                if label:
                    log.warning("message_loop(%s) TIMEOUT after %dms",
                                label, timeout_ms)
                return None

            # MsgWaitForMultipleObjects with the remaining timeout so we
            # don't block past the deadline (GetMessageW would block
            # indefinitely if no messages arrive).
            rc = _user32.MsgWaitForMultipleObjects(
                0, None, False, remaining_ms, _QS_ALLINPUT)
            if rc == _WAIT_TIMEOUT:
                continue  # loop back to check deadline

            # Drain all available messages via PeekMessage
            while _user32.PeekMessageW(
                    ctypes.byref(msg), None, 0, 0, _PM_REMOVE):
                # TriggerMessage — BEFORE dispatch (C++ line 1057)
                trigger_message(msg.message, msg.wParam, msg.lParam)

                # "If we are inside a running dialog box (the top-level window
                # is the magic class named #32770), then we want to make sure
                # that we process the dialog messages."
                # — Joel Gould, DragonCode.cpp (messageLoop)
                hWnd = _user32.GetActiveWindow()
                if hWnd:
                    _GetClassNameW(hWnd, cls_buf, 128)
                    if cls_buf.value == "#32770":
                        if _user32.IsDialogMessageW(hWnd, ctypes.byref(msg)):
                            continue

                _user32.TranslateMessage(ctypes.byref(msg))
                _user32.DispatchMessageW(ctypes.byref(msg))

                # IsMessageTriggered — AFTER dispatch (C++ line 1078)
                # "This post message will make sure that we enter the loop
                # again to look for any triggered messages."
                # — Joel Gould, DragonCode.cpp (messageLoop, line 1080)
                if entry.triggered:
                    if label:
                        log.debug("message_loop(%s): triggered, %.0fms",
                                  label, (time.monotonic() - t_start_t) * 1000)
                    return entry.lparam
    finally:
        try:
            _message_stack.remove(entry)
        except ValueError:
            pass


def pump(h_event=None, timeout_ms=0, label="", h_events=None):
    """Pump Win32 messages, optionally waiting for event handle(s).

    Single event (sync operations):
        pump(h_event, 60000, "mimic")   — wait for one event
        Returns True if signaled, False on timeout.

    Multiple events (launcher main loop):
        pump(h_events=[h1, h2], timeout_ms=2000)
        Returns the index of the signaled event (0, 1, ...),
        -1 on timeout, or -2 on error.

    No events:
        pump()  — dispatch pending messages, return True.
    """
    if h_event is None and h_events is None:
        _dispatch_pending()
        return True

    if h_events is not None:
        n = len(h_events)
        h_array = (ctypes.c_void_p * n)(*h_events)
    else:
        n = 1
        h_array = (ctypes.c_void_p * 1)(h_event)

    t_start = time.monotonic()
    result = False if h_event is not None else -1
    deadline = t_start + timeout_ms / 1000.0 if timeout_ms > 0 else None

    while True:
        if deadline is not None:
            remaining = max(0, int((deadline - time.monotonic()) * 1000))
            if remaining <= 0:
                break
        else:
            remaining = 0xFFFFFFFF

        rc = _user32.MsgWaitForMultipleObjects(
            n, h_array, False, remaining, _QS_ALLINPUT)

        if _WAIT_OBJECT_0 <= rc < _WAIT_OBJECT_0 + n:
            _dispatch_pending()
            if h_events is not None:
                result = rc - _WAIT_OBJECT_0
            else:
                result = True
            break
        elif rc == _WAIT_OBJECT_0 + n:
            _dispatch_pending()
            if h_events is not None:
                continue
        elif rc in (-1, 0xFFFFFFFF):  # WAIT_FAILED
            log.error("MsgWaitForMultipleObjects failed: %d",
                      _kernel32.GetLastError())
            result = -2 if h_events is not None else False
            break
        else:
            break  # timeout

    wait_ms = (time.monotonic() - t_start) * 1000
    signaled = result is True or (isinstance(result, int) and result >= 0)
    if not signaled and label:
        log.warning("pump(%s) TIMEOUT after %.0fms", label, wait_ms)
    elif signaled and wait_ms > 500 and label:
        log.warning("pump(%s) slow: %.0fms", label, wait_ms)
    elif label:
        log.debug("pump(%s): %.0fms", label, wait_ms)
    return result


# --- Win32 timer (SetTimer/KillTimer) ---
# Matches C++ CDragonCode::setTimerCallback:
#   m_nTimer = SetTimer(m_hMsgWnd, 2, nMilliseconds, NULL)
# WM_TIMER is delivered to the hidden window and dispatched by
# DispatchMessage.  hiddenWndProc → onTimer() fires the callback.
# No TIMERPROC, no extra thread — same as original natlink.

_TIMER_ID = 2  # C++ uses timer ID 2
_active_timer_id = 0
_timer_callback = None


def set_timer(interval_ms: int, callback) -> int:
    """Install a Win32 timer that fires *callback* every *interval_ms* ms.

    Matches C++ SetTimer(m_hMsgWnd, 2, nMilliseconds, NULL):
    WM_TIMER is posted to the hidden window; the hidden-window handler
    invokes the callback on the main thread during DispatchMessage.

    "first we clean up from the previous call (this makes sure that we
    delete the timer)"
    — Joel Gould, DragonCode.cpp (setTimerCallback)
    """
    global _active_timer_id, _timer_callback

    # Kill any existing timer first
    if _active_timer_id:
        from . import _hidden_wnd
        _user32.KillTimer(_hidden_wnd.hwnd() or 0, _active_timer_id)
        _active_timer_id = 0
        _timer_callback = None

    _timer_callback = callback

    # Register WM_TIMER handler on hidden window.  WM_TIMER is an OS-
    # generated message, not one of our dispatch/signal channels, so it
    # goes through the generic message-handler slot alongside signal
    # channels (WM_PLAYBACK, etc.).
    from . import _hidden_wnd
    WM_TIMER = 0x0113
    _hidden_wnd.register_message_handler(WM_TIMER, _on_wm_timer)

    hwnd = _hidden_wnd.hwnd() or 0
    _active_timer_id = _user32.SetTimer(hwnd, _TIMER_ID, interval_ms, None)
    if not _active_timer_id:
        _timer_log.error("SetTimer failed: %d", _kernel32.GetLastError())
    else:
        _timer_log.info("Win32 timer installed: id=%d, interval=%dms",
                        _active_timer_id, interval_ms)
    return _active_timer_id


def _on_wm_timer(wp, lp):
    """WM_TIMER handler — matches C++ hiddenWndProc WM_TIMER case."""
    cb = _timer_callback
    if cb is None:
        return
    _timer_log.debug("WM_TIMER fired")
    try:
        cb()
    except Exception:
        _timer_log.exception("Timer callback error")


def kill_timer() -> None:
    """Cancel the active Win32 timer.

    Matches C++ KillTimer(m_hMsgWnd, m_nTimer).
    """
    global _active_timer_id, _timer_callback
    if _active_timer_id:
        from . import _hidden_wnd
        _user32.KillTimer(_hidden_wnd.hwnd() or 0, _active_timer_id)
        _timer_log.info("Win32 timer killed: id=%d", _active_timer_id)
        _active_timer_id = 0
        _timer_callback = None
