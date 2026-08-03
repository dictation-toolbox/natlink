"""test_cli.py - Unit tests for natlink_compat._cli.

These tests do NOT require Dragon — all external calls are mocked.
"""

import sys
import unittest
from io import StringIO
from unittest.mock import patch


class TestCLIStop(unittest.TestCase):

    @patch("natlink_com._launcher.request_shutdown", return_value=True)
    def test_stop_running(self, mock_shutdown):
        with patch.object(sys, "argv", ["natlink", "stop"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        self.assertIn("stopped", mock_out.getvalue().lower())

    @patch("natlink_com._launcher.request_shutdown", return_value=False)
    def test_stop_not_running(self, mock_shutdown):
        with patch.object(sys, "argv", ["natlink", "stop"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        self.assertIn("not running", mock_out.getvalue().lower())


class TestCLIInfo(unittest.TestCase):

    @patch("natlink_com._config.print_config")
    @patch("natlink_com._config.load_config")
    def test_info_configured(self, mock_load, mock_print):
        import configparser
        cfg = configparser.ConfigParser()
        cfg.add_section("dragon")
        mock_load.return_value = cfg

        with patch.object(sys, "argv", ["natlink", "info"]):
            from natlink_compat._cli import main
            main()

        mock_print.assert_called_once_with(cfg)

    @patch("natlink_com._config.load_config")
    def test_info_not_configured(self, mock_load):
        import configparser
        mock_load.return_value = configparser.ConfigParser()

        with patch.object(sys, "argv", ["natlink", "info"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        self.assertIn("natlink-ui", mock_out.getvalue())


class TestCLILoaderCommands(unittest.TestCase):

    @patch("natlink_com._config.enable_loader")
    def test_enable_loader(self, mock_enable):
        with patch.object(sys, "argv", ["natlink", "enable-loader", "myloader"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        mock_enable.assert_called_once_with("myloader")
        self.assertIn("enabled", mock_out.getvalue().lower())

    @patch("natlink_com._config.disable_loader")
    def test_disable_loader(self, mock_disable):
        with patch.object(sys, "argv", ["natlink", "disable-loader", "myloader"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        mock_disable.assert_called_once_with("myloader")
        self.assertIn("disabled", mock_out.getvalue().lower())

    def test_enable_loader_missing_name(self):
        with patch.object(sys, "argv", ["natlink", "enable-loader"]):
            with patch("sys.stdout", new_callable=StringIO):
                from natlink_compat._cli import main
                with self.assertRaises(SystemExit) as ctx:
                    main()
                self.assertEqual(ctx.exception.code, 1)


class TestCLIDragonSubcommands(unittest.TestCase):

    @patch("natlink_compat._actions.start_dragon", return_value=0)
    def test_dragon_start(self, mock_start):
        with patch.object(sys, "argv", ["natlink", "dragon", "start"]):
            with self.assertRaises(SystemExit) as ctx:
                from natlink_compat._cli import main
                main()
            self.assertEqual(ctx.exception.code, 0)

    @patch("natlink_compat._actions.dragon_status", return_value=0)
    def test_dragon_status(self, mock_status):
        with patch.object(sys, "argv", ["natlink", "dragon", "status"]):
            with self.assertRaises(SystemExit) as ctx:
                from natlink_compat._cli import main
                main()
            self.assertEqual(ctx.exception.code, 0)

    def test_dragon_no_subcommand(self):
        with patch.object(sys, "argv", ["natlink", "dragon"]):
            with patch("sys.stdout", new_callable=StringIO):
                from natlink_compat._cli import main
                with self.assertRaises(SystemExit) as ctx:
                    main()
                self.assertEqual(ctx.exception.code, 1)


class TestCLIUsage(unittest.TestCase):

    def test_no_command_shows_usage(self):
        with patch.object(sys, "argv", ["natlink"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        self.assertIn("usage", mock_out.getvalue().lower())

    def test_unknown_command_shows_usage(self):
        with patch.object(sys, "argv", ["natlink", "foobar"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                from natlink_compat._cli import main
                main()
        self.assertIn("usage", mock_out.getvalue().lower())
