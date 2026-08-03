"""
Start, stop, restart, or check Dragon NaturallySpeaking.

Usage (standalone):
    python -m natlink_com._dragon start
    python -m natlink_com._dragon stop
    python -m natlink_com._dragon restart
    python -m natlink_com._dragon status

Also used by the tray menu and CLI.
"""

import argparse
import ctypes
import ctypes.wintypes as wt
import logging
import subprocess
import sys
import time

from ._win32 import is_dragon_running, kernel32 as _kernel32

log = logging.getLogger("natlink.com.dragon")

PROCESS_NAMES = ["natspeak.exe", "dragonbar.exe"]
DETACHED_PROCESS = 0x00000008

_PROCESS_TERMINATE = 0x0001
_TH32CS_SNAPPROCESS = 0x00000002


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wt.DWORD), ("cntUsage", wt.DWORD),
        ("th32ProcessID", wt.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
        ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wt.DWORD), ("szExeFile", wt.WCHAR * 260),
    ]


def _iter_dragon_pids():
    """Yield (exe_name, pid) for each running Dragon process."""
    targets = {n.lower() for n in PROCESS_NAMES}
    snap = _kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
    if snap == -1:
        return
    try:
        entry = _PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not _kernel32.Process32FirstW(snap, ctypes.byref(entry)):
            return
        while True:
            name = entry.szExeFile.lower()
            if name in targets:
                yield name, entry.th32ProcessID
            if not _kernel32.Process32NextW(snap, ctypes.byref(entry)):
                break
    finally:
        _kernel32.CloseHandle(snap)


def _kill_processes():
    """Kill Dragon processes using Win32 API."""
    for name, pid in _iter_dragon_pids():
        h = _kernel32.OpenProcess(_PROCESS_TERMINATE, False, pid)
        if h:
            _kernel32.TerminateProcess(h, 1)
            log.debug("TerminateProcess: %s (pid=%d)", name, pid)
            _kernel32.CloseHandle(h)


def _get_exe_path():
    """Get Dragon exe path from config."""
    try:
        from ._config import load_config
        cfg = load_config()
        exe = cfg.get("dragon", "exe_path", fallback="")
        if exe:
            return exe
    except Exception:
        pass
    log.error("Dragon exe_path not found in natlink.ini. Run: natlink-ui")
    return ""


def launch():
    """Launch the Dragon process without waiting.

    Returns True if the process was started (or already running),
    False if the executable was not found.
    """
    if is_dragon_running():
        log.info("Dragon is already running.")
        return True
    exe = _get_exe_path()
    if not exe:
        return False
    log.info("Launching Dragon: %s", exe)
    subprocess.Popen([exe], creationflags=DETACHED_PROCESS)
    return True


def start(wait=20):
    """Start Dragon and wait for initialization."""
    if not launch():
        return 1

    log.info("Waiting for Dragon to initialize (%ds)...", wait)
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if is_dragon_running():
            log.info("Dragon is running.")
            return 0
        time.sleep(1)

    if is_dragon_running():
        log.info("Dragon is running.")
        return 0
    log.error("Dragon did not start within %ds.", wait)
    return 1


def save_profile(conn=None):
    """Save the current Dragon user profile via COM.

    Args:
        conn: An active COM connection (NatlinkCOM.conn).
              Callers are responsible for obtaining it from _state.

    Returns True if saved, False if not connected or failed.
    """
    if conn is None:
        return False
    try:
        from ._user_ops import save_speaker
        save_speaker(conn)
        log.info("Dragon profile saved.")
        return True
    except Exception:
        log.warning("Could not save Dragon profile", exc_info=True)
        return False


def _close_dragon_windows():
    """Send WM_CLOSE to Dragon's main windows for graceful shutdown."""
    from ._win32 import user32, DRAGON_CLS
    WM_CLOSE = 0x0010

    for cls in [DRAGON_CLS, "DgnResultsBoxMainWindowCls"]:
        hwnd = user32.FindWindowW(cls, None)
        if hwnd:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            log.debug("Sent WM_CLOSE to %s (hwnd=%d)", cls, hwnd)


def _is_process_running():
    """Check if any Dragon process is still alive (not just the window)."""
    return any(True for _ in _iter_dragon_pids())


def stop(force=False, conn=None):
    """Stop Dragon. Saves profile first, then graceful close, then force-kill.

    Args:
        conn: Optional COM connection for saving the profile before shutdown.
    """
    if not _is_process_running():
        log.info("Dragon is not running.")
        return 0

    # Try to save the user profile before shutdown.
    save_profile(conn)

    if force:
        log.info("Force-killing Dragon...")
        _kill_processes()
        time.sleep(1)
    else:
        # Try graceful close via WM_CLOSE first.
        log.info("Stopping Dragon (graceful)...")
        _close_dragon_windows()
        # Wait for the process to exit, not just the window
        for i in range(15):
            if not _is_process_running():
                log.info("Dragon process exited after %ds", i)
                break
            time.sleep(1)
        else:
            log.info("Dragon still running after 15s wait")

        if _is_process_running():
            log.info("Graceful close failed, force-killing...")
            _kill_processes()
            time.sleep(2)

    if _is_process_running():
        log.error("Could not stop Dragon.")
        return 1

    log.info("Dragon stopped.")
    return 0


def restart(wait=20, force=True):
    """Stop then start Dragon."""
    rc = stop(force=force)
    if rc != 0:
        return rc
    return start(wait)


def status():
    """Return 0 if running, 1 if not."""
    if is_dragon_running():
        log.info("Dragon is running.")
        return 0
    log.info("Dragon is NOT running.")
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Dragon NaturallySpeaking manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"])
    parser.add_argument("--wait", type=int, default=20,
                        help="Seconds to wait after starting (default: 20)")
    parser.add_argument("--graceful", action="store_true",
                        help="Try graceful shutdown before force-kill")
    args = parser.parse_args()

    actions = {
        "start": lambda: start(args.wait),
        "stop": lambda: stop(force=not args.graceful),
        "restart": lambda: restart(args.wait, force=not args.graceful),
        "status": status,
    }
    sys.exit(actions[args.action]())
