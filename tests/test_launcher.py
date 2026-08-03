"""test_launcher.py - Unit tests for natlink_compat._launcher.

Tests launcher logic: provider discovery, connect sequences, restart guard.
Does NOT require Dragon — all COM/launcher calls are mocked.
"""

import threading
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, PropertyMock


class TestDiscoverUIProvider(unittest.TestCase):

    @patch("importlib.metadata.entry_points", return_value=[])
    def test_no_entry_points_falls_back_to_natlink_ui(self, mock_eps):
        with patch("natlink_ui.UIProvider") as MockUI:
            mock_instance = MagicMock()
            MockUI.return_value = mock_instance

            from natlink_compat._launcher import _discover_ui_provider
            provider = _discover_ui_provider()
            self.assertIs(provider, mock_instance)

    @patch("importlib.metadata.entry_points", return_value=[])
    def test_no_entry_points_no_natlink_ui_returns_none(self, mock_eps):
        from natlink_compat._launcher import _discover_ui_provider
        with patch("natlink_compat._launcher.log"):
            # Make the natlink_ui import fail
            import builtins
            real_import = builtins.__import__
            def fake_import(name, *args, **kwargs):
                if name == "natlink_ui":
                    raise ImportError("no natlink_ui")
                return real_import(name, *args, **kwargs)
            with patch("builtins.__import__", side_effect=fake_import):
                provider = _discover_ui_provider()
                self.assertIsNone(provider)

    def test_entry_point_loaded(self):
        mock_ep = MagicMock()
        mock_ep.name = "custom_ui"
        mock_ep.value = "my_package:MyUI"
        mock_provider = MagicMock()
        mock_ep.load.return_value = lambda: mock_provider

        with patch("importlib.metadata.entry_points", return_value=[mock_ep]):
            from natlink_compat._launcher import _discover_ui_provider
            provider = _discover_ui_provider()
            self.assertIs(provider, mock_provider)

    def test_failing_entry_point_falls_through(self):
        mock_ep = MagicMock()
        mock_ep.name = "bad_ui"
        mock_ep.value = "bad:UI"
        mock_ep.load.side_effect = RuntimeError("broken")

        with patch("importlib.metadata.entry_points", return_value=[mock_ep]):
            with patch("natlink_ui.UIProvider") as MockUI:
                mock_instance = MagicMock()
                MockUI.return_value = mock_instance

                from natlink_compat._launcher import _discover_ui_provider
                provider = _discover_ui_provider()
                self.assertIs(provider, mock_instance)

    def test_non_default_entry_point_takes_priority(self):
        custom_ep = MagicMock()
        custom_ep.name = "custom_ui"
        custom_ep.value = "custom:UI"
        custom_provider = MagicMock(name="custom_provider")
        custom_ep.load.return_value = lambda: custom_provider

        default_ep = MagicMock()
        default_ep.name = "default"
        default_ep.value = "natlink_ui:UIProvider"
        default_provider = MagicMock(name="default_provider")
        default_ep.load.return_value = lambda: default_provider

        with patch("importlib.metadata.entry_points", return_value=[default_ep, custom_ep]):
            from natlink_compat._launcher import _discover_ui_provider
            provider = _discover_ui_provider()

        self.assertIs(provider, custom_provider)

    def test_direct_import_fallback_returns_single_provider(self):
        with patch("importlib.metadata.entry_points", return_value=[]):
            with patch("natlink_ui.UIProvider") as MockUI:
                mock_instance = MagicMock()
                MockUI.return_value = mock_instance

                from natlink_compat._launcher import _discover_ui_provider
                provider = _discover_ui_provider()

        self.assertIs(provider, mock_instance)


class TestRestartLock(unittest.TestCase):
    """Test the restart lock prevents concurrent restarts."""

    def test_restart_lock_blocks_concurrent(self):
        from natlink_compat._launcher import _restart_lock

        # Acquire the lock
        acquired = _restart_lock.acquire(blocking=False)
        self.assertTrue(acquired)
        try:
            # Second acquire should fail (non-blocking)
            second = _restart_lock.acquire(blocking=False)
            self.assertFalse(second)
        finally:
            _restart_lock.release()

    def test_restart_lock_released_after(self):
        from natlink_compat._launcher import _restart_lock

        _restart_lock.acquire(blocking=False)
        _restart_lock.release()

        # Should be acquirable again
        acquired = _restart_lock.acquire(blocking=False)
        self.assertTrue(acquired)
        _restart_lock.release()


class TestProbeAndWait(unittest.TestCase):

    @patch("natlink_compat._launcher._wait_for_profile_via_log")
    @patch("natlink_compat._launcher._wait_for_com_ready")
    @patch("natlink_compat._launcher._wait_for_dragon_window", return_value=True)
    def test_full_probe(self, mock_window, mock_com, mock_profile):
        from natlink_compat._launcher import _probe_and_wait
        result = _probe_and_wait(wait_for_window=True, wait_for_profile=True)
        self.assertTrue(result)
        mock_window.assert_called_once()
        mock_com.assert_called_once()
        mock_profile.assert_called_once()

    @patch("natlink_compat._launcher._wait_for_com_ready")
    @patch("natlink_compat._launcher._wait_for_dragon_window", return_value=False)
    def test_probe_shutdown_during_window_wait(self, mock_window, mock_com):
        from natlink_compat._launcher import _probe_and_wait
        result = _probe_and_wait(wait_for_window=True, wait_for_profile=True)
        self.assertFalse(result)
        mock_com.assert_not_called()

    @patch("natlink_compat._launcher._wait_for_com_ready")
    def test_probe_skip_window_wait(self, mock_com):
        from natlink_compat._launcher import _probe_and_wait
        result = _probe_and_wait(wait_for_window=False, wait_for_profile=False)
        self.assertTrue(result)
        mock_com.assert_called_once()


class TestConnect(unittest.TestCase):

    def test_connect_success(self):
        from natlink_compat._launcher import _connect
        mock_natlink = MagicMock()
        result = _connect(mock_natlink, [])
        self.assertTrue(result)
        mock_natlink.natConnect.assert_called_once_with(discovered_loaders=[])

    def test_connect_failure(self):
        from natlink_compat._launcher import _connect
        mock_natlink = MagicMock()
        mock_natlink.natConnect.side_effect = RuntimeError("COM error")
        result = _connect(mock_natlink, [])
        self.assertFalse(result)

    def test_connect_forwards_discovered(self):
        from natlink_compat._launcher import _connect
        mock_natlink = MagicMock()
        fake_discovered = [("mod_a", "a"), ("mod_b", "b")]
        _connect(mock_natlink, fake_discovered)
        mock_natlink.natConnect.assert_called_once_with(discovered_loaders=fake_discovered)


class TestWaitAndConnect(unittest.TestCase):

    @patch("natlink_compat._launcher._start_monitor_if_needed")
    @patch("natlink_compat._launcher._connect", return_value=False)
    @patch("natlink_compat._launcher._probe_and_wait", return_value=True)
    @patch("natlink_compat._launcher._wait_for_dragon_window", return_value=True)
    @patch("natlink_com._win32.is_dragon_running", return_value=True)
    def test_returns_false_when_initial_connect_fails(
            self, mock_running, mock_window, mock_probe, mock_connect, mock_monitor):
        from natlink_compat._launcher import _wait_and_connect

        session = SimpleNamespace(
            discovered=[("mod", "name")],
            shutdown=11,
            restart=22,
        )
        cfg = MagicMock()
        cfg.getboolean.return_value = False
        natlink = MagicMock()

        result = _wait_and_connect(session, cfg, natlink)

        self.assertFalse(result)
        mock_connect.assert_called_once_with(natlink, session.discovered)
        mock_monitor.assert_not_called()


class TestDoRestartOnMainAbort(unittest.TestCase):
    """Shutdown signaled mid-restart must short-circuit remaining stages."""

    def _make_session(self, shutdown_signaled_after=None):
        """Build a session whose shutdown event "fires" after N _aborting checks.

        shutdown_signaled_after=None  -> never signaled (normal restart)
        shutdown_signaled_after=0     -> signaled before first check
        shutdown_signaled_after=K     -> signaled before the (K+1)-th check
        """
        session = MagicMock()
        session.events.shutdown = 0xABCD
        session.discovered = [("m", "n")]
        session.stop_monitor = MagicMock()
        return session

    def _run_with_abort_at(self, n_checks_before_abort):
        """Run _do_restart_on_main with shutdown signaled after N _aborting() calls.

        Returns dict of call counts for the downstream stages.
        """
        from natlink_compat import _launcher

        session = self._make_session()
        natlink = MagicMock()

        state = MagicMock()
        state.connected = True
        state.conn = MagicMock()

        call_count = {"aborting": 0}

        def fake_aborting(_s):
            call_count["aborting"] += 1
            return call_count["aborting"] > n_checks_before_abort

        # Ensure natlink_com._dragon is importable as an attribute before patching.
        import natlink_com
        import natlink_com._dragon as real_dragon  # noqa: F401

        mock_dragon = MagicMock()
        with patch.object(_launcher, "_aborting", side_effect=fake_aborting), \
             patch.object(_launcher, "_probe_and_wait", return_value=True) as mock_probe, \
             patch.object(_launcher, "_connect", return_value=True) as mock_connect, \
             patch.object(_launcher, "_start_monitor_if_needed") as mock_monitor, \
             patch.object(natlink_com, "_dragon", mock_dragon), \
             patch("natlink_compat._launcher._disconnect") as mock_disconnect, \
             patch("natlink_compat._state._state", state):
            _launcher._do_restart_on_main(session, natlink)

        return {
            "stop_monitor": session.stop_monitor.call_count,
            "save_profile": mock_dragon.save_profile.call_count,
            # Restart uses the internal real teardown (_disconnect); the public
            # natDisconnect no-ops while the launcher is active (issue #228).
            "natDisconnect": mock_disconnect.call_count,
            "dragon_stop": mock_dragon.stop.call_count,
            "dragon_start": mock_dragon.start.call_count,
            "probe": mock_probe.call_count,
            "connect": mock_connect.call_count,
            "monitor": mock_monitor.call_count,
            "aborting_checks": call_count["aborting"],
        }

    def test_abort_after_stop_monitor(self):
        # First _aborting() check returns True -> stop after stop_monitor.
        counts = self._run_with_abort_at(0)
        self.assertEqual(counts["stop_monitor"], 1)
        self.assertEqual(counts["save_profile"], 0)
        self.assertEqual(counts["natDisconnect"], 0)
        self.assertEqual(counts["dragon_stop"], 0)
        self.assertEqual(counts["dragon_start"], 0)
        self.assertEqual(counts["probe"], 0)
        self.assertEqual(counts["connect"], 0)

    def test_abort_before_dragon_stop(self):
        # save_profile + natDisconnect happen, then the 2nd _aborting returns True.
        counts = self._run_with_abort_at(1)
        self.assertEqual(counts["save_profile"], 1)
        self.assertEqual(counts["natDisconnect"], 1)
        self.assertEqual(counts["dragon_stop"], 0)
        self.assertEqual(counts["dragon_start"], 0)
        self.assertEqual(counts["probe"], 0)
        self.assertEqual(counts["connect"], 0)

    def test_abort_after_dragon_stop(self):
        # dragon.stop runs, then abort before dragon.start.
        counts = self._run_with_abort_at(2)
        self.assertEqual(counts["dragon_stop"], 1)
        self.assertEqual(counts["dragon_start"], 0)
        self.assertEqual(counts["probe"], 0)
        self.assertEqual(counts["connect"], 0)

    def test_abort_after_dragon_start(self):
        # dragon.start runs, then abort before probe_and_wait.
        counts = self._run_with_abort_at(3)
        self.assertEqual(counts["dragon_stop"], 1)
        self.assertEqual(counts["dragon_start"], 1)
        self.assertEqual(counts["probe"], 0)
        self.assertEqual(counts["connect"], 0)
        self.assertEqual(counts["monitor"], 0)

    def test_no_abort_runs_full_sequence(self):
        counts = self._run_with_abort_at(99)  # never abort
        self.assertEqual(counts["dragon_stop"], 1)
        self.assertEqual(counts["dragon_start"], 1)
        self.assertEqual(counts["probe"], 1)
        self.assertEqual(counts["connect"], 1)
        self.assertEqual(counts["monitor"], 1)

    def test_restart_lock_released_on_early_abort(self):
        from natlink_compat._launcher import _restart_lock
        self._run_with_abort_at(0)
        # Lock must be released even when we returned early.
        self.assertTrue(_restart_lock.acquire(blocking=False))
        _restart_lock.release()


class TestHandleDragonReappeared(unittest.TestCase):

    @patch("natlink_compat._launcher._start_monitor_if_needed")
    @patch("natlink_compat._launcher._connect")
    @patch("natlink_compat._launcher._probe_and_wait", return_value=True)
    def test_reconnects_when_disconnected(self, mock_probe, mock_connect, mock_monitor):
        from natlink_compat._launcher import _handle_dragon_reappeared

        mock_natlink = MagicMock()
        discovered = [("m", "n")]
        session = SimpleNamespace(connected=False, discovered=discovered)
        mock_connect.return_value = True
        _handle_dragon_reappeared(session, mock_natlink)

        mock_probe.assert_called_once()
        mock_connect.assert_called_once_with(mock_natlink, discovered)
        mock_monitor.assert_called_once()

    @patch("natlink_compat._launcher._probe_and_wait")
    def test_skips_when_already_connected(self, mock_probe):
        from natlink_compat._launcher import _handle_dragon_reappeared

        mock_natlink = MagicMock()
        session = SimpleNamespace(connected=True, discovered=[])
        _handle_dragon_reappeared(session, mock_natlink)

        mock_probe.assert_not_called()
