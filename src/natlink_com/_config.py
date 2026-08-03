"""Natlink configuration — INI file management.

Stores Python environment path, Dragon info, and user preferences.
Created by runtime setup, read at runtime.
"""

import logging
import os
import sys
import winreg
from pathlib import Path

from ._ini_file import IniFile

log = logging.getLogger("natlink.com")

_CONFIG_DIR = Path(os.environ.get(
    "NATLINK_SETTINGS_DIR",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "natlink"),
))
_CONFIG_FILE = _CONFIG_DIR / "natlink.ini"

_ini = IniFile(_CONFIG_FILE)


def get_config_path():
    """Return the path to natlink.ini."""
    return _CONFIG_FILE


def load_config():
    """Load config from INI file. Returns ConfigParser (thread-safe)."""
    return _ini.load()


def save_config(cfg):
    """Save config to INI file (thread-safe)."""
    _ini.save(cfg)


def get_bool_setting(section, key, fallback=False):
    """Read a boolean setting from the INI."""
    return _ini.get_bool(section, key, fallback)


def set_bool_setting(section, key, value):
    """Write a boolean setting to the INI (ensures section exists)."""
    _ini.set_bool(section, key, value)


def toggle_bool_setting(section, key, fallback=False):
    """Toggle a boolean setting in the INI. Returns the new value."""
    return _ini.toggle_bool(section, key, fallback)


def find_dragon_install():
    """Find Dragon's install path and version from the uninstall registry.

    Returns (version: int, install_path: str, exe_path: str) or (0, '', '').
    """
    uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, uninstall_key,
                                    0, winreg.KEY_READ | view)
        except OSError:
            continue
        try:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    i += 1
                except OSError:
                    break
                try:
                    with winreg.OpenKeyEx(key, subkey_name, 0,
                                          winreg.KEY_READ | view) as sk:
                        name = winreg.QueryValueEx(sk, "DisplayName")[0]
                        if "Dragon" not in name:
                            continue
                        install_path = winreg.QueryValueEx(sk, "InstallLocation")[0]
                        version_str = winreg.QueryValueEx(sk, "DisplayVersion")[0]
                    major = int(version_str.split(".")[0])
                    exe = str(Path(install_path) / "Program" / "natspeak.exe")
                    return major, install_path.rstrip("\\"), exe
                except (FileNotFoundError, ValueError, OSError):
                    continue
        finally:
            winreg.CloseKey(key)
    return 0, "", ""


_cached_dragon_major = None


def detect_dragon_major() -> int:
    """Detect Dragon major version from INI or uninstall registry.

    Returns the major version (e.g. 16, 15, 13) or 0 if unknown.
    Result is cached per-process since Dragon version cannot change at runtime.
    """
    global _cached_dragon_major
    if _cached_dragon_major is not None:
        return _cached_dragon_major
    cfg = load_config()
    ver_str = cfg.get("dragon", "version", fallback="")
    if ver_str:
        try:
            ver = int(ver_str)
        except ValueError:
            ver = 0
        if 13 <= ver <= 20:
            log.debug("Dragon %d from natlink.ini", ver)
            _cached_dragon_major = ver
            return ver
        log.debug("Ignoring invalid dragon version %r in natlink.ini", ver_str)
    ver, _, _ = find_dragon_install()
    if ver:
        log.debug("Dragon %d from uninstall registry", ver)
    else:
        log.warning("Could not detect Dragon version from registry")
    _cached_dragon_major = ver
    return ver


def setup_config():
    """Detect environment, write INI, ensure COM overrides.

    Called on every entry path (install, start, start_tray) so the
    config always reflects the current venv and Dragon install.
    Idempotent — safe to call multiple times per process.
    """
    cfg = load_config()
    log.info("Config: %s (sections: %s)",
             _CONFIG_FILE, ", ".join(cfg.sections()) or "none")

    # --- Dragon detection ---
    version, install_path, exe_path = find_dragon_install()
    if version:
        if not cfg.has_section("dragon"):
            cfg.add_section("dragon")
        cfg.set("dragon", "version", str(version))
        cfg.set("dragon", "install_path", install_path)
        cfg.set("dragon", "exe_path", exe_path)

    # --- Python / venv path (updated every run) ---
    if not cfg.has_section("Launch"):
        cfg.add_section("Launch")
    cfg.set("Launch", "python", sys.executable)

    save_config(cfg)
    return cfg





def _set_loader(name, value):
    """Set a loader's state in the [loaders] section of natlink.ini."""
    cfg = load_config()
    if not cfg.has_section("loaders"):
        cfg.add_section("loaders")
    cfg.set("loaders", name, value)
    save_config(cfg)


def enable_loader(name):
    """Enable a loader in natlink.ini."""
    _set_loader(name, "enabled")


def disable_loader(name):
    """Disable a loader in natlink.ini."""
    _set_loader(name, "disabled")


def cli_main():
    """CLI entry point for low-level config management."""
    import argparse
    parser = argparse.ArgumentParser(description="Natlink Setup")
    parser.add_argument("--info", action="store_true",
                        help="Show current configuration")
    parser.add_argument("--setup", action="store_true",
                        help="Run setup (detect Dragon, store Python path)")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"),
                        help="Set a config value (e.g., --set debug true)")
    parser.add_argument("--enable-loader", metavar="NAME",
                        help="Enable a loader (e.g., --enable-loader dragonfly)")
    parser.add_argument("--disable-loader", metavar="NAME",
                        help="Disable a loader (e.g., --disable-loader dragonfly)")
    args = parser.parse_args()

    if args.setup:
        cfg = setup_config()
        print(f"Configuration saved to: {_CONFIG_FILE}")
        print()
        print_config(cfg)
    elif args.info:
        cfg = load_config()
        if not cfg.sections():
            print("No configuration found. Run: natlink-ui")
        else:
            print_config(cfg)
    elif args.set:
        cfg = load_config()
        key, value = args.set
        section, _, option = key.partition(".")
        if not option:
            section, option = "settings", section
        if not cfg.has_section(section):
            cfg.add_section(section)
        cfg.set(section, option, value)
        save_config(cfg)
        print(f"Set [{section}] {option} = {value}")
    elif args.enable_loader:
        enable_loader(args.enable_loader)
        print(f"Loader '{args.enable_loader}' enabled")
    elif args.disable_loader:
        disable_loader(args.disable_loader)
        print(f"Loader '{args.disable_loader}' disabled")
    else:
        parser.print_help()


def print_config(cfg):
    """Pretty-print configuration."""
    for section in cfg.sections():
        print(f"[{section}]")
        for key, value in cfg.items(section):
            print(f"  {key} = {value}")
        print()


if __name__ == "__main__":
    cli_main()
