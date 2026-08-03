"""Launcher — process lifecycle: init, connect, pump, teardown.

``run()`` owns the whole process lifetime. ``_wait_and_connect`` and
``_teardown`` are factored out because restart/reconnect reuse them.

Dependency direction: ``natlink_compat`` → ``natlink_com`` (never reversed).
"""

import ctypes
import gc
import logging
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from natlink_com._launcher import (
    _wait_for_com_ready, _wait_for_dragon_window, _wait_for_profile_via_log,
    _acquire_single_instance,
    _SHUTDOWN_EVENT_NAME, _RESTART_EVENT_NAME,
    _DEACTIVATE_EVENT_NAME, _ACTIVATE_EVENT_NAME,
)
from natlink_com._win32 import kernel32

from ._lifecycle import _disconnect  # real teardown; public natDisconnect
                                     # no-ops while the launcher is active

log = logging.getLogger("natlink.compat.launcher")

ole32 = ctypes.windll.ole32


@dataclass
class Launcher:
    """Process-scoped launcher: event handles, monitor thread, discovered loaders."""
    discovered: list
    shutdown: int
    restart: int
    dragon_exited: int
    dragon_reappeared: int
    deactivate: int = 0          # issue #228: release Dragon to another process
    activate: int = 0            # issue #228: reconnect Dragon
    inactive: bool = False       # True while Dragon is intentionally released
    _monitor_thread: threading.Thread | None = None
    _monitor_stop: threading.Event = field(default_factory=threading.Event)

    # Back-compat alias so _monitor.py and existing callers can read
    # ``session.events.dragon_exited`` etc. without change.
    @property
    def events(self):
        return self

    @property
    def connected(self) -> bool:
        from ._state import _state
        return _state.connected

    @property
    def monitor_stop_event(self) -> threading.Event:
        return self._monitor_stop

    def set_monitor_thread(self, thread) -> None:
        self._monitor_thread = thread
        self._monitor_stop.clear()

    def is_monitor_alive(self) -> bool:
        return self._monitor_thread is not None and self._monitor_thread.is_alive()

    def stop_monitor(self) -> None:
        self._monitor_stop.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=10)
        self._monitor_thread = None

    def close_handles(self) -> None:
        for h in (self.shutdown, self.restart,
                  self.dragon_exited, self.dragon_reappeared,
                  self.deactivate, self.activate):
            if h:
                kernel32.CloseHandle(h)


# ---------------------------------------------------------------------------
# Shared helpers — used by initial connect, reconnect, and restart
# ---------------------------------------------------------------------------

def _probe_and_wait(h_shutdown=None, wait_for_window=True, wait_for_profile=True):
    """Wait for Dragon window + COM readiness + profile load.

    Returns True if ready, False if shutdown was signaled.
    """
    from ._ui_protocol import (set_phase, PHASE_WAITING_FOR_DRAGON,
                               PHASE_CONNECTING, PHASE_LOADING_PROFILE)

    if wait_for_window:
        set_phase(PHASE_WAITING_FOR_DRAGON)
        if not _wait_for_dragon_window(h_shutdown):
            return False

    set_phase(PHASE_CONNECTING)
    _wait_for_com_ready()

    if wait_for_profile:
        set_phase(PHASE_LOADING_PROFILE)
        _wait_for_profile_via_log(max_wait=30)

    return True


def _connect(natlink, discovered):
    """Connect to Dragon via ``natlink.natConnect()``. Returns True on success.

    ``discovered`` is the launcher's cached loader list so setup() hooks
    don't re-run — they are not idempotent.
    """
    from ._ui_protocol import set_phase, PHASE_ERROR
    try:
        natlink.natConnect(discovered_loaders=discovered)
        return True
    except Exception as e:
        log.debug("Connect failed: %s", e, exc_info=True)
        set_phase(PHASE_ERROR, str(e))
        return False


def _start_monitor_if_needed(launcher):
    """Start the Dragon-process monitor iff it isn't already running."""
    if not launcher.is_monitor_alive():
        from ._monitor import start_dragon_monitor
        start_dragon_monitor(launcher)


def _discover_ui_provider():
    """Entry-point UI provider, or the natlink_ui fallback, or None (headless)."""
    try:
        from importlib.metadata import entry_points
        eps = list(entry_points(group="natlink.ui_provider"))
    except Exception:
        eps = []

    eps.sort(key=lambda ep: (ep.name == "default", ep.name))

    for ep in eps:
        try:
            provider = ep.load()()
            log.info("UI provider: %s (from %s)", ep.name, ep.value)
            return provider
        except Exception:
            log.warning("Failed to load UI provider %r", ep.name, exc_info=True)

    try:
        from natlink_ui import UIProvider as DefaultUI
        provider = DefaultUI()
        log.info("UI provider: natlink_ui (direct import fallback)")
        return provider
    except ImportError:
        log.info("No UI provider found — running headless")
        return None


def _wait_and_connect(launcher, cfg, natlink):
    """Auto-launch Dragon if configured, wait for it, probe COM, connect,
    start the monitor. Returns True on success, False if shutdown signaled."""
    from ._ui_protocol import set_phase, PHASE_WAITING_FOR_DRAGON
    from natlink_com._win32 import is_dragon_running

    set_phase(PHASE_WAITING_FOR_DRAGON)

    if cfg.getboolean("settings", "auto_launch_dragon", fallback=False):
        if not is_dragon_running():
            log.info("Auto-launching Dragon...")
            from natlink_com._dragon import launch
            launch()

    dragon_was_running = is_dragon_running()

    log.info("Waiting for Dragon...")
    if not _wait_for_dragon_window(launcher.shutdown, launcher.restart):
        log.info("Shutdown requested while waiting for Dragon")
        return False

    # Window already observed; only wait for profile if we launched Dragon.
    if not _probe_and_wait(launcher.shutdown,
                           wait_for_window=False,
                           wait_for_profile=not dragon_was_running):
        return False

    if not _connect(natlink, launcher.discovered):
        return False
    _start_monitor_if_needed(launcher)
    return True


# ---------------------------------------------------------------------------
# Pump-event handlers
# ---------------------------------------------------------------------------

_restart_lock = threading.Lock()


def _aborting(launcher) -> bool:
    """True if shutdown has been signaled."""
    return kernel32.WaitForSingleObject(launcher.shutdown, 0) == 0


def _do_restart_on_main(launcher, natlink):
    """Restart Dragon from the main thread.

    Restart runs synchronously and blocks the pump for up to ~60s across
    stop + start + probe. Between stages we poll the shutdown event and
    bail; the outer pump observes the same event and _teardown runs.
    ``_dragon.stop`` / ``_dragon.start`` don't accept a shutdown handle,
    so mid-call interruption isn't possible — checks straddle them.
    """
    from ._ui_protocol import set_phase, PHASE_RESTARTING, PHASE_ERROR
    from natlink_com import _dragon
    from ._state import _state

    if not _restart_lock.acquire(blocking=False):
        log.warning("Restart already in progress — ignoring duplicate")
        return

    try:
        set_phase(PHASE_RESTARTING)
        launcher.stop_monitor()
        if _aborting(launcher):
            log.info("Restart: shutdown requested after stop_monitor — aborting")
            return

        conn = _state.conn
        if conn:
            _dragon.save_profile(conn)

        if _state.connected:
            try:
                _disconnect()
            except Exception:
                log.debug("Restart: disconnect error", exc_info=True)

        gc.collect()
        if _aborting(launcher):
            log.info("Restart: shutdown requested before _dragon.stop — aborting")
            return

        _dragon.stop(force=False)
        if _aborting(launcher):
            log.info("Restart: shutdown requested after _dragon.stop — aborting")
            return

        _dragon.start(wait=30)
        if _aborting(launcher):
            # Dragon was re-launched but no client is attached. _teardown
            # won't kill it — quitting natlink doesn't imply quitting Dragon.
            log.info("Restart: shutdown requested after _dragon.start — "
                     "aborting (Dragon left running)")
            return

        if not _probe_and_wait(launcher.shutdown,
                               wait_for_window=True,
                               wait_for_profile=True):
            log.info("Restart: shutdown requested while waiting for Dragon")
            return

        if _connect(natlink, launcher.discovered):
            _start_monitor_if_needed(launcher)
            from ._ui_protocol import notify_text
            notify_text("[Dragon restarted successfully.]\r\n")
    except Exception:
        log.exception("Restart: unexpected error")
        set_phase(PHASE_ERROR, "Restart failed")
    finally:
        _restart_lock.release()


def _handle_dragon_exited(launcher, natlink):
    """Disconnect COM on Dragon shutdown. Returns immediately; the monitor
    will signal dragon_reappeared if Dragon comes back."""
    if launcher.connected:
        try:
            _disconnect()
        except Exception:
            log.debug("Disconnect error", exc_info=True)
    gc.collect()
    _log_unreleased_com_warning_async()


def _log_unreleased_com_warning_async():
    """Background check: warn if natspeak.exe survives 10s after disconnect."""
    def _check():
        from natlink_com._dragon import _is_process_running
        from natlink_com._win32 import is_dragon_running
        for _i in range(10):
            time.sleep(1)
            if not _is_process_running() or is_dragon_running():
                return
        if _is_process_running():
            log.warning("natspeak.exe still running 10s after disconnect — "
                        "possible unreleased COM objects")
    threading.Thread(target=_check, daemon=True,
                     name="dragon-exit-diagnostic").start()


def _handle_dragon_reappeared(launcher, natlink):
    """Probe COM, reconnect, restart monitor."""
    if launcher.connected:
        return

    log.info("Dragon detected — reconnecting...")
    if _probe_and_wait(wait_for_window=False, wait_for_profile=True):
        if _connect(natlink, launcher.discovered):
            _start_monitor_if_needed(launcher)


def _do_deactivate_on_main(launcher, natlink):
    """Release Dragon and enter the inactive state (issue #228).

    Stops the monitor, saves the profile, then disconnects — which releases
    every grammar, callback, and timer and drops the NatlinkConnectionActive
    mutex so another process (a standalone loader or test suite) can take
    ownership. That process must release its resources and call natDisconnect
    when finished; the user reconnects natlink via the tray (Inactive off).
    """
    if launcher.inactive:
        return
    from ._ui_protocol import set_phase, PHASE_INACTIVE, notify_text
    from natlink_com import _dragon
    from ._state import _state

    log.info("Deactivate: releasing Dragon connection (inactive state)")
    launcher.inactive = True
    launcher.stop_monitor()

    conn = _state.conn
    if conn:
        _dragon.save_profile(conn)
    if _state.connected:
        try:
            _disconnect()  # releases the connection mutex
        except Exception:
            log.debug("Deactivate: disconnect error", exc_info=True)
    gc.collect()
    set_phase(PHASE_INACTIVE)
    notify_text("[Natlink inactive — Dragon connection released. "
                "Another process may now connect.]\r\n")


def _do_activate_on_main(launcher, natlink):
    """Leave the inactive state and reconnect to Dragon (issue #228).

    Stays inactive if reconnection fails (e.g. another process still owns
    the connection), so the UI keeps reflecting the released state.
    """
    if not launcher.inactive:
        return
    from ._ui_protocol import set_phase, PHASE_INACTIVE, notify_text

    from natlink_com._win32 import is_dragon_running

    log.info("Activate: reconnecting to Dragon")
    # Releasing the connection leaves the Dragon process alone, so a Dragon
    # that is still up has its profile loaded already. Waiting for the log to
    # announce a profile load that will never happen again costs the full
    # 30s timeout on every reclaim. Only wait when Dragon is not up yet --
    # it restarted while we were released, and the profile really is coming.
    dragon_was_running = is_dragon_running()
    if not _probe_and_wait(launcher.shutdown, wait_for_window=True,
                           wait_for_profile=not dragon_was_running):
        log.info("Activate: shutdown requested while waiting for Dragon")
        return
    if _connect(natlink, launcher.discovered):
        launcher.inactive = False
        _start_monitor_if_needed(launcher)
        notify_text("[Natlink active — reconnected to Dragon.]\r\n")
        return

    # _connect left the phase at PHASE_ERROR, but we are still inactive and
    # the flag still suppresses restart/exited/reappeared in the event loop.
    # The UI derives its toggle from the phase, so leaving it at ERROR
    # unchecks "Release Dragon" while inactive is True — the reclaim branch
    # becomes unreachable and _do_deactivate_on_main early-returns, wedging
    # the launcher until restart. Restore the phase that matches the flag.
    from ._state import _state
    reason = _state.error_message or "another process may still own it"
    set_phase(PHASE_INACTIVE)
    notify_text(f"[Natlink could not reconnect to Dragon — {reason}. "
                "Still inactive; uncheck Configure > Release Dragon to "
                "retry.]\r\n")


# ---------------------------------------------------------------------------
# Pump loop
# ---------------------------------------------------------------------------

_pump_active = threading.local()


def _pump_loop(launcher, natlink):
    """Dispatch shutdown / restart / dragon-exited / dragon-reappeared events
    until shutdown is signaled."""
    from natlink_com._pump import pump

    handles = [launcher.shutdown, launcher.restart,
               launcher.dragon_exited, launcher.dragon_reappeared,
               launcher.deactivate, launcher.activate]
    _SHUTDOWN, _RESTART, _EXITED, _REAPPEARED, _DEACTIVATE, _ACTIVATE = (
        0, 1, 2, 3, 4, 5)

    _pump_active.running = True
    try:
        while True:
            rc = pump(h_events=handles, timeout_ms=2000)
            if rc < 0:
                continue  # timeout or transient
            if rc == _SHUTDOWN:
                log.info("Shutdown event signaled")
                return
            if rc == _RESTART:
                if launcher.inactive:
                    log.info("Restart ignored — natlink is inactive")
                else:
                    log.info("Restart Dragon event signaled")
                    _do_restart_on_main(launcher, natlink)
            elif rc == _EXITED:
                kernel32.ResetEvent(launcher.dragon_exited)
                if launcher.inactive:
                    continue  # we released Dragon on purpose
                log.info("Dragon is shutting down — disconnecting")
                _handle_dragon_exited(launcher, natlink)
            elif rc == _REAPPEARED:
                kernel32.ResetEvent(launcher.dragon_reappeared)
                if launcher.inactive:
                    continue  # don't reclaim the connection while inactive
                _handle_dragon_reappeared(launcher, natlink)
            elif rc == _DEACTIVATE:
                _do_deactivate_on_main(launcher, natlink)
            elif rc == _ACTIVATE:
                _do_activate_on_main(launcher, natlink)
    except KeyboardInterrupt:
        pass
    finally:
        _pump_active.running = False


def is_pump_active_on_this_thread() -> bool:
    """True if the launcher's pump is currently running on the calling thread."""
    return getattr(_pump_active, "running", False)


def _teardown(launcher, natlink):
    """Clean disconnect, stop UI provider, close event handles."""
    from ._state import _state
    from ._actions import stop_provider

    launcher.stop_monitor()

    if _state.connected:
        _disconnect()  # real teardown (public natDisconnect no-ops while launcher-active)
    _state.launcher_active = False

    provider = _state.ui_provider
    _state.ui_provider = None
    if provider is not None:
        try:
            stop_provider(provider)
        except Exception:
            pass

    launcher.close_handles()


def run():
    """Main entry point."""
    _acquire_single_instance()
    sys.coinit_flags = 2  # STA

    # Only prepend the checkout's src/ when running from a source tree.
    # An installed package lives under site-packages, whose parent must
    # not be inserted at the front of sys.path.
    src_path = Path(__file__).resolve().parent.parent
    src_dir = str(src_path)
    if src_path.name == "src" and src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    ole32.CoInitializeEx(None, 2)  # STA, idempotent

    from ._logging_setup import init_file_logging
    init_file_logging()

    from natlink_com._config import load_config
    cfg = load_config()

    from ._lifecycle import discover_loaders
    from ._state import _state
    # Launcher owns the process + the single shared connection (issue #228),
    # so loader re-entrant natConnect/natDisconnect calls become no-ops.
    _state.launcher_active = True
    discovered = discover_loaders()
    if _state.ui_provider is None:
        _state.ui_provider = _discover_ui_provider()

    from ._monitor import DRAGON_EXITED_EVENT, DRAGON_REAPPEARED_EVENT
    launcher = Launcher(
        discovered=discovered,
        shutdown=kernel32.CreateEventW(None, True, False, _SHUTDOWN_EVENT_NAME),
        restart=kernel32.CreateEventW(None, False, False, _RESTART_EVENT_NAME),
        dragon_exited=kernel32.CreateEventW(None, True, False, DRAGON_EXITED_EVENT),
        dragon_reappeared=kernel32.CreateEventW(None, True, False, DRAGON_REAPPEARED_EVENT),
        deactivate=kernel32.CreateEventW(None, False, False, _DEACTIVATE_EVENT_NAME),
        activate=kernel32.CreateEventW(None, False, False, _ACTIVATE_EVENT_NAME),
    )

    import natlink_compat as natlink
    try:
        if _wait_and_connect(launcher, cfg, natlink):
            _pump_loop(launcher, natlink)
    finally:
        _teardown(launcher, natlink)
