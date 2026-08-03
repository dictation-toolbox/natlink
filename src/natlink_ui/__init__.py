"""natlink_ui — default Win32 tray UI for natlink.

Implements the natlink_compat UIProvider protocol with a system tray
icon and RichEdit output window. Serves as both the shipping default
and a reference implementation for third-party UI providers.

Entry point registration (pyproject.toml)::

    [project.entry-points."natlink.ui_provider"]
    default = "natlink_ui:UIProvider"

Third parties replace by registering their own entry point with
a non-"default" name.
"""

import logging
import os
import threading

import natlink_compat
from natlink_compat import (
    NatlinkState,
    PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
    PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING,
    PHASE_INACTIVE, PHASE_ERROR,
)

log = logging.getLogger("natlink.ui")

_ICON_MAP = {
    PHASE_CONNECTED: "connected",
    PHASE_ERROR: "error",
}

_TOOLTIPS = {
    PHASE_IDLE: "Natlink - Disconnected",
    PHASE_WAITING_FOR_DRAGON: "Natlink - Waiting for Dragon",
    PHASE_CONNECTING: "Natlink - Connecting...",
    PHASE_LOADING_PROFILE: "Natlink - Loading profile...",
    PHASE_CONNECTED: "Natlink - Connected",
    PHASE_RESTARTING: "Natlink - Restarting Dragon...",
    PHASE_INACTIVE: "Natlink - Inactive (Dragon released)",
    PHASE_ERROR: "Natlink - {error}",
}


class UIProvider:
    """Default UIProvider — Win32 tray icon + RichEdit output window.

    Also provides app-specific features: startup shortcut management,
    show-on-error behavior, config/log file opening. These extras are
    not part of the UIProvider protocol — they're implementation details
    of the default UI that third parties don't need to replicate.
    """

    def __init__(self):
        from ._config import load as load_ui_config, save as save_ui_config
        from ._window import NatlinkWindow

        self._lock = threading.Lock()
        self._latest_phase = PHASE_IDLE
        self._window = NatlinkWindow(
            load_config=load_ui_config, save_config=save_ui_config)
        self._build_menu()
        self._window.show_tray_icon(tooltip="Natlink", icon_name="disconnected")
        self._started = True
        if self._is_show_messages_enabled():
            self._window.show()

    # --- UIProvider protocol ---

    def on_state_changed(self, state: NatlinkState) -> None:
        self._latest_phase = state.phase
        icon = _ICON_MAP.get(state.phase, "disconnected")
        tooltip = _TOOLTIPS.get(state.phase, "Natlink")
        if state.phase == PHASE_ERROR and state.error_message:
            tooltip = tooltip.format(error=state.error_message)
        self._window.show_tray_icon(tooltip, icon)

    def on_text(self, text: str, level: int = logging.INFO) -> None:
        self._window.write(text, level >= logging.WARNING)
        if level >= logging.ERROR and not self._window.is_visible:
            if self._is_show_on_error_enabled():
                self._window.show()

    # --- Optional UIProvider extensions ---

    def show_output(self):
        self._window.show()

    def hide_output(self):
        self._window.hide()

    def clear_output(self):
        self._window.clear()

    def stop(self):
        with self._lock:
            if self._started:
                self._window.destroy_safe()
                self._started = False

    # --- UI-specific settings (stored in natlink_ui.ini) ---

    @staticmethod
    def _is_show_messages_enabled():
        from ._config import get_bool
        return get_bool("settings", "show_messages_on_startup", fallback=True)

    @staticmethod
    def _is_show_on_error_enabled():
        from ._config import get_bool
        return get_bool("settings", "show_on_error", fallback=False)

    @staticmethod
    def _toggle_show_messages():
        from ._config import toggle_bool
        toggle_bool("settings", "show_messages_on_startup", fallback=True)

    @staticmethod
    def _toggle_show_on_error():
        from ._config import toggle_bool
        toggle_bool("settings", "show_on_error", fallback=False)

    # --- Inactive (release/reclaim Dragon — issue #228) ---

    def _is_inactive(self):
        return self._latest_phase == PHASE_INACTIVE

    def _toggle_inactive(self):
        """Release or reclaim Dragon. Runs on the worker thread.

        Enabling releases the single Dragon connection (and all grammars,
        callbacks, and timers) so another process can connect — gated behind
        a confirmation dialog. Disabling reconnects without confirmation.
        """
        from natlink_compat import msgbox, MB_ICONWARNING, MB_YESNO, IDYES
        if self._is_inactive():
            self._warn_if_unserviced(natlink_compat.set_inactive(False))
            return
        confirm = msgbox(
            "Release Dragon?\n\n"
            "This drops all active grammars, callbacks, and timers and frees "
            "the Dragon connection so another process can connect. Natlink "
            "stays released until you uncheck this item.",
            "Natlink", MB_YESNO | MB_ICONWARNING)
        if confirm == IDYES:
            self._warn_if_unserviced(natlink_compat.set_inactive(True))

    @staticmethod
    def _warn_if_unserviced(signaled):
        """Report a request no launcher was running to service.

        set_inactive only signals a named event; the work happens on the
        launcher's main thread. Without a launcher the signal goes nowhere,
        and the phase never changes — so the menu item silently springs back
        with no indication the request was dropped.
        """
        if signaled:
            return
        from natlink_compat import msgbox, MB_ICONWARNING
        msgbox("No natlink launcher is running to service this request.",
               "Natlink", MB_ICONWARNING)

    # --- Desktop file-opening actions ---

    @staticmethod
    def _open_config():
        from ._config import _get_store
        path = _get_store().path
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        os.startfile(path)

    @staticmethod
    def _open_natlink_log():
        import natlink_compat
        log_path = natlink_compat.get_log_path()
        if log_path.is_file():
            os.startfile(log_path)

    @staticmethod
    def _open_dragon_log():
        import natlink_compat
        base = natlink_compat.get_dragon_log_dir()
        if base is None:
            return
        os.startfile(base)

    # --- Shortcuts (delegate to _shortcuts module) ---

    @staticmethod
    def toggle_startup():
        from . import _shortcuts
        if _shortcuts.is_startup_installed():
            _shortcuts.uninstall_startup()
        else:
            _shortcuts.install_startup()

    @staticmethod
    def is_startup_installed():
        from . import _shortcuts
        return _shortcuts.is_startup_installed()

    # --- Menu ---

    def _toggle_topmost(self):
        self._window.set_topmost(not self._window.is_topmost)

    # --- Logging submenu ---------------------------------------------------

    @staticmethod
    def _category_group(name: str) -> str:
        """Return the display group for a logging category."""
        if name == "natlink":
            return "Root"
        if name == "natlink.com.sink" or name.startswith("natlink.com.sink."):
            return "Sinks"
        if name == "natlink.com" or name.startswith("natlink.com."):
            return "COM"
        if name == "natlink.callbacks" or name.startswith("natlink.callbacks."):
            return "Callbacks"
        if name == "natlink.compat" or name.startswith("natlink.compat."):
            return "Compat"
        if name == "natlink.ui" or name.startswith("natlink.ui."):
            return "UI"
        return "Other"

    @staticmethod
    def _current_cat_level(name: str) -> str:
        """Return current client level string for a category (or '')."""
        cat = natlink_compat.get_log_category(name)
        return cat["client"] if cat else ""

    def _build_logging_submenu(self):
        """Build the nested Logging submenu: Reset / Presets / Categories."""
        cats = natlink_compat.list_log_categories()
        presets = natlink_compat.list_log_presets()

        preset_items = [
            (p["label"],
             (lambda pid=p["id"]: lambda: natlink_compat.apply_log_preset(pid))(),
             None)
            for p in presets
        ]

        level_names = ("DEBUG", "INFO", "WARNING", "ERROR")

        # Group categories by display bucket, preserving declaration order
        groups: dict = {
            "Root": [], "COM": [], "Sinks": [], "Callbacks": [],
            "Compat": [], "UI": [], "Other": [],
        }
        for cat in cats:
            groups[self._category_group(cat["name"])].append(cat)

        group_menus = []
        for group_label, group_cats in groups.items():
            if not group_cats:
                continue
            cat_items = []
            for cat in group_cats:
                name = cat["name"]
                lvl_items = [
                    (lvl,
                     (lambda n=name, l=lvl:
                        lambda: natlink_compat.set_log_level(n, l))(),
                     (lambda n=name, l=lvl:
                        lambda: self._current_cat_level(n) == l)())
                    for lvl in level_names
                ]
                lvl_items.append(None)
                lvl_items.append((
                    "Reset",
                    (lambda n=name:
                        lambda: natlink_compat.reset_log_level(n))(),
                    None,
                ))
                cat_items.append(("submenu", name, lvl_items))
            group_menus.append(("submenu", group_label, cat_items))

        return [
            ("Reset all overrides",
             lambda: natlink_compat.reset_log_levels(), None),
            None,
            ("submenu", "Presets", preset_items),
            None,
            *group_menus,
        ]

    def _build_loader_submenu(self):
        """Build the Loaders submenu from current loader states."""
        loader_items = [("Reload Grammars", lambda: natlink_compat.reload_grammars(), None)]
        states = natlink_compat.get_loader_states()
        if states:
            loader_items.append(None)
        for name, _enabled, _running in states:
            loader_items.append(
                (name,
                 (lambda n: lambda: natlink_compat.toggle_loader(n))(name),
                 (lambda n: lambda: {s[0]: s[1] for s in natlink_compat.get_loader_states()}.get(n, True))(name)))
        return loader_items

    def _build_menu(self):
        w = self._window

        w.add_submenu("Message Window", [
            ("Show", self._window.show, None),
            ("Hide", self._window.hide, None),
            ("Clear", self._window.clear, None),
            ("Always on Top", self._toggle_topmost, lambda: self._window.is_topmost),
        ])

        w.add_separator()
        w.add_submenu("Logs", [
            ("Natlink Log", self._open_natlink_log, None),
            ("Dragon Log", self._open_dragon_log, None),
            None,
            # Lazy: rebuilt on each right-click so log categories added or
            # removed after startup appear.
            ("submenu", "Logging", self._build_logging_submenu),
        ])

        w.add_separator()
        # Lazy: rebuilt on each right-click so loaders reflect current state.
        w.add_submenu("Loaders", self._build_loader_submenu)

        w.add_submenu("Configure", [
            ("Edit Config", self._open_config, None),
            ("Run at Startup", self.toggle_startup, self.is_startup_installed),
            ("Auto-launch Dragon", lambda: natlink_compat.toggle_auto_launch(), lambda: natlink_compat.is_auto_launch_enabled()),
            ("Show Messages on Startup", self._toggle_show_messages, self._is_show_messages_enabled),
            ("Show on Error", self._toggle_show_on_error, self._is_show_on_error_enabled),
            # Unlike its neighbours this is runtime state, not a persisted
            # setting: it hands the single Dragon connection to another
            # process and is dropped on restart.
            ("Release Dragon", self._toggle_inactive, self._is_inactive),
        ])

        w.add_separator()

        def _dragon_label():
            return "Restart Dragon" if natlink_compat.is_dragon_running() else "Launch Dragon"

        def _dragon_action():
            if natlink_compat.is_dragon_running():
                natlink_compat.restart_dragon()
            else:
                natlink_compat.start_dragon()

        w.add_menu_item(_dragon_label, _dragon_action)
        w.add_menu_item("Exit", lambda: natlink_compat.exit_natlink())


# ---------------------------------------------------------------------------
# Module-level UI control — import natlink_ui; natlink_ui.show_output()
# ---------------------------------------------------------------------------

def _get_provider():
    """Return our UIProvider from the active provider slot, or None."""
    import natlink_compat
    provider = natlink_compat.get_ui_provider()
    if isinstance(provider, UIProvider):
        return provider
    return None


def show_output():
    p = _get_provider()
    if p is not None:
        p.show_output()


def hide_output():
    p = _get_provider()
    if p is not None:
        p.hide_output()


def clear_output():
    p = _get_provider()
    if p is not None:
        p.clear_output()


# ---------------------------------------------------------------------------
# UI install/uninstall
# ---------------------------------------------------------------------------

def bootstrap_config() -> int:
    """Configure runtime if possible."""
    cfg = natlink_compat.configure_runtime()
    if not cfg.has_section("dragon"):
        print("Dragon NaturallySpeaking not found.\n"
              "Install Dragon first, then run: natlink-ui")
        return 1

    from natlink_compat import print_config
    print_config(cfg)
    return 0


def install_ui(*, startup: bool = False) -> int:
    """Configure runtime and install default UI integration."""
    from natlink_compat import request_shutdown
    from . import _shortcuts

    # Stop running natlink instance to avoid config/shortcut conflicts
    if request_shutdown():
        print("Stopped running natlink instance.")

    rc = bootstrap_config()
    if rc:
        return rc

    desktop_ok = _shortcuts.create_desktop_shortcut()
    startup_ok = True
    if startup:
        startup_ok = _shortcuts.install_startup()

    if not desktop_ok:
        print("Warning: desktop shortcut was not created.")
    if startup and not startup_ok:
        print("Warning: startup shortcut was not created.")

    print("\nNatlink configured. Run 'natlink start' to launch.")
    return 0


def uninstall_ui(*, remove_config: bool = True) -> int:
    """Remove default UI integration and optionally natlink.ini."""
    from natlink_compat import request_shutdown
    from . import _shortcuts

    if request_shutdown():
        print("Natlink stopped.")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        natlink_compat.stop_dragon()
    except Exception:
        print("Warning: could not stop Dragon (it may not be running)")

    _shortcuts.uninstall_startup()
    _shortcuts.remove_desktop_shortcut()

    if remove_config:
        config_path = natlink_compat.get_config_path()
        try:
            natlink_compat.remove_runtime_config()
            print(f"Removed: {config_path}")
        except OSError as exc:
            print(f"Could not remove {config_path}: {exc}")
            return 1
    return 0


def cli_main() -> None:
    """Console entry point for UI-owned install and uninstall."""
    import argparse

    parser = argparse.ArgumentParser(prog="natlink-ui", description="Natlink UI setup")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Configure natlink and install UI shortcuts")
    install_parser.add_argument("--startup", action="store_true", help="Install a Windows Startup shortcut")

    uninstall_parser = subparsers.add_parser("uninstall", help="Remove UI shortcuts and natlink configuration")
    uninstall_parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Remove UI integration but leave natlink.ini in place",
    )

    args = parser.parse_args()
    if args.command == "install":
        raise SystemExit(install_ui(startup=args.startup))
    if args.command == "uninstall":
        raise SystemExit(uninstall_ui(remove_config=not args.keep_config))
    parser.print_help()


# ---------------------------------------------------------------------------
# Entry point — natlink-ui GUI launcher
# ---------------------------------------------------------------------------

def main():
    """GUI entry point for natlink-ui. No console window."""
    import argparse

    parser = argparse.ArgumentParser(prog="natlink-ui")
    parser.add_argument("--install-shortcuts", action="store_true",
                        help="Configure natlink and create the desktop shortcut")
    parser.add_argument("--startup", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--keep-config", action="store_true")
    args, _unknown = parser.parse_known_args()

    import natlink_compat
    if args.uninstall:
        raise SystemExit(uninstall_ui(remove_config=not args.keep_config))
    if args.install_shortcuts or args.startup:
        raise SystemExit(install_ui(startup=args.startup))

    if not natlink_compat.is_configured():
        if bootstrap_config():
            from ._win32 import msgbox, MB_ICONERROR
            msgbox("Natlink is not configured.\n"
                   "Install Dragon first, then run natlink-ui again.",
                   "Natlink", MB_ICONERROR)
            return

    try:
        natlink_compat.configure()
        natlink_compat.run()
    except Exception:
        log.exception("Natlink failed")
