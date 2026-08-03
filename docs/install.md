# Install Natlink

## Requirements

- Windows 10 or 11
- Dragon NaturallySpeaking 13, 14, 15, or 16
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs Python automatically)

## Quick Install

1. Create a virtual environment and install natlink:

   ```powershell
   mkdir C:\natlink
   cd C:\natlink
   uv venv --python 3.14
   uv pip install natlink
   ```

2. Start natlink:

   ```powershell
   uv run natlink-ui
   ```

3. Optional: create shortcuts:

   ```powershell
   uv run natlink-ui --install-shortcuts
   ```

   - `uv run natlink-ui --startup` also runs natlink at login

Run all commands from the `C:\natlink` directory — `uv run` finds the `.venv`
automatically, no activation needed.

## Traditional Activation

If you prefer to activate the virtual environment instead of using `uv run`:

```powershell
cd C:\natlink
.venv\Scripts\activate
natlink-ui
```

You need to activate each time you open a new terminal.

## Uninstall

Automatically stops natlink and Dragon, removes shortcuts and settings:

```powershell
uv run natlink-ui --uninstall
```

## What To Expect

Starting natlink launches a tray icon:

- red: waiting for Dragon or disconnected
- green: connected
- yellow: error

If Dragon is already running, natlink connects automatically. Otherwise it
waits for Dragon to start.

## Optional Third-Party Packages

Natlink is a bridge — grammar frameworks and loaders are separate packages.
Install them into the same environment:

```powershell
uv pip install <package-name>
```

See each project's own documentation for configuration.

## See Also

- [Configuration](configuration/index.md) for `natlink.ini`
- [CLI](cli.md) for command-line operations
- [Troubleshooting](troubleshooting.md) if setup fails
- [FAQ](faq.md) for common environment questions
