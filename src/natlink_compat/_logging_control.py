"""Runtime control of log category levels.

JSON-shaped surface: string levels in and out, primitive args and
returns, safe for in-process callers and IPC bridges alike.
"""

import logging
from typing import Callable, Optional, Union

from ._state import _state
from ._logging_setup import (
    _default_levels,
    _category_registry,
    _parse_level,
    _W, _I, _D,
)

log = logging.getLogger("natlink.compat")

LevelLike = Union[int, str, None]

_INI_SECTION = "Logging.Levels"


def _level_to_int(level: LevelLike, default: int) -> int:
    if level is None:
        return default
    if isinstance(level, int):
        return level
    return _parse_level(str(level), default)


def _level_to_str(level: int) -> str:
    name = logging.getLevelName(level)
    return name if isinstance(name, str) else str(level)


def _modify_ini(mutate: Callable) -> None:
    """Read natlink.ini, apply *mutate(cfg)*, save.

    IO errors are logged at WARNING and re-raised-as-nothing — the
    in-memory filter mutation proceeds so the user's change takes
    effect for the current session even if persistence fails.
    """
    try:
        from natlink_com._config import load_config, save_config
        cfg = load_config()
        mutate(cfg)
        save_config(cfg)
    except Exception:
        log.warning("Failed to persist logging config to natlink.ini",
                    exc_info=True)


def _read_ini_override(name: str,
                       default_c: int,
                       default_f: int) -> "tuple[int, int]":
    """Return (client, file) from ``[Logging.Levels]`` or the defaults."""
    try:
        from natlink_com._config import load_config
        cfg = load_config()
    except Exception:
        return default_c, default_f
    if not cfg.has_section(_INI_SECTION):
        return default_c, default_f
    try:
        raw = cfg.get(_INI_SECTION, name, fallback="").strip()
    except Exception:
        return default_c, default_f
    if not raw:
        return default_c, default_f
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 2:
        return (_parse_level(parts[0], default_c),
                _parse_level(parts[1], default_f))
    lvl = _parse_level(parts[0], default_c)
    return lvl, lvl


def _effective_levels(name: str) -> "tuple[int, int]":
    """Current (client, file) — live filters if installed, else INI."""
    entry = _category_registry.get(name)
    if entry is not None:
        _, cf, ff = entry
        return cf.level, ff.level
    default_c, default_f = _default_levels.get(name, (_W, _I))
    return _read_ini_override(name, default_c, default_f)


def _apply_in_memory(name: str, client_int: int, file_int: int) -> None:
    """Mutate live filters / logger level for *name*. Caller holds the lock."""
    entry = _category_registry.get(name)
    if entry is not None:
        logger, cf, ff = entry
        cf.level = client_int
        ff.level = file_int
        logger.setLevel(min(client_int, file_int))
    else:
        logging.getLogger(name).setLevel(min(client_int, file_int))


def _ini_set_entry(cfg, name: str, client_int: int, file_int: int,
                   default_c: int, default_f: int) -> None:
    """Set or remove one entry. Ensures the section exists on add."""
    if client_int == default_c and file_int == default_f:
        if cfg.has_section(_INI_SECTION):
            cfg.remove_option(_INI_SECTION, name)
        return
    if not cfg.has_section(_INI_SECTION):
        cfg.add_section(_INI_SECTION)
    if client_int == file_int:
        cfg.set(_INI_SECTION, name, _level_to_str(client_int))
    else:
        cfg.set(_INI_SECTION, name,
                f"{_level_to_str(client_int)},{_level_to_str(file_int)}")


def _reset_all_in_memory() -> None:
    """Revert all live filters to declared defaults. Caller holds the lock."""
    for name, (logger_, cf, ff) in _category_registry.items():
        dc, df = _default_levels.get(name, (_W, _I))
        cf.level = dc
        ff.level = df
        logger_.setLevel(min(dc, df))


# ---------------------------------------------------------------------------
# Public read API
# ---------------------------------------------------------------------------

def _category_info(name: str, dc: int, df: int) -> dict:
    c, f = _effective_levels(name)
    return {
        "name": name,
        "client": _level_to_str(c),
        "file": _level_to_str(f),
        "default_client": _level_to_str(dc),
        "default_file": _level_to_str(df),
        "has_override": (c != dc) or (f != df),
    }


def _arbitrary_info(name: str) -> "Optional[dict]":
    """Category info for a name not in the declared taxonomy.

    Returns ``None`` when there's no customization at all: no INI
    entry *and* the logger's own level is NOTSET. Otherwise reports
    the override with ``default_*`` set to ``NOTSET`` so callers can
    distinguish declared from arbitrary entries.
    """
    ini_c, ini_f = _read_ini_override(name, logging.NOTSET, logging.NOTSET)
    live = logging.getLogger(name).level
    if ini_c == logging.NOTSET and ini_f == logging.NOTSET and live == logging.NOTSET:
        return None
    if ini_c != logging.NOTSET or ini_f != logging.NOTSET:
        c, f = ini_c, ini_f
    else:
        c, f = live, live
    return {
        "name": name,
        "client": _level_to_str(c),
        "file": _level_to_str(f),
        "default_client": "NOTSET",
        "default_file": "NOTSET",
        "has_override": True,
    }


def list_log_categories() -> "list[dict]":
    """Return every declared category plus any arbitrary overrides.

    Declared categories come first in their declaration order;
    arbitrary entries (names set via ``set_log_level`` outside the
    declared taxonomy, or present in ``[Logging.Levels]``) follow.
    """
    result = [_category_info(name, dc, df)
              for name, (dc, df) in _default_levels.items()]
    try:
        from natlink_com._config import load_config
        cfg = load_config()
    except Exception:
        return result
    if not cfg.has_section(_INI_SECTION):
        return result
    for opt in cfg.options(_INI_SECTION):
        if opt in _default_levels:
            continue
        info = _arbitrary_info(opt)
        if info is not None:
            result.append(info)
    return result


def get_log_category(name: str) -> "Optional[dict]":
    """Return one category's current state.

    Falls back to ``_arbitrary_info`` for names outside the declared
    taxonomy — returns ``None`` only when the name is undeclared *and*
    has no persistent override *and* the live logger level is NOTSET.
    """
    entry = _default_levels.get(name)
    if entry is not None:
        return _category_info(name, *entry)
    return _arbitrary_info(name)


# ---------------------------------------------------------------------------
# Public write API
# ---------------------------------------------------------------------------

def set_log_level(name: str,
                  level: LevelLike,
                  *,
                  file: LevelLike = None) -> None:
    """Set a category's level. ``file`` defaults to match ``level``."""
    dc, df = _default_levels.get(name, (_W, _I))
    c = _level_to_int(level, dc)
    f = _level_to_int(file, c)

    with _state.lock:
        _modify_ini(lambda cfg: _ini_set_entry(cfg, name, c, f, dc, df))
        _apply_in_memory(name, c, f)


def reset_log_level(name: str) -> None:
    """Revert one category to its declared default."""
    def _remove(cfg):
        if cfg.has_section(_INI_SECTION):
            cfg.remove_option(_INI_SECTION, name)

    with _state.lock:
        _modify_ini(_remove)
        if name in _default_levels:
            dc, df = _default_levels[name]
            _apply_in_memory(name, dc, df)
        else:
            logging.getLogger(name).setLevel(logging.NOTSET)


def reset_log_levels() -> None:
    """Revert every declared category to its default."""
    with _state.lock:
        _modify_ini(lambda cfg: cfg.remove_section(_INI_SECTION))
        _reset_all_in_memory()


# ---------------------------------------------------------------------------
# Presets — debug-mode groupings by user concern, not by layer
# ---------------------------------------------------------------------------

# Every preset currently bumps its categories to DEBUG; if a future preset
# needs a mixed level map, replace "categories" with a dict on that entry
# and generalize apply_log_preset.
_PRESETS: "list[dict]" = [
    {
        "id": "debug_grammar",
        "label": "Debug grammar",
        "description": (
            "Grammar load, activation, phrase recognition, "
            "and hypothesis callbacks."),
        "categories": [
            "natlink.com.grammar",
            "natlink.com.sink.grammar",
            "natlink.com.sink.grammar.hypothesis",
            "natlink.callbacks.grammar_begin",
            "natlink.callbacks.phrase_hypothesis",
        ],
    },
    {
        "id": "debug_dictation",
        "label": "Debug dictation",
        "description": (
            "Dictation objects, text-changed events, and JIT pauses."),
        "categories": [
            "natlink.com.dictation",
            "natlink.com.sink.dict",
            "natlink.com.sink.dict.text_changed",
            "natlink.callbacks.dict_text_changed",
        ],
    },
    {
        "id": "debug_connection",
        "label": "Debug connection",
        "description": (
            "COM connect/disconnect, TLB, marshal DLLs, launcher, "
            "and message pump."),
        "categories": [
            "natlink.com.conn",
            "natlink.com.tlb",
            "natlink.com.marshal",
            "natlink.com.launcher",
            "natlink.com.pump",
            "natlink.com.timer",
            "natlink.com.dragon",
            "natlink.com.sta",
            "natlink.com.sta.dispatch",
            "natlink.com.sta.drain",
            "natlink.com.sta.health",
            "natlink.com.sta.error",
        ],
    },
    {
        "id": "debug_loaders",
        "label": "Debug loaders",
        "description": (
            "Loader discovery, start/stop, and orchestrator lifecycle."),
        "categories": [
            "natlink.compat.loaders",
            "natlink.compat.launcher",
        ],
    },
    {
        "id": "debug_all",
        "label": "Debug everything",
        "description": "Bump all declared categories to DEBUG.",
        "categories": list(_default_levels),
    },
]


def list_log_presets() -> "list[dict]":
    """Return ``[{id, label, description}, ...]``."""
    return [
        {"id": p["id"], "label": p["label"], "description": p["description"]}
        for p in _PRESETS
    ]


def apply_log_preset(preset_id: str) -> None:
    """Replace all current overrides with the named preset."""
    preset = next((p for p in _PRESETS if p["id"] == preset_id), None)
    if preset is None:
        raise ValueError(f"Unknown logging preset: {preset_id!r}")

    names = preset["categories"]

    def _write(cfg):
        cfg.remove_section(_INI_SECTION)
        cfg.add_section(_INI_SECTION)
        for name in names:
            dc, df = _default_levels.get(name, (_W, _I))
            _ini_set_entry(cfg, name, _D, _D, dc, df)

    with _state.lock:
        _modify_ini(_write)
        _reset_all_in_memory()
        for name in names:
            _apply_in_memory(name, _D, _D)
