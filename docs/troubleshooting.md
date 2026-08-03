# Troubleshooting

Audience: users diagnosing natlink runtime problems.

Purpose: give the shortest path to logs, common failures, and operational
checks when natlink is not working as expected.

See also:

- [Configuration](configuration/logging.md) for logging settings
- [CLI](cli.md) for command usage
- [Developer Debugging](developer-debugging.md) for debugger, tests, and docs workflow

## Log Files

Python Natlink writes to:

    - the message window
    - `%LOCALAPPDATA%\natlink\natlink.log`
    - stdout/stderr when running interactively

See [Configuration](configuration/logging.md) for log categories and settings.

- Dragon's log file is at:

    ```text
    %ProgramData%\Nuance\NaturallySpeaking16\logs\<username>\Dragon.log
    ```

Adjust the version number for your Dragon install.

## Common Issues

### Connection Fails

**Symptom**: `NatlinkCOMError: CoCreateInstance(DgnSite) ... Is Dragon running?`

- verify Dragon is running
- verify you are using 64-bit Python
- set `sys.coinit_flags = 2` before importing `comtypes` when running interactively

**Symptom**: `QueryService failed` or `QI failed`

- check that natlink was installed correctly
- check the natlink log for marshaling or COM registration failures

### Deadlock During Callbacks

**Symptom**: Dragon stops responding during a callback.

- keep callback work short

## Useful Commands

```text
natlink info
natlink start
natlink stop
```
