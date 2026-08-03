"""Dragon process lifecycle monitor — auto-disconnect/reconnect.

Uses Win32 named events so the launcher's pump (MsgWaitForMultipleObjects)
wakes instantly when Dragon exits or reappears — no polling delay.

The monitor thread detects Dragon exit/restart but does NOT call
natConnect/natDisconnect directly — COM objects are owned by the
main thread.
"""

import ctypes
import ctypes.wintypes as wt
import logging
import threading
import time

from ._win32 import user32, kernel32, DRAGON_CLS

log = logging.getLogger("natlink.compat")

SYNCHRONIZE = 0x00100000
WAIT_TIMEOUT = 0x00000102

# Names are shared with the launcher's CreateEventW calls so both sides
# open the same kernel objects.
DRAGON_EXITED_EVENT = "NatlinkDragonExited"
DRAGON_REAPPEARED_EVENT = "NatlinkDragonReappeared"


def _get_dragon_handle():
    """Get a waitable process handle for Dragon, or None."""
    hwnd = user32.FindWindowW(DRAGON_CLS, None)
    if not hwnd:
        return None
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None
    return kernel32.OpenProcess(SYNCHRONIZE, False, pid.value)


def start_dragon_monitor(session):
    """Start a daemon thread that watches Dragon's lifecycle.

    ``session`` is a launcher-owned object that exposes:
      * ``connected``
      * ``monitor_stop_event``
      * ``set_monitor_thread(thread)``
      * ``events.dragon_exited`` / ``events.dragon_reappeared`` (Win32 handles)

    Signals Win32 events on the session so the launcher's pump wakes instantly.
    """
    stop_event = session.monitor_stop_event
    h_exited = session.events.dragon_exited
    h_reappeared = session.events.dragon_reappeared

    kernel32.ResetEvent(h_exited)
    kernel32.ResetEvent(h_reappeared)

    def _signal_exited():
        kernel32.SetEvent(h_exited)

    def _signal_reappeared():
        kernel32.SetEvent(h_reappeared)

    def _monitor():
        log.info("Dragon monitor started")
        while not stop_event.is_set():
            if session.connected:
                handle = _get_dragon_handle()
                if not handle:
                    if session.connected:
                        log.debug("Dragon process gone")
                        _signal_exited()
                    stop_event.wait(2)
                    continue
                try:
                    while not stop_event.is_set():
                        rc = kernel32.WaitForSingleObject(handle, 500)
                        if rc != WAIT_TIMEOUT:
                            if session.connected:
                                log.debug("Dragon process exited")
                                _signal_exited()
                            break
                        if not user32.FindWindowW(DRAGON_CLS, None):
                            if session.connected:
                                log.debug("Dragon window closed")
                                _signal_exited()
                            break
                finally:
                    kernel32.CloseHandle(handle)
            else:
                if user32.FindWindowW(DRAGON_CLS, None):
                    log.info("Dragon detected")
                    _signal_reappeared()
                    for _ in range(60):
                        if session.connected or stop_event.is_set():
                            break
                        time.sleep(1)
                else:
                    stop_event.wait(2)

    t = threading.Thread(target=_monitor, daemon=True, name="dragon-monitor")
    session.set_monitor_thread(t)
    t.start()
