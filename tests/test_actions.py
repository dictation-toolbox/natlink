"""test_actions.py - Unit tests for natlink_compat._actions.

These tests do NOT require Dragon — all external calls are mocked.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


@pytest.fixture(autouse=True)
def _run_actions_inline(monkeypatch):
    """Force ``_dispatch_or_run`` down its inline path.

    ``toggle_loader``/``reload_grammars``/``set_mic`` route their work
    through ``_dispatch_or_run``, which queues onto the STA thread whenever
    a hidden window exists and only runs inline when one does not.  These
    are unit tests asserting that an action invokes its implementation, so
    they depend on the inline path — but if an online test earlier in the
    session left a live connection up, the hidden window is alive, the call
    is queued instead of run, and the assertions see zero calls.

    Pinning ``dispatch`` to False reproduces the no-hidden-window
    environment ``_dispatch_or_run`` documents for unit tests, making these
    tests independent of connection state and suite ordering.  Without it
    the ``assert_not_called`` tests also pass vacuously.
    """
    monkeypatch.setattr("natlink_com._hidden_wnd.dispatch",
                        lambda *a, **k: False)


class TestDragonProcessControl(unittest.TestCase):
    """Test Dragon process control actions."""

    @patch("natlink_com._win32.is_dragon_running", return_value=True)
    def test_is_dragon_running_true(self, mock_running):
        from natlink_compat._actions import is_dragon_running
        self.assertTrue(is_dragon_running())
        mock_running.assert_called_once()

    @patch("natlink_com._win32.is_dragon_running", return_value=False)
    def test_is_dragon_running_false(self, mock_running):
        from natlink_compat._actions import is_dragon_running
        self.assertFalse(is_dragon_running())

    @patch("natlink_com._dragon.start", return_value=0)
    def test_start_dragon(self, mock_start):
        from natlink_compat._actions import start_dragon
        rc = start_dragon(wait=10)
        self.assertEqual(rc, 0)
        mock_start.assert_called_once_with(wait=10)

    @patch("natlink_com._dragon.stop", return_value=0)
    @patch("natlink_compat._state._state")
    def test_stop_dragon(self, mock_state, mock_stop):
        mock_state.conn = None
        from natlink_compat._actions import stop_dragon
        rc = stop_dragon(force=True)
        self.assertEqual(rc, 0)
        mock_stop.assert_called_once_with(force=True, conn=None)

    @patch("natlink_com._launcher.signal_restart", return_value=True)
    def test_restart_dragon_via_launcher(self, mock_signal):
        from natlink_compat._actions import restart_dragon
        rc = restart_dragon()
        self.assertEqual(rc, 0)
        mock_signal.assert_called_once()

    @patch("natlink_com._dragon.restart", return_value=0)
    @patch("natlink_com._launcher.signal_restart", return_value=False)
    def test_restart_dragon_direct_fallback(self, mock_signal, mock_restart):
        from natlink_compat._actions import restart_dragon
        rc = restart_dragon()
        self.assertEqual(rc, 0)
        mock_restart.assert_called_once()

    @patch("natlink_com._dragon.status", return_value=0)
    def test_dragon_status(self, mock_status):
        from natlink_compat._actions import dragon_status
        rc = dragon_status()
        self.assertEqual(rc, 0)


class TestLoaderActions(unittest.TestCase):
    """Test loader cache and toggle logic."""

    def setUp(self):
        from natlink_compat._actions import invalidate_loader_cache
        invalidate_loader_cache()

    def test_get_loader_states_caches_result(self):
        from natlink_compat import _actions

        _actions.invalidate_loader_cache()
        with patch("natlink_compat._loaders.get_all_loader_names",
                   return_value=[("natlinkcore", "natlinkcore")]):
            with patch("natlink_compat._loaders.get_disabled_loaders",
                       return_value=set()):
                with patch("natlink_compat._loaders.get_loaders",
                           return_value=[]):
                    result = _actions.get_loader_states()
                    self.assertEqual(result, [("natlinkcore", True, False)])

    def test_get_loader_states_returns_cached(self):
        from natlink_compat import _actions
        from natlink_compat._state import _state

        cached = [("cached_loader", False, False)]
        with _state.loader_cache_lock:
            _state.loader_states_cache = cached

        result = _actions.get_loader_states()
        self.assertEqual(result, cached)

        # Cleanup
        _actions.invalidate_loader_cache()

    def test_invalidate_loader_cache(self):
        from natlink_compat import _actions
        from natlink_compat._state import _state

        with _state.loader_cache_lock:
            _state.loader_states_cache = [("x", True, False)]

        _actions.invalidate_loader_cache()

        with _state.loader_cache_lock:
            self.assertIsNone(_state.loader_states_cache)

    def test_get_loader_states_returns_empty_on_error(self):
        from natlink_compat import _actions

        _actions.invalidate_loader_cache()
        with patch("natlink_compat._loaders.get_all_loader_names",
                   side_effect=ImportError("no loaders")):
            result = _actions.get_loader_states()
            self.assertEqual(result, [])

    @patch("natlink_compat._loaders.get_disabled_loaders", return_value={"myloader"})
    @patch("natlink_com._config.enable_loader")
    @patch("natlink_compat._actions._start_loader_by_name")
    def test_toggle_loader_enables_disabled(self, mock_start, mock_enable, mock_disabled):
        from natlink_compat._actions import toggle_loader, invalidate_loader_cache
        invalidate_loader_cache()

        toggle_loader("myloader")
        mock_enable.assert_called_once_with("myloader")
        mock_start.assert_called_once_with("myloader")

    @patch("natlink_compat._loaders.get_disabled_loaders", return_value=set())
    @patch("natlink_com._config.disable_loader")
    @patch("natlink_compat._actions._stop_loader_by_name")
    def test_toggle_loader_disables_enabled(self, mock_stop, mock_disable, mock_disabled):
        from natlink_compat._actions import toggle_loader, invalidate_loader_cache
        invalidate_loader_cache()

        toggle_loader("myloader")
        mock_disable.assert_called_once_with("myloader")
        mock_stop.assert_called_once_with("myloader")


class TestReloadGrammars(unittest.TestCase):

    @patch("natlink_compat._loaders.reload_loader")
    @patch("natlink_compat._loaders.get_loaders", return_value=["loader_a"])
    @patch("natlink_compat._loaders._loader_base_name", return_value="loader_a")
    @patch("natlink_compat._loaders.get_disabled_loaders", return_value=set())
    def test_reload_grammars_calls_reload(self, mock_disabled, mock_base, mock_get, mock_reload):
        from natlink_compat._actions import reload_grammars
        reload_grammars()
        mock_reload.assert_called_once_with(["loader_a"])

    @patch("natlink_compat._loaders.reload_loader")
    @patch("natlink_compat._loaders.get_loaders", return_value=["loader_a"])
    @patch("natlink_compat._loaders._loader_base_name", return_value="loader_a")
    @patch("natlink_compat._loaders.get_disabled_loaders", return_value={"loader_a"})
    def test_reload_skips_disabled(self, mock_disabled, mock_base, mock_get, mock_reload):
        from natlink_compat._actions import reload_grammars
        reload_grammars()
        mock_reload.assert_not_called()


class TestConfigActions(unittest.TestCase):

    @patch("natlink_com._config.toggle_bool_setting")
    def test_toggle_auto_launch(self, mock_toggle):
        from natlink_compat._actions import toggle_auto_launch
        toggle_auto_launch()
        mock_toggle.assert_called_once_with("settings", "auto_launch_dragon", fallback=False)

    @patch("natlink_com._config.get_bool_setting", return_value=True)
    def test_is_auto_launch_enabled(self, mock_get):
        from natlink_compat._actions import is_auto_launch_enabled
        self.assertTrue(is_auto_launch_enabled())


class TestMicAndShutdown(unittest.TestCase):

    @patch("natlink_compat._state._state")
    def test_set_mic_delegates(self, mock_state):
        mock_backend = MagicMock()
        mock_state.backend = mock_backend
        from natlink_compat._actions import set_mic
        set_mic("on")
        mock_backend.set_mic_state.assert_called_once_with("on")

    @patch("natlink_compat._state._state")
    def test_set_mic_no_backend(self, mock_state):
        mock_state.backend = None
        from natlink_compat._actions import set_mic
        set_mic("on")  # Should not raise

    @patch("natlink_com._launcher.request_shutdown")
    def test_exit_natlink(self, mock_shutdown):
        from natlink_compat._actions import exit_natlink
        exit_natlink()
        mock_shutdown.assert_called_once()


class TestStopProvider(unittest.TestCase):

    def test_stop_provider_calls_stop(self):
        from natlink_compat._actions import stop_provider
        provider = MagicMock()
        stop_provider(provider)
        provider.stop.assert_called_once()
