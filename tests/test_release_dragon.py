"""test_release_dragon.py - The release/reclaim Dragon state machine (issue #228).

Tray "Configure > Release Dragon" hands natlink's single Dragon connection to
another process. The tray runs on a worker thread but the COM objects belong
to the main STA thread, so the menu only signals a named event; the launcher's
main loop does the work. Covered here:

  - the teardown  (_do_deactivate_on_main)
  - the reconnect (_do_activate_on_main)
  - the event-loop guards that stop the monitor reclaiming a connection the
    user deliberately gave away
  - set_inactive's signal-only contract

Does NOT require Dragon — all COM/launcher calls are mocked.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class _InactiveTestBase(unittest.TestCase):

    def _launcher(self, inactive=False):
        return SimpleNamespace(
            inactive=inactive,
            shutdown=0x1000,
            discovered=[("mod", "name")],
            stop_monitor=MagicMock(),
        )

    def _state(self, connected=True, error_message=""):
        state = MagicMock()
        state.connected = connected
        state.conn = MagicMock()
        state.error_message = error_message
        return state


class TestDeactivateOnMain(_InactiveTestBase):

    def _run(self, launcher, state=None):
        import natlink_com
        import natlink_com._dragon  # noqa: F401  (importable before patching)
        from natlink_compat import _launcher

        mock_dragon = MagicMock()
        with patch("natlink_compat._ui_protocol.set_phase") as set_phase, \
             patch("natlink_compat._ui_protocol.notify_text"), \
             patch.object(natlink_com, "_dragon", mock_dragon), \
             patch.object(_launcher, "_disconnect") as disconnect, \
             patch("natlink_compat._state._state", state or self._state()):
            _launcher._do_deactivate_on_main(launcher, MagicMock())
        return set_phase, disconnect, mock_dragon

    def test_releases_connection_and_enters_inactive(self):
        from natlink_compat._ui_protocol import PHASE_INACTIVE

        launcher = self._launcher()
        set_phase, disconnect, dragon = self._run(launcher)

        self.assertTrue(launcher.inactive)
        launcher.stop_monitor.assert_called_once()
        dragon.save_profile.assert_called_once()
        disconnect.assert_called_once()
        set_phase.assert_called_once_with(PHASE_INACTIVE)

    def test_profile_saved_before_disconnect(self):
        """Saving after teardown would use a released connection."""
        import natlink_com
        import natlink_com._dragon  # noqa: F401
        from natlink_compat import _launcher

        order = []
        mock_dragon = MagicMock()
        mock_dragon.save_profile.side_effect = lambda *a: order.append("save")

        with patch("natlink_compat._ui_protocol.set_phase"), \
             patch("natlink_compat._ui_protocol.notify_text"), \
             patch.object(natlink_com, "_dragon", mock_dragon), \
             patch.object(_launcher, "_disconnect",
                          side_effect=lambda: order.append("disconnect")), \
             patch("natlink_compat._state._state", self._state()):
            _launcher._do_deactivate_on_main(self._launcher(), MagicMock())

        self.assertEqual(order, ["save", "disconnect"])

    def test_already_inactive_is_a_no_op(self):
        launcher = self._launcher(inactive=True)
        set_phase, disconnect, _ = self._run(launcher)

        disconnect.assert_not_called()
        launcher.stop_monitor.assert_not_called()
        set_phase.assert_not_called()

    def test_disconnect_failure_still_enters_inactive(self):
        """A raising teardown must not strand the launcher half-released."""
        import natlink_com
        import natlink_com._dragon  # noqa: F401
        from natlink_compat import _launcher
        from natlink_compat._ui_protocol import PHASE_INACTIVE

        launcher = self._launcher()
        with patch("natlink_compat._ui_protocol.set_phase") as set_phase, \
             patch("natlink_compat._ui_protocol.notify_text"), \
             patch.object(natlink_com, "_dragon", MagicMock()), \
             patch.object(_launcher, "_disconnect",
                          side_effect=RuntimeError("dragon gone")), \
             patch("natlink_compat._state._state", self._state()):
            _launcher._do_deactivate_on_main(launcher, MagicMock())

        self.assertTrue(launcher.inactive)
        set_phase.assert_called_once_with(PHASE_INACTIVE)

    def test_skips_disconnect_when_not_connected(self):
        launcher = self._launcher()
        _, disconnect, _ = self._run(launcher, state=self._state(connected=False))
        disconnect.assert_not_called()
        self.assertTrue(launcher.inactive)


class TestActivateOnMain(_InactiveTestBase):

    def _run(self, launcher, connect_ok=True, probe_ok=True, state=None,
             dragon_running=True):
        from natlink_compat import _launcher

        with patch("natlink_compat._ui_protocol.set_phase") as set_phase, \
             patch("natlink_com._win32.is_dragon_running",
                   return_value=dragon_running), \
             patch("natlink_compat._ui_protocol.notify_text"), \
             patch.object(_launcher, "_probe_and_wait",
                          return_value=probe_ok) as probe, \
             patch.object(_launcher, "_connect", return_value=connect_ok) as connect, \
             patch.object(_launcher, "_start_monitor_if_needed") as monitor, \
             patch("natlink_compat._state._state", state or self._state()):
            _launcher._do_activate_on_main(launcher, MagicMock())
        self.probe = probe
        return set_phase, connect, monitor

    def test_running_dragon_skips_the_profile_wait(self):
        """Regression: reclaiming used to stall a full 30s.

        _wait_for_profile_via_log waits for a *new* "Normal mode" line in
        Dragon's log. Releasing the connection never stops Dragon, so its
        profile stays loaded and that line never comes again — the wait ran
        to its 30s timeout, returned False, and connected anyway.
        """
        self._run(self._launcher(inactive=True), dragon_running=True)
        self.assertIs(self.probe.call_args.kwargs["wait_for_profile"], False)

    def test_restarted_dragon_still_waits_for_the_profile(self):
        """Dragon came back while we were released — the profile is loading."""
        self._run(self._launcher(inactive=True), dragon_running=False)
        self.assertIs(self.probe.call_args.kwargs["wait_for_profile"], True)

    def test_reconnects_and_leaves_inactive(self):
        launcher = self._launcher(inactive=True)
        _, connect, monitor = self._run(launcher)

        self.assertFalse(launcher.inactive)
        connect.assert_called_once()
        monitor.assert_called_once()

    def test_not_inactive_is_a_no_op(self):
        launcher = self._launcher(inactive=False)
        _, connect, _ = self._run(launcher)
        connect.assert_not_called()

    def test_shutdown_during_probe_does_not_connect(self):
        launcher = self._launcher(inactive=True)
        _, connect, monitor = self._run(launcher, probe_ok=False)

        connect.assert_not_called()
        monitor.assert_not_called()
        self.assertTrue(launcher.inactive)

    def test_failed_reconnect_restores_inactive_phase(self):
        """Regression: a failed reclaim used to leave the phase at ERROR.

        ``_connect`` sets PHASE_ERROR on failure, but ``inactive`` stays True
        and keeps suppressing restart/exited/reappeared. The tray derives its
        checkbox from the phase, so an ERROR phase unchecked "Release Dragon"
        while still inactive: clicking it took the release branch, which
        early-returns on ``if launcher.inactive``, and nothing could ever
        reclaim the connection again.
        """
        from natlink_compat._ui_protocol import PHASE_INACTIVE

        launcher = self._launcher(inactive=True)
        set_phase, _, monitor = self._run(launcher, connect_ok=False)

        self.assertTrue(launcher.inactive)
        monitor.assert_not_called()
        set_phase.assert_called_once_with(PHASE_INACTIVE)

    def test_failed_reconnect_reports_the_connect_error(self):
        from natlink_compat import _launcher

        launcher = self._launcher(inactive=True)
        state = self._state(error_message="Another process is already connected")
        with patch("natlink_compat._ui_protocol.set_phase"), \
             patch("natlink_compat._ui_protocol.notify_text") as notify, \
             patch.object(_launcher, "_probe_and_wait", return_value=True), \
             patch.object(_launcher, "_connect", return_value=False), \
             patch.object(_launcher, "_start_monitor_if_needed"), \
             patch("natlink_compat._state._state", state):
            _launcher._do_activate_on_main(launcher, MagicMock())

        self.assertIn("Another process is already connected",
                      notify.call_args[0][0])


class TestInactiveSuppressesMonitorEvents(_InactiveTestBase):
    """While released, natlink must not reclaim the connection on its own."""

    def _drive(self, first_rc, inactive):
        """Run one event-loop iteration returning first_rc, then shutdown."""
        from natlink_compat import _launcher

        launcher = SimpleNamespace(
            inactive=inactive,
            shutdown=0, restart=1, dragon_exited=2,
            dragon_reappeared=3, deactivate=4, activate=5,
        )
        # pump() returns the index into the handle list; index 0 is shutdown,
        # so a second return of 0 ends the loop.
        with patch("natlink_com._pump.pump", side_effect=[first_rc, 0]), \
             patch.object(_launcher, "kernel32", MagicMock()), \
             patch.object(_launcher, "_do_restart_on_main") as restart, \
             patch.object(_launcher, "_handle_dragon_exited") as exited, \
             patch.object(_launcher, "_handle_dragon_reappeared") as reappeared, \
             patch.object(_launcher, "_do_deactivate_on_main") as deactivate, \
             patch.object(_launcher, "_do_activate_on_main") as activate:
            _launcher._pump_loop(launcher, MagicMock())
        return {"restart": restart, "exited": exited, "reappeared": reappeared,
                "deactivate": deactivate, "activate": activate}

    def test_restart_ignored_while_inactive(self):
        self._drive(1, inactive=True)["restart"].assert_not_called()

    def test_restart_runs_while_active(self):
        self._drive(1, inactive=False)["restart"].assert_called_once()

    def test_dragon_exited_ignored_while_inactive(self):
        self._drive(2, inactive=True)["exited"].assert_not_called()

    def test_dragon_exited_handled_while_active(self):
        self._drive(2, inactive=False)["exited"].assert_called_once()

    def test_dragon_reappeared_does_not_reclaim_while_inactive(self):
        self._drive(3, inactive=True)["reappeared"].assert_not_called()

    def test_dragon_reappeared_reconnects_while_active(self):
        self._drive(3, inactive=False)["reappeared"].assert_called_once()

    def test_deactivate_dispatches(self):
        self._drive(4, inactive=False)["deactivate"].assert_called_once()

    def test_activate_dispatches(self):
        self._drive(5, inactive=True)["activate"].assert_called_once()


class TestSetInactiveSignalling(unittest.TestCase):
    """set_inactive only signals; it never touches COM from the caller thread."""

    def test_true_signals_deactivate(self):
        with patch("natlink_com._launcher.signal_deactivate",
                   return_value=True) as sig, \
             patch("natlink_com._launcher.signal_activate") as other:
            from natlink_compat._actions import set_inactive
            self.assertTrue(set_inactive(True))
            sig.assert_called_once()
            other.assert_not_called()

    def test_false_signals_activate(self):
        with patch("natlink_com._launcher.signal_activate",
                   return_value=True) as sig, \
             patch("natlink_com._launcher.signal_deactivate") as other:
            from natlink_compat._actions import set_inactive
            self.assertTrue(set_inactive(False))
            sig.assert_called_once()
            other.assert_not_called()

    def test_returns_false_when_no_launcher_is_running(self):
        """The named event does not exist, so nothing services the request."""
        with patch("natlink_com._launcher.signal_deactivate", return_value=False):
            from natlink_compat._actions import set_inactive
            self.assertFalse(set_inactive(True))


class TestUIReportsUnservicedRequest(unittest.TestCase):
    """A dropped signal must not look like a completed toggle."""

    def _provider(self):
        import natlink_ui
        provider = object.__new__(natlink_ui.UIProvider)
        provider._latest_phase = "connected"
        return provider

    def test_warns_when_no_launcher_serviced_the_release(self):
        import natlink_compat

        provider = self._provider()
        with patch.object(natlink_compat, "msgbox") as msgbox, \
             patch.object(natlink_compat, "set_inactive", return_value=False):
            msgbox.return_value = natlink_compat.IDYES
            provider._toggle_inactive()

        # First call is the confirmation, second reports the dropped request.
        self.assertEqual(msgbox.call_count, 2)
        self.assertIn("No natlink launcher is running",
                      msgbox.call_args[0][0])

    def test_silent_when_the_request_was_serviced(self):
        import natlink_compat

        provider = self._provider()
        with patch.object(natlink_compat, "msgbox") as msgbox, \
             patch.object(natlink_compat, "set_inactive", return_value=True):
            msgbox.return_value = natlink_compat.IDYES
            provider._toggle_inactive()

        self.assertEqual(msgbox.call_count, 1)

    def test_declining_the_confirmation_does_not_release(self):
        import natlink_compat

        provider = self._provider()
        with patch.object(natlink_compat, "msgbox") as msgbox, \
             patch.object(natlink_compat, "set_inactive") as set_inactive:
            msgbox.return_value = natlink_compat.IDNO
            provider._toggle_inactive()

        set_inactive.assert_not_called()

    def test_reclaim_skips_the_confirmation(self):
        """Only giving the connection away is destructive enough to confirm."""
        import natlink_compat
        from natlink_compat._ui_protocol import PHASE_INACTIVE

        provider = self._provider()
        provider._latest_phase = PHASE_INACTIVE
        with patch.object(natlink_compat, "msgbox") as msgbox, \
             patch.object(natlink_compat, "set_inactive",
                          return_value=True) as set_inactive:
            provider._toggle_inactive()

        msgbox.assert_not_called()
        set_inactive.assert_called_once_with(False)


class TestDeactivateEventsAreAutoReset(unittest.TestCase):
    """Deactivate/activate are one-shot commands, not level-triggered states.

    The event loop explicitly calls ResetEvent for dragon_exited and
    dragon_reappeared but not for these two, which is only correct while they
    are created auto-reset.
    """

    def test_named_event_flags(self):
        import re
        from pathlib import Path

        src = Path(__file__).parent.parent / "src/natlink_compat/_launcher.py"
        text = src.read_text(encoding="utf-8")
        for field in ("deactivate", "activate"):
            m = re.search(rf"{field}=kernel32\.CreateEventW\(None, (\w+),", text)
            self.assertIsNotNone(m, f"{field} event creation not found")
            self.assertEqual(m.group(1), "False",
                             f"{field} must be auto-reset (bManualReset=False)")
