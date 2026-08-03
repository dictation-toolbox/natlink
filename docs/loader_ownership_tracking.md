# Loader Ownership Tracking

## Status

Current contract plus design notes. Today, loaders are treated as authoritative
owners of their framework resources. This document also outlines what would need
to be tracked if natlink itself ever grows deterministic per-loader ownership.

## Why This Exists

The current code correctly treats the Dragon COM connection as shared process
state, but loader ownership is still too loose. A loader is not just a module
with `start()` and `stop()`. In practice, a loader may create or register:

- grammars
- dictation objects
- begin/change/timer callbacks
- timer subscriptions
- deferred work queued against grammar or dict handles
- results objects created by its recognitions
- logging integrations

Today these resources are expected to be tracked by the framework loader that
created them. Without explicit natlink-side ownership, natlink cannot safely
infer all resources belonging to one loader without risking sibling loaders.

## Reference Model

From the original C++ code in `Reference/natlink-master/NatlinkSource`:

- `CDragonCode` owns the connection and the global runtime.
- grammar objects are tracked in a linked list
- dictation objects are tracked in a linked list
- result objects are tracked in a linked list
- begin/change/timer callbacks are global connection state
- timer state is global connection state
- hidden-window dispatch and pause/deferred-cookie state are connection state

Relevant references:

- `DragonCode.h`
- `DragonCode.cpp`
- `GrammarObject.h` / `GrammarObject.cpp`
- `DictationObject.h` / `DictationObject.cpp`
- `ResultObject.h` / `ResultObject.cpp`

The Python port mirrors this split:

- connection-owned state in `src/natlink_compat/_state.py`
- loader runtime in `src/natlink_compat/_loaders.py`
- callback routing in `src/natlink_compat/_callbacks.py`
- grammar ownership in `src/natlink_compat/_gram_obj.py`
- dictation ownership in `src/natlink_compat/_dict_obj.py`
- deferred handle-routed work in `src/natlink_com/_connection.py`
- hidden-window queueing in `src/natlink_com/_hidden_wnd.py`

## Current Loader Cleanup Contract

Loader cleanup is framework-owned.

If a loader defines `stop()`, natlink treats that hook as authoritative. The
loader is responsible for unloading the resources it created:

- grammar objects and framework grammar wrappers
- dictation objects
- global begin/change/timer callbacks it registered
- grammar/dict callbacks it attached
- framework timer managers and logical timer subscriptions
- imported grammar modules and references/cycles that keep objects alive

After `stop()` returns, natlink unregisters the loader from the loader registry.
It does not globally unload grammars or dictation objects and it does not run
package-based callback cleanup for that loader. This keeps one framework's
reload/unload from disturbing sibling frameworks.

Loaders that expose `unload_all_loaded_modules()` instead of `stop()` are still
responsible for their own cleanup. Natlink does not perform package-based
callback cleanup on per-loader stop/reload paths, because callback ownership
cannot be inferred safely from Python function/module/object metadata.

### File/module loaders

File loaders, such as a framework that scans grammar directories and imports
grammar modules, are framework-internal unless they are explicitly registered
with natlink as loader objects.

Natlink sees the framework entry point, not each grammar file. That means:

- the framework owns the mapping from file/module to grammar objects
- the framework owns module reload and unload ordering
- the framework owns callbacks and timers installed by those modules
- natlink does not infer ownership from `__module__`, package names, function
  names, closures, or import paths during per-loader stop/reload

If a framework wants per-file reload, it must unload that file's grammar
objects, unregister its callbacks/timers, clear its module references, and then
reimport/restart that file itself. Natlink's role is only to provide the raw
C++-compatible objects and connection-global primitives those frameworks use.

## Current Reload Behavior

`reload_loader(loader)` has two paths:

- If the loader has `trigger_load(force_load=True)`, natlink calls it in-place.
  The framework owns whatever unload/reload semantics that implies.
- Otherwise natlink calls `stop_loader(loader)`, unregisters that loader,
  reloads/imports the loader module when possible, and starts it again.

In neither per-loader path does natlink call `natDisconnect()`, clear the
grammar registry, destroy all dictation objects, reset global callbacks, or
stop sibling loaders.

`natDisconnect()` is different: it is connection-wide teardown. It stops all
loaders and then globally releases remaining grammars, result objects, and
dictation objects because the Dragon connection is being torn down.

## Scope Rules

These boundaries should be treated as hard rules.

### Process scope

Owned by launcher/session logic, not by loaders:

- Dragon monitor
- restart/reconnect policy
- launcher event handles
- UI provider process lifetime

### Connection scope

Owned by the active COM connection, shared by all loaders:

- backend COM interfaces
- sink registration / unregistration
- hidden window and message routing
- pause-recognition / deferred-cookie state
- global callback depth and deferred change replay
- global timer primitive

### Loader scope

Owned today by one framework loader runtime. If natlink later adds explicit
ownership tracking, these resources must be attributable to that loader:

- grammars it loaded
- dictation objects it created
- callbacks it registered directly or through helper objects
- timer registrations/subscriptions it owns
- deferred work posted on behalf of its grammar/dict handles
- logging hooks or handler adoption attached to the loader

### Derived / indirect scope

Not structurally owned by a loader, but may need attribution:

- result objects created from recognitions of that loader's grammars

## Critical Resource Inventory

This is the minimum set of loader-owned resources we need to be able to
identify and unwind.

### 1. Grammar handles

Track every grammar handle created by the loader.

Why:

- grammar callbacks route by handle
- grammars can unload while deferred work is still queued
- reconnect/unload must know exactly which grammar objects belong to which loader

Current Python surfaces:

- `_state.grammar_registry`
- `GramObj`
- handle-routed grammar callbacks in `natlink_com._connection`

### 2. Dictation handles

Track every dictation handle created by the loader.

Why:

- dictation objects have their own begin/change callback surfaces
- dictation objects maintain extra state like lock count and text buffer access
- deferred text-change work routes by dict handle

Current Python surfaces:

- `_state.dict_registry`
- `DictObj`
- handle-routed dict callbacks in `natlink_com._connection`

### 3. Callback registrations

Track all callback refs attributable to the loader, including helper objects.

This includes:

- natlink global begin callbacks
- natlink global change callbacks
- natlink timer callbacks
- grammar begin/results/hypothesis callbacks
- dictation begin/change callbacks

Why:

- stopping a loader must remove its callback participation without disturbing siblings
- reconnect should restore only the correct callback set
- package-wide callback removal is necessary but should become explicit data, not inference

Current Python surfaces:

- `_state.begin_callbacks`
- `_state.change_callbacks`
- `_state.timer_callbacks`
- `_callbacks._remove_callbacks_for`

Current contract:

- Explicit `stop()` loaders must remove their own callbacks precisely.
- Loaders that use `unload_all_loaded_modules()` must also remove their own
  callbacks precisely.
- Natlink does not run `_remove_callbacks_for(loader)` during per-loader
  stop/reload paths.
- Lambdas, closures, `functools.partial`, shared helper functions, and bound
  methods on utility objects are only reliably removable by the framework that
  retained the exact callback reference.

### 4. Timer ownership

Track which loader owns which timer registrations.

Why:

- there is one underlying connection-level Win32 timer primitive
- loaders may multiplex logical timers on top of that shared primitive
- unload must remove only the loader-owned timer callbacks/subscriptions

Current Python surfaces:

- `setTimerCallback`
- `_state.timer_callbacks`
- `natlink_com._pump.set_timer`

Current contract:

- Explicit `stop()` loaders must stop their own timer managers and unregister
  timer callbacks they registered.
- Natlink does not currently maintain a per-loader timer ownership map.
- Full `natDisconnect()` may disable the underlying connection timer because
  the whole connection is being torn down.

### 5. Deferred queued work

Track queued work associated with a loader's grammar or dict handles.

This is critical.

Examples:

- pending phrase-finish delivery
- pending phrase-hypothesis delivery
- pending dict text-change delivery

Why:

- a loader can unload after work is posted but before it drains
- reconnect/disconnect can begin while queued closures still exist
- ownership must include "in-flight" work, not just currently alive objects

Current Python surfaces:

- `natlink_com._connection.defer_send_results`
- `natlink_com._connection.defer_phrase_hypo`
- `natlink_com._connection.defer_dict_text_changed`
- `natlink_com._hidden_wnd` dispatch queues

### 6. Result lifetimes

Track whether result objects created from a loader's grammars need attribution.

Why:

- results objects hold COM state alive
- they are globally tracked today, but a loader unload/reconnect may want to
  reason about loader-originated results explicitly

Current Python surfaces:

- `natlink_com._res_obj._live_res_objs`

This may remain connection-scoped, but it must be an explicit decision.

### 7. Logging integrations

Track loader logging adoption or handler changes.

Why:

- the current port may attach notify handlers to loader loggers
- unload should be able to reverse loader-specific logging state cleanly

Current Python surfaces:

- `_loaders._adopt_loader_logger`
- `_logging_setup`

## Loader Runtime Record

Any serious ownership model should converge on a per-loader runtime record.

At minimum, each record should hold:

- loader object/module
- module path / package base
- discovery origin
  - discovered at startup
  - added at runtime
- lifecycle state
  - discovered
  - started
  - stopping
  - stopped
  - failed
- grammar handles
- dict handles
- callback refs
- timer refs
- pending dispatch refs or counts
- logging hooks

Optional but likely useful:

- result refs
- diagnostics like start time, stop reason, last error

## Rules We Need To Decide Explicitly

These rules are currently underdefined and should be resolved before further
implementation work.

### Runtime-added loaders across reconnect

Choose one:

- runtime-added loaders are ephemeral and die on disconnect
- runtime-added loaders are launcher-session persistent and must restart on reconnect

Current behavior is not explicit enough.

### Add-before-connect behavior

If a loader is added while disconnected, define whether it is:

- pending for next connection activation
- merely registered metadata until explicitly started

Current behavior is not explicit enough.

### Results attribution

Decide whether result objects remain purely connection-owned or whether loader
origin must be tracked for deterministic unload diagnostics.

### Timer semantics

If natlink later owns timers explicitly, decide whether loaders own:

- concrete timer callbacks only
- logical timer subscriptions
- both

### Deferred work semantics

If natlink later owns deferred work explicitly, define whether loader stop:

- drains existing queued work
- rejects and drops queued work
- unwinds queued work with explicit cancellation bookkeeping

The answer may differ by channel.

## Non-Negotiable Safety Rules

These should hold regardless of implementation shape.

1. A loader `stop()` must reject new loader-owned registrations before teardown.
2. A loader `stop()` must remove loader-owned callbacks before releasing owned objects.
3. A loader unload must account for already-queued work, not just live objects.
4. Reconnect must not rerun non-idempotent loader setup hooks unintentionally.
5. Loader stop/reload must not disturb sibling loaders sharing the same connection.
6. Connection teardown still owns the final global ordering from the original
   `natDisconnect` design.

## Recommended Next Step

Before implementing more loader behavior, write a small ownership spec that
answers:

- what a loader is allowed to own
- what remains connection-owned forever
- what survives reconnect
- what survives disconnect
- how queued work is attributed and unwound

Only after that should code be changed.
