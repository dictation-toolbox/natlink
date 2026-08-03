# Settings

Audience: users editing natlink's main configuration file.

Purpose: document the main natlink settings, where they live, and the most
common sections in `natlink.ini`.

See also:

- [Configuration](index.md)
- [Logging](logging.md)
- [CLI](../cli.md)

## Location

```text
%LOCALAPPDATA%\Natlink\natlink.ini
```

Override with `NATLINK_SETTINGS_DIR`.

## Creating The File

Run:

```powershell
natlink-ui
```

This detects Dragon and creates `natlink.ini` automatically.

## Common Sections

```ini
[dragon]
version = 13
install_path = C:\Program Files (x86)\Nuance\NaturallySpeaking13
exe_path = C:\Program Files (x86)\Nuance\NaturallySpeaking13\Program\natspeak.exe

[Launch]
python = C:\path\to\venv\Scripts\pythonw.exe

[settings]
auto_launch_dragon = false
show_messages_on_startup = true
show_on_error = false
```

Readers:

- `[dragon] version` — `natlink_com._config`, `natlink_com._launcher`,
  `natlink_compat.__init__` (log path selection).
- `[dragon] exe_path` — `natlink_com._dragon.launch`.
- `[dragon] install_path` — populated at config refresh; consumed by
  external tools.
- `[Launch] python` — written every run with `sys.executable` so external
  tools (loaders, installers) can locate the venv interpreter. Not read
  by natlink itself.
- `[settings] auto_launch_dragon` — `natlink_compat._launcher`.
- `[settings] show_messages_on_startup` / `show_on_error` — `natlink_ui`.

## Output Window

The output window remembers its size and position in `natlink_ui.ini`:

```ini
[window]
x = 100
y = 100
width = 800
height = 500
font_size = 18
```

## Dragon Launch Behavior

```ini
[settings]
auto_launch_dragon = false
```

When enabled, the tray starts Dragon automatically instead of waiting for it.

The same behavior can be toggled from the tray menu under the configure
options, but `natlink.ini` is the canonical place to document the setting.

## Loader Settings

Loaders are enabled or disabled in `natlink.ini`:

```ini
[loaders]
natlinkcore = enabled
# dragonfly = disabled
```

Natlink discovers loaders via the `natlink.loaders` entry point group, then
uses this section to decide which discovered loaders are active.

To change loader state without editing the file directly:

```text
natlink enable-loader natlinkcore
natlink disable-loader dragonfly
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NATLINK_SETTINGS_DIR` | `%LOCALAPPDATA%\Natlink` | Directory containing `natlink.ini` |
| `NATLINK_LOG_PATH` | `%LOCALAPPDATA%\natlink\natlink.log` | Log file path |
