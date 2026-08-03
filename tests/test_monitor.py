"""Tests for natlink_compat._monitor — Dragon process lifecycle monitor."""

import threading
import unittest
from types import SimpleNamespace
from unittest import mock

import natlink_compat._monitor as mod


def _fake_session(*, connected=False, h_exited=0xAA, h_reappeared=0xBB,
                  stop_event=None):
    events = SimpleNamespace(
        dragon_exited=h_exited,
        dragon_reappeared=h_reappeared,
    )
    s = mock.MagicMock()
    s.connected = connected
    s.events = events
    s.monitor_stop_event = stop_event if stop_event is not None else threading.Event()
    return s


class TestGetDragonHandle(unittest.TestCase):
    @mock.patch("natlink_compat._monitor.user32")
    def test_returns_none_when_no_window(self, mock_u32):
        mock_u32.FindWindowW.return_value = 0
        self.assertIsNone(mod._get_dragon_handle())
        mock_u32.FindWindowW.assert_called_once_with(mod.DRAGON_CLS, None)

    @mock.patch("natlink_compat._monitor.kernel32")
    @mock.patch("natlink_compat._monitor.user32")
    def test_returns_handle_on_success(self, mock_u32, mock_k32):
        mock_u32.FindWindowW.return_value = 0x1234

        def fake_get_pid(hwnd, lp_pid):
            import ctypes
            ctypes.cast(lp_pid, ctypes.POINTER(ctypes.wintypes.DWORD)).contents.value = 42

        mock_u32.GetWindowThreadProcessId.side_effect = fake_get_pid
        mock_k32.OpenProcess.return_value = 0xDEAD

        self.assertEqual(mod._get_dragon_handle(), 0xDEAD)
        mock_k32.OpenProcess.assert_called_once_with(mod.SYNCHRONIZE, False, 42)


class TestStartDragonMonitor(unittest.TestCase):
    @mock.patch("natlink_compat._monitor.kernel32")
    @mock.patch("natlink_compat._monitor.user32")
    def test_starts_daemon_thread(self, mock_u32, mock_k32):
        stop = threading.Event(); stop.set()
        session = _fake_session(stop_event=stop)

        mod.start_dragon_monitor(session)

        session.set_monitor_thread.assert_called_once()
        thread = session.set_monitor_thread.call_args[0][0]
        self.assertTrue(thread.daemon)
        self.assertEqual(thread.name, "dragon-monitor")
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())

    @mock.patch("natlink_compat._monitor.kernel32")
    @mock.patch("natlink_compat._monitor.user32")
    def test_resets_both_events_on_start(self, mock_u32, mock_k32):
        stop = threading.Event(); stop.set()
        session = _fake_session(stop_event=stop, h_exited=0xAA, h_reappeared=0xBB)

        mod.start_dragon_monitor(session)
        thread = session.set_monitor_thread.call_args[0][0]
        thread.join(timeout=2)

        mock_k32.ResetEvent.assert_any_call(0xAA)
        mock_k32.ResetEvent.assert_any_call(0xBB)

    @mock.patch("natlink_compat._monitor.kernel32")
    @mock.patch("natlink_compat._monitor.user32")
    def test_signals_exited_when_connected_no_dragon(self, mock_u32, mock_k32):
        stop = threading.Event()
        session = _fake_session(connected=True, stop_event=stop, h_exited=0xAA)

        mock_u32.FindWindowW.return_value = 0

        mod.start_dragon_monitor(session)
        import time
        time.sleep(0.2)
        stop.set()
        thread = session.set_monitor_thread.call_args[0][0]
        thread.join(timeout=2)

        mock_k32.SetEvent.assert_any_call(0xAA)


if __name__ == "__main__":
    unittest.main()
