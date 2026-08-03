# Natlink subagents

Four code-owning agents plus one read-only scribe. Main agent routes to
specialists; specialists return to main with handoff notes.

## Agents

| Agent                  | Owns                                                      |
| ---------------------- | --------------------------------------------------------- |
| `com-bridge`           | `src/natlink_com/` + tests importing `natlink_com`        |
| `compat-layer`         | `src/natlink_compat/` + tests, packaging, CI, top-level README, shared test infra (`conftest.py`, `_helpers.py`, `loader_test/`) |
| `ui`                   | `src/natlink_ui/` + tests importing `natlink_ui`          |
| `architecture-scribe`  | `docs/`, `CLAUDE.md`, diagrams, memory (read-only on code) |

## Shared rules

`.claude/agents/_shared.md` — import direction, STA discipline, comment
policy, test ownership rule, handoff protocol. All code-owning agents
inherit it.

## Interface contracts

Cross-boundary contracts live in **module docstrings at the top of the
exporting file**. Treat the docstring as the contract; changing a
signature means updating the docstring in the same commit.

Key contract files (each owned by the listed agent):

- `src/natlink_com/_connection.py` — `DragonConnection` (`com-bridge`)
- `src/natlink_com/_hidden_wnd.py` — dispatch/signal (`com-bridge`)
- `src/natlink_com/_pump.py` — pump/trigger (`com-bridge`)
- `src/natlink_com/_dragon.py` — process control (`com-bridge`)
- `src/natlink_com/_launcher.py` — single-instance, Dragon waits, event names (`com-bridge`)
- `src/natlink_compat/_ui_protocol.py` — phase constants, the `UIProvider`
  Protocol, `build_state_snapshot`, `notify_ui` (`compat-layer`)
- `src/natlink_compat/_loader_protocol.py` — `LoaderProtocol`, `is_loader`
  (`compat-layer`)
- `src/natlink_compat/_loaders.py` — loader management API (`compat-layer`)
- `src/natlink_compat/_callbacks.py` — `CALLBACK_SLOTS` (`compat-layer`, shared with `com-bridge`)
- `src/natlink_compat/__init__.py` — public `natlink.*` surface (`compat-layer`)

## Enforcement

- Import direction is checked by `import-linter`
  (`pyproject.toml [tool.importlinter]`). There is no CI, and the tool is
  not installed by default, so run `lint-imports` by hand.
- Ownership rules are social; the main agent enforces them at routing
  time.
