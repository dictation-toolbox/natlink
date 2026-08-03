"""test_ui_config.py - Unit tests for natlink_ui._config.

Tests config load/save/toggle with a temporary config directory.
Does NOT require Dragon or a running UI.
"""

import configparser
import tempfile
import threading
import unittest
from pathlib import Path

from natlink_com._ini_file import IniFile


class TestUIConfig(unittest.TestCase):
    """Test natlink_ui._config with a temp directory."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._config_path = Path(self._tmpdir.name) / "natlink_ui.ini"
        # Install a temp-backed IniFile as the module's store
        import natlink_ui._config as _mod
        self._orig_store = getattr(_mod, "_store", None)
        _mod._store = IniFile(self._config_path)

    def tearDown(self):
        import natlink_ui._config as _mod
        if self._orig_store is not None:
            _mod._store = self._orig_store
        else:
            try:
                del _mod._store
            except AttributeError:
                pass
        self._tmpdir.cleanup()

    def test_load_empty(self):
        from natlink_ui._config import load
        cfg = load()
        self.assertEqual(cfg.sections(), [])

    def test_save_and_load(self):
        from natlink_ui._config import load, save

        cfg = configparser.ConfigParser()
        cfg.add_section("test")
        cfg.set("test", "key", "value")
        save(cfg)

        loaded = load()
        self.assertEqual(loaded.get("test", "key"), "value")

    def test_get_bool_default(self):
        from natlink_ui._config import get_bool
        self.assertFalse(get_bool("settings", "missing_key", fallback=False))
        self.assertTrue(get_bool("settings", "missing_key", fallback=True))

    def test_get_bool_from_file(self):
        from natlink_ui._config import save, get_bool

        cfg = configparser.ConfigParser()
        cfg.add_section("settings")
        cfg.set("settings", "flag", "true")
        save(cfg)

        self.assertTrue(get_bool("settings", "flag", fallback=False))

    def test_get_int_default(self):
        from natlink_ui._config import get_int
        self.assertEqual(get_int("window", "font_size", fallback=18), 18)

    def test_toggle_bool_creates_section(self):
        from natlink_ui._config import toggle_bool, get_bool

        result = toggle_bool("settings", "flag", fallback=False)
        self.assertTrue(result)
        self.assertTrue(get_bool("settings", "flag", fallback=False))

    def test_toggle_bool_flips(self):
        from natlink_ui._config import toggle_bool, save

        # Set initial value
        cfg = configparser.ConfigParser()
        cfg.add_section("settings")
        cfg.set("settings", "flag", "true")
        save(cfg)

        # Toggle should flip to false
        result = toggle_bool("settings", "flag", fallback=False)
        self.assertFalse(result)

        # Toggle again should flip back to true
        result = toggle_bool("settings", "flag", fallback=False)
        self.assertTrue(result)

    def test_toggle_bool_thread_safety(self):
        """Multiple threads toggling the same key should not corrupt config."""
        from natlink_ui._config import toggle_bool, get_bool

        errors = []

        def toggle_many():
            try:
                for _ in range(20):
                    toggle_bool("settings", "flag", fallback=False)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=toggle_many) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        # Value should be a valid bool regardless of toggle count
        val = get_bool("settings", "flag", fallback=False)
        self.assertIsInstance(val, bool)

    def test_save_creates_parent_directory(self):
        import natlink_ui._config as _mod
        from natlink_ui._config import save

        nested = Path(self._tmpdir.name) / "sub" / "dir" / "natlink_ui.ini"
        _mod._store = IniFile(nested)
        try:
            cfg = configparser.ConfigParser()
            cfg.add_section("test")
            save(cfg)
            self.assertTrue(nested.is_file())
        finally:
            _mod._store = IniFile(self._config_path)
