"""Natlink CLI — headless core commands.

    natlink start                — launch headless pump (+ discovered UI provider)
    natlink stop                 — stop the launcher
    natlink info                 — show config
    natlink list-loaders         — show discovered loaders and status
    natlink enable-loader NAME   — enable a loader
    natlink disable-loader NAME  — disable a loader
    natlink dragon start|stop|restart|status — manage Dragon
"""

import logging
import sys


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""

    if cmd == "start":
        import natlink_compat
        if not natlink_compat.is_configured():
            print("Natlink is not configured. Run: natlink-ui")
            sys.exit(1)
        natlink_compat.configure()
        try:
            natlink_compat.run()
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif cmd == "stop":
        from natlink_com._launcher import request_shutdown
        if request_shutdown():
            print("Natlink stopped.")
        else:
            print("Natlink is not running.")

    elif cmd == "info":
        from natlink_com._config import load_config, print_config
        cfg = load_config()
        if cfg.sections():
            print_config(cfg)
        else:
            print("Not configured. Run: natlink-ui")

    elif cmd == "list-loaders":
        from natlink_compat._loaders import get_all_loader_names, get_disabled_loaders
        disabled = get_disabled_loaders()
        names = get_all_loader_names()
        if not names:
            print("No loaders discovered.")
        else:
            for name, mod_path in names:
                status = "disabled" if name in disabled else "enabled"
                print(f"  {name} ({mod_path}) [{status}]")

    elif cmd == "enable-loader":
        if len(args) < 2:
            print("Usage: natlink enable-loader NAME")
            sys.exit(1)
        from natlink_com._config import enable_loader
        enable_loader(args[1])
        print(f"Loader '{args[1]}' enabled")

    elif cmd == "disable-loader":
        if len(args) < 2:
            print("Usage: natlink disable-loader NAME")
            sys.exit(1)
        from natlink_com._config import disable_loader
        disable_loader(args[1])
        print(f"Loader '{args[1]}' disabled")

    elif cmd == "dragon":
        sub = args[1] if len(args) > 1 else ""
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        from . import _actions
        force = "--force" in args
        if sub == "start":
            sys.exit(_actions.start_dragon())
        elif sub == "stop":
            sys.exit(_actions.stop_dragon(force=force))
        elif sub == "restart":
            sys.exit(_actions.restart_dragon())
        elif sub == "status":
            sys.exit(_actions.dragon_status())
        else:
            print("Usage: natlink dragon start|stop|restart|status [--force]")
            sys.exit(1)

    else:
        print("Usage: natlink start | stop | info | list-loaders"
              " | enable-loader NAME | disable-loader NAME"
              " | dragon start|stop|restart|status")


if __name__ == "__main__":
    main()
