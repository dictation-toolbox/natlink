"""test_logging_setup.py - Tests for natlink_compat._logging_setup."""

import configparser
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from natlink_compat import _logging_setup
from natlink_compat._logging_setup import (
    _DispatchingHandler, _NameLevelFilter, _NotifyTextHandler,
    _parse_level, _read_log_config, init_file_logging, teardown_logging,
)


class TestParseLevel(unittest.TestCase):

    def test_empty_returns_default(self):
        self.assertEqual(_parse_level("", 42), 42)
        self.assertEqual(_parse_level("   ", 42), 42)

    def test_numeric_mapping(self):
        self.assertEqual(_parse_level("1", 0), logging.ERROR)
        self.assertEqual(_parse_level("3", 0), logging.INFO)
        self.assertEqual(_parse_level("5", 0), logging.DEBUG)
        self.assertEqual(_parse_level("99", 0), logging.INFO)  # unknown int

    def test_named_levels(self):
        self.assertEqual(_parse_level("DEBUG", 0), logging.DEBUG)
        self.assertEqual(_parse_level("warning", 0), logging.WARNING)
        self.assertEqual(_parse_level("bogus", 42), 42)


class TestNameLevelFilter(unittest.TestCase):

    def _rec(self, name, level):
        return logging.LogRecord(name=name, level=level, pathname="",
                                 lineno=0, msg="", args=(), exc_info=None)

    def test_threshold(self):
        f = _NameLevelFilter("natlink.com", logging.WARNING)
        self.assertTrue(f.filter(self._rec("natlink.com", logging.WARNING)))
        self.assertFalse(f.filter(self._rec("natlink.com", logging.DEBUG)))

    def test_child_and_unrelated(self):
        f = _NameLevelFilter("natlink.com", logging.ERROR)
        self.assertFalse(f.filter(self._rec("natlink.com.grammar", logging.DEBUG)))
        self.assertTrue(f.filter(self._rec("other", logging.DEBUG)))
        self.assertTrue(f.filter(self._rec("natlink.compat", logging.DEBUG)))


class TestDispatchingHandler(unittest.TestCase):

    def test_routing(self):
        h = _DispatchingHandler()
        t1, t2 = MagicMock(), MagicMock()
        f1, f2 = MagicMock(), MagicMock()
        f1.filter.return_value = True
        f2.filter.return_value = False
        h.add_target(t1, f1)
        h.add_target(t2, f2)
        rec = logging.LogRecord(name="x", level=logging.INFO, pathname="",
                                lineno=0, msg="", args=(), exc_info=None)
        h.emit(rec)
        t1.handle.assert_called_once_with(rec)
        t2.handle.assert_not_called()


class TestNotifyTextHandler(unittest.TestCase):

    def test_emits_and_guards_reentrancy(self):
        h = _NotifyTextHandler()
        h.setFormatter(logging.Formatter("%(message)s"))
        calls = []

        def fake(msg, level=logging.INFO):
            calls.append(msg)
            # re-entrant call should be suppressed
            rec2 = logging.LogRecord(name="x", level=logging.INFO, pathname="",
                                     lineno=0, msg="reentrant", args=(), exc_info=None)
            h.emit(rec2)

        rec = logging.LogRecord(name="x", level=logging.INFO, pathname="",
                                lineno=0, msg="hello", args=(), exc_info=None)
        with patch("natlink_compat._ui_protocol.notify_text", side_effect=fake):
            h.emit(rec)
        self.assertEqual(len(calls), 1)

    def test_swallows_exception(self):
        h = _NotifyTextHandler()
        h.setFormatter(logging.Formatter("%(message)s"))
        rec = logging.LogRecord(name="x", level=logging.INFO, pathname="",
                                lineno=0, msg="", args=(), exc_info=None)
        with patch("natlink_compat._ui_protocol.notify_text", side_effect=RuntimeError):
            h.emit(rec)  # should not raise


class TestReadLogConfig(unittest.TestCase):

    def _cfg(self, text):
        cp = configparser.ConfigParser()
        cp.read_string(text)
        return cp

    @patch("natlink_com._config.load_config")
    def test_defaults(self, m):
        m.return_value = self._cfg("")
        r = _read_log_config()
        self.assertEqual(r["log_file"], "")
        self.assertEqual(r["slow_callback_ms"], 500)
        self.assertEqual(r["category_levels"], {})

    @patch("natlink_com._config.load_config")
    def test_overrides(self, m):
        m.return_value = self._cfg(
            "[Logging]\nLogFile = C:/x.log\nSlowCallbackMs = 200\nClientLevel = 1\n"
            "\n[Logging.Levels]\nnatlink.com = 1, 4\n")
        r = _read_log_config()
        self.assertEqual(r["log_file"], "C:/x.log")
        self.assertEqual(r["slow_callback_ms"], 200)
        self.assertEqual(r["category_levels"]["natlink"][0], logging.ERROR)
        c, f = r["category_levels"]["natlink.com"]
        self.assertEqual(c, logging.ERROR)
        self.assertEqual(f, logging.DEBUG)


class TestInitAndTeardown(unittest.TestCase):

    def setUp(self):
        self._fh = _logging_setup._file_handler
        self._nh = _logging_setup._notify_handler
        self._il = _logging_setup._installed_loggers[:]
        self._root = logging.getLogger("natlink")
        self._rh = self._root.handlers[:]
        _logging_setup._file_handler = None
        _logging_setup._notify_handler = None
        _logging_setup._installed_loggers = []

    def tearDown(self):
        if _logging_setup._file_handler and _logging_setup._file_handler is not self._fh:
            try: _logging_setup._file_handler.close()
            except Exception: pass
        _logging_setup._file_handler = self._fh
        _logging_setup._notify_handler = self._nh
        _logging_setup._installed_loggers = self._il
        self._root.handlers = self._rh

    @patch("natlink_compat._logging_setup._resolve_log_path")
    def test_init_creates_handlers_and_is_idempotent(self, mock_path):
        d = tempfile.mkdtemp()
        mock_path.return_value = Path(d) / "test.log"
        init_file_logging(rotate=False)
        self.assertIsNotNone(_logging_setup._file_handler)
        self.assertIsInstance(_logging_setup._notify_handler, _NotifyTextHandler)
        first = _logging_setup._file_handler
        init_file_logging(rotate=False)
        self.assertIs(_logging_setup._file_handler, first)

    @patch("natlink_compat._logging_setup._resolve_log_path")
    def test_teardown_clears(self, mock_path):
        d = tempfile.mkdtemp()
        mock_path.return_value = Path(d) / "test.log"
        init_file_logging(rotate=False)
        teardown_logging()
        self.assertIsNone(_logging_setup._file_handler)
