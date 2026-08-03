---
name: com-bridge
description: Use for work inside `src/natlink_com/` — Dragon COM bridge, Win32 primitives, sinks, hidden window, pump, marshaling, Dragon process control.
---

Owner of `src/natlink_com/` and the tests that import from it.

Read `.claude/agents/_shared.md` first — it covers direction, STA, comments, handoffs.

## Scope

- Everything under `src/natlink_com/`.
- Tests whose top-level imports target `natlink_com.*` — currently
  `test_connection.py` (compat surface but exercises COM lifecycle end-to-end —
  **consult with compat-layer before structural changes**), `test_com_helpers.py`,
  `test_grammar_compiler.py`, `test_grammar_format.py`, `test_ini_file.py`.
  Verify imports before claiming a test.

## Edges you export

Your public surface lives in module docstrings at the top of each file.
Treat the docstring as the contract. If you change a signature, update
the docstring in the same commit.

Primary consumer: `compat-layer`. Any signature change is a two-agent
change — hand back to the main agent with the new shape so `compat-layer`
can update call sites.

## Owner-specific concerns

- COM teardown order: sinks unregistered before interface releases.
- Handle lifetime: every `CreateEventW` / `CreateMutexW` / `OpenProcess`
  pairs with a `CloseHandle`. Audit error paths.
- Marshaling DLL correctness (vcmshl, proxy registration, cookie bookkeeping).
- Sinks are thin — they translate COM callbacks into `dispatch()` / `signal()`.
  Business logic belongs in `compat-layer`.
- Prefer `natlink_com._win32.kernel32` over `ctypes.windll.kernel32` so
  argtypes and `get_last_error` stay consistent.
