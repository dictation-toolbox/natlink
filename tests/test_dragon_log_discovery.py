"""test_dragon_log_discovery.py - Picking the Dragon log Dragon is using.

Dragon keeps one log subdirectory per profile plus a SYSTEM directory written
once at install time. SYSTEM sorts first and never changes again, so taking
the first match in directory order selected a file frozen at install --
observed live as a 1,402-byte SYSTEM log from two months earlier winning over
a 6 MB live profile log.
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from natlink_com._launcher import find_dragon_log, dragon_log_dir


class _LogTree(unittest.TestCase):

    def _tree(self, *, entries):
        """Build logs/<name>/Dragon.log for each (name, mtime) pair."""
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name) / "Nuance" / "NaturallySpeaking13" / "logs"
        base.mkdir(parents=True)  # exists even when empty, as after an install
        for name, mtime in entries:
            d = base / name
            d.mkdir(parents=True)
            log = d / "Dragon.log"
            log.write_text(name)
            os.utime(log, (mtime, mtime))
        self.enterContext(patch.dict(os.environ, {"PROGRAMDATA": tmp.name}))
        return base


class TestFindDragonLog(_LogTree):

    def test_prefers_newest_over_directory_order(self):
        """SYSTEM sorts first but is frozen at install time."""
        self._tree(entries=[("SYSTEM", 1_000_000), ("TechMeh", 2_000_000)])
        self.assertEqual(find_dragon_log("13").parent.name, "TechMeh")

    def test_order_independent(self):
        """Same answer when the stale directory sorts last instead."""
        self._tree(entries=[("aaa_stale", 1_000_000), ("zzz_live", 2_000_000)])
        self.assertEqual(find_dragon_log("13").parent.name, "zzz_live")

    def test_single_profile(self):
        self._tree(entries=[("OnlyUser", 1_000_000)])
        self.assertEqual(find_dragon_log("13").parent.name, "OnlyUser")

    def test_none_when_no_log_exists(self):
        self._tree(entries=[])
        self.assertIsNone(find_dragon_log("13"))

    def test_none_when_tree_is_absent(self):
        self._tree(entries=[])
        self.assertIsNone(find_dragon_log("99"))

    def test_ignores_stray_files_beside_the_profile_dirs(self):
        """A dgnsetup*.log file sits next to the profile directories."""
        base = self._tree(entries=[("TechMeh", 2_000_000)])
        (base / "dgnsetup662026053332.log").write_text("installer noise")
        self.assertEqual(find_dragon_log("13").parent.name, "TechMeh")

    def test_dir_is_version_specific(self):
        self._tree(entries=[])
        self.assertEqual(dragon_log_dir("16").name, "logs")
        self.assertEqual(dragon_log_dir("16").parent.name, "NaturallySpeaking16")


class TestTrayLogDir(_LogTree):
    """natlink_compat.get_dragon_log_dir feeds the tray's "Open Dragon log"."""

    def test_opens_the_live_profile_dir(self):
        self._tree(entries=[("SYSTEM", 1_000_000), ("TechMeh", 2_000_000)])
        import natlink_compat
        with patch.object(natlink_compat, "load_config") as cfg:
            cfg.return_value.get.return_value = "13"
            self.assertEqual(natlink_compat.get_dragon_log_dir().name, "TechMeh")

    def test_falls_back_to_base_when_no_log_found(self):
        self._tree(entries=[])
        import natlink_compat
        with patch.object(natlink_compat, "load_config") as cfg:
            cfg.return_value.get.return_value = "13"
            self.assertEqual(natlink_compat.get_dragon_log_dir().name, "logs")
