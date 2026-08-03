"""Tests for natlink_ui install and uninstall entry points."""

import configparser
import sys
import unittest
from io import StringIO
from unittest.mock import patch


class TestInstallUI(unittest.TestCase):

    @patch("natlink_ui._shortcuts.create_desktop_shortcut", return_value=True)
    @patch("natlink_compat.print_config")
    @patch("natlink_compat.configure_runtime")
    def test_install_ui_configures_runtime_and_desktop_shortcut(
        self,
        mock_configure_runtime,
        mockprint_config,
        mock_create_desktop_shortcut,
    ):
        cfg = configparser.ConfigParser()
        cfg.add_section("dragon")
        mock_configure_runtime.return_value = cfg

        from natlink_ui import install_ui

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = install_ui()

        self.assertEqual(rc, 0)
        mock_configure_runtime.assert_called_once_with()
        mockprint_config.assert_called_once_with(cfg)
        mock_create_desktop_shortcut.assert_called_once_with()
        self.assertIn("configured", mock_out.getvalue().lower())

    @patch("natlink_ui._shortcuts.install_startup", return_value=True)
    @patch("natlink_ui._shortcuts.create_desktop_shortcut", return_value=True)
    @patch("natlink_compat.print_config")
    @patch("natlink_compat.configure_runtime")
    def test_install_ui_with_startup_installs_startup_shortcut(
        self,
        mock_configure_runtime,
        mockprint_config,
        mock_create_desktop_shortcut,
        mock_install_startup,
    ):
        cfg = configparser.ConfigParser()
        cfg.add_section("dragon")
        mock_configure_runtime.return_value = cfg

        from natlink_ui import install_ui

        rc = install_ui(startup=True)

        self.assertEqual(rc, 0)
        mock_install_startup.assert_called_once_with()

    @patch("natlink_compat.configure_runtime")
    def test_install_ui_without_dragon_returns_error(self, mock_configure_runtime):
        mock_configure_runtime.return_value = configparser.ConfigParser()

        from natlink_ui import install_ui

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = install_ui()

        self.assertEqual(rc, 1)
        self.assertIn("natlink-ui", mock_out.getvalue())


class TestUninstallUI(unittest.TestCase):

    @patch("natlink_compat.remove_runtime_config")
    @patch("natlink_compat.get_config_path")
    @patch("natlink_ui._shortcuts.remove_desktop_shortcut", return_value=True)
    @patch("natlink_ui._shortcuts.uninstall_startup", return_value=True)
    @patch("natlink_compat.stop_dragon")
    @patch("natlink_compat.request_shutdown", return_value=True)
    def test_uninstall_ui_removes_shortcuts_and_config(
        self,
        mock_request_shutdown,
        mock_stop_dragon,
        mock_uninstall_startup,
        mock_remove_desktop_shortcut,
        mock_get_config_path,
        mock_remove_runtime_config,
    ):
        from pathlib import Path
        from natlink_ui import uninstall_ui

        mock_get_config_path.return_value = Path("C:/tmp/natlink.ini")

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = uninstall_ui()

        self.assertEqual(rc, 0)
        mock_request_shutdown.assert_called_once_with()
        mock_stop_dragon.assert_called_once_with()
        mock_uninstall_startup.assert_called_once_with()
        mock_remove_desktop_shortcut.assert_called_once_with()
        mock_remove_runtime_config.assert_called_once_with()
        self.assertIn("removed", mock_out.getvalue().lower())

    @patch("natlink_compat.remove_runtime_config")
    @patch("natlink_ui._shortcuts.remove_desktop_shortcut", return_value=True)
    @patch("natlink_ui._shortcuts.uninstall_startup", return_value=True)
    @patch("natlink_compat.stop_dragon")
    @patch("natlink_compat.request_shutdown", return_value=False)
    def test_uninstall_ui_keep_config_skips_config_removal(
        self,
        mock_request_shutdown,
        mock_stop_dragon,
        mock_uninstall_startup,
        mock_remove_desktop_shortcut,
        mock_remove_runtime_config,
    ):
        from natlink_ui import uninstall_ui

        rc = uninstall_ui(remove_config=False)

        self.assertEqual(rc, 0)
        mock_remove_runtime_config.assert_not_called()


class TestUISetupCli(unittest.TestCase):

    @patch("natlink_ui.install_ui", return_value=0)
    def test_cli_main_install(self, mock_install_ui):
        from natlink_ui import cli_main

        with patch.object(sys, "argv", ["natlink-ui", "install", "--startup"]):
            with self.assertRaises(SystemExit) as ctx:
                cli_main()

        self.assertEqual(ctx.exception.code, 0)
        mock_install_ui.assert_called_once_with(startup=True)

    @patch("natlink_ui.uninstall_ui", return_value=0)
    def test_cli_main_uninstall_keep_config(self, mock_uninstall_ui):
        from natlink_ui import cli_main

        with patch.object(sys, "argv", ["natlink-ui", "uninstall", "--keep-config"]):
            with self.assertRaises(SystemExit) as ctx:
                cli_main()

        self.assertEqual(ctx.exception.code, 0)
        mock_uninstall_ui.assert_called_once_with(remove_config=False)
