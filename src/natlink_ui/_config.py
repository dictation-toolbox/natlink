"""UI-specific configuration — separate from core natlink.ini.

Stored in natlink_ui.ini alongside natlink.ini. Third-party UIs
bring their own config — this file is specific to the default UI.
"""

import logging

from natlink_compat import IniFile

log = logging.getLogger("natlink.ui.config")


def _get_store() -> IniFile:
    """Lazy init — avoids import-time dependency on natlink_compat."""
    global _store
    try:
        return _store
    except NameError:
        import natlink_compat
        _store = IniFile(natlink_compat.get_config_dir() / "natlink_ui.ini")
        return _store


def load():
    return _get_store().load()


def save(cfg):
    _get_store().save(cfg)


def get_bool(section, key, fallback=False):
    return _get_store().get_bool(section, key, fallback)


def get_int(section, key, fallback=0):
    return _get_store().get_int(section, key, fallback)


def toggle_bool(section, key, fallback=False):
    return _get_store().toggle_bool(section, key, fallback)
