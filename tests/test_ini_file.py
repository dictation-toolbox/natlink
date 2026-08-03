"""test_ini_file.py - Tests for natlink_com._ini_file.IniFile."""

import configparser
import tempfile
import threading
import unittest
from pathlib import Path

from natlink_com._ini_file import IniFile


class TestIniFile(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.ini = IniFile(Path(self._tmpdir.name) / "test.ini")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_load_nonexistent_returns_empty(self):
        self.assertEqual(self.ini.load().sections(), [])

    def test_save_load_roundtrip(self):
        cfg = configparser.ConfigParser()
        cfg.add_section("t")
        cfg.set("t", "k", "v")
        self.ini.save(cfg)
        self.assertEqual(self.ini.load().get("t", "k"), "v")

    def test_save_creates_parent_dirs(self):
        nested = Path(self._tmpdir.name) / "a" / "b" / "c.ini"
        ini = IniFile(nested)
        cfg = configparser.ConfigParser()
        cfg.add_section("x")
        ini.save(cfg)
        self.assertTrue(nested.is_file())

    def test_get_bool_and_fallback(self):
        self.assertFalse(self.ini.get_bool("s", "k", fallback=False))
        self.assertTrue(self.ini.get_bool("s", "k", fallback=True))
        self.ini.set_bool("s", "k", True)
        self.assertTrue(self.ini.get_bool("s", "k"))

    def test_get_int_and_fallback(self):
        self.assertEqual(self.ini.get_int("s", "n", fallback=99), 99)
        self.ini.set_value("s", "n", "42")
        self.assertEqual(self.ini.get_int("s", "n"), 42)

    def test_set_value_creates_section_and_overwrites(self):
        self.ini.set_value("s", "k", "a")
        self.ini.set_value("s", "k", "b")
        self.assertEqual(self.ini.load().get("s", "k"), "b")

    def test_toggle_bool_roundtrip(self):
        self.assertTrue(self.ini.toggle_bool("s", "f", fallback=False))
        self.assertFalse(self.ini.toggle_bool("s", "f"))
        self.assertFalse(self.ini.get_bool("s", "f"))

    def test_concurrent_toggle(self):
        errors = []
        def toggle():
            try:
                for _ in range(20):
                    self.ini.toggle_bool("s", "f", fallback=False)
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=toggle) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])

    def test_path_property(self):
        self.assertTrue(str(self.ini.path).endswith("test.ini"))
