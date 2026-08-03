"""test_ui_protocol.py - Unit tests for natlink_compat._ui_protocol.

Tests NatlinkState dataclass and UIProvider protocol.
Does NOT require Dragon.
"""

import unittest


class TestNatlinkState(unittest.TestCase):
    """Test the NatlinkState frozen dataclass."""

    def test_defaults(self):
        from natlink_compat._ui_protocol import NatlinkState, PHASE_IDLE
        state = NatlinkState()
        self.assertFalse(state.connected)
        self.assertEqual(state.phase, PHASE_IDLE)
        self.assertEqual(state.mic_state, "")
        self.assertEqual(state.user_name, "")
        self.assertEqual(state.user_directory, "")
        self.assertEqual(state.dragon_version, (0, 0, 0))
        self.assertEqual(state.loader_states, ())
        self.assertEqual(state.error_message, "")

    def test_frozen(self):
        from natlink_compat._ui_protocol import NatlinkState
        state = NatlinkState()
        with self.assertRaises(AttributeError):
            state.connected = True

    def test_custom_values(self):
        from natlink_compat._ui_protocol import NatlinkState, PHASE_CONNECTED
        state = NatlinkState(
            connected=True,
            phase=PHASE_CONNECTED,
            mic_state="on",
            user_name="TestUser",
            dragon_version=(15, 0, 0),
            loader_states=(("natlinkcore", True, True),),
        )
        self.assertTrue(state.connected)
        self.assertEqual(state.mic_state, "on")
        self.assertEqual(state.loader_states, (("natlinkcore", True, True),))

    def test_equality(self):
        from natlink_compat._ui_protocol import NatlinkState
        s1 = NatlinkState(connected=True, mic_state="on")
        s2 = NatlinkState(connected=True, mic_state="on")
        self.assertEqual(s1, s2)

    def test_asdict(self):
        from dataclasses import asdict
        from natlink_compat._ui_protocol import NatlinkState
        state = NatlinkState(connected=True, mic_state="on")
        d = asdict(state)
        self.assertTrue(d["connected"])
        self.assertEqual(d["mic_state"], "on")


class TestUIProviderProtocol(unittest.TestCase):
    """Test that classes can satisfy the UIProvider protocol."""

    def test_protocol_check(self):
        from natlink_compat._ui_protocol import UIProvider

        class MyUI:
            def on_state_changed(self, state): pass
            def on_text(self, text, level=20): pass
            def stop(self): pass

        self.assertIsInstance(MyUI(), UIProvider)

    def test_incomplete_not_provider(self):
        from natlink_compat._ui_protocol import UIProvider

        class Incomplete:
            def on_state_changed(self, state): pass
            # missing on_text and stop

        self.assertNotIsInstance(Incomplete(), UIProvider)


class TestPhaseConstants(unittest.TestCase):
    """Test that all phase constants are distinct strings."""

    def test_all_phases_unique(self):
        from natlink_compat._ui_protocol import (
            PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
            PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING,
            PHASE_ERROR,
        )
        phases = [PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
                  PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING,
                  PHASE_ERROR]
        self.assertEqual(len(phases), len(set(phases)))
        for p in phases:
            self.assertIsInstance(p, str)
