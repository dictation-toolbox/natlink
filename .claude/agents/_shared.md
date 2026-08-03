# Shared rules for all code-owning agents

Not an agent. A reference document. Every code-owning agent (`com-bridge`,
`compat-layer`, `ui`) inherits these.

## Import direction (hard invariant)

```
natlink_com  ←  natlink_compat  ←  natlink_ui
```

- `natlink_com/**` never imports from `natlink_compat` or `natlink_ui`.
- `natlink_compat/**` never imports from `natlink_ui`.
- Tests may import across layers as needed.

Enforced by `import-linter` (see `pyproject.toml [tool.importlinter]`).
Run `lint-imports` locally — it is declared in the `dev` extra but is not
installed by default, and there is no CI, so the contract only runs when
someone runs it.

## STA / threading discipline

- All COM state transitions run on the STA thread established by
  `natlink_compat._launcher.run()` (sets `sys.coinit_flags = 2`, then
  `CoInitializeEx(None, 2)`).
- Worker threads (monitor, RPC delivery) only `SetEvent`. The pump
  consumes on the main thread and dispatches via `_hidden_wnd.dispatch`
  or `signal` / `trigger_message`.
- No cross-thread marshaling. If work seems to require it, redesign.

## Comment policy

- Default: write no comments.
- Keep only non-obvious WHY — hidden constraints, Dragon quirks, retry
  rationale, teardown ordering.
- Delete narrating comments: "we refactored...", "used to be X...",
  "this splits the old path...", "post-refactor...", "referenced by
  the tray code at Y...". The diff already says that; the code already
  does that.
- Keep Joel-Gould attributions when they carry real WHY; drop them when
  they only narrate lineage.

## Test ownership rule

A test belongs to the agent that owns the module the test imports at
its boundary. When a test imports `natlink_compat` as its entry point
but exercises the full stack (end-to-end via `_helpers.do_mimic`), it
belongs to whichever agent owns the public API surface being tested —
almost always `compat-layer`.

When assigning a new test, do not guess from the filename. Read the
imports.

## Git / commit style

- No `Co-Authored-By` lines.
- Commit message summarizes the WHY in 1–2 sentences.
- One logical change per commit where practical.

## Handoff protocol

Subagents do not call each other (the runtime doesn't let them). When
a task crosses your scope, return to the main agent with:

1. What you completed inside scope.
2. What remains, as a `file:line` list.
3. Which agent should handle it.

The main agent re-delegates. Do not silently reach across the boundary.
