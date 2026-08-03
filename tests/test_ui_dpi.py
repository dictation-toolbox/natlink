"""test_ui_dpi.py - Per-monitor DPI support for the tray UI.

The failure these guard against is silent: a DPI-unaware process is told every
monitor is 96 DPI, so nothing inside it can observe that it is being
bitmap-stretched. Windows renders it blurry and reports success.

Pure unit tests — no window is created.
"""

import ctypes
import unittest
from unittest.mock import MagicMock, patch

from natlink_ui import _dpi


class TestScale(unittest.TestCase):

    def test_96_dpi_is_identity(self):
        self.assertEqual(_dpi.scale(800, 96), 800)

    def test_150_percent(self):
        self.assertEqual(_dpi.scale(800, 144), 1200)
        self.assertEqual(_dpi.scale(500, 144), 750)

    def test_125_percent_rounds(self):
        self.assertEqual(_dpi.scale(500, 120), 625)
        self.assertEqual(_dpi.scale(19, 120), 24)  # 23.75 -> 24

    def test_200_percent(self):
        self.assertEqual(_dpi.scale(18, 192), 36)


class TestAwarenessFallback(unittest.TestCase):
    """Newest API first, degrading to whatever the OS actually has."""

    def setUp(self):
        # Defeat the memo per scenario, then restore it — leaving it None
        # would make the next real caller re-run the chain against an
        # already-aware process.
        self.addCleanup(setattr, _dpi, "_applied", _dpi._applied)
        _dpi._applied = None

    def _run(self, user32, shcore=None, already="unaware"):
        # The real process is already aware by the time tests run, which would
        # short-circuit the chain; pin it so each scenario is reachable.
        with patch.object(_dpi, "current_awareness", return_value=already), \
             patch.object(_dpi, "user32", user32):
            if shcore is None:
                return _dpi.set_process_dpi_aware()
            windll = MagicMock()
            windll.shcore = shcore
            with patch.object(ctypes, "windll", windll):
                return _dpi.set_process_dpi_aware()

    def test_already_aware_reports_the_truth_not_a_downgrade(self):
        """Regression: the naive chain reported "system" for a per-monitor
        process.

        Awareness can only be set once. On a second call every Set* fails,
        but SetProcessDPIAware returns TRUE for an already-aware process, so
        the chain claimed the weakest mode. The log line this feeds exists to
        diagnose DPI problems, so a wrong value is worse than none.
        """
        u = MagicMock()
        u.SetProcessDpiAwarenessContext.return_value = 0  # already set
        u.SetProcessDPIAware.return_value = 1             # "succeeds" anyway
        self.assertEqual(self._run(u, already="per-monitor"), "per-monitor")
        u.SetProcessDPIAware.assert_not_called()

    def test_prefers_per_monitor_v2(self):
        u = MagicMock()
        u.SetProcessDpiAwarenessContext.return_value = 1
        self.assertEqual(self._run(u), "per-monitor-v2")

    def test_passes_the_v2_sentinel_not_a_count(self):
        """DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 is the handle -4."""
        u = MagicMock()
        u.SetProcessDpiAwarenessContext.return_value = 1
        self._run(u)
        arg = u.SetProcessDpiAwarenessContext.call_args[0][0]
        self.assertEqual(ctypes.cast(arg, ctypes.c_void_p).value,
                         ctypes.c_void_p(-4).value)

    def test_falls_back_to_shcore_before_1703(self):
        u = MagicMock()
        del u.SetProcessDpiAwarenessContext      # AttributeError, as on <1703
        shcore = MagicMock()
        shcore.SetProcessDpiAwareness.return_value = 0   # S_OK
        self.assertEqual(self._run(u, shcore), "per-monitor")

    def test_falls_back_to_system_dpi_before_8_1(self):
        u = MagicMock()
        del u.SetProcessDpiAwarenessContext
        u.SetProcessDPIAware.return_value = 1
        shcore = MagicMock()
        shcore.SetProcessDpiAwareness.side_effect = AttributeError
        self.assertEqual(self._run(u, shcore), "system")

    def test_reports_unaware_when_nothing_works(self):
        u = MagicMock()
        del u.SetProcessDpiAwarenessContext
        del u.SetProcessDPIAware
        shcore = MagicMock()
        shcore.SetProcessDpiAwareness.side_effect = AttributeError
        self.assertEqual(self._run(u, shcore), "unaware")

    def test_is_idempotent(self):
        """Every entry point that might be first calls this uncoordinated."""
        u = MagicMock()
        u.SetProcessDpiAwarenessContext.return_value = 1
        # current_awareness must be pinned: the real process is already aware
        # by the time some orderings reach this test, which would short-circuit
        # before the memo is even exercised.
        with patch.object(_dpi, "current_awareness", return_value="unaware"), \
             patch.object(_dpi, "user32", u):
            first = _dpi.set_process_dpi_aware()
            second = _dpi.set_process_dpi_aware()
        self.assertEqual(first, second)
        self.assertEqual(u.SetProcessDpiAwarenessContext.call_count, 1)


class TestDpiQueries(unittest.TestCase):

    def test_window_dpi_prefers_per_window(self):
        u = MagicMock()
        u.GetDpiForWindow.return_value = 144
        u.GetDpiForSystem.return_value = 96
        with patch.object(_dpi, "user32", u):
            self.assertEqual(_dpi.dpi_for_window(0x1234), 144)

    def test_window_dpi_falls_back_to_system_before_1607(self):
        u = MagicMock()
        del u.GetDpiForWindow
        u.GetDpiForSystem.return_value = 120
        with patch.object(_dpi, "user32", u):
            self.assertEqual(_dpi.dpi_for_window(0x1234), 120)

    def test_null_hwnd_uses_system_dpi(self):
        u = MagicMock()
        u.GetDpiForSystem.return_value = 144
        with patch.object(_dpi, "user32", u):
            self.assertEqual(_dpi.dpi_for_window(None), 144)
        u.GetDpiForWindow.assert_not_called()

    def test_zero_dpi_never_propagates(self):
        """A 0 would make scale() collapse every dimension to nothing."""
        u = MagicMock()
        u.GetDpiForSystem.return_value = 0
        with patch.object(_dpi, "user32", u):
            self.assertEqual(_dpi.dpi_for_system(), 96)

    def test_small_icon_size_defaults_when_metric_unavailable(self):
        u = MagicMock()
        u.GetSystemMetrics.return_value = 0
        with patch.object(_dpi, "user32", u):
            self.assertEqual(_dpi.small_icon_size(), 16)


class TestLiveEnvironment(unittest.TestCase):
    """Against the real Windows this suite is running on."""

    def test_process_is_dpi_aware(self):
        """Regression: natlink shipped DPI-unaware and was silently stretched."""
        _dpi.set_process_dpi_aware()
        awareness = ctypes.c_int()
        hr = ctypes.windll.shcore.GetProcessDpiAwareness(
            None, ctypes.byref(awareness))
        self.assertEqual(hr, 0)
        self.assertNotEqual(awareness.value, 0, "process is DPI UNAWARE")

    def test_reported_dpi_is_plausible(self):
        _dpi.set_process_dpi_aware()
        self.assertGreaterEqual(_dpi.dpi_for_system(), 96)

    def test_tray_icon_is_at_least_16px(self):
        self.assertGreaterEqual(_dpi.small_icon_size(), 16)


class TestWindowIntegration(unittest.TestCase):
    """Against a real HWND — the assertions that source inspection cannot make.

    Grepping the source for "WM_DPICHANGED" would pass on a handler that
    ignored the suggested rect, which is the whole behaviour under test.
    """

    @classmethod
    def setUpClass(cls):
        import time
        from natlink_ui._window import NatlinkWindow
        # No config callbacks: exercise the scaled defaults, not saved pixels.
        cls.win = NatlinkWindow(title="natlink dpi test", width=800, height=500)
        time.sleep(0.5)
        if not cls.win._hwnd:
            cls.tearDownClass()
            raise unittest.SkipTest("window could not be created")

    @classmethod
    def tearDownClass(cls):
        import time
        win = getattr(cls, "win", None)
        if win is not None:
            win.destroy_safe()
            time.sleep(0.3)

    def _rect(self):
        import ctypes.wintypes as wt
        rect = wt.RECT()
        _dpi.user32.GetWindowRect(self.win._hwnd, ctypes.byref(rect))
        return rect

    def test_default_geometry_is_dpi_scaled(self):
        """Regression: __init__ measured DPI before declaring awareness.

        An unaware process is told every monitor is 96 DPI, so the scaling
        silently multiplied by 1.0 and the window came out at its raw
        design size.
        """
        dpi = _dpi.dpi_for_window(self.win._hwnd)
        rect = self._rect()
        self.assertEqual(rect.right - rect.left, _dpi.scale(800, dpi))
        self.assertEqual(rect.bottom - rect.top, _dpi.scale(500, dpi))

    def test_font_exists_at_window_dpi(self):
        self.assertTrue(self.win._font)

    def test_first_window_in_a_fresh_process_is_scaled(self):
        """Regression: __init__ measured DPI before declaring awareness.

        Must run in a subprocess. Awareness is process-wide and permanent, so
        once anything in this interpreter has declared it, a window built with
        the declaration removed still scales correctly — the in-process test
        above passes against the bug. Only the very first window in a fresh
        process can observe the ordering.
        """
        import subprocess
        import sys

        script = (
            "from natlink_ui._window import NatlinkWindow\n"
            "from natlink_ui import _dpi\n"
            "import ctypes, ctypes.wintypes as wt, time\n"
            "w = NatlinkWindow(title='dpi order test', width=800, height=500)\n"
            "time.sleep(0.5)\n"
            "r = wt.RECT()\n"
            "ctypes.windll.user32.GetWindowRect(w._hwnd, ctypes.byref(r))\n"
            "dpi = _dpi.dpi_for_window(w._hwnd)\n"
            "print(r.right - r.left, _dpi.scale(800, dpi))\n"
            "w.destroy_safe()\n"
        )
        out = subprocess.run([sys.executable, "-c", script],
                             capture_output=True, text=True, timeout=90)
        self.assertEqual(out.returncode, 0, out.stderr)
        actual, expected = out.stdout.split()[-2:]
        self.assertEqual(actual, expected,
                         "first window was not DPI-scaled — awareness was "
                         "declared after the geometry was computed")

    def test_dpichanged_adopts_the_suggested_rect(self):
        """The rect Windows supplies is what keeps the window under the
        cursor mid-drag; computing our own would make it jump."""
        import ctypes.wintypes as wt
        import time

        before_font = self.win._font
        suggested = wt.RECT(300, 200, 300 + 640, 200 + 400)
        # addressof, not byref: SendMessageW's argtypes are pinned to an
        # integral LPARAM elsewhere in the process.
        _dpi.user32.SendMessageW(self.win._hwnd, _dpi.WM_DPICHANGED,
                                 (96 << 16) | 96, ctypes.addressof(suggested))
        time.sleep(0.3)

        rect = self._rect()
        self.assertEqual((rect.left, rect.top), (300, 200))
        self.assertEqual((rect.right - rect.left, rect.bottom - rect.top),
                         (640, 400))
        # Font is sized in physical pixels, so it does not follow the window
        # across monitors by itself.
        self.assertTrue(self.win._font)
        self.assertNotEqual(self.win._font, before_font)
