"""_logging_setup.py - Logging configuration and output redirect for natlink_compat.

Dragonfly-style logging: each category has independent (client, file) default
levels.  [Logging.Levels] in natlink.ini overrides per category.
"""

import configparser
import logging
import os
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Optional, Tuple

from ._state import _state

log = logging.getLogger("natlink.compat")
_log_root = logging.getLogger("natlink")

_W = logging.WARNING
_I = logging.INFO
_D = logging.DEBUG

# Numeric INI levels (1=Error..5=Trace) → Python logging levels
_LEVEL_MAP = {1: logging.ERROR, 2: _W, 3: _I, 4: _D, 5: _D}

# (client_level, file_level) — client = message window, file = rotating log
#
# Taxonomy by layer in the COM flow:
#   natlink.com.*         — COM backend: connection, TLB, marshal, results parsing
#   natlink.com.sink.*    — inbound notifications *from* Dragon (producer side)
#   natlink.callbacks.*   — dispatch *to* user Python callbacks (consumer side)
#   natlink.compat.*      — compat-layer glue (state, orchestration, ui dispatch)
#   natlink.ui.*          — tray window, shortcuts, UI config
#
# High-frequency children are pinned to INFO in the file log so normal
# operation stays legible.  Slow-callback warnings still propagate up.
# Bump any of them to DEBUG via [Logging.Levels] in natlink.ini to
# investigate a specific event.
_default_levels: Dict[str, Tuple[int, int]] = {
    "natlink":                                  (_W, _I),

    # COM backend — infrastructure, connection, type library, marshaling
    "natlink.com":                              (_W, _D),
    "natlink.com.conn":                         (_I, _D),
    "natlink.com.tlb":                          (_W, _I),
    "natlink.com.grammar":                      (_W, _I),
    "natlink.com.dictation":                    (_W, _I),
    "natlink.com.results":                      (_W, _I),
    "natlink.com.marshal":                      (_I, _I),
    "natlink.com.lexicon":                      (_W, _I),
    "natlink.com.launcher":                     (_I, _I),
    "natlink.com.dragon":                       (_W, _I),
    "natlink.com.sendinput":                    (_W, _I),
    "natlink.com.pump":                         (_W, _I),
    "natlink.com.timer":                        (_W, _I),  # WM_TIMER fires

    # STA dispatch machinery — closure queue + signal primitives in _hidden_wnd
    "natlink.com.sta":                          (_W, _I),  # lifecycle
    "natlink.com.sta.dispatch":                 (_W, _I),  # per-enqueue
    "natlink.com.sta.drain":                    (_W, _I),  # per-drain w/ timing
    "natlink.com.sta.health":                   (_W, _I),  # backlog / drops
    "natlink.com.sta.error":                    (_W, _D),  # handler exceptions

    # COM sinks — raw notifications arriving from Dragon
    "natlink.com.sink":                         (_W, _D),
    "natlink.com.sink.grammar":                 (_W, _D),
    "natlink.com.sink.grammar.hypothesis":      (_W, _I),  # per-partial
    "natlink.com.sink.dict":                    (_W, _D),
    "natlink.com.sink.dict.text_changed":       (_W, _I),  # per-edit
    "natlink.com.sink.engine":                  (_W, _D),
    "natlink.com.sink.engine.attrib_changed":   (_W, _I),  # MICSTATE etc., idle-chatty
    "natlink.com.sink.action":                  (_W, _D),

    # Compat dispatch — delivering events to user Python callbacks
    "natlink.callbacks":                        (_W, _D),
    "natlink.callbacks.timer":                  (_W, _I),  # ~60Hz poll
    "natlink.callbacks.begin":                  (_W, _I),  # per-utterance
    "natlink.callbacks.grammar_begin":          (_W, _I),  # N grammars × utterance
    "natlink.callbacks.phrase_finish":          (_W, _I),  # per-utterance
    "natlink.callbacks.phrase_hypothesis":      (_W, _I),  # per-partial
    "natlink.callbacks.change":                 (_W, _I),  # mic/user state
    "natlink.callbacks.dict_begin":             (_W, _I),  # per-dictation-begin
    "natlink.callbacks.dict_text_changed":      (_W, _I),  # per-edit

    # Compat layer — state, orchestration, loaders, UI dispatch
    "natlink.compat":                           (_W, _I),
    "natlink.compat.launcher":                  (_I, _I),
    "natlink.compat.loaders":                   (_I, _I),

    # UI layer — tray window, shortcuts, config (children propagate up)
    "natlink.ui":                               (_W, _I),
}

_FILE_FORMAT = (
    "[%(asctime)s.%(msecs)03d][%(levelname)-5s]"
    "[%(threadName)s][%(name)s] %(message)s"
)
_FILE_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _parse_level(value: str, default: int) -> int:
    """Parse a log level from string — accepts int (1-5) or name (ERROR, DEBUG, etc.)."""
    value = value.strip()
    if not value:
        return default
    try:
        return _LEVEL_MAP.get(int(value), _I)
    except ValueError:
        pass
    numeric = getattr(logging, value.upper(), None)
    if isinstance(numeric, int):
        return numeric
    return default


class _NameLevelFilter(logging.Filter):
    """Pass records from this logger (or unregistered children) at or above a threshold."""

    def __init__(self, name: str, level: int):
        super().__init__(name)
        self.level = level
        self._prefix = name + "."

    def filter(self, record: logging.LogRecord) -> bool:
        # Apply threshold to this logger and any child that propagated up
        if record.name == self.name or record.name.startswith(self._prefix):
            return record.levelno >= self.level
        return True


class _DispatchingHandler(logging.Handler):
    """Routes records to multiple handlers, each with its own filter."""

    def __init__(self):
        super().__init__()
        self._targets: list = []

    def add_target(self, handler: logging.Handler, filt: logging.Filter):
        self._targets.append((handler, filt))

    def emit(self, record: logging.LogRecord) -> None:
        for handler, filt in self._targets:
            if filt.filter(record):
                handler.handle(record)


class _NotifyTextHandler(logging.Handler):
    """Logging handler that routes log records through notify_text().

    This reaches all registered UIProviders automatically — no separate
    registration needed. The UI provider just implements on_text().
    """

    _guard = threading.local()

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(self._guard, "in_emit", False):
            return
        self._guard.in_emit = True
        try:
            from ._ui_protocol import notify_text
            msg = self.format(record) + "\r\n"
            notify_text(msg, level=record.levelno)
        except Exception:
            pass
        finally:
            self._guard.in_emit = False


_file_handler: Optional[RotatingFileHandler] = None
_notify_handler: Optional[_NotifyTextHandler] = None
_installed_loggers: list = []

# (logger, client_filter, file_filter) per category — in-place mutation
# target for _logging_control.set_log_level.
_category_registry: Dict[str, Tuple[
    logging.Logger, "_NameLevelFilter", "_NameLevelFilter"
]] = {}

# Saved originals for stdout/stderr redirect undo
_original_stdout = None
_original_stderr = None


def _resolve_log_path() -> Path:
    """Compute the log file path from env vars and INI config."""
    log_cfg = _read_log_config()
    raw = (
        os.environ.get("NATLINK_LOG_PATH")
        or log_cfg.get("log_file", "")
    )
    if raw:
        return Path(raw)
    return Path(os.environ.get("LOCALAPPDATA", "")) / "natlink" / "natlink.log"


def init_file_logging(rotate=True):
    """Create the file handler and attach it to the root logger.

    Call this once at process start (from the launcher) so that all
    startup phases are captured.  _setup_logging_and_redirect() later
    reuses the same handler inside per-category dispatching handlers.

    Pass ``rotate=False`` to use a plain FileHandler (no rotation or
    rollover) — useful for test runs where rotation is unwanted.
    """
    global _file_handler
    if _file_handler is not None:
        return

    log_path = _resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if rotate:
        fh = RotatingFileHandler(
            log_path, maxBytes=5 * 1024 * 1024, backupCount=10,
            encoding="utf-8")
        try:
            if log_path.stat().st_size > 0:
                fh.doRollover()
        except OSError:
            pass
    else:
        fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_FILE_FORMAT, datefmt=_FILE_DATEFMT))
    _file_handler = fh

    # Attach directly to "natlink" root so early startup logs are captured.
    # _setup_logging_and_redirect() will detach this and re-route through
    # per-category dispatching handlers.
    _log_root.addHandler(fh)

    global _notify_handler
    _notify_handler = _NotifyTextHandler()
    _notify_handler.setLevel(logging.INFO)
    _notify_handler.setFormatter(logging.Formatter(
        "[%(name)s] %(message)s"))
    _log_root.addHandler(_notify_handler)

    _log_root.setLevel(logging.DEBUG)


def _read_log_config() -> dict:
    """Read logging config from natlink.ini.

    Returns dict with keys: log_file, slow_callback_ms, category_levels.
    category_levels maps name -> (client_level, file_level).
    """
    result = {
        "log_file": "",
        "slow_callback_ms": 500,
        "category_levels": {},
    }
    from natlink_com._config import load_config
    config = load_config()
    if not config.sections():
        return result

    try:
        result["log_file"] = config.get("Logging", "LogFile", fallback="")
    except configparser.Error:
        pass
    try:
        result["slow_callback_ms"] = config.getint(
            "Logging", "SlowCallbackMs", fallback=500)
    except (ValueError, configparser.Error):
        pass

    # Global overrides for ClientLevel / FileLevel apply to root
    global_client = None
    global_file = None
    try:
        raw = config.get("Logging", "ClientLevel", fallback="")
        if raw.strip():
            global_client = _parse_level(raw, _W)
    except configparser.Error:
        pass
    try:
        raw = config.get("Logging", "FileLevel", fallback="")
        if raw.strip():
            global_file = _parse_level(raw, _I)
    except configparser.Error:
        pass
    if global_client is not None or global_file is not None:
        base_c, base_f = _default_levels.get("natlink", (_W, _I))
        result["category_levels"]["natlink"] = (
            global_client if global_client is not None else base_c,
            global_file if global_file is not None else base_f,
        )

    # Per-category overrides: [Logging.Levels]
    section = "Logging.Levels"
    if config.has_section(section):
        for name, value in config.items(section):
            # Value can be a single level or "client,file"
            parts = [v.strip() for v in value.split(",")]
            if len(parts) == 2:
                base_c, base_f = _default_levels.get(name, (_W, _I))
                c = _parse_level(parts[0], base_c)
                f = _parse_level(parts[1], base_f)
                result["category_levels"][name] = (c, f)
            else:
                level = _parse_level(parts[0], _W)
                result["category_levels"][name] = (level, level)

    return result


def _remove_handlers():
    """Detach dispatching handlers from loggers and reset their config.

    The shared _file_handler is kept open — it persists for the process
    lifetime.

    Caller must hold _state.lock.
    """
    global _installed_loggers
    for name in set(_installed_loggers) | set(_default_levels):
        logger = logging.getLogger(name)
        for h in logger.handlers[:]:
            if h is not _file_handler:
                try:
                    h.close()
                except Exception:
                    pass
        logger.handlers.clear()
        logger.filters.clear()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True
    _installed_loggers = []
    _category_registry.clear()


def _setup_logging_and_redirect():
    """Set up stdout/stderr redirect and logging handlers for the connection.

    Dragonfly-style: each category gets its own logger with per-handler
    level filters.  [Logging.Levels] in INI overrides defaults.

    Reuses the shared _file_handler created by init_file_logging().
    """
    def _delegate_fileno(stream, original):
        """Give natlinkcore's redirect stream a working ``fileno()``.

        ``natlinkcore.redirect_output.FakeTextIO.fileno()`` raises
        NotImplementedError, so once ``redirect()`` is installed anything
        needing a real file descriptor breaks process-wide for the rest of
        the session: ``subprocess(..., stderr=sys.stderr)``, logging
        handlers, and pytest's capture machinery.  Delegate to the stream we
        just replaced; if that one has no descriptor either, leave the
        stream as-is rather than promise a descriptor we do not have.
        """
        try:
            fd = original.fileno()
        except Exception:
            return
        try:
            stream.fileno = lambda: fd
        except Exception:
            log.debug("could not install fileno() on %r", stream, exc_info=True)

    with _state.lock:
        global _original_stdout, _original_stderr
        global _file_handler, _notify_handler, _installed_loggers
        try:
            import sys as _sys2
            _original_stdout = _sys2.stdout
            _original_stderr = _sys2.stderr
            from natlinkcore.redirect_output import redirect
            redirect()
            _delegate_fileno(_sys2.stdout, _original_stdout)
            _delegate_fileno(_sys2.stderr, _original_stderr)
        except Exception:
            log.debug("redirect_output not available", exc_info=True)

        _remove_handlers()
        try:
            log_cfg = _read_log_config()
            _state.slow_callback_ms = log_cfg["slow_callback_ms"]

            # Reuse the shared file handler; create one if init_file_logging
            # was never called (e.g. standalone natConnect without launcher).
            fh = _file_handler
            if fh is None:
                init_file_logging()
                fh = _file_handler
                # init_file_logging adds fh (+ ui_handler) directly to root
                # for early startup logging.  Remove them now — the per-
                # category dispatch handlers below will route instead.
                _log_root.handlers.clear()

            # Merge defaults with INI overrides
            merged = dict(_default_levels)
            merged.update(log_cfg["category_levels"])

            # Dragonfly pattern: each category logger gets a dispatching
            # handler that routes to file + UI through per-name level filters.
            nh = _notify_handler
            if nh is None:
                nh = _NotifyTextHandler()
                nh.setLevel(logging.DEBUG)
                nh.setFormatter(logging.Formatter(
                    "[%(threadName)s][%(name)s] %(message)s"))
                _notify_handler = nh

            # Silence noisy third-party loggers
            logging.getLogger("comtypes").setLevel(logging.WARNING)

            for name, (client_level, file_level) in merged.items():
                logger = logging.getLogger(name)
                logger.setLevel(min(client_level, file_level))
                logger.propagate = False

                client_filter = _NameLevelFilter(name, client_level)
                file_filter = _NameLevelFilter(name, file_level)

                dispatch = _DispatchingHandler()
                dispatch.add_target(nh, client_filter)
                dispatch.add_target(fh, file_filter)
                logger.addHandler(dispatch)

                _installed_loggers.append(name)
                _category_registry[name] = (logger, client_filter, file_filter)

        except Exception:
            import traceback
            traceback.print_exc()
            # Fallback: basic stderr logging so messages aren't silently lost
            _fallback_setup()


def _fallback_setup():
    """Install minimal stderr handler on root so log output isn't silently lost."""
    import sys
    _remove_handlers()
    root = logging.getLogger("natlink")
    root.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "[%(levelname)s][%(name)s] %(message)s"))
    root.addHandler(handler)


def teardown_logging():
    """Remove logging handlers, close the file handler, and restore stdout/stderr.

    Called during natDisconnect to flush logs and undo stdout/stderr redirection.
    """
    import sys as _sys

    with _state.lock:
        global _original_stdout, _original_stderr, _file_handler
        _remove_handlers()

        if _file_handler is not None:
            _file_handler.close()
            _file_handler = None

        if _original_stdout is not None:
            _sys.stdout = _original_stdout
            _sys.stderr = _original_stderr
            _original_stdout = None
            _original_stderr = None


def ensure_natlinkcore_logging() -> None:
    """Display a summary of modules that failed to load.

    Call this AFTER natlinkcore.loader.run().
    """
    if not _state.connected:
        return

    try:
        from ._ui_protocol import notify_text
        for entry in _state.loader_registry:
            loader = entry.loader
            bad = getattr(loader, "bad_modules", set())
            if bad:
                notify_text(
                    f"\r\n--- {len(bad)} module(s) failed to load ---\r\n",
                    level=logging.ERROR,
                )
                for mod_path in sorted(bad, key=str):
                    name_str = os.path.basename(str(mod_path))
                    notify_text(f"  FAILED: {name_str}\r\n", level=logging.ERROR)
                notify_text("\r\n")
    except Exception:
        pass
