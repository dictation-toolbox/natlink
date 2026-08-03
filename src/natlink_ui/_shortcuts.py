"""Shortcut management for the default natlink UI.

Handles: desktop shortcut, Windows Startup folder, exe discovery.
All paths and logic are specific to the default Win32 UI —
third-party UIs bring their own installation mechanisms.
"""

import ctypes
import ctypes.wintypes as wt
import logging
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

log = logging.getLogger("natlink.ui.shortcuts")

_shell32 = ctypes.windll.shell32
_shell32.SHGetKnownFolderPath.argtypes = [
    ctypes.POINTER(ctypes.c_byte), wt.DWORD, wt.HANDLE,
    ctypes.POINTER(ctypes.c_wchar_p),
]
_shell32.SHGetKnownFolderPath.restype = ctypes.c_long


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _icon_path() -> str:
    return str(Path(__file__).resolve().parent / "icons" / "natlink.ico")


def _startup_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise OSError("APPDATA environment variable is not set")
    return (Path(appdata)
            / "Microsoft" / "Windows" / "Start Menu"
            / "Programs" / "Startup" / "Natlink.lnk")


def _desktop_dir() -> Path:
    folder_id = (ctypes.c_byte * 16).from_buffer_copy(
        uuid.UUID("{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}").bytes_le
    )
    path_ptr = ctypes.c_wchar_p()
    hr = _shell32.SHGetKnownFolderPath(folder_id, 0, None, ctypes.byref(path_ptr))
    if hr < 0:
        raise OSError(f"SHGetKnownFolderPath(Desktop) failed: 0x{hr & 0xFFFFFFFF:08X}")
    result = path_ptr.value
    ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(path_ptr, ctypes.c_void_p))
    if not result:
        raise OSError("SHGetKnownFolderPath(Desktop) returned empty")
    return Path(result)


def _desktop_shortcut_path() -> Path:
    return _desktop_dir() / "Natlink.lnk"


def _find_ui_exe() -> str:
    """Find natlink-ui.exe.

    Checks beside the Python interpreter first (standard venv / uv pip
    install layout), then falls back to PATH so installs via ``uv tool
    install`` or ``pipx install`` — which put the exe in a shim dir
    outside sys.executable's parent — are still found.
    """
    name = "natlink-ui.exe"
    py_dir = Path(sys.executable).parent
    for candidate in (py_dir / name, py_dir / "Scripts" / name):
        if candidate.is_file():
            return str(candidate)
    resolved = shutil.which(name)
    if resolved:
        return resolved
    return ""


# ---------------------------------------------------------------------------
# Shortcut creation
# ---------------------------------------------------------------------------

def _create_shortcut(shortcut_path, target_path, **properties):
    """Create a Windows .lnk shortcut via PowerShell."""
    def _ps_escape(s):
        return str(s).replace("'", "''")
    props = ''.join(
        f"$s.{key} = '{_ps_escape(val)}'; "
        for key, val in properties.items() if val
    )
    ps_script = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{_ps_escape(shortcut_path)}'); "
        f"$s.TargetPath = '{_ps_escape(target_path)}'; "
        f"{props}"
        f"$s.Save()"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps_script],
        capture_output=True, timeout=10)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        log.warning("Shortcut creation failed (rc=%d): %s", result.returncode, stderr)
        return False
    return True


# ---------------------------------------------------------------------------
# Public operations
# ---------------------------------------------------------------------------

def is_startup_installed() -> bool:
    return _startup_path().is_file()


def install_startup():
    exe = _find_ui_exe()
    if not exe:
        print("natlink-ui.exe not found. Is natlink installed?")
        return False
    path = _startup_path()
    icon = _icon_path()
    created = _create_shortcut(
        str(path), exe,
        Description="Natlink — Dragon speech recognition bridge",
        IconLocation=f"{icon},0",
    )
    if created:
        print(f"Installed startup shortcut: {path}")
    return created


def uninstall_startup():
    path = _startup_path()
    try:
        existed = path.is_file()
        path.unlink(missing_ok=True)
        if existed:
            print(f"Removed: {path}")
        return existed
    except OSError:
        return False


def create_desktop_shortcut():
    try:
        path = _desktop_shortcut_path()
        if path.exists():
            return True
        exe = _find_ui_exe()
        if not exe:
            return False
        icon = _icon_path()
        created = _create_shortcut(
            str(path), exe,
            Description="Natlink — Dragon speech recognition bridge",
            IconLocation=f"{icon},0",
        )
        if created:
            print(f"Created desktop shortcut: {path}")
        return created
    except Exception:
        log.debug("Could not create desktop shortcut", exc_info=True)
        return False


def remove_desktop_shortcut():
    try:
        path = _desktop_shortcut_path()
        existed = path.exists()
        path.unlink(missing_ok=True)
        if existed:
            print(f"Removed: {path}")
        return existed
    except OSError:
        return False
