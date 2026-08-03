"""_loaders.py - Loader discovery, lifecycle, and runtime management.

Consolidates all loader concerns: discovery (entry points + natlinkcore
fallback), start/stop/reload, and the public add/remove/get API.

Multiple loaders can be active simultaneously (e.g. natlinkcore + dragonfly).
"""

import importlib
import logging
import sys as _sys
import traceback
from dataclasses import dataclass, field
from typing import List

from ._logging_setup import _NotifyTextHandler
from ._state import _state

log = logging.getLogger("natlink.compat.loaders")


@dataclass
class _LoaderEntry:
    """One active loader in the registry."""
    loader: object
    mod_name: str = ""
    name: str = ""
    # False while a loader is registered but its start()/run() has not been
    # called — the state add_loader() leaves behind when invoked before
    # natConnect. Registry membership alone cannot mean "running": the tray
    # and get_loader_states() would report a loader that never started.
    started: bool = False

    def __post_init__(self):
        if not self.name:
            self.name = getattr(self.loader, "__name__", None) or type(self.loader).__name__

    @property
    def base_name(self):
        """Top-level package name (e.g. 'natlinkcore' from 'natlinkcore.loader')."""
        return self.mod_name.split(".")[0] if self.mod_name else ""


# The registry lives in _state; these helpers access it.
def _find_entry(loader) -> '_LoaderEntry | None':
    """Find registry entry for a loader object."""
    for entry in _state.loader_registry:
        if entry.loader is loader:
            return entry
    return None


def _find_entry_by_name(name: str) -> '_LoaderEntry | None':
    """Find registry entry by base name."""
    for entry in _state.loader_registry:
        if entry.base_name == name:
            return entry
    return None


def _register(loader, mod_name="", started=False):
    """Add a loader to the registry. No-op if already present."""
    if _find_entry(loader) is not None:
        return
    _state.loader_registry.append(
        _LoaderEntry(loader=loader, mod_name=mod_name, started=started))


def _unregister(loader):
    """Remove a loader from the registry."""
    _state.loader_registry[:] = [e for e in _state.loader_registry if e.loader is not loader]


def _display(text, level=20):
    """Write to the message window if available."""
    try:
        from ._ui_protocol import notify_text
        notify_text(text, level)
    except Exception:
        log.debug("_display failed", exc_info=True)


def _on_loaders_changed():
    """Invalidate loader cache and push to UI."""
    try:
        from ._actions import invalidate_loader_cache
        invalidate_loader_cache()
        from ._ui_protocol import notify_ui
        notify_ui()
    except Exception:
        log.debug("_on_loaders_changed failed", exc_info=True)


# ---------------------------------------------------------------------------
# Public naming helpers (used by _actions.py)
# ---------------------------------------------------------------------------

def _loader_name(loader):
    """Best-effort human-readable name for a loader."""
    entry = _find_entry(loader)
    if entry:
        return entry.name
    return getattr(loader, "__name__", None) or type(loader).__name__


def _loader_base_name(loader):
    """Top-level package name (e.g. 'natlinkcore' from 'natlinkcore.loader')."""
    entry = _find_entry(loader)
    if entry:
        return entry.base_name
    return ""


def _get_module_name(loader):
    """Return the module name string for a loader, or '' if unknown."""
    entry = _find_entry(loader)
    return entry.mod_name if entry else ""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def get_disabled_loaders():
    """Read [loaders] section from natlink.ini to find disabled loaders.

    Returns a set of loader names marked 'disabled'.
    """
    try:
        from natlink_com._config import load_config
        cfg = load_config()
        if not cfg.has_section("loaders"):
            return set()
        return {
            name for name, value in cfg.items("loaders")
            if value.strip().lower() == "disabled"
        }
    except Exception:
        log.debug("Could not read [loaders] config", exc_info=True)
        return set()


def get_all_loader_names():
    """Return all discoverable loader names (entry points + natlinkcore fallback).

    Returns list of (name, module_path) tuples. Does not import modules.
    """
    names = []
    try:
        from importlib.metadata import entry_points
        for ep in entry_points(group="natlink.loaders"):
            names.append((ep.name, ep.value))
    except Exception:
        pass
    if not any(n == "natlinkcore" for n, _ in names):
        from importlib.util import find_spec
        if find_spec("natlinkcore.loader") is not None:
            names.append(("natlinkcore", "natlinkcore.loader"))
    return names


def discover_and_import():
    """Find and import all enabled loaders.

    Returns list of (module, module_name_str) tuples.
    """
    all_names = get_all_loader_names()
    if not all_names:
        log.warning("No loaders discovered.")
        return []

    disabled = get_disabled_loaders()
    if log.isEnabledFor(logging.DEBUG):
        log.debug("Loader discovery: found %d loader(s)", len(all_names))
        for name, mod_path in all_names:
            status = "disabled" if name in disabled else "enabled"
            log.debug("  %s (%s) [%s]", name, mod_path, status)

    loaders = []
    for name, mod_path in all_names:
        if name in disabled:
            log.info("Loader disabled in config, skipping: %s", name)
            continue
        try:
            mod = importlib.import_module(mod_path)
            loaders.append((mod, mod_path))
            log.info("Discovered loader: %s (%s)", name, mod_path)
        except Exception:
            log.exception("Failed to load loader: %s", name)

    if not loaders:
        log.warning("All discovered loaders are disabled. Check [loaders] in natlink.ini.")

    return loaders


# ---------------------------------------------------------------------------
# Start / stop
# ---------------------------------------------------------------------------

def _adopt_loader_logger(loader, mod_name):
    """Wire a loader's logger into the messages window.

    Replaces any StreamHandler the loader installed with a
    _NotifyTextHandler so output goes directly to the UI —
    no dependency on stdout redirect.

    Loaders can opt out by setting ``natlink_manage_logging = False``.
    Called after start() so the loader's own setup is complete.
    """
    if not mod_name:
        return
    if getattr(loader, "natlink_manage_logging", True) is False:
        return
    base = mod_name.split(".")[0]
    logger = logging.getLogger(base)
    if any(isinstance(h, _NotifyTextHandler) for h in logger.handlers):
        return
    for h in logger.handlers[:]:
        if type(h) is logging.StreamHandler:
            logger.removeHandler(h)
    nh = _NotifyTextHandler()
    nh.setLevel(logging.INFO)
    nh.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    logger.addHandler(nh)


def _start_impl(loader, mod_name=""):
    """Call start() on a loader. Returns True on success, False on failure."""
    name = _loader_name(loader) or mod_name
    try:
        start_fn = getattr(loader, "start", None) or getattr(loader, "run", None)
        if start_fn is None:
            raise AttributeError(f"{name} has no start() or run()")
        log.info("Starting loader: %s", name)
        # Tag callbacks registered during start() with this loader's package
        # so reload/remove can release exactly its begin/change/timer callbacks.
        from ._callbacks import loader_registration
        with loader_registration(loader):
            start_fn()
        _adopt_loader_logger(loader, mod_name)
        log.info("Loader started: %s", name)
        return True
    except Exception:
        log.exception("Loader failed to start: %s", name)
        _display(f"Loader failed: {name}\r\n", level=40)
        _display(traceback.format_exc(), level=40)
        return False


def start_loader(loader, mod_name="", *, _notify=True):
    """Start a loader and register it.

    Handles loaders that self-register during start() (e.g. natlinkcore
    sets natlink.active_loader = self) and loaders that don't.
    Returns True if the loader started successfully.

    _notify: if False, skip _on_loaders_changed (caller will batch).
    """
    count_before = len(_state.loader_registry)

    ok = _start_impl(loader, mod_name=mod_name)
    if not ok:
        return False

    # Detect if loader self-registered during start()
    self_registered = len(_state.loader_registry) > count_before
    if self_registered:
        entry = _state.loader_registry[-1]
        if mod_name and not entry.mod_name:
            entry.mod_name = mod_name
        entry.started = True
    elif _find_entry(loader) is None:
        _register(loader, mod_name, started=True)
        log.info("Loader registered (already running): %s", _loader_name(loader))
    else:
        _find_entry(loader).started = True

    if _notify:
        _on_loaders_changed()
    return True


def stop_loader(loader):
    """Stop a single loader.

    Entry-point frameworks are authoritative for their own cleanup:
    grammars, callbacks, timers, imported grammar modules, and framework-level
    references.
    """
    name = _loader_name(loader)
    log.info("Stopping loader: %s", name)
    try:
        if hasattr(loader, "stop"):
            loader.stop()
        elif hasattr(loader, "unload_all_loaded_modules"):
            loader.unload_all_loaded_modules()
    except Exception:
        log.exception("Loader stop failed: %s", name)

def stop_loaders():
    """Stop all active loaders. Called by natDisconnect."""
    for entry in list(_state.loader_registry):
        stop_loader(entry.loader)
    clear_all()


# ---------------------------------------------------------------------------
# Public API: add / remove / reload / get
# ---------------------------------------------------------------------------

def add_loader(loaders, *, _module_name=""):
    """Add and start one or more loaders.

    Accepts a single loader or a list. Each must have a start() or run()
    method. If connected, start() is called immediately.
    """
    for loader in _as_list(loaders):
        if _find_entry(loader) is not None:
            log.debug("add_loader: %s already active", _loader_name(loader))
            continue
        from ._loader_protocol import is_loader
        if not is_loader(loader):
            raise TypeError(
                f"Loader must have start() or run(), got {type(loader)}")
        if _state.connected:
            start_loader(loader, _module_name)
        else:
            _register(loader, _module_name)
            log.info("Loader added: %s", _loader_name(loader))
            _on_loaders_changed()


def remove_loader(loaders):
    """Stop and remove one or more loaders. No-op for inactive loaders."""
    for loader in _as_list(loaders):
        if _find_entry(loader) is None:
            continue
        stop_loader(loader)
        # Backstop after the framework's own teardown: release only what is
        # demonstrably this loader's and was not cleaned up.
        release_objects_for(loader)
        _unregister(loader)
        log.info("Loader removed: %s", _loader_name(loader))
    _on_loaders_changed()


def reload_loader(loaders=None):
    """Reload grammars for one, several, or all loaders.

    If the loader has trigger_load() (natlinkcore), calls it in-place.
    Otherwise falls back to full stop/reimport/restart.
    """
    if loaders is None:
        targets = [(e.loader, e.mod_name) for e in list(_state.loader_registry)]
    else:
        targets = []
        for loader in _as_list(loaders):
            entry = _find_entry(loader)
            targets.append((loader, entry.mod_name if entry else ""))

    if not targets:
        _display("No active loaders to reload.\r\n")
        return

    for target, mod_name in targets:
        trigger = getattr(target, "trigger_load", None)
        if trigger is not None:
            name = _loader_name(target)
            log.info("Reloading grammars: %s", name)
            _display(f"Reloading grammars ({name})...\r\n")
            try:
                from ._callbacks import loader_registration
                with loader_registration(target):
                    trigger(force_load=True)
                _display(f"Grammars reloaded.\r\n")
            except Exception:
                log.exception("trigger_load failed: %s", name)
                _display(f"Reload failed: {name}\r\n", level=40)
            continue

        # Slow path: full stop/reimport/restart
        from ._callbacks import _remove_callbacks_for
        _remove_callbacks_for(target)
        if _find_entry(target) is not None:
            stop_loader(target)
            _unregister(target)

        if mod_name:
            mod = _sys.modules.get(mod_name)
            try:
                if mod is not None:
                    importlib.reload(mod)
                else:
                    mod = importlib.import_module(mod_name)
                start_loader(mod, mod_name, _notify=False)
            except Exception:
                log.exception("Failed to reload loader: %s", mod_name)
        else:
            log.warning("Cannot reload %s: no module name known",
                        _loader_name(target))
    _on_loaders_changed()


def register_running_loader(loader):
    """Register a loader that is already running.

    Supports frameworks that publish their active loader object from inside
    start/run, such as natlinkcore's natlink.active_loader pattern.
    """
    if loader is None:
        # `natlink.active_loader = None` is how a loader publishes that it has
        # shut down. Registering it would put a NoneType entry in the registry
        # and get_loaders() would hand callers a None.
        return
    if _find_entry(loader) is not None:
        _find_entry(loader).started = True
        return
    _register(loader, started=True)
    log.info("Loader registered (already running): %s", _loader_name(loader))
    _on_loaders_changed()


def get_loaders():
    """Return a list of all active loader objects (snapshot)."""
    return [e.loader for e in _state.loader_registry]


def _objects_owned_by(pkg, registry):
    with _state.lock:
        return [o for o in registry.values()
                if getattr(o, "_owner_pkg", None) == pkg]


def get_grammars_for(loader):
    """Grammars created while *loader* was starting, reloading, or dispatching.

    Objects created outside any loader context are unattributed and never
    returned here.
    """
    # Same notion of "package" callbacks use, so ownership agrees across both.
    # Deferred: _callbacks imports this module (cycle: _loaders -> _callbacks).
    from ._callbacks import _loader_package
    pkg = _loader_package(loader)
    return _objects_owned_by(pkg, _state.grammar_registry) if pkg else []


def get_dictation_objects_for(loader):
    """Dictation objects attributed to *loader*. See get_grammars_for."""
    from ._callbacks import _loader_package
    pkg = _loader_package(loader)
    return _objects_owned_by(pkg, _state.dict_registry) if pkg else []


def release_objects_for(loader):
    """Unload *loader*'s grammars and destroy its dictation objects.

    Called by ``remove_loader`` after the framework's own ``stop()`` has run,
    so it only ever acts on what that teardown left behind. A framework that
    cleans up properly makes this a no-op.

    This does not conflict with "frameworks are authoritative for their own
    cleanup". That contract exists so natlink does not *guess* -- see
    ``_remove_callbacks_for``, which falls back to inference and could take
    another loader's callbacks. Objects do not need guessing: each records the
    loader it was created under, and unattributed objects are never touched.
    Leaving a removed loader's grammars loaded is not neutral -- Dragon keeps
    recognising them, so the user disables a loader and its commands still fire.

    ``deactivate()`` is not enough for dictation objects: Dragon holds every
    reference until ``destroy()``.

    Returns ``(grammars_released, dictation_released)``.
    """
    grams = get_grammars_for(loader)
    dicts = get_dictation_objects_for(loader)
    for g in grams:
        try:
            g.unload()
        except Exception:
            log.debug("releasing grammar for %s failed", _loader_name(loader),
                      exc_info=True)
    for d in dicts:
        try:
            d.destroy()
        except Exception:
            log.debug("releasing dictation object for %s failed",
                      _loader_name(loader), exc_info=True)
    if grams or dicts:
        # Reaching here means the loader's own teardown left these behind.
        log.info("Released %d grammar(s) and %d dictation object(s) left by %s",
                 len(grams), len(dicts), _loader_name(loader))
    return len(grams), len(dicts)


def get_running_loaders():
    """Loaders whose start()/run() has actually been called."""
    return [e.loader for e in _state.loader_registry if e.started]


def start_pending_loaders():
    """Start loaders registered before the connection existed.

    ``add_loader()`` called while disconnected can only register — there is no
    engine for the loader to attach to yet. Nothing started them afterwards,
    so they stayed registered-but-never-started while being reported as
    running. natConnect calls this once the backend is up.
    """
    pending = [e for e in _state.loader_registry if not e.started]
    for entry in pending:
        log.info("Starting loader deferred from before connect: %s", entry.name)
        start_loader(entry.loader, entry.mod_name, _notify=False)
    if pending:
        _on_loaders_changed()
    return len(pending)


def clear_all():
    """Clear the loader registry."""
    _state.loader_registry.clear()


def _as_list(loader_or_loaders):
    """Normalize a single loader or list to a list."""
    if isinstance(loader_or_loaders, (list, tuple)):
        return list(loader_or_loaders)
    return [loader_or_loaders]
