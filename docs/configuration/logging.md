# Logging

Audience: users and developers tuning natlink logging.

Purpose: document log file location, logging sections in `natlink.ini`, and the
available logger categories.

See also:

- [Configuration](index.md)
- [Settings](settings.md)
- [Troubleshooting](../troubleshooting.md)

## Log File

Default log file:

```text
%LOCALAPPDATA%\natlink\natlink.log
```

Override with `NATLINK_LOG_PATH`.

## Logging Section

```ini
[Logging]
ClientLevel = INFO
FileLevel = DEBUG
LogFile =
SlowCallbackMs = 200
```

## Per-Category Levels

```ini
[Logging.Levels]
natlink.callbacks = WARNING, DEBUG
natlink.com.grammar = DEBUG
```

Each category can use one level for both outputs or `client,file` for separate
message-window and file settings.

## Categories

| Category | Client | File | What it covers |
|----------|--------|------|---------------|
| `natlink` | WARNING | INFO | Root logger |
| `natlink.callbacks` | WARNING | DEBUG | Callback dispatch to user Python |
| `natlink.com` | WARNING | DEBUG | COM bridge, speech ops, pump |
| `natlink.com.conn` | INFO | DEBUG | Connection lifecycle |
| `natlink.com.tlb` | WARNING | INFO | Type library loading |
| `natlink.com.grammar` | WARNING | INFO | Grammar object operations |
| `natlink.com.dictation` | WARNING | INFO | Dictation object operations |
| `natlink.com.results` | WARNING | INFO | Result parsing |
| `natlink.com.marshal` | INFO | INFO | Marshal DLL registration |
| `natlink.com.lexicon` | WARNING | INFO | Vocabulary queries |
| `natlink.com.launcher` | INFO | INFO | COM-side launcher lifecycle |
| `natlink.com.dragon` | WARNING | INFO | Dragon process discovery |
| `natlink.com.sendinput` | WARNING | INFO | SendInput key/text injection |
| `natlink.com.pump` | WARNING | INFO | Win32 message pump, hidden window |
| `natlink.com.timer` | WARNING | INFO | Win32 SetTimer/WM_TIMER source |
| `natlink.com.sink` | WARNING | DEBUG | Dragon → client sink notifications |
| `natlink.com.sink.engine.attrib_changed` | WARNING | INFO | AttribChanged2 (MICSTATE, USER_CHANGED) — idle-chatty |
| `natlink.compat` | WARNING | INFO | Compatibility layer glue, UI dispatch |
| `natlink.compat.launcher` | INFO | INFO | Compat-side orchestrator (connection lifecycle) |
| `natlink.compat.loaders` | INFO | INFO | Loader discovery, start/stop/reload |
| `natlink.ui` | WARNING | INFO | Tray window, shortcuts, UI config |
