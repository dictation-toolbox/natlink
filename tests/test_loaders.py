"""test_loaders.py - Tests for natlink_compat._loaders."""

import sys
import unittest
from unittest.mock import MagicMock, patch

from natlink_compat._state import _state
from natlink_compat import _loaders
from natlink_compat._loaders import (
    _loader_name, _loader_base_name, _as_list, _LoaderEntry,
    _adopt_loader_logger, _register, _find_entry,
    get_disabled_loaders, get_all_loader_names, discover_and_import,
    start_loader, stop_loader, stop_loaders,
    add_loader, remove_loader, reload_loader, register_running_loader,
    get_loaders, clear_all,
)


def _make_loader(name="fake", has_start=True, has_run=False,
                 has_stop=True, has_trigger_load=False):
    loader = MagicMock()
    loader.__name__ = name
    if not has_start: del loader.start
    if not has_run: del loader.run
    if not has_stop: del loader.stop
    if not has_trigger_load: del loader.trigger_load
    if hasattr(loader, "unload_all_loaded_modules"):
        del loader.unload_all_loaded_modules
    return loader


def _reset():
    _state.loader_registry.clear()
    _state.reset()


class TestNaming(unittest.TestCase):

    def test_loader_name(self):
        m = MagicMock(); m.__name__ = "x"
        self.assertEqual(_loader_name(m), "x")
        self.assertEqual(_loader_name(object()), "object")

    def test_base_name(self):
        m = MagicMock()
        _register(m, "natlinkcore.loader")
        self.assertEqual(_loader_base_name(m), "natlinkcore")
        _state.loader_registry.clear()

    def test_as_list(self):
        o = object()
        self.assertEqual(_as_list(o), [o])
        self.assertEqual(_as_list([1, 2]), [1, 2])
        self.assertEqual(_as_list((1,)), [1])


class TestDiscovery(unittest.TestCase):

    def setUp(self): _reset()
    def tearDown(self): _reset()

    def test_disabled_loaders(self):
        cfg = MagicMock()
        cfg.has_section.return_value = True
        cfg.items.return_value = [("a", "disabled"), ("b", "enabled")]
        with patch("natlink_com._config.load_config", return_value=cfg):
            self.assertEqual(get_disabled_loaders(), {"a"})

    def test_all_loader_names_entry_points(self):
        ep = MagicMock(); ep.name = "natlinkcore"; ep.value = "natlinkcore.loader"
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            with patch("importlib.util.find_spec", return_value=None):
                result = get_all_loader_names()
        self.assertEqual(result, [("natlinkcore", "natlinkcore.loader")])

    def test_natlinkcore_fallback(self):
        with patch("importlib.metadata.entry_points", return_value=[]):
            with patch("importlib.util.find_spec", return_value=MagicMock()):
                result = get_all_loader_names()
        self.assertEqual(result, [("natlinkcore", "natlinkcore.loader")])

    def test_discover_skips_disabled(self):
        with patch.object(_loaders, "get_disabled_loaders", return_value={"bad"}):
            with patch.object(_loaders, "get_all_loader_names",
                              return_value=[("ok", "ok.mod"), ("bad", "bad.mod")]):
                with patch("importlib.import_module", return_value=MagicMock()) as mi:
                    discover_and_import()
        mi.assert_called_once_with("ok.mod")


class TestStartStop(unittest.TestCase):

    def setUp(self): _reset()
    def tearDown(self): _reset()

    def test_start_calls_start_or_run(self):
        self.assertTrue(start_loader(_make_loader(has_start=True)))
        _state.loader_registry.clear()
        self.assertTrue(start_loader(_make_loader(has_start=False, has_run=True)))
        _state.loader_registry.clear()
        self.assertFalse(start_loader(_make_loader(has_start=False, has_run=False)))

    def test_start_exception_returns_false(self):
        l = _make_loader(); l.start.side_effect = RuntimeError
        self.assertFalse(start_loader(l))

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_start_loader(self, _):
        l = _make_loader()
        self.assertTrue(start_loader(l, "m"))
        entry = _find_entry(l)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.mod_name, "m")

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_self_registration(self, _):
        sentinel = MagicMock()
        l = _make_loader()
        l.start.side_effect = lambda: _register(sentinel)
        start_loader(l, "sr")
        self.assertIsNotNone(_find_entry(sentinel))
        self.assertIsNone(_find_entry(l))

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_stop_and_stop_all(self, mock_rm):
        l1, l2 = _make_loader("a"), _make_loader("b")
        _register(l1); _register(l2)
        stop_loaders()
        self.assertEqual(_state.loader_registry, [])
        mock_rm.assert_not_called()
        l1.stop.assert_called_once()
        l2.stop.assert_called_once()

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_unload_all_loaded_modules_does_not_guess_callback_cleanup(self, mock_rm):
        l = _make_loader("fallback", has_stop=False)
        l.unload_all_loaded_modules = MagicMock()
        stop_loader(l)
        l.unload_all_loaded_modules.assert_called_once()
        mock_rm.assert_not_called()


class TestPublicAPI(unittest.TestCase):

    def setUp(self): _reset()
    def tearDown(self): _reset()

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_add_not_connected(self, _):
        l = _make_loader()
        add_loader(l)
        self.assertIn(l, get_loaders())
        l.start.assert_not_called()

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_add_connected_starts(self, _):
        _state.backend = MagicMock()
        l = _make_loader()
        add_loader(l)
        l.start.assert_called_once()

    def test_add_rejects_no_start_or_run(self):
        with self.assertRaises(TypeError):
            add_loader(_make_loader(has_start=False, has_run=False))

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_add_skips_duplicate(self, _):
        l = _make_loader()
        _register(l)
        add_loader(l)
        self.assertEqual(len([e for e in _state.loader_registry if e.loader is l]), 1)

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_remove(self, _):
        l = _make_loader()
        _register(l)
        remove_loader(l)
        self.assertNotIn(l, get_loaders())

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_reload_trigger_load(self, _):
        l = _make_loader(has_trigger_load=True)
        _register(l)
        reload_loader(l)
        l.trigger_load.assert_called_once_with(force_load=True)

    @patch("natlink_compat._callbacks._remove_callbacks_for")
    def test_reload_all(self, _):
        l1 = _make_loader("a", has_trigger_load=True)
        l2 = _make_loader("b", has_trigger_load=True)
        _register(l1); _register(l2)
        reload_loader(None)
        l1.trigger_load.assert_called_once()
        l2.trigger_load.assert_called_once()

    def test_register_running_and_get(self):
        l = _make_loader()
        register_running_loader(l)
        self.assertEqual(get_loaders(), [l])

    def test_clear_all(self):
        _register(_make_loader())
        clear_all()
        self.assertEqual(_state.loader_registry, [])


class TestAdoptLoaderLogger(unittest.TestCase):

    def setUp(self):
        import logging
        self._logger = logging.getLogger("_test_adopt")
        self._logger.handlers.clear()
        self._logger.propagate = False

    def tearDown(self):
        self._logger.handlers.clear()
        self._logger.propagate = True

    def test_adds_notify_handler(self):
        import logging
        from natlink_compat._logging_setup import _NotifyTextHandler
        loader = MagicMock()
        # Simulate what natlinkcore's setup_logger does
        self._logger.addHandler(logging.StreamHandler())
        _adopt_loader_logger(loader, "_test_adopt.loader")
        types = [type(h) for h in self._logger.handlers]
        self.assertIn(_NotifyTextHandler, types)
        self.assertNotIn(logging.StreamHandler, types)

    def test_noop_if_already_adopted(self):
        from natlink_compat._logging_setup import _NotifyTextHandler
        loader = MagicMock()
        _adopt_loader_logger(loader, "_test_adopt.loader")
        count = sum(1 for h in self._logger.handlers
                    if isinstance(h, _NotifyTextHandler))
        _adopt_loader_logger(loader, "_test_adopt.loader")
        count2 = sum(1 for h in self._logger.handlers
                     if isinstance(h, _NotifyTextHandler))
        self.assertEqual(count, count2)

    def test_noop_for_empty_name(self):
        _adopt_loader_logger(MagicMock(), "")
        self.assertEqual(self._logger.handlers, [])

    def test_opt_out(self):
        import logging
        loader = MagicMock()
        loader.natlink_manage_logging = False
        self._logger.addHandler(logging.StreamHandler())
        _adopt_loader_logger(loader, "_test_adopt.loader")
        types = [type(h) for h in self._logger.handlers]
        self.assertIn(logging.StreamHandler, types)


class TestDisplayText(unittest.TestCase):

    def test_routes_to_notify_text(self):
        captured = []
        def fake_notify(text, level=20):
            captured.append((text, level))

        with patch("natlink_compat._ui_protocol.notify_text", fake_notify):
            from natlink_compat._legacy import displayText
            displayText("hello\r\n", False)
            displayText("error\r\n", True)

        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0], ("hello\r\n", 20))   # INFO
        self.assertEqual(captured[1], ("error\r\n", 40))    # ERROR

    def test_fallback_to_stdout(self):
        import io
        fake_stdout = io.StringIO()
        with patch("natlink_compat._ui_protocol.notify_text",
                   side_effect=ImportError):
            with patch("sys.__stdout__", fake_stdout):
                from natlink_compat._legacy import displayText
                displayText("fallback\r\n", False)
        self.assertEqual(fake_stdout.getvalue(), "fallback\r\n")
