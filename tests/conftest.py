"""conftest.py - Shared fixtures and auto-skip logic for natlink tests.

Markers:
    online  — Test requires Dragon running.  Auto-skipped when not available.
    offline — Test requires Dragon NOT running.  Auto-skipped when available.

By default *all* tests are collected; those whose requirements aren't met are
skipped automatically.

natlink_com connects directly to Dragon via COM.
"""

import logging
import os
import sys
import time

import pytest

# STA — callbacks serialized on main thread (matches C++ original)
if not hasattr(sys, 'coinit_flags'):
    sys.coinit_flags = 2

# Keep comtypes codegen in-memory for tests. The default cache location may
# resolve into installed site-packages, which is not writable in this env.
import comtypes.client
comtypes.client.gen_dir = None

# ---------------------------------------------------------------------------
# Log file setup — single log for both test markers and natlink runtime
# ---------------------------------------------------------------------------
_project_root = os.path.dirname(os.path.dirname(__file__))
_log_path = os.path.join(_project_root, "natlink_com.log")
os.environ.setdefault("NATLINK_LOG_PATH", _log_path)

# Initialize logging early with rotation disabled — tests append to a
# single log file without rollover.  Because init_file_logging() is
# guarded by `if _file_handler is not None: return`, calling it here
# prevents natConnect from creating a second (rotating) handler later.
from natlink_compat._logging_setup import init_file_logging
init_file_logging(rotate=False)


# ---------------------------------------------------------------------------
# Detection helpers (single implementation, shared by all test modules)
# ---------------------------------------------------------------------------

def dragon_running() -> bool:
    """True if natspeak.exe is found among running processes."""
    from natlink_com._win32 import is_dragon_running
    return is_dragon_running()


# Evaluate once at collection time.
_DRAGON_RUNNING = dragon_running()


# ---------------------------------------------------------------------------
# Message pump helper for deferred callbacks
# ---------------------------------------------------------------------------

def wait_for_callback(predicate, timeout=2.0):
    """Pump Win32 messages until predicate() is True or timeout.

    Use instead of time.sleep() when waiting for deferred Dragon callbacks.
    Returns True if predicate was satisfied, False on timeout.
    """
    from natlink_com._pump import pump
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        pump()
        if predicate():
            return True
        time.sleep(0.01)
    return False


# ---------------------------------------------------------------------------
# Pytest hooks
# ---------------------------------------------------------------------------

# Execution order for test files (tests within a file run top-to-bottom).
# Tests build on each other: connection first, then grammar, then callbacks, etc.
_TEST_FILE_ORDER = [
    "test_minimal",
    "test_exceptions",
    "test_connection",
    "test_system_info",
    "test_grammar",
    "test_callbacks",
    "test_lists",
    "test_dictation",
    "test_vocabulary",
    "test_mimic",
    "test_editwindow",
    "test_syncops",
    "test_grammar_compiler",
    "test_grammar_format",
    "test_natlink_compat",
    "test_nsformat",
    "test_ini_file",
    "test_loaders",
    "test_logging_setup",
    "test_stream_redirect",
    "test_monitor",
    "test_ui_provider",
]


def _file_sort_key(item):
    """Sort key that orders test files by _TEST_FILE_ORDER."""
    module = item.module.__name__
    try:
        return _TEST_FILE_ORDER.index(module)
    except ValueError:
        return len(_TEST_FILE_ORDER)


def pytest_addoption(parser):
    parser.addoption(
        "--restart-dragon", action="store_true", default=False,
        help="Restart Dragon before the session and wait until it accepts a "
             "COM connection. Use for measurement runs and for reproducing "
             "cross-run effects: Dragon carries state between sessions "
             "(notably stale CNotify sink registrations), which skews "
             "refcount assertions and can mask teardown bugs.")


def _wait_for_com_ready(timeout=180):
    """Block until Dragon accepts and releases a real COM connection.

    ``_dragon.start()`` only waits for the *process*, which appears long
    before the engine is usable — connecting too early fails with
    CO_E_SERVER_EXEC_FAILURE, or with SRERR_NOUSERSELECTED if the profile has
    not loaded. Connecting is the only check that means anything.
    """
    import natlink_compat as natlink
    from natlink_compat._state import _state

    class _NullUI:
        def on_state_changed(self, state): pass
        def on_text(self, text, level=20): pass

    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            if _state.ui_provider is None:
                _state.ui_provider = _NullUI()
            natlink.natConnect(discovered_loaders=[])
            user = natlink.getCurrentUser()
            natlink.natDisconnect()
            if user and user[0]:
                return True
            last = "connected but no user profile loaded"
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            try:
                natlink.natDisconnect()
            except Exception:
                pass
        time.sleep(3)
    _test_log.error("Dragon not ready after %ds: %s", timeout, last)
    return False


def pytest_configure(config):
    """Optionally restart Dragon so the session starts from known state."""
    if not config.getoption("--restart-dragon"):
        return
    from natlink_com import _dragon
    print("\n[conftest] restarting Dragon for a clean session...")
    _dragon.restart(wait=30)
    if _wait_for_com_ready():
        print("[conftest] Dragon ready.")
    else:
        print("[conftest] WARNING: Dragon did not become ready; "
              "online tests will likely fail.")


def pytest_collection_modifyitems(config, items):
    """Order tests, auto-skip based on Dragon status, deselect opt-in groups."""
    # Sort by explicit file order
    items.sort(key=_file_sort_key)

    # Check if the user explicitly asked for opt-in test groups
    markexpr = config.getoption("-m", default="")
    want_experimental = "experimental" in markexpr
    want_nsformat = "nsformat" in markexpr
    want_teardown = "teardown" in markexpr

    deselected = []
    remaining = []
    for item in items:
        if "experimental" in item.keywords and not want_experimental:
            deselected.append(item)
            continue
        if "nsformat" in item.keywords and not want_nsformat:
            deselected.append(item)
            continue
        if "teardown" in item.keywords and not want_teardown:
            deselected.append(item)
            continue
        if "online" in item.keywords and not _DRAGON_RUNNING:
            item.add_marker(pytest.mark.skip(
                reason="Dragon not running (online)"))
        elif "offline" in item.keywords and _DRAGON_RUNNING:
            item.add_marker(pytest.mark.skip(
                reason="Dragon is running (offline)"))
        remaining.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining


# ---------------------------------------------------------------------------
# Test-name logging — uses the natlink root logger so markers appear in
# the same log file alongside runtime events (Paused, PhraseFinish, etc.)
# ---------------------------------------------------------------------------

_test_log = logging.getLogger("natlink.test")


@pytest.fixture(autouse=True)
def _log_test_name(request):
    """Log test name before and after each test."""
    name = request.node.nodeid
    _test_log.info(">>> START %s", name)
    yield
    _test_log.info("<<< END   %s", name)


# ---------------------------------------------------------------------------
# Session-scoped natlink connection — ONE natConnect for the entire session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def live_connection():
    """Shared natlink connection for all live (online) tests.

    Connects once at session start via natlink_com (direct COM).
    Disconnects at session end.  Tests that disconnect mid-session can do so
    freely — the ``_ensure_connected`` autouse fixture reconnects.
    """
    if not _DRAGON_RUNNING:
        yield None
        return

    import natlink_compat as natlink
    from natlink_compat._state import _state

    # Install a null UI provider — tests don't need a tray icon.
    class _NullUI:
        def on_state_changed(self, state): pass
        def on_text(self, text, level=20): pass

    if _state.ui_provider is None:
        _state.ui_provider = _NullUI()

    # Empty discovered_loaders tells the lifecycle "discovery happened, produced
    # nothing" — gives tests a deterministic loader environment independent
    # of whatever is installed on the machine.
    natlink.natConnect(discovered_loaders=[])

    # Start with mic off so Dragon isn't listening during tests
    try:
        natlink.setMicState("off")
    except Exception:
        pass

    yield
    try:
        natlink.setMicState("off")
        from natlink_com._pump import pump
        pump()
    except Exception:
        pass
    try:
        natlink.natDisconnect()
    except Exception:
        _state.reset()


@pytest.fixture(autouse=True)
def _ensure_connected(request):
    """Auto-reconnect before any online test that uses live_connection.

    Lightweight no-op when already connected.  Handles the case where a
    previous test called natDisconnect().
    """
    if "online" not in request.keywords:
        return
    if "live_connection" not in request.fixturenames:
        return

    from natlink_compat._state import _state

    if _state.connected:
        # Quick liveness check: can we still talk to Dragon?
        try:
            _state.backend.get_mic_state()
            return
        except Exception:
            _test_log.warning("COM connection dead, reconnecting...")
            # Attempt proper disconnect to unregister sinks from Dragon's
            # CNotify list.  Without this, old sink registrations are
            # orphaned and Dragon keeps trying to deliver callbacks to
            # dead RPC endpoints.
            import natlink_compat as _natlink
            try:
                _natlink.natDisconnect()
            except Exception:
                _state.reset()

    import natlink_compat as natlink

    # Prevent real UI startup during reconnect; tests only need a sink object
    if _state.ui_provider is None:
        class _NullUI:
            def on_state_changed(self, state): pass
            def on_text(self, text, level=20): pass
        _state.ui_provider = _NullUI()
    natlink.natConnect(discovered_loaders=[])


@pytest.fixture(autouse=True)
def _detect_grammar_leaks(request):
    """Fail a test that leaves grammars in the registry it didn't start with.

    Pure diagnostic — does NOT drain. If a test leaks, the assertion names
    the offender so we can fix it rather than masking the leak.
    """
    if "online" not in request.keywords:
        yield
        return
    from natlink_compat._state import _state
    pre_gram = set(_state.grammar_registry)
    pre_dict = set(_state.dict_registry)
    yield
    post_gram = set(_state.grammar_registry)
    post_dict = set(_state.dict_registry)
    leaked_gram = post_gram - pre_gram
    leaked_dict = post_dict - pre_dict
    assert not leaked_gram, (
        f"{request.node.nodeid} leaked grammar handles: {sorted(leaked_gram)}")
    assert not leaked_dict, (
        f"{request.node.nodeid} leaked dict handles: {sorted(leaked_dict)}")


# ---------------------------------------------------------------------------
# Session-scoped EDIT window — launched for ALL live tests so Dragon always
# has a safe text target (prevents mimic/playString typing into the terminal)
# ---------------------------------------------------------------------------

_editwin_proc = None  # module-level so atexit/signal can reach it


def _kill_editwin():
    """Kill the edit window process if still alive."""
    global _editwin_proc
    if _editwin_proc is not None:
        try:
            _editwin_proc.terminate()
            _editwin_proc.wait(timeout=3)
        except Exception:
            try:
                _editwin_proc.kill()
            except Exception:
                pass
        _editwin_proc = None


@pytest.fixture(scope="session")
def _editwin_session():
    """Launch one EDIT window for the entire session.

    Always active when Dragon is running so that dictation output from
    recognitionMimic goes into the edit control instead of whatever
    window happens to be foreground (terminal, IDE, etc.).
    """
    global _editwin_proc
    if not _DRAGON_RUNNING:
        yield None
        return

    from _helpers import launch_editwin, focus_window
    import atexit

    proc, main_hwnd, edit_hwnd = launch_editwin()
    _editwin_proc = proc
    atexit.register(_kill_editwin)
    time.sleep(0.5)
    try:
        focus_window(main_hwnd)
    except RuntimeError:
        # Another window owns the foreground right now.  Don't cascade
        # every test into error — `_focus_editwin` retries per-test.
        pass
    yield main_hwnd, edit_hwnd
    _kill_editwin()
    atexit.unregister(_kill_editwin)


@pytest.fixture(autouse=True)
def _focus_editwin(request, _editwin_session):
    """Re-focus the EDIT window before every online test."""
    if "online" not in request.keywords:
        return
    if _editwin_session is None:
        return
    from _helpers import focus_window
    main_hwnd, _ = _editwin_session
    try:
        focus_window(main_hwnd)
    except RuntimeError:
        pass  # best effort — some CI environments block focus


@pytest.fixture(scope="session")
def editwin_proc(_editwin_session):
    """Alias for tests that explicitly need the edit window handles."""
    if _editwin_session is None:
        pytest.skip("Edit window not available (Dragon not running)")
    return _editwin_session
