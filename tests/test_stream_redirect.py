"""test_stream_redirect.py - Tests for natlink_ui._stream_redirect."""

import logging
import sys
import unittest
from unittest.mock import patch


class TestOutputRedirector(unittest.TestCase):

    def _make(self, level=logging.INFO):
        from natlink_ui._stream_redirect import _OutputRedirector
        return _OutputRedirector(level=level)

    @patch("natlink_compat.notify_text")
    def test_write_dispatches_text_at_level(self, mock_notify):
        r = self._make(level=logging.ERROR)
        self.assertEqual(r.write("err"), 3)
        mock_notify.assert_called_once_with("err", level=logging.ERROR)

    @patch("natlink_compat.notify_text")
    def test_write_skips_blank(self, mock_notify):
        r = self._make()
        self.assertEqual(r.write(""), 0)
        self.assertEqual(r.write("  \n"), 3)
        mock_notify.assert_not_called()

    @patch("natlink_compat.notify_text", side_effect=RuntimeError)
    def test_write_survives_exception(self, _):
        self.assertEqual(self._make().write("x"), 1)

    def test_textio_interface(self):
        r = self._make()
        self.assertFalse(r.closed)
        self.assertTrue(r.writable())
        self.assertFalse(r.readable())
        self.assertFalse(r.seekable())
        self.assertEqual(r.mode, "w")
        for fn in (r.read, r.readline, r.seek, r.tell):
            with self.assertRaises(OSError):
                fn()


class TestInstallUninstall(unittest.TestCase):

    def setUp(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def tearDown(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def test_install_and_uninstall(self):
        from natlink_ui._stream_redirect import (
            install_redirect, uninstall_redirect, _OutputRedirector)
        install_redirect()
        self.assertIsInstance(sys.stdout, _OutputRedirector)
        self.assertIsInstance(sys.stderr, _OutputRedirector)
        uninstall_redirect()
        self.assertNotIsInstance(sys.stdout, _OutputRedirector)
        self.assertNotIsInstance(sys.stderr, _OutputRedirector)
