"""_lifecycle.py - Connection lifecycle: natConnect, natDisconnect, waitForSpeech.

Natlink is a "global client" — not tied to a specific application window.
"This implementation is designed to be a global client and not a app-specific
client.  That decision simplifies the design somewhat."
— Joel Gould, appsupp.cpp

As a global client, Dragon calls Register once at startup and UnRegister once
at shutdown.  AddProcess/EndProcess (per-app lifecycle) are no-ops.
"""

import atexit
import contextlib
import logging
import threading
import time
from typing import Optional, Sequence

from natlink_com import NatlinkCOM

from ._state import _state
from ._helpers import _require_not_during_init, _require_not_paused


def _atexit_disconnect():
    """Emergency cleanup on process exit — unregister sinks + Resume.

    Calls the real teardown directly (not the launcher-gated public
    natDisconnect) so the connection is released even when the launcher
    owns it.
    """
    if _state.connected:
        try:
            _disconnect()
        except Exception:
            pass


atexit.register(_atexit_disconnect)

from . import _callbacks


log = logging.getLogger("natlink.compat")


def _teardown_objects():
    """Drain grammars, results, and dictation objects.

    Matches C++ ``CDragonCode::releaseObjects``: grammars → results →
    dicts, all in one function at the same layer.
    """
    for label, registry, method in [
        ("grammars", _state.grammar_registry, "unload"),
    ]:
        with _state.lock:
            objects = list(registry.values())
        if objects:
            log.debug("natDisconnect: tearing down %d %s", len(objects), label)
        for obj in objects:
            try:
                getattr(obj, method)()
            except Exception:
                log.debug("%s teardown failed", label, exc_info=True)

    # Results drain (keyed in natlink_com._res_obj — no wrapper-level registry
    # because ResObj wrappers are ephemeral callback arguments, not
    # user-constructed).
    try:
        from natlink_com._res_obj import release_all_res_objs
        release_all_res_objs()
    except Exception:
        log.debug("result objects teardown failed", exc_info=True)

    for label, registry, method in [
        ("dictation objects", _state.dict_registry, "destroy"),
    ]:
        with _state.lock:
            objects = list(registry.values())
        if objects:
            log.debug("natDisconnect: tearing down %d %s", len(objects), label)
        for obj in objects:
            try:
                getattr(obj, method)()
            except Exception:
                log.debug("%s teardown failed", label, exc_info=True)


def discover_loaders():
    """Phase 1: Import loader modules so they can register providers/helpers.

    Returns list of (module, module_name) tuples. Does NOT start loaders.
    """
    from ._loaders import discover_and_import
    discovered = discover_and_import()

    # Call optional setup() hook on each discovered loader, tagging any
    # callbacks it registers with the loader's package (see loader_registration).
    from ._callbacks import loader_registration
    for mod, name in discovered:
        setup_fn = getattr(mod, "setup", None)
        if setup_fn and callable(setup_fn):
            try:
                with loader_registration(mod):
                    setup_fn()
            except Exception:
                log.debug("Loader setup() failed: %s", name, exc_info=True)

    return discovered


@contextlib.contextmanager
def _connect_cm():
    """Internal helper yielded to `with natConnect():` callers."""
    try:
        yield
    finally:
        natDisconnect()


def _establish_com_connection():
    """Phase A of natConnect: pure COM — mutex, backend, sinks, callbacks.

    The backend's connect() implements CDragonCode::initGetSiteObject:
    "We connect to NatSpeak through a site object which is a better way
    than using the SAPI enumerator objects because it also gives us access
    to the other DgnSAPI interfaces at the same time."
    — Joel Gould, DragonCode.cpp (initGetSiteObject)
    """
    import ctypes
    from ._win32 import kernel32

    # Single active connection — hard limit (issue #228). Natlink serializes
    # all Dragon COM on one STA main thread, so two owners would race events
    # and freeze Dragon. If the NatlinkConnectionActive mutex already exists,
    # another process (a second natlink, a standalone loader, or the test
    # suite) owns the connection; refuse rather than corrupt event ordering.
    # The owner releases it via natDisconnect (tray Configure > Release Dragon).
    # A handle still sitting here means a previous teardown did not run to
    # completion (_state.reset closes it). Release it before creating a new
    # one: otherwise CreateMutexW returns a *second* handle to the same named
    # object with ERROR_ALREADY_EXISTS, the branch below closes only that new
    # handle, and the original leaks with nothing left referencing it — the
    # mutex then stays held for the life of the process and every later
    # natConnect fails with ConnectionInUse, including our own reconnects.
    if _state._conn_mutex:
        kernel32.CloseHandle(_state._conn_mutex)
        _state._conn_mutex = None

    handle = kernel32.CreateMutexW(None, True, "NatlinkConnectionActive")
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(handle)
        from ._exceptions import ConnectionInUse
        raise ConnectionInUse(
            "Another process is already connected to Dragon. Release that "
            "connection (natlink tray menu > Configure > Release Dragon, or "
            "call natDisconnect) "
            "before connecting.")
    _state._conn_mutex = handle

    _state.during_init = True
    try:
        backend = NatlinkCOM()
        backend.connect()
        _state.backend = backend
        _callbacks.register_all()
    except BaseException:
        # Release the mutex handle — natDisconnect won't run because
        # _state.connected is still False when backend is unset.
        if _state._conn_mutex:
            kernel32.CloseHandle(_state._conn_mutex)
            _state._conn_mutex = None
        raise
    finally:
        _state.during_init = False


def _display_startup_banner(discovered_loaders):
    """Banner: Python version, loader versions, or disabled-loader warnings."""
    import sys as _sys
    backend = _state.backend
    try:
        backend.display_text(f"Python Version: {_sys.version}\r\n", False)
        if discovered_loaders:
            for mod, mod_name in discovered_loaders:
                base = mod_name.split(".")[0]
                ver = getattr(mod, "__version__", None) \
                    or getattr(_sys.modules.get(base), "__version__", None)
                if ver:
                    backend.display_text(f"{base} Version: {ver}\r\n", False)
        backend.display_text("Natlink is loaded...\r\n\r\n", False)
        if not discovered_loaders:
            from ._loaders import get_all_loader_names, get_disabled_loaders
            all_names = get_all_loader_names()
            if all_names:
                disabled = get_disabled_loaders()
                backend.display_text(
                    "WARNING: All discovered loaders are disabled.\r\n", True)
                for name, mod_path in all_names:
                    status = "disabled" if name in disabled else "enabled"
                    backend.display_text(
                        f"  {name} ({mod_path}) [{status}]\r\n", True)
            else:
                backend.display_text(
                    "WARNING: No loaders discovered.\r\n"
                    "Install a loader package or check your configuration.\r\n", True)
    except Exception:
        log.debug("Failed to display startup text", exc_info=True)


def _cache_initial_state():
    """Cache mic/user state for UI snapshots (avoids COM calls in callbacks)."""
    try:
        mic = _state.backend.get_mic_state()
    except Exception:
        mic = ""
    try:
        user, user_dir = _state.backend.get_current_user()
    except Exception:
        user, user_dir = "", ""
    _state.cache_user_state(mic, user, user_dir)


def _activate(discovered):
    """Phase B of natConnect: banner, logging redirect, state cache, loaders.

    Does NOT start the Dragon process monitor — that is launcher scope,
    owned by ``natlink_compat._launcher._start_monitor_if_needed``.
    """
    from ._logging_setup import _setup_logging_and_redirect
    from ._ui_protocol import PHASE_CONNECTED, set_phase

    _display_startup_banner(discovered)
    _setup_logging_and_redirect()
    log.info("Connection state: connected")

    _cache_initial_state()
    set_phase(PHASE_CONNECTED)

    if discovered:
        from ._loaders import start_loader, _on_loaders_changed
        for mod, mod_name in discovered:
            start_loader(mod, mod_name, _notify=False)
        _on_loaders_changed()

    # Loaders handed to add_loader() before there was a connection could only
    # be registered at the time; start them now that the backend exists.
    from ._loaders import start_pending_loaders
    start_pending_loaders()


def natConnect(bUseThreads: bool = False, *,
               discovered_loaders: "Optional[Sequence[tuple]]" = None):
    """Connect to Dragon NaturallySpeaking.

    This will launch Dragon if it is not already running. As a side effect,
    natlink acquires COM interface pointers into Dragon's speech engine.

    Returns a context manager that calls natDisconnect on exit::

        with natlink.natConnect():
            # connected to Dragon
            ...
        # automatically disconnected

    Args:
        bUseThreads: Accepted for backwards compatibility (threading is
            always enabled in the current implementation).
        discovered_loaders: Optional pre-discovered loader list, as returned by
            ``discover_loaders()``. Used by the launcher (so setup() hooks run
            before the Dragon-wait) and by tests (empty list = skip discovery).
            When None, natConnect discovers itself.
    """
    if _state.connected:
        if _state.launcher_active:
            # Launcher owns the process + the single shared connection
            # (issue #228). A loader/framework calling natConnect() must not
            # tear down and rebuild it — that would drop every other loader's
            # grammars and callbacks. Hand back a no-op handle; the real
            # connection lives until launcher teardown or
            # tray Configure > Release Dragon.
            log.debug("natConnect: launcher already connected — returning "
                      "no-op handle")
            return contextlib.nullcontext()
        # Standalone caller reconnecting (no launcher): tear down then
        # rebuild, as legacy natlink did.
        log.debug("natConnect: already connected, disconnecting first")
        _disconnect()

    from natlink_com._win32 import kernel32 as _k32
    _k32.ResetEvent(_state._disconnect_event_handle)
    log.info("natConnect: connecting to Dragon via COM...")

    if discovered_loaders is not None:
        discovered = discovered_loaders
    else:
        discovered = discover_loaders()
        for _mod, mod_name in discovered:
            log.info("Loader: %s", mod_name)

    _establish_com_connection()
    log.info("Connected to Dragon.")

    _activate(discovered)

    return _connect_cm()


def natDisconnect() -> None:
    """Disconnect from Dragon.

    When the launcher owns the process (issue #228), a loader's
    ``natDisconnect()`` is a no-op: the launcher controls the single shared
    connection's lifetime, so one loader must not tear it down for the others.
    Real teardown then happens only at launcher shutdown, on restart, or when
    the user releases Dragon via the tray "Inactive" item. In a standalone
    process (no launcher), ``natDisconnect()`` tears the connection down as in
    legacy natlink.
    """
    if _state.launcher_active:
        log.debug("natDisconnect: ignored — launcher owns the connection "
                  "(use tray Configure > Release Dragon)")
        return
    _disconnect()


def _disconnect() -> None:
    """Release all internal COM interface pointers and runtime objects.

    The real teardown. Invoked by the launcher (shutdown / restart / inactive)
    and by standalone ``natDisconnect()``. Causes Dragon to stop running if it
    was launched by natConnect; all grammars, result objects, and dictation
    objects are invalidated.
    """
    from ._ui_protocol import PHASE_IDLE, set_phase

    log.info("natDisconnect: cleaning up...")

    # Every step below is best-effort and _state.reset() runs in the finally.
    # reset() is what clears the backend and closes the connection mutex, so a
    # step raising on the way there would leave _state.connected True with the
    # mutex still held: the monitor keeps re-signalling dragon_exited, every
    # later natConnect fails with ConnectionInUse, and the process can never
    # reconnect. Teardown must reach the end even when Dragon is already gone.
    try:
        _disconnect_steps(set_phase, PHASE_IDLE)
    finally:
        _state.reset()
    log.info("natDisconnect: done")


def _disconnect_steps(set_phase, PHASE_IDLE) -> None:
    # Reject new dispatches before stop_loaders()/set_phase so sink
    # callbacks fired during teardown unwind cleanly instead of racing
    # _queues.clear() in destroy().
    if _state.backend is not None and _state.backend.conn is not None:
        _state.backend.conn.begin_shutdown()

    # Update tray immediately — COM teardown may block if Dragon is gone
    set_phase(PHASE_IDLE)

    # Dragon monitoring is launcher scope. Direct natDisconnect tears down
    # only the COM connection and its attached runtime objects.

    # Disable COM timer before stopping loaders (needs live backend)
    if _state.timer_callbacks:
        try:
            _state.backend.set_timer_callback(False)
        except Exception:
            pass

    from ._loaders import stop_loaders
    try:
        stop_loaders()
    except Exception:
        log.debug("stop_loaders failed during disconnect", exc_info=True)

    from natlink_com._win32 import kernel32 as _k32
    _k32.SetEvent(_state._disconnect_event_handle)  # unblock waitForSpeech

    # Match original C++ CDragonCode::natDisconnect order:
    # 0. "check for special training mode which we should cancel"
    #    — Joel Gould, DragonCode.cpp (natDisconnect, line 1865)
    #    (not applicable here: training mode is Dragon-internal)
    # 1. Unregister engine sink — "The Unregister call will caused
    #    NatSpeak to release its references on the notification sink"
    #    — Joel Gould, DragonCode.cpp (natDisconnect, line 1875-1877)
    # 2. Unload grammars + destroy results + destroy dicts (releaseObjects)
    # 3. Release COM interfaces
    # Sinks MUST be unregistered first — otherwise Dragon's RPC threads
    # can fire callbacks that acquire _state.lock while the main thread
    # is also trying to acquire it, causing a deadlock.
    if _state.backend is not None:
        try:
            _state.backend.unregister_sinks()
        except Exception:
            log.debug("Sink unregistration failed during disconnect", exc_info=True)

    # Clear callback slots AFTER sinks are unregistered — between
    # unregister_sinks and this point, Dragon may still deliver in-flight
    # callbacks that need the slots to call Resume (preventing freeze).
    try:
        _callbacks.unregister_all()
    except Exception:
        log.debug("unregister_all failed during disconnect", exc_info=True)

    # Flush logs and restore stdout/stderr before tearing down COM.
    from ._logging_setup import teardown_logging
    try:
        teardown_logging()
    except Exception:
        log.debug("teardown_logging failed during disconnect", exc_info=True)

    try:
        _teardown_objects()
    except Exception:
        log.debug("_teardown_objects failed during disconnect", exc_info=True)

    if _state.backend is not None:
        try:
            _state.backend.disconnect()
        except Exception:
            log.debug("Backend disconnect failed", exc_info=True)




def isNatSpeakRunning() -> int:
    """Check if Dragon NaturallySpeaking is running.

    Returns 1 if Dragon is running, 0 otherwise. This is the only natlink
    function that can be called before natConnect.
    """
    if _state.backend is not None:
        try:
            return 1 if _state.backend.is_dragon_running_remote() else 0
        except Exception:
            return 1  # Connected means running
    try:
        from ._win32 import user32, DRAGON_CLS
        return 1 if user32.FindWindowW(DRAGON_CLS, None) else 0
    except Exception:
        log.debug("isNatSpeakRunning: FindWindowW failed", exc_info=True)
        return 0


def waitForSpeech(timeout_ms: int = 0) -> None:
    """Enter a Windows message loop to allow speech to be processed.

    Previously established callback functions will be invoked as speech
    events occur. The function blocks until natDisconnect is called or the
    timeout elapses.

    Args:
        timeout_ms: Timeout in milliseconds. ``0`` means wait indefinitely.
            A negative value suppresses any UI and returns when the timeout
            elapses.
    """
    _require_not_during_init("waitForSpeech")
    _require_not_paused("waitForSpeech")
    if not _state.connected:
        return

    from ._launcher import is_pump_active_on_this_thread
    if is_pump_active_on_this_thread():
        # A nested pump here would ignore the launcher's shutdown/restart/
        # dragon events and wedge the process. The launcher is already
        # pumping; return immediately and let it own the loop.
        log.debug("waitForSpeech: launcher pump already running on this "
                  "thread — returning without nesting")
        return

    log.info("waitForSpeech: pumping messages until disconnect...")
    from natlink_com._pump import pump
    from natlink_com._win32 import kernel32 as _k32

    WAIT_OBJECT_0 = 0
    h_disc = _state._disconnect_event_handle
    deadline = (time.monotonic() + timeout_ms / 1000.0) if timeout_ms > 0 else None
    while True:
        if _k32.WaitForSingleObject(h_disc, 0) == WAIT_OBJECT_0:
            break
        if deadline:
            remaining = int((deadline - time.monotonic()) * 1000)
            if remaining <= 0:
                break
            wait_ms = min(remaining, 2000)
        else:
            wait_ms = 2000
        pump(h_event=h_disc, timeout_ms=wait_ms, label="")
    log.info("waitForSpeech: unblocked")
