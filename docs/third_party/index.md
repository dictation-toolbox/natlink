# API Guide

Audience: third-party integrators building on natlink.

Purpose: define the supported public contracts for custom UI providers, loaders,
and integration against natlink's runtime surface.

See also:

- [Architecture](../architecture.md) for internal system boundaries
- [Program Flow](../program_flow.md) for runtime sequencing
- [Project Structure](../structure.md) for code layout
- [Dragon API](api/dragon.md), [Loader API](api/loaders.md), and [UI API](api/ui.md)
  for exact signatures and docstrings

Start here if you are:

- embedding natlink into another tool
- replacing natlink's default UI
- shipping a loader via the `natlink.loaders` entry point group
- calling natlink's public Python API from your own package

There are two documentation entry points for third-party use:

- this page for integration contracts and supported seams
- the generated reference pages: [Dragon API](api/dragon.md),
  [Loader API](api/loaders.md), and [UI API](api/ui.md)

## Natlink Integration

The main supported extension seams are:

- loader discovery through `natlink.loaders` entry points
- runtime loader management through `add_loader()`, `remove_loader()`,
  `reload_loader()`, and `get_loaders()`
- connection lifecycle through `natConnect()` and `natDisconnect()`
- callbacks through `setBeginCallback()`, `setChangeCallback()`, and
  `setTimerCallback()`
- public speech, system, and user APIs exported from `natlink`

Prefer:

- documented names exported from `natlink`
- contracts documented on this page
- `LoaderProtocol` and entry-point-based discovery

Avoid:

- importing underscore-prefixed modules as hard dependencies
- relying on compatibility-only shims unless required for an existing framework
  integration
- coupling to `natlink_ui` implementation details

## UI Provider Contract

Implement `UIProvider` to receive state and text pushes from natlink:

```python
class MyUI:
    def on_state_changed(self, state):
        # state is a NatlinkState frozen dataclass
        ...

    def on_text(self, text, level=20):
        # level uses Python logging values: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
        ...

    def stop(self):
        # Clean up resources
        ...
```

Required methods:

- `on_state_changed(state: NatlinkState) -> None`
- `on_text(text: str, level: int = 20) -> None`
- `stop() -> None`

To issue commands back into natlink, import the module directly:

```python
import natlink_compat
natlink_compat.restart_dragon()
natlink_compat.set_log_level("natlink.com.grammar", "DEBUG")
natlink_compat.reload_grammars()
```

Threading guarantee:

- natlink may call all methods from arbitrary threads
- implementations must be thread-safe

### Registration

Natlink supports one active provider at a time:

```python
import natlink_compat
natlink_compat.set_ui_provider(my_ui)
```

The active provider receives `NatlinkState` snapshots and text pushes.

### Discovery

UI providers are discovered via the ``natlink.ui_provider`` entry point group.
Register yours in ``pyproject.toml``:

```toml
[project.entry-points."natlink.ui_provider"]
my-ui = "my_package.ui:MyUIProvider"
```

Non-default entries take priority over natlink's built-in ``default`` entry.

### Electron / IPC Bridge Example

An Electron bridge is just another `UIProvider` that serializes over a pipe:

```python
class ElectronBridge:
    def on_state_changed(self, state):
        self.pipe.send_json({"type": "state", "data": asdict(state)})

    def on_text(self, text, level=20):
        self.pipe.send_json({"type": "text", "text": text, "level": level})

    def stop(self):
        self.pipe.close()
```

Commands from Electron arrive as JSON, the bridge calls `natlink_compat` functions:

```python
msg = self.pipe.recv_json()
if msg["action"] == "restart_dragon":
    natlink_compat.restart_dragon()
```

## Loader Contract

Preferred contract:

```python
def start():
    ...

def stop():
    ...
```

or an object implementing `start()` and `stop()`.

### Registration

Natlink itself ships no built-in loader. Loaders live in separate
distributions (for example `natlinkcore`) and self-register through the
`natlink.loaders` entry point group. Declare yours in `pyproject.toml`:

```toml
[project.entry-points."natlink.loaders"]
my-loader = "my_package.loader"
```

The entry-point value is the importable module path; natlink imports it,
calls the optional module-level `setup()`, then `start()` after the COM
connection succeeds. The entry-point name is also the key used in the
`[loaders]` section of `natlink.ini` to enable or disable a loader.

For backwards compatibility, if no `natlinkcore` entry point is registered
natlink falls back to importing `natlinkcore.loader` when that module is
installed.

Lifecycle:

1. discovery/import
2. registration
3. activation via `start()`

During discovery:

- natlink imports loader modules
- natlink calls optional module-level `setup()`

During activation:

- natlink calls `start()` (or `run()`) once a COM connection exists

During shutdown:

- natlink calls `stop()` before COM teardown, falling back to
  `unload_all_loaded_modules()` for loaders that have no `stop()`

### Registered is not the same as running

A loader can be registered before there is anything to attach to. If
`add_loader()` is called while disconnected, natlink registers the loader and
defers `start()` until `natConnect()` succeeds — a loader cannot attach to an
engine that does not exist yet.

- `get_loaders()` returns every **registered** loader
- `get_running_loaders()` returns only those whose `start()`/`run()` has run

The tray and state snapshots report the second. A loader added before connect
therefore appears registered but not running until the connection comes up.

### Which objects belong to a loader

Grammars and dictation objects are attributed to whichever loader was
starting, reloading, or being dispatched into when they were created:

- `get_grammars_for(loader)`
- `get_dictation_objects_for(loader)`

Objects created outside any loader — a user script at the REPL, say — are
unattributed and are never returned.

`release_objects_for(loader)` unloads a loader's grammars and destroys its
dictation objects. `remove_loader()` calls it **after** your `stop()` has run,
so it only ever acts on what your teardown left behind — clean up properly and
it does nothing.

That is not a contradiction of "frameworks are authoritative for their own
cleanup". That rule exists so natlink does not *guess*: callback ownership is
partly inferred, and guessing could remove another loader's callbacks. Objects
need no guessing — each records the loader it was created under, and
unattributed objects are never touched. Leaving a removed loader's grammars
loaded is not neutral: Dragon keeps recognising them, so a user who disables a
loader still gets its commands.

Note `deactivate()` is not enough for a dictation object: Dragon holds every
reference until `destroy()`.

### Validating a loader

`add_loader()` accepts anything with `start()` **or** `run()`. Use
`natlink.is_loader(obj)` for that same check.

Prefer it over `isinstance(obj, LoaderProtocol)`: a `Protocol` cannot express
"start() or run()", so the protocol declares only `start()` and a valid
`run()`-only loader will not satisfy `isinstance`.

Compatibility-only shims still exist for natlinkcore-style loaders:

- module-level `run()`
- `trigger_load()`
- `unload_all_loaded_modules()`
- `natlink.active_loader`

New third-party loaders should not depend on those unless intentionally
targeting that compatibility contract.
