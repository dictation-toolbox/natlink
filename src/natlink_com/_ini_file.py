"""Reusable INI file wrapper — thread-safe load/save/get/toggle.

Used by natlink_com._config (natlink.ini) and natlink_ui._config
(natlink_ui.ini) to avoid duplicating ConfigParser boilerplate.
"""

import configparser
import threading
from pathlib import Path


class IniFile:
    """Thread-safe wrapper around a single INI file."""

    def __init__(self, path: Path):
        self._path = path
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> configparser.ConfigParser:
        cfg = configparser.ConfigParser()
        with self._lock:
            if self._path.is_file():
                cfg.read(str(self._path), encoding="utf-8")
        return cfg

    def save(self, cfg: configparser.ConfigParser) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                cfg.write(f)

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        return self.load().getboolean(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        return self.load().getint(section, key, fallback=fallback)

    def set_value(self, section: str, key: str, value: str) -> None:
        cfg = self.load()
        if not cfg.has_section(section):
            cfg.add_section(section)
        cfg.set(section, key, value)
        self.save(cfg)

    def set_bool(self, section: str, key: str, value: bool) -> None:
        self.set_value(section, key, "true" if value else "false")

    def toggle_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Toggle a boolean setting. Returns the new value."""
        current = self.get_bool(section, key, fallback)
        self.set_bool(section, key, not current)
        return not current
