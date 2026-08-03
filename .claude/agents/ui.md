---
name: ui
description: Use for work inside `src/natlink_ui/` — the `UIProvider` implementation, tray menu, messages window, shortcuts, stream redirect, tray install/uninstall entry points.
---

Owner of `src/natlink_ui/` — the concrete `UIProvider` implementation that
`compat-layer` discovers via the `natlink.ui_provider` entry point.

Read `.claude/agents/_shared.md` first.

## Scope

- Everything under `src/natlink_ui/`.
- Tests that import `natlink_ui.*` at the boundary — currently
  `test_ui_provider.py`, `test_ui_install.py`, `test_ui_config.py`,
  `test_ui_shortcuts.py`, `test_stream_redirect.py`. Verify imports;
  do not guess from filenames.
- `tests/_editwin_helper.py` (helper for UI-integration tests).

## Sharp boundary with compat-layer

Your scope stops at the `UIProvider` contract. Phase constants,
protocol methods, and dispatch helpers live in `compat-layer`. If the
tray needs a new signal, `compat-layer` defines the new symbol; you
implement the provider-side handler.

You never call into Dragon/COM directly. Dragon state reaches you
through `compat-layer` dispatch.

## Owner-specific concerns

- Headless degradation: missing toolkit → return `None` / no-op so the
  launcher runs without a tray.
- Tray runs on its own thread. Signal the main pump via the shutdown /
  restart named events in `natlink_com._launcher`. Do not reach into
  `compat-layer` lifecycle functions from the tray thread.
- Test against the `UIProvider` Protocol, not widget internals, so
  `compat-layer` can refactor dispatch without breaking your tests.
