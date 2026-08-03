# CLI

Natlink has two entry points:

- **`natlink`** — headless engine (no GUI). Runs the COM pump, discovers loaders and a UI provider, but does not own any windows itself.
- **`natlink-ui`** — default GUI shell. Provides the tray icon, output window, and desktop shortcuts. Delegates engine work to `natlink` internally.

Use `natlink` when running headless (e.g. behind an external shell or in CI).
Use `natlink-ui` for the standard desktop experience.

Run commands from the natlink directory — `uv run` finds the `.venv`
automatically. Or activate the venv first and omit `uv run`.

See also: [Install](install.md), [Configuration](configuration/index.md), [Troubleshooting](troubleshooting.md)

## Core Commands (headless)

```text
uv run natlink start        launch the engine (COM pump + loaders + UI provider)
uv run natlink stop         stop a running engine
uv run natlink info         print current configuration
```

## UI Commands

```text
uv run natlink-ui                             launch the tray UI (configures + starts engine)
uv run natlink-ui --install-shortcuts         create desktop shortcut
uv run natlink-ui --startup                   also install a Windows Startup shortcut
uv run natlink-ui --uninstall                 stop, remove shortcuts and config
uv run natlink-ui --uninstall --keep-config   remove shortcuts but keep natlink.ini
```

Install and uninstall automatically stop a running natlink instance first.
Uninstall also stops Dragon. You do not need to close anything manually.

## Loader Commands

```text
uv run natlink list-loaders          show discovered loaders and their status
uv run natlink enable-loader NAME    enable a loader in natlink.ini
uv run natlink disable-loader NAME   disable a loader in natlink.ini
```

## Dragon Commands

```text
uv run natlink dragon start         launch Dragon
uv run natlink dragon stop          graceful shutdown
uv run natlink dragon stop --force  force-kill Dragon
uv run natlink dragon restart       stop then start
uv run natlink dragon status        show whether Dragon is running
```
