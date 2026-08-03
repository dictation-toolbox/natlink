# Architecture

Audience: natlink developers and maintainers.

Purpose: explain the system boundaries, major layers, and architectural
invariants. This page is not the API reference and not the lifecycle walkthrough.

See also:

- [Program Flow](program_flow.md) for step-by-step startup, reconnect, and shutdown
- [Project Structure](structure.md) for code layout
- [Natlink](third_party/index.md) for the public UI and loader contracts

## System Shape

Natlink is a pure-Python out-of-process COM client for Dragon. It replaces the
old in-process C++ extension model with a layered Python stack:

```text
User grammars / natlinkcore / Dragonfly / Unimacro / Caster
                      |
                 import natlink
                      |
               +--------------+
               |   natlink    |  public re-export
               +--------------+
                      |
               +--------------+
               | natlink_compat | compatibility surface + orchestration
               +--------------+
                      |
               +--------------+
               | natlink_com  | direct COM backend
               +--------------+
                      |
                 Dragon COM


               +--------------+
               | natlink_ui   | Win32 tray (or any UIProvider)
               +--------------+
                      |
                imports from
                      |
               natlink_compat
```

## Layer Responsibilities

### `natlink`

Owns the public import surface used by grammars and loader ecosystems. It
re-exports the compatibility layer and preserves the legacy
`natlink.active_loader` behavior for natlinkcore compatibility.

### `natlink_compat`

Owns the compatibility API: module-level functions, `GramObj`/`ResObj`/`DictObj`,
exceptions, loader registration helpers, and the UI provider dispatch.
Also owns the CLI (`_cli.py`), the launcher (`_launcher.py`),
and action functions (`_actions.py`).

### `natlink_com`

Owns direct COM integration with Dragon: connection lifecycle, interface
resolution, sink registration, marshal DLL setup, and the low-level object
wrappers that back the compatibility layer. Provides launcher primitives
(COM probing, event hooks, mutex, startup shortcuts) but does not own
the orchestration that ties them together.

COM interface wrappers are vendored (pre-generated from type libraries) rather
than generated at runtime, eliminating the fragile codegen cache.
`scripts\build.ps1` rebuilds all native artifacts from the IDL sources.

### `natlink_ui`

Default Win32 tray + RichEdit output window. Implements the `UIProvider`
protocol. Third parties can replace it entirely by registering their own
entry point.

Also owns presentation infrastructure: stream redirection (`_stream_redirect.py`),
desktop shortcuts (`_shortcuts.py`), and UI-specific config (`_config.py`).

## UI Integration

One protocol, one provider slot, one direction:

```text
Engine pushes:   natlink_compat  ──on_state_changed──▶  UIProvider
                 natlink_compat  ──on_text(text,level)──▶  UIProvider

UI commands:     UIProvider  ──import natlink_compat──▶  natlink_compat.restart_dragon()
                                                         natlink_compat.set_log_level("natlink.com.grammar", "DEBUG")
                                                         natlink_compat.reload_grammars()
                                                         ...plain functions
```

- **`UIProvider`** protocol: `on_state_changed(NatlinkState)`, `on_text(text, level)`, `stop()`
- **`NatlinkState`**: frozen dataclass, serializable via `dataclasses.asdict()`
- **`level`**: standard Python logging values (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR)
- **Single active provider**: `set_ui_provider()` / `clear_ui_provider()` / `get_ui_provider()`
- **UI control**: `import natlink_ui; natlink_ui.show_output()` — direct import, not protocol

Dependency arrow only goes one way: `natlink_ui → natlink_compat → natlink_com`.
`natlink_compat` discovers `natlink_ui` via entry points (`try/except ImportError`).

## Key Invariants

- Natlink connects to Dragon as an out-of-process COM client.
- Dependencies flow strictly downward: `natlink` → `natlink_compat` → `natlink_com`.
  `natlink_com` never imports from `natlink_compat`.
- `natlink_ui` imports from `natlink_compat`, never the reverse (except optional discovery).
- The public import surface is `natlink`, not underscore-prefixed modules.
- Third-party integration happens through explicit seams:
    - **UI providers** (`UIProvider` protocol) — receive state/text pushes, issue commands via direct import
    - **Loaders** (`LoaderProtocol`) — grammar/plugin discovery
    - Exported public functions/classes
- `natConnect()` does COM only — no UI logic. UI setup is the caller's responsibility.
- COM callbacks return quickly; heavy work is deferred onto the message pump.
- COM calls must happen on the STA main thread. Actions triggered from other
  threads (UI worker, timer) use `push_to_com()` to post work to the hidden
  window, which the main thread's pump dispatches.
- Loader discovery and loader activation are separate phases.

## Why The Architecture Looks Like This

The design is driven by three constraints:

- Dragon is a 32-bit application, while modern Python usage is typically 64-bit.
- Existing natlink grammars and ecosystems expect the historic `natlink` API.
- COM callbacks and Win32 message pumping require strict thread ownership and
  careful re-entrancy handling.
- Some hosts want a Python-owned desktop UI, while others want natlink to run
  as a headless engine behind an external shell.

That combination leads to the current split:

- `natlink` preserves the expected public surface
- `natlink_compat` preserves behavior and coordinates layers
- `natlink_com` isolates the COM-specific machinery
- `natlink_ui` owns presentation as the default unified shell — replaceable, optional

## Public Versus Internal

Public and stable:

- names exported from `natlink`
- `UIProvider` protocol and `NatlinkState` dataclass
- `LoaderProtocol` and entry-point-based discovery
- action functions (`restart_dragon`, `reload_grammars`, etc.)
- generated API reference under `third_party/api/`

Internal and subject to change:

- underscore-prefixed modules
- callback dispatch internals
- Win32 tray/output implementation details
- COM marshaling implementation details
