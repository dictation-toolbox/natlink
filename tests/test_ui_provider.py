"""Tests for natlink_ui.UIProvider — state change and text output behavior."""

import logging
import unittest
from unittest.mock import MagicMock, patch

from natlink_compat import (
    NatlinkState,
    PHASE_IDLE,
    PHASE_CONNECTED,
    PHASE_ERROR,
)


def _make_provider():
    """Create a UIProvider with NatlinkWindow fully mocked out."""
    mock_window = MagicMock()
    mock_window.is_visible = False
    mock_window.is_topmost = False

    with (
        patch("natlink_ui._window.NatlinkWindow", return_value=mock_window),
        patch("natlink_ui._config.load"),
        patch("natlink_ui._config.save"),
        patch("natlink_ui._config.get_bool", return_value=False),
    ):
        from natlink_ui import UIProvider
        provider = UIProvider()

    # Reset mock so constructor calls don't pollute test assertions.
    mock_window.reset_mock()
    return provider, mock_window


class TestProviderContract(unittest.TestCase):
    """UIProvider must satisfy the ABC declared in natlink_compat._ui_protocol."""

    def test_instance_implements_protocol(self):
        from natlink_compat._ui_protocol import UIProvider as UIProviderProtocol
        provider, _ = _make_provider()
        self.assertIsInstance(provider, UIProviderProtocol)

    def test_handles_every_well_known_phase(self):
        from natlink_compat._ui_protocol import (
            PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
            PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING, PHASE_ERROR,
        )
        provider, _ = _make_provider()
        for phase in (PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
                      PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING,
                      PHASE_ERROR):
            provider.on_state_changed(NatlinkState(phase=phase))

    def test_stop_is_callable(self):
        provider, _ = _make_provider()
        provider.stop()


class TestOnStateChanged(unittest.TestCase):
    """UIProvider.on_state_changed should update the tray icon and tooltip."""

    def setUp(self):
        self.provider, self.window = _make_provider()

    def test_connected_phase(self):
        state = NatlinkState(phase=PHASE_CONNECTED)
        self.provider.on_state_changed(state)
        self.window.show_tray_icon.assert_called_once_with(
            "Natlink - Connected", "connected")

    def test_error_phase_includes_message(self):
        state = NatlinkState(phase=PHASE_ERROR, error_message="COM failed")
        self.provider.on_state_changed(state)
        self.window.show_tray_icon.assert_called_once_with(
            "Natlink - COM failed", "error")

    def test_idle_phase_uses_disconnected_icon(self):
        state = NatlinkState(phase=PHASE_IDLE)
        self.provider.on_state_changed(state)
        self.window.show_tray_icon.assert_called_once_with(
            "Natlink - Disconnected", "disconnected")


class TestOnText(unittest.TestCase):
    """UIProvider.on_text should write text and conditionally show the window."""

    def setUp(self):
        self.provider, self.window = _make_provider()

    def test_info_writes_not_error(self):
        self.provider.on_text("hello", logging.INFO)
        self.window.write.assert_called_once_with("hello", False)

    def test_warning_writes_as_error(self):
        self.provider.on_text("watch out", logging.WARNING)
        self.window.write.assert_called_once_with("watch out", True)

    def test_error_shows_window_when_hidden_and_enabled(self):
        self.window.is_visible = False
        with patch("natlink_ui._config.get_bool", return_value=True):
            self.provider.on_text("boom", logging.ERROR)
        self.window.show.assert_called_once()

    def test_error_does_not_show_window_when_already_visible(self):
        self.window.is_visible = True
        with patch("natlink_ui._config.get_bool", return_value=True):
            self.provider.on_text("boom", logging.ERROR)
        self.window.show.assert_not_called()


if __name__ == "__main__":
    unittest.main()
