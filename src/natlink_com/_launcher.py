"""Natlink launcher primitives — low-level COM probing, event hooks, mutex.

High-level orchestration (run(), restart) lives in natlink_compat._launcher.

This module provides:
  - COM readiness probing (replaces blind sleep)
  - Wait-for-Dragon via SetWinEventHook (zero polling)
  - Profile-ready detection via Dragon log monitoring
  - Single instance mutex
  - Shutdown/restart event signaling
"""

import ctypes
import ctypes.wintypes as wt
import logging
import os
import re
import sys
import time
from pathlib import Path

from ._com_helpers import release_raw
from ._connection import (CLSCTX_LOCAL_SERVER,  # also sets CoCreateInstance argtypes
                          CLSCTX_ACTIVATE_32_BIT_SERVER)
from ._win32 import user32, kernel32, DRAGON_CLS

log = logging.getLogger("natlink.com.launcher")


ole32 = ctypes.windll.ole32

_PROFILE_READY_RE = re.compile(r"Normal mode: You can dictate", re.IGNORECASE)


# WinEventProc callback type (module-level to avoid recreating each call)
_WINEVENTPROC = ctypes.WINFUNCTYPE(
    None, wt.HANDLE, wt.DWORD, wt.HWND,
    ctypes.c_long, ctypes.c_long, wt.DWORD, wt.DWORD)


# ---------------------------------------------------------------------------
# COM readiness probing
# ---------------------------------------------------------------------------

def _wait_for_com_ready(max_wait=30, initial_delay=0.5):
    """Retry CoCreateInstance(DgnSite) until Dragon's COM server responds.

    Dragon's toolbar window appears several seconds before its COM
    server accepts connections.  Probes with exponential backoff
    (0.5s, 1s, 2s, ...) capped at 4s per retry.

    Uses pump() between retries so the STA message loop stays responsive
    (UI thread's run_on_ui_thread and Dragon callbacks aren't blocked).
    """
    from ._guids import CLSID_DgnSite, IID_IUnknown
    from ._pump import pump

    delay = initial_delay
    deadline = time.monotonic() + max_wait

    # Temporary event handle for pump() — never signaled, just used for
    # timed message dispatch.
    h_wait = kernel32.CreateEventW(None, True, False, None)

    try:
        while time.monotonic() < deadline:
            ppv = ctypes.c_void_p()
            hr = ole32.CoCreateInstance(
                ctypes.byref(CLSID_DgnSite), None,
                # Must match DragonConnection.connect exactly. Dragon is a
                # 32-bit LocalServer32; without ACTIVATE_32_BIT_SERVER this
                # probe resolves to the 64-bit-view DgnSite entry and can
                # never succeed, so it burns the full max_wait on every
                # connect and reconnect before "connecting anyway".
                CLSCTX_LOCAL_SERVER | CLSCTX_ACTIVATE_32_BIT_SERVER,
                ctypes.byref(IID_IUnknown), ctypes.byref(ppv))
            if hr >= 0:
                if ppv.value:
                    release_raw(ppv)
                log.debug("Dragon COM ready after probe")
                return True
            log.debug("COM probe hr=0x%08X, retry in %.1fs", hr & 0xFFFFFFFF, delay)
            # Pump messages while waiting — keeps STA responsive
            pump(h_event=h_wait, timeout_ms=int(delay * 1000))
            delay = min(delay * 2, 4.0)
    finally:
        kernel32.CloseHandle(h_wait)

    log.warning("COM readiness probe timed out after %ds — connecting anyway", max_wait)
    return False


# ---------------------------------------------------------------------------
# Wait for Dragon window (SetWinEventHook — zero polling)
# ---------------------------------------------------------------------------

def _wait_for_dragon_window(h_shutdown=None, h_restart=None):
    """Block until Dragon's main window appears or shutdown is signaled.

    Uses SetWinEventHook with EVENT_OBJECT_CREATE for zero-polling
    notification.  Falls back to FindWindowW polling if the hook fails.

    If h_restart is signaled while waiting, Dragon is launched.

    Returns True if Dragon was found, False if shutdown was requested.
    """
    if user32.FindWindowW(DRAGON_CLS, None):
        return True

    EVENT_OBJECT_CREATE = 0x8000
    WINEVENT_OUTOFCONTEXT = 0x0000
    OBJID_WINDOW = 0

    found_event = kernel32.CreateEventW(None, True, False, None)
    if not found_event:
        return _poll_for_dragon_window(h_shutdown, h_restart)

    def _on_event(hHook, event, hwnd, idObject, idChild, dwThread, dwTime):
        if event == EVENT_OBJECT_CREATE and idObject == OBJID_WINDOW and hwnd:
            buf = ctypes.create_unicode_buffer(256)
            if user32.GetClassNameW(hwnd, buf, 256) and buf.value == DRAGON_CLS:
                kernel32.SetEvent(found_event)

    callback = _WINEVENTPROC(_on_event)

    hook = user32.SetWinEventHook(
        EVENT_OBJECT_CREATE, EVENT_OBJECT_CREATE,
        None, callback, 0, 0, WINEVENT_OUTOFCONTEXT)

    if not hook:
        log.warning("SetWinEventHook failed, falling back to polling")
        kernel32.CloseHandle(found_event)
        return _poll_for_dragon_window(h_shutdown, h_restart)

    from ._pump import pump

    handles = [found_event]
    _FOUND_IDX = 0
    _SHUTDOWN_IDX = None
    _RESTART_IDX = None
    if h_shutdown:
        _SHUTDOWN_IDX = len(handles)
        handles.append(h_shutdown)
    if h_restart:
        _RESTART_IDX = len(handles)
        handles.append(h_restart)

    try:
        while True:
            rc = pump(h_events=handles, timeout_ms=2000)
            if rc == _FOUND_IDX:
                return True
            if _SHUTDOWN_IDX is not None and rc == _SHUTDOWN_IDX:
                return False
            if _RESTART_IDX is not None and rc == _RESTART_IDX:
                log.info("Restart event signaled while waiting — launching Dragon")
                from ._dragon import launch
                launch()
            if user32.FindWindowW(DRAGON_CLS, None):
                return True
    finally:
        user32.UnhookWinEvent(hook)
        kernel32.CloseHandle(found_event)


def _poll_for_dragon_window(h_shutdown=None, h_restart=None):
    """Fallback: poll FindWindowW every 2 seconds.

    Returns True if Dragon was found, False if shutdown was requested.
    """
    while not user32.FindWindowW(DRAGON_CLS, None):
        if h_shutdown and kernel32.WaitForSingleObject(h_shutdown, 0) == 0:
            return False
        if h_restart and kernel32.WaitForSingleObject(h_restart, 0) == 0:
            log.info("Restart event signaled while polling — launching Dragon")
            from ._dragon import launch
            launch()
        time.sleep(2)
    return True


# ---------------------------------------------------------------------------
# Wait for Dragon profile to be loaded (via log monitoring)
# ---------------------------------------------------------------------------

def dragon_log_dir(version):
    """Root of Dragon's per-profile log tree for a major version."""
    return (Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData"))
            / "Nuance" / f"NaturallySpeaking{version}" / "logs")


def find_dragon_log(version):
    """Newest Dragon.log across profile subdirectories, or None.

    Dragon keeps one subdirectory per profile plus a SYSTEM directory
    written once at install time. Taking the first match in directory order
    picks SYSTEM -- it sorts before real profile names and its Dragon.log
    never changes again, so a watcher on it can never observe anything.
    Most-recently-modified is the one Dragon is actually using.
    """
    base = dragon_log_dir(version)
    if not base.is_dir():
        log.debug("Dragon log dir not found: %s", base)
        return None

    newest = None
    newest_mtime = -1.0
    for entry in base.iterdir():
        candidate = entry / "Dragon.log"
        try:
            if not candidate.is_file():
                continue
            mtime = candidate.stat().st_mtime
        except OSError:
            continue
        if mtime > newest_mtime:
            newest, newest_mtime = candidate, mtime
    return newest


def _wait_for_profile_via_log(max_wait=30):
    """Wait for Dragon to fully load the profile by monitoring its log.

    Watches Dragon's log for 'updateModesMenu ... Normal mode' which
    signals the profile is loaded and Dragon is ready for voice commands.

    Returns False if the marker does not arrive. Note that Dragon only
    writes this log while its DragonLoggerService is running; with the
    service stopped there is nothing to observe and this always times out.
    """
    try:
        from ._config import load_config
        cfg = load_config()
        version = cfg.get("dragon", "version", fallback="16")
    except Exception:
        version = "16"

    dragon_log = find_dragon_log(version)
    if not dragon_log:
        log.debug("Dragon.log not found under %s", dragon_log_dir(version))
        return False

    try:
        start_pos = dragon_log.stat().st_size
    except OSError:
        start_pos = 0

    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        time.sleep(0.5)
        try:
            size = dragon_log.stat().st_size
            if size <= start_pos:
                continue
            with open(dragon_log, "r", encoding="utf-8", errors="replace") as f:
                f.seek(start_pos)
                new_content = f.read()
            start_pos = size  # advance so we don't re-read
            if _PROFILE_READY_RE.search(new_content):
                log.info("Dragon log: profile ready (Normal mode detected)")
                return True
        except Exception:
            pass

    log.debug("Dragon log: no Normal mode signal after %ds", max_wait)
    return False



def signal_restart():
    """Signal the launcher's main loop to restart Dragon.

    Called from the tray menu's worker thread. The actual restart
    runs on the main thread which owns the COM objects.
    """
    if _signal_named_event(_RESTART_EVENT_NAME):
        log.info("Restart event signaled")
        return True
    log.warning("Could not open restart event — launcher not running?")
    return False


# ---------------------------------------------------------------------------
# Shutdown / single instance
# ---------------------------------------------------------------------------

_MUTEX_NAME = "NatlinkLauncherMutex"
_SHUTDOWN_EVENT_NAME = "NatlinkShutdown"
_RESTART_EVENT_NAME = "NatlinkRestartDragon"
_DEACTIVATE_EVENT_NAME = "NatlinkDeactivate"  # issue #228: release Dragon
_ACTIVATE_EVENT_NAME = "NatlinkActivate"      # issue #228: reconnect Dragon
_EVENT_MODIFY_STATE = 0x0002
_instance_mutex = None  # prevent GC of mutex handle


def _signal_named_event(name):
    """Open a named auto-reset event and set it. Returns False if absent."""
    h = kernel32.OpenEventW(_EVENT_MODIFY_STATE, False, name)
    if not h:
        return False
    kernel32.SetEvent(h)
    kernel32.CloseHandle(h)
    return True


def signal_deactivate():
    """Signal the launcher's main loop to release Dragon (issue #228).

    Called from the tray menu's worker thread; the disconnect runs on the
    main thread which owns the COM objects.
    """
    if _signal_named_event(_DEACTIVATE_EVENT_NAME):
        log.info("Deactivate event signaled")
        return True
    log.warning("Could not open deactivate event — launcher not running?")
    return False


def signal_activate():
    """Signal the launcher's main loop to reconnect to Dragon (issue #228)."""
    if _signal_named_event(_ACTIVATE_EVENT_NAME):
        log.info("Activate event signaled")
        return True
    log.warning("Could not open activate event — launcher not running?")
    return False


def request_shutdown(timeout_ms=5000):
    """Signal the launcher to shut down cleanly.

    Returns True if the shutdown event was signaled (and, for external
    callers, the launcher exited within timeout_ms).
    Returns False if no launcher is running.
    """
    if not _signal_named_event(_SHUTDOWN_EVENT_NAME):
        return False

    # If called from inside the launcher process (tray Exit menu),
    # don't poll — the main loop handles cleanup after we return.
    if _instance_mutex is not None:
        return True

    # External caller (e.g., `natlink stop`) — wait for the launcher to exit.
    deadline = time.monotonic() + timeout_ms / 1000.0
    while time.monotonic() < deadline:
        mutex = kernel32.CreateMutexW(None, True, _MUTEX_NAME)
        err = ctypes.get_last_error()
        if err != 183:  # not ERROR_ALREADY_EXISTS — launcher exited
            kernel32.CloseHandle(mutex)
            return True
        kernel32.CloseHandle(mutex)
        time.sleep(0.2)
    return False


def _acquire_single_instance():
    """Ensure only one launcher runs. Stores mutex handle as module global."""
    global _instance_mutex
    _instance_mutex = kernel32.CreateMutexW(None, True, _MUTEX_NAME)
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        print("Natlink is already running.")
        sys.exit(0)



