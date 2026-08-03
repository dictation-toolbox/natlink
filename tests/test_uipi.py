"""test_uipi.py - Detecting input blocked across an integrity boundary.

Dragon runs its engine at medium integrity but DragonBar and the UIA servers
elevated. When an elevated window holds the foreground, a medium-integrity
natlink cannot direct keystrokes at it -- and the failure is invisible from
the call: SendInput reported 4/4 events accepted with GetLastError zero while
the intended window received nothing. Comparing integrity levels is the only
thing that detects that case, so these pin the comparison and the reporting.
"""

import ctypes
import logging
import unittest
from unittest.mock import MagicMock, patch

from natlink_com import _uipi


class TestLevelNames(unittest.TestCase):

    def test_known_levels(self):
        self.assertEqual(_uipi.level_name(_uipi.MEDIUM), "MEDIUM")
        self.assertEqual(_uipi.level_name(_uipi.HIGH), "HIGH")
        self.assertEqual(_uipi.level_name(_uipi.SYSTEM), "SYSTEM")

    def test_unknown_level_is_shown_as_a_rid(self):
        self.assertEqual(_uipi.level_name(0x2100), "0x2100")

    def test_missing_level_is_not_rendered_as_a_number(self):
        self.assertEqual(_uipi.level_name(None), "unknown")

    def test_levels_are_ordered(self):
        self.assertLess(_uipi.LOW, _uipi.MEDIUM)
        self.assertLess(_uipi.MEDIUM, _uipi.HIGH)
        self.assertLess(_uipi.HIGH, _uipi.SYSTEM)


class TestForegroundComparison(unittest.TestCase):

    def setUp(self):
        _uipi._warned_for.clear()
        self.addCleanup(_uipi._warned_for.clear)

    def _foreground(self, theirs, ours=_uipi.MEDIUM, hwnd=0x1234, pid=999):
        """Pin the foreground window's owner and our own level."""
        u = MagicMock()
        u.GetForegroundWindow.return_value = hwnd

        def _pid(_hwnd, out):
            ctypes.cast(out, ctypes.POINTER(ctypes.c_ulong))[0] = pid
            return 1
        u.GetWindowThreadProcessId.side_effect = _pid
        u.GetWindowTextW.side_effect = lambda h, buf, n: 0

        def _level(p=None):
            return ours if p is None else theirs

        return patch.multiple(_uipi, user32=u,
                              process_level=MagicMock(side_effect=_level))

    def test_elevated_foreground_is_reported(self):
        with self._foreground(theirs=_uipi.HIGH), \
             patch.object(_uipi, "_own_level", _uipi.MEDIUM):
            found = _uipi.foreground_blocks_input()
        self.assertIsNotNone(found)
        self.assertEqual(found[1], _uipi.HIGH)

    def test_same_level_foreground_is_fine(self):
        with self._foreground(theirs=_uipi.MEDIUM), \
             patch.object(_uipi, "_own_level", _uipi.MEDIUM):
            self.assertIsNone(_uipi.foreground_blocks_input())

    def test_lower_level_foreground_is_fine(self):
        with self._foreground(theirs=_uipi.LOW), \
             patch.object(_uipi, "_own_level", _uipi.MEDIUM):
            self.assertIsNone(_uipi.foreground_blocks_input())

    def test_elevated_natlink_can_reach_a_medium_window(self):
        with self._foreground(theirs=_uipi.MEDIUM, ours=_uipi.HIGH), \
             patch.object(_uipi, "_own_level", _uipi.HIGH):
            self.assertIsNone(_uipi.foreground_blocks_input())

    def test_unreadable_level_is_not_treated_as_a_mismatch(self):
        """Failing to read a level is not evidence that one outranks us."""
        with self._foreground(theirs=None), \
             patch.object(_uipi, "_own_level", _uipi.MEDIUM):
            self.assertIsNone(_uipi.foreground_blocks_input())

    def test_no_foreground_window(self):
        u = MagicMock()
        u.GetForegroundWindow.return_value = 0
        with patch.object(_uipi, "user32", u):
            self.assertIsNone(_uipi.foreground_blocks_input())


class TestWarning(unittest.TestCase):

    def setUp(self):
        _uipi._warned_for.clear()
        self.addCleanup(_uipi._warned_for.clear)

    def test_warns_once_per_window(self):
        """playString runs per utterance; one warning per window, not per key."""
        with patch.object(_uipi, "foreground_blocks_input",
                          return_value=("DragonBar", _uipi.HIGH)), \
             self.assertLogs("natlink.com.uipi", logging.WARNING) as cm:
            self.assertTrue(_uipi.warn_if_foreground_outranks_us("playString"))
            self.assertTrue(_uipi.warn_if_foreground_outranks_us("playString"))
        self.assertEqual(len(cm.output), 1)

    def test_message_names_the_window_and_both_levels(self):
        with patch.object(_uipi, "foreground_blocks_input",
                          return_value=("DragonBar", _uipi.HIGH)), \
             patch.object(_uipi, "_own_level", _uipi.MEDIUM), \
             self.assertLogs("natlink.com.uipi", logging.WARNING) as cm:
            _uipi.warn_if_foreground_outranks_us("playString")
        message = cm.output[0]
        self.assertIn("DragonBar", message)
        self.assertIn("HIGH", message)
        self.assertIn("MEDIUM", message)
        self.assertIn("playString", message)

    def test_a_different_window_warns_again(self):
        with patch.object(_uipi, "_own_level", _uipi.MEDIUM), \
             self.assertLogs("natlink.com.uipi", logging.WARNING) as cm:
            with patch.object(_uipi, "foreground_blocks_input",
                              return_value=("DragonBar", _uipi.HIGH)):
                _uipi.warn_if_foreground_outranks_us("playString")
            with patch.object(_uipi, "foreground_blocks_input",
                              return_value=("Registry Editor", _uipi.HIGH)):
                _uipi.warn_if_foreground_outranks_us("playString")
        self.assertEqual(len(cm.output), 2)

    def test_silent_when_nothing_outranks_us(self):
        with patch.object(_uipi, "foreground_blocks_input", return_value=None):
            self.assertFalse(_uipi.warn_if_foreground_outranks_us("playString"))


class TestSendInputReporting(unittest.TestCase):
    """_send_inputs must say *why* an injection was short, not just that it was."""

    def _send(self, accepted, err, requested=4):
        from natlink_com import _sendinput

        u = MagicMock()
        u.SendInput.return_value = accepted
        inputs = [_sendinput.INPUT() for _ in range(requested)]
        with patch.object(_sendinput, "_user32_err", u), \
             patch.object(_uipi, "warn_if_foreground_outranks_us",
                          return_value=False), \
             patch.object(_sendinput, "_last_error", return_value=err), \
             self.assertLogs("natlink.com.sendinput", logging.WARNING) as cm:
            _sendinput._send_inputs(inputs, "playString")
        return cm.output[0]

    def test_access_denied_explains_the_integrity_boundary(self):
        message = self._send(accepted=0, err=5)
        self.assertIn("higher integrity level", message)
        self.assertIn("elevated", message)

    def test_other_errors_report_the_code(self):
        message = self._send(accepted=2, err=1400)
        self.assertIn("2/4", message)
        self.assertIn("1400", message)

    def test_full_delivery_is_silent(self):
        from natlink_com import _sendinput

        u = MagicMock()
        u.SendInput.return_value = 4
        inputs = [_sendinput.INPUT() for _ in range(4)]
        with patch.object(_sendinput, "_user32_err", u), \
             patch.object(_uipi, "warn_if_foreground_outranks_us",
                          return_value=False), \
             patch.object(_sendinput.log, "warning") as warn:
            _sendinput._send_inputs(inputs, "playString")
        warn.assert_not_called()

    def test_integrity_is_checked_before_injecting(self):
        """A full-success injection into an elevated window still warns."""
        from natlink_com import _sendinput

        u = MagicMock()
        u.SendInput.return_value = 4
        inputs = [_sendinput.INPUT() for _ in range(4)]
        with patch.object(_sendinput, "_user32_err", u), \
             patch.object(_uipi, "warn_if_foreground_outranks_us") as check:
            _sendinput._send_inputs(inputs, "playString")
        check.assert_called_once_with("playString")

    def test_empty_input_does_nothing(self):
        from natlink_com import _sendinput

        with patch.object(_uipi, "warn_if_foreground_outranks_us") as check:
            _sendinput._send_inputs([], "playString")
        check.assert_not_called()


class TestLiveEnvironment(unittest.TestCase):

    def test_own_level_is_readable(self):
        self.assertIn(_uipi.level_name(_uipi.own_level()),
                      {"LOW", "MEDIUM", "HIGH", "SYSTEM"})

    def test_own_level_is_cached(self):
        _uipi.own_level()
        with patch.object(_uipi, "process_level") as query:
            _uipi.own_level()
        query.assert_not_called()
