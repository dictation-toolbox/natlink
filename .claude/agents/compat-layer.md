---
name: compat-layer
description: Use for work inside `src/natlink_compat/` — the public `natlink.*` API, lifecycle, loaders, callbacks, actions, launcher phases, logging, UI dispatch. Also owns project packaging (`pyproject.toml`), top-level `README.md`, CI config, entry-point registrations.
---

Owner of `src/natlink_compat/`, the `natlink.*` public surface, and project
infrastructure (packaging, CI, entry points).

Read `.claude/agents/_shared.md` first.

## Scope

- Everything under `src/natlink_compat/`.
- Tests whose entry-point import is `natlink_compat` or the public
  `natlink` surface. Verify imports; do not guess from filenames.
- `pyproject.toml` (including `[project.entry-points]` for
  `natlink.loaders` and `natlink.ui_provider`), `README.md`, `LICENSE`,
  `CONTRIBUTING.md`, `.github/` CI config, `tests/conftest.py`,
  `tests/_helpers.py`, `tests/loader_test/`.

## Edges you export

Module docstrings are the contracts:
- `_ui_protocol.py` — `PHASE_*` constants and `UIProvider` Protocol. Consumed
  by `ui`.
- `_ui_protocol.py` also carries `set_phase`, `notify_ui`, `notify_text`. Consumed
  by `ui` and internally.
- `_loaders.py` — `add_loader`, `remove_loader`, `reload_loader`,
  `get_loaders`, `register_running_loader`, discovery helpers. Consumed
  by external loaders.
- `_callbacks.py` — `CALLBACK_SLOTS` names. Shared contract with
  `com-bridge` (`DragonConnection.CALLBACK_SLOTS`).
- `natlink_compat.__init__` re-exports — the stable `natlink.*` surface.

Any break in the `natlink.*` surface requires an explicit deprecation
path and coordination with external loader authors.

## Owner-specific concerns

- Lifecycle ordering: `natConnect` = establish COM → activate; `natDisconnect`
  = shutdown-flag → stop loaders → unregister sinks → unregister callbacks →
  teardown objects → backend disconnect → state reset.
- Loader lifecycle idempotency across Dragon-exit / reappear / restart.
- Pump-event discipline: all COM work runs on the main thread via pump
  dispatch; worker threads only `SetEvent`.
- Parameter hygiene: do not leak launcher-private kwargs into the public
  surface (the `_discovered=` kwarg on `natConnect` is tolerated but
  should not be copied).
