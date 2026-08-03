"""test_ui_dispatch.py - Unit tests for natlink_compat._ui_protocol.

Tests state snapshot building, phase setting, and UI provider notification.
Does NOT require Dragon.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestBuildStateSnapshot(unittest.TestCase):

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.reset()

    def tearDown(self):
        self._state.reset()

    def test_disconnected_state(self):
        from natlink_compat._ui_protocol import build_state_snapshot
        from natlink_compat._ui_protocol import PHASE_IDLE

        with patch("natlink_compat._actions.get_loader_states", return_value=[]):
            state = build_state_snapshot()
        self.assertFalse(state.connected)
        self.assertEqual(state.phase, PHASE_IDLE)
        self.assertEqual(state.mic_state, "")
        self.assertEqual(state.user_name, "")
        self.assertEqual(state.loader_states, ())

    def test_connected_state(self):
        from natlink_compat._ui_protocol import build_state_snapshot
        from natlink_compat._ui_protocol import PHASE_CONNECTED

        mock_backend = MagicMock()
        mock_backend.dragon_version = (15, 0, 0)

        self._state.backend = mock_backend
        self._state.phase = PHASE_CONNECTED
        self._state.last_mic_state = "on"
        self._state.last_user_name = "TestUser"

        state = build_state_snapshot()
        self.assertTrue(state.connected)
        self.assertEqual(state.phase, PHASE_CONNECTED)
        self.assertEqual(state.mic_state, "on")
        self.assertEqual(state.user_name, "TestUser")
        self.assertEqual(state.dragon_version, (15, 0, 0))

    def test_snapshot_is_frozen(self):
        from natlink_compat._ui_protocol import build_state_snapshot

        state = build_state_snapshot()
        with self.assertRaises(AttributeError):
            state.connected = True


class TestSetPhase(unittest.TestCase):

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.reset()

    def tearDown(self):
        self._state.reset()

    def test_set_phase_updates_state(self):
        from natlink_compat._ui_protocol import set_phase
        from natlink_compat._ui_protocol import PHASE_CONNECTING

        set_phase(PHASE_CONNECTING)
        self.assertEqual(self._state.phase, PHASE_CONNECTING)

    def test_set_phase_with_error(self):
        from natlink_compat._ui_protocol import set_phase
        from natlink_compat._ui_protocol import PHASE_ERROR

        set_phase(PHASE_ERROR, "connection failed")
        self.assertEqual(self._state.phase, PHASE_ERROR)
        self.assertEqual(self._state.error_message, "connection failed")


class TestNotifyUI(unittest.TestCase):

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.reset()

    def tearDown(self):
        self._state.ui_provider = None
        self._state.reset()

    def test_notify_ui_calls_provider(self):
        from natlink_compat._ui_protocol import notify_ui

        mock_provider = MagicMock()
        self._state.ui_provider = mock_provider

        notify_ui()
        mock_provider.on_state_changed.assert_called_once()
        state_arg = mock_provider.on_state_changed.call_args[0][0]
        self.assertFalse(state_arg.connected)

    def test_notify_ui_survives_provider_error(self):
        from natlink_compat._ui_protocol import notify_ui

        bad_provider = MagicMock()
        bad_provider.on_state_changed.side_effect = RuntimeError("boom")
        self._state.ui_provider = bad_provider
        notify_ui()  # Should not raise

    def test_no_providers_is_noop(self):
        from natlink_compat._ui_protocol import notify_ui
        self._state.ui_provider = None
        notify_ui()  # Should not raise


class TestNotifyText(unittest.TestCase):

    def setUp(self):
        from natlink_compat._state import _state
        self._state = _state
        self._state.reset()

    def tearDown(self):
        self._state.ui_provider = None
        self._state.reset()

    def test_notify_text_calls_provider(self):
        from natlink_compat._ui_protocol import notify_text

        mock_provider = MagicMock()
        self._state.ui_provider = mock_provider

        notify_text("hello", level=20)
        mock_provider.on_text.assert_called_once_with("hello", 20)

    def test_notify_text_survives_provider_error(self):
        from natlink_compat._ui_protocol import notify_text

        bad_provider = MagicMock()
        bad_provider.on_text.side_effect = RuntimeError("boom")
        self._state.ui_provider = bad_provider

        notify_text("hello")  # Should not raise

    def test_notify_text_reentrancy_guard(self):
        """Verify that re-entrant calls to notify_text are suppressed."""
        from natlink_compat._ui_protocol import notify_text, _guard

        calls = []

        class ReentrantProvider:
            def on_state_changed(self, state): pass
            def on_text(self, text, level=20):
                calls.append(text)
                if text == "first":
                    notify_text("second")  # Re-entrant call

        self._state.ui_provider = ReentrantProvider()
        notify_text("first")

        # Only "first" should appear — "second" is suppressed
        self.assertEqual(calls, ["first"])
