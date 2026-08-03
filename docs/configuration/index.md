# Configuration

Audience: users and administrators configuring natlink after installation.

Purpose: explain where natlink settings live and where to find each category of
settings.

See also:

- [Install](../install.md) for first-time setup
- [CLI](../cli.md) for command-line operations
- [Troubleshooting](../troubleshooting.md) for logs and troubleshooting

## Config Files

Natlink's main configuration file is:

```text
%LOCALAPPDATA%\Natlink\natlink.ini
```

Override this location with the `NATLINK_SETTINGS_DIR` environment variable.

Natlinkcore has its own separate configuration for grammar directories and
loader behavior. That setup belongs to natlinkcore documentation.

## Sections

- [Settings](settings.md)
- [Logging](logging.md)
