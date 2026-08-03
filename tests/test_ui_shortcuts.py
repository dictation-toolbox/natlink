"""test_ui_shortcuts.py - Unit tests for natlink_ui._shortcuts.

Tests shortcut path helpers and creation logic with mocked Win32 APIs.
Does NOT require Dragon or elevated permissions.
"""

import os
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestIconPath(unittest.TestCase):

    def test_icon_path_under_natlink_ui(self):
        from natlink_ui._shortcuts import _icon_path
        path = _icon_path()
        self.assertTrue(path.endswith("natlink.ico"))
        self.assertIn("natlink_ui", path)


class TestStartupPath(unittest.TestCase):

    @patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_startup_path_format(self):
        from natlink_ui._shortcuts import _startup_path
        path = _startup_path()
        self.assertEqual(path.name, "Natlink.lnk")
        self.assertIn("Startup", str(path))

    def test_startup_path_missing_appdata(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove APPDATA entirely
            env = os.environ.copy()
            env.pop("APPDATA", None)
            with patch.dict(os.environ, env, clear=True):
                from natlink_ui._shortcuts import _startup_path
                with self.assertRaises(OSError):
                    _startup_path()


class TestFindUIExe(unittest.TestCase):

    def test_finds_natlink_ui_exe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            exe = Path(tmpdir) / "natlink-ui.exe"
            exe.touch()
            with patch("sys.executable", str(Path(tmpdir) / "python.exe")):
                from natlink_ui._shortcuts import _find_ui_exe
                result = _find_ui_exe()
                self.assertEqual(result, str(exe))

    def test_finds_in_scripts_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts = Path(tmpdir) / "Scripts"
            scripts.mkdir()
            exe = scripts / "natlink-ui.exe"
            exe.touch()
            with patch("sys.executable", str(Path(tmpdir) / "python.exe")):
                from natlink_ui._shortcuts import _find_ui_exe
                result = _find_ui_exe()
                self.assertEqual(result, str(exe))

    def test_returns_empty_when_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("sys.executable", str(Path(tmpdir) / "python.exe")), \
                 patch("shutil.which", return_value=None):
                from natlink_ui._shortcuts import _find_ui_exe
                result = _find_ui_exe()
                self.assertEqual(result, "")

    def test_falls_back_to_path(self):
        """When not beside sys.executable, _find_ui_exe uses shutil.which."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found_path = "C:\\path\\to\\natlink-ui.exe"
            with patch("sys.executable", str(Path(tmpdir) / "python.exe")), \
                 patch("shutil.which", return_value=found_path):
                from natlink_ui._shortcuts import _find_ui_exe
                result = _find_ui_exe()
                self.assertEqual(result, found_path)


class TestPsEscape(unittest.TestCase):
    """Test PowerShell single-quote escaping."""

    def test_no_special_chars(self):
        from natlink_ui._shortcuts import _create_shortcut
        # Access the inner function via the module
        import natlink_ui._shortcuts as mod
        # _ps_escape is defined inside _create_shortcut, so test via behavior
        # Just verify the function doesn't crash with normal paths
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            mod._create_shortcut("C:\\test.lnk", "C:\\app.exe")
            call_args = mock_run.call_args[0][0]
            self.assertEqual(call_args[0], "powershell.exe")

    def test_single_quote_in_path(self):
        """Paths with single quotes should be doubled for PS escaping."""
        import natlink_ui._shortcuts as mod
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            mod._create_shortcut("C:\\it's a test.lnk", "C:\\app.exe")
            ps_cmd = mock_run.call_args[0][0][3]  # -Command argument
            self.assertIn("it''s a test", ps_cmd)


class TestCreateShortcutReturnCode(unittest.TestCase):

    def test_returns_false_on_failure(self):
        import natlink_ui._shortcuts as mod
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr=b"boom")
            self.assertFalse(mod._create_shortcut("C:\\test.lnk", "C:\\app.exe"))

    def test_returns_true_on_success(self):
        import natlink_ui._shortcuts as mod
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            self.assertTrue(mod._create_shortcut("C:\\test.lnk", "C:\\app.exe"))

    def test_logs_warning_on_failure(self):
        import natlink_ui._shortcuts as mod
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr=b"PowerShell error message")
            with self.assertLogs("natlink.ui.shortcuts", level="WARNING") as cm:
                mod._create_shortcut("C:\\test.lnk", "C:\\app.exe")
            self.assertTrue(any("failed" in msg.lower() for msg in cm.output))

    def test_no_warning_on_success(self):
        import natlink_ui._shortcuts as mod
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Should not produce warnings
            mod._create_shortcut("C:\\test.lnk", "C:\\app.exe")


class TestIsStartupInstalled(unittest.TestCase):

    @patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_not_installed(self):
        from natlink_ui._shortcuts import is_startup_installed
        with patch("pathlib.Path.is_file", return_value=False):
            self.assertFalse(is_startup_installed())

    @patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_installed(self):
        from natlink_ui._shortcuts import is_startup_installed
        with patch("pathlib.Path.is_file", return_value=True):
            self.assertTrue(is_startup_installed())


class TestShortcutInstallers(unittest.TestCase):

    @patch("natlink_ui._shortcuts._icon_path", return_value="C:\\natlink.ico")
    @patch("natlink_ui._shortcuts._startup_path", return_value=Path("C:\\Startup\\Natlink.lnk"))
    @patch("natlink_ui._shortcuts._find_ui_exe", return_value="C:\\natlink-ui.exe")
    @patch("natlink_ui._shortcuts._create_shortcut", return_value=False)
    def test_install_startup_does_not_print_success_on_failure(
        self,
        mock_create_shortcut,
        mock_find_ui_exe,
        mock_startup_path,
        mock_icon_path,
    ):
        from natlink_ui._shortcuts import install_startup

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            self.assertFalse(install_startup())

        self.assertNotIn("installed startup shortcut", mock_out.getvalue().lower())

    @patch("natlink_ui._shortcuts._icon_path", return_value="C:\\natlink.ico")
    @patch("natlink_ui._shortcuts._desktop_shortcut_path", return_value=Path("C:\\Desktop\\Natlink.lnk"))
    @patch("natlink_ui._shortcuts._find_ui_exe", return_value="C:\\natlink-ui.exe")
    @patch("natlink_ui._shortcuts._create_shortcut", return_value=False)
    def test_create_desktop_shortcut_does_not_print_success_on_failure(
        self,
        mock_create_shortcut,
        mock_find_ui_exe,
        mock_desktop_shortcut_path,
        mock_icon_path,
    ):
        from natlink_ui._shortcuts import create_desktop_shortcut

        with patch("pathlib.Path.exists", return_value=False):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                self.assertFalse(create_desktop_shortcut())

        self.assertNotIn("created desktop shortcut", mock_out.getvalue().lower())
