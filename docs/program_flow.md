# Program Flow

Audience: natlink developers and maintainers.

Purpose: describe the operational sequence of launcher startup, COM connection,
callback dispatch, restart, and shutdown.

This document describes how natlink connects to Dragon, processes speech recognition events, restarts Dragon, and shuts down.

## Launcher Startup

Entry point: `natlink_compat._cli:main` → `natlink_compat._launcher.run()`.
`run()` is a straight-line procedure (`src/natlink_compat/_launcher.py`):

1. **Init** — acquire single-instance mutex (`NatlinkLauncherMutex`),
   set STA (`sys.coinit_flags = 2`), insert `src` on `sys.path`,
   `CoInitializeEx(STA)`, init file logging, load `natlink.ini`.
2. **Discovery** — `discover_loaders()` (imports loader modules via
   `natlink.loaders` entry points and runs their optional `setup()`
   hooks). If no UI provider was installed by a loader, resolve one via
   `natlink.ui_provider` entry points (non-`default` preferred), falling
   back to a direct `natlink_ui.UIProvider` import.
3. **Launcher** — construct `Launcher` holding the four Win32 event
   handles (`shutdown`, `restart`, `dragon_exited`, `dragon_reappeared`)
   plus the discovered loader list.
4. **`_wait_and_connect(launcher, cfg, natlink)`** — set phase
   `waiting_for_dragon`; auto-launch Dragon if `[settings]
   auto_launch_dragon = true`; wait for Dragon's `DgnBarMainWindowCls`
   window via `SetWinEventHook(EVENT_OBJECT_CREATE)` (falling back to
   polling); probe COM readiness; wait for profile load (skipped when
   Dragon was already running); `natConnect(discovered_loaders=...)`;
   start the Dragon process monitor.
5. **`_pump_loop(launcher, natlink)`** — `pump(h_events=[shutdown,
   restart, dragon_exited, dragon_reappeared], timeout_ms=2000)` on a
   loop. An `if/elif` on the returned index dispatches to
   `_do_restart_on_main`, `_handle_dragon_exited`, or
   `_handle_dragon_reappeared`. Shutdown returns the pump.
6. **`_teardown(launcher, natlink)`** — stop the monitor, call
   `natDisconnect()` if still connected, stop the UI provider,
   close all event handles.

Restart and reconnect reuse `_probe_and_wait` and `_connect`. The
launcher (not `natConnect`) owns the Dragon process monitor because
only the pump loop consumes the events it signals.

## Connection Flow

`natConnect(bUseThreads=False, *, discovered_loaders=None)` runs in two
internal phases:

- If `discovered_loaders` is not provided, `discover_loaders()` is called
  (the launcher always threads its cached list through so loader `setup()`
  hooks run exactly once per process).
- `_establish_com_connection()` then `_activate(discovered)`.

See [Natlink](third_party/index.md) for the public loader contract.

### Phase A: COM Connection — `_establish_com_connection()`

1. **Acquire connection mutex** (`NatlinkConnectionActive`) — warns if another natlink process is already connected.
2. **Initialize deferred callback infrastructure** — creates the hidden message window used for cross-thread callback dispatch.
3. **Create backend** — instantiates `NatlinkCOM` (or uses an injected backend).
4. **`NatlinkCOM.connect()`** delegates to `DragonConnection.connect()`:
   - Detects Dragon version from registry (HKLM, WOW64 32-bit view)
   - Loads the version-specific type library (`dragon_interfaces.tlb`) via `comtypes.client.GetModule`
   - Registers the 64-bit marshal DLL (`marshal64_v13_v14.dll` or `marshal64_v15_v16.dll`) per-process via `LoadLibrary` + `DllGetClassObject` + `CoRegisterClassObject`, then `CoRegisterPSClsid` for each interface
   - Calls `CoCreateInstance(CLSID_DgnSite, CLSCTX_LOCAL_SERVER)` to get an `IUnknown` pointer to Dragon's site object
   - `QueryInterface` for `IServiceProvider`
   - `IServiceProvider::QueryService(DgnDictate, ISRCentralW)` to get the central speech recognition interface
   - `QueryService(SpchServices, IUnknown)` for the speech services object (output events, script interpreter)
   - **Core QI** on ISRCentralW: `IDgnSREngineControlW`, `ISRSpeakerW`, `IDgnSRLexiconW`, `IDgnLexWordW`, `IDgnSRAudioFileSourceW`; on SpchServices: `IDgnSSvcOutputEventW`, `IDgnSSvcInterpreterW`
   - Creates hidden COM message window (sinks post to it immediately on registration)
   - Registers engine notification sink (`IDgnSREngineNotifySinkW`) and action notification sink; wires `WM_ATTRIBCHANGED`, `WM_PAUSED`, `WM_MIMICDONE`, `WM_SENDRESULTS` message handlers
   - **Late QI**: `IDgnSRTrainingA` (after sinks, matching C++ order)
   - Gets Dragon version via `IDgnSREngineControlW::GetVersion()`
5. **Register callbacks** — connects the backend's sink events to natlink's callback dispatch system.

### Phase B: Activation — `_activate(discovered)`

1. **Display startup banner** in the output surface (Python version, loader
   versions, or warnings if all loaders are disabled / none discovered).
2. **Set up logging and redirect** — message-window handler, redirect
   stdout/stderr through `notify_text()`.
3. **Cache mic + user state** for UI snapshots (avoids COM calls in
   callbacks).
4. **Set phase `connected`** — the active provider receives a connected
   state snapshot.
5. **Start loaders** — calls `start_loader()` on each discovered loader
   and fires `_on_loaders_changed()` once.

The Dragon process monitor is started by the launcher's
`_start_monitor_if_needed(session)`, not by `_activate`. An `atexit`
handler registered at `_lifecycle` import time ensures emergency disconnect
if the process exits while still connected.

## UI State Transitions

The launcher tracks its current phase via `set_phase()`. Providers decide how to render each phase; the default `natlink_ui` tray maps phases to icon color and tooltip text.

```
                          +-----------+
                          |   idle    |  (initial state)
                          +-----+-----+
                                |
                                v
                   +-------------------+
                   | waiting_for_dragon |  (tray: red/disconnected)
                   +--------+----------+
                            |
                            v
                      +------------+
                      | connecting |  (tray: yellow/connecting)
                      +-----+------+
                            |
                            v
                   +-----------------+
                   | loading_profile |  (tray: yellow/connecting)
                   +--------+--------+
                            |
                            v
                      +-----------+
              +------>| connected |  (tray: green/connected)
              |       +-----+-----+
              |             |
              |             | (Dragon exits or restart requested)
              |             v
              |      +------------+
              |      | restarting |  (tray: yellow/restarting)
              |      +-----+------+
              |            |
              |            v
              |  +-------------------+
              |  | waiting_for_dragon |
              |  +--------+----------+
              |           |
              |           v
              |     +------------+
              |     | connecting |
              |     +-----+------+
              |           |
              |           v
              |  +-----------------+
              |  | loading_profile |
              |  +--------+--------+
              |           |
              +----------+
              (reconnect succeeds)

              Any state ----> error  (tray: red/error with message)
```

## Dragon Restart

Natlink can restart Dragon without restarting itself (e.g., from the tray menu's "Restart Dragon" option).

### Signal Path

1. **`signal_restart()`** — called from a UI action or another controller
   thread. Opens the `NatlinkRestartDragon` named event and sets it.
2. **Pump wakes** — `pump(h_events=[...])` returns the restart handle's
   index; the `if rc == _RESTART` branch in `_pump_loop` calls
   `_do_restart_on_main`.
3. **`_do_restart_on_main(launcher, natlink)`** runs on the main thread
   (COM-safe, since the main thread owns COM objects). Guarded by
   `_restart_lock`; a duplicate restart is logged and ignored.

### Restart Sequence

The restart runs entirely on the main thread. `_dragon.stop` / `_dragon.start`
do not accept a shutdown handle, so `_aborting(session)` is polled
between every stage — if shutdown was signaled, the restart bails out
early and `_teardown` observes the same event on the next pump
iteration.

1. **Set phase `restarting`** — the active provider receives the restart phase.
2. **Stop Dragon monitor** — prevents the monitor from interfering during restart.
3. **Save current profile** via `_dragon.save_profile(conn)` while COM is still live.
4. **Disconnect COM** — `natDisconnect()` to cleanly release all COM resources.
5. **`gc.collect()`** — releases lingering COM reference cycles before Dragon exits.
6. **Close Dragon** — `_dragon.stop(force=False)` sends `WM_CLOSE`, waits, falls back to force-kill.
7. **Launch Dragon** — `_dragon.start(wait=30)`.
8. **`_probe_and_wait(wait_for_window=True, wait_for_profile=True)`** —
   phases `waiting_for_dragon` → `connecting` → `loading_profile`.
9. **Reconnect** — `_connect(natlink, launcher.discovered)` threads the
   cached loader list so `setup()` hooks do not re-run.
   `_start_monitor_if_needed(session)` restarts the monitor. On success
   notifies `[Dragon restarted successfully.]`.
10. **On failure** — sets phase `error` with the exception message.

## Speech Recognition Flow

### Utterance Begin

When Dragon starts processing an utterance:

1. Dragon calls the engine sink's `Paused(qCookie)` method.
2. The engine sink calls `_hidden_wnd.dispatch(self._do_paused, qCookie,
   channel=WM_PAUSED)` — a closure on the per-channel deque; the pump's
   `wndproc` drains it on the next `DispatchMessage`.
3. `_do_paused(qCookie)` runs on the STA main thread. If
   `_pause_recog > 0` (results still pending), the cookie is appended
   to `_deferred_cookies` and returns; otherwise `_do_paused_processing`
   fires the begin callback (`on_paused_dispatch`) then
   `ISRCentralW::Resume(qCookie)`, incrementing `_resume_count`.

### Phrase Finish

When Dragon completes recognition of a phrase:

1. The grammar sink's `PhraseFinish` method receives the `SRPHRASEW`
   result on an RPC thread, parses it, wraps a `ComResObj`, AddRefs the
   underlying `IUnknown`, increments `pause_recog`, and calls
   `conn.defer_send_results(gram_handle, dwFlags, res_obj)` —
   handle-keyed routing owned by the connection so closures capture the
   connection (long-lived) rather than the grammar sink (unloadable).
   `defer_send_results` dispatches on `WM_SENDRESULTS`.
2. `wndproc` drains the closure on the STA main thread, which looks up
   the grammar in `_grammar_sinks[handle]` and calls
   `_do_phrase_finish(...)`. If the grammar has been unloaded during
   the race, `reset_pause_recog()` unwinds the guard and returns.
3. The user's `gotResultsObject` / `gotResults` / `gotResultsInit` runs;
   `pause_recog--`; deferred `Paused` cookies (if any) are processed
   and `Resume` is called on the main thread.

### Hypothesis

For grammar sinks registered with hypothesis notifications, Dragon calls `PhraseHypothesis` with partial results during recognition. This fires the user's `gotHypothesis` callback if registered.

## Sync Operations

All four sync operations (`recognitionMimic`, `playString`, `playEvents`,
`execScript`) use the same completion architecture, matching the original C++
`CDragonCode::messageLoop` pattern. Completion channels are posted via
`_hidden_wnd.signal(msg, wparam, lparam, data=...)` rather than a closure
queue — the real Win32 `wparam`/`lparam` values travel in the `MSG` struct
so `pump.message_loop` can match waiters by client code. Each sink
advertises its completion channels via a `completion_channels()` function;
`DragonConnection._register_completion_handlers()` wires these to the
pump's `trigger_message` on connect.

1. **Unique client code**: each call generates a unique client code. Dragon
   echoes it back in the completion callback.
2. **signal()**: completion callbacks call `_hidden_wnd.signal(WM_*, code,
   status)`; optional payloads (e.g. `ExecutionAborted` error string)
   travel via the `data=` sidecar, retrieved with `take_signal_data`.
3. **message_loop**: `push_message_entry` registers the expected
   `(message, wParam)` pair. `message_loop` pumps messages and calls
   `trigger_message` both from the `wndproc` (for dispatches reaching
   the handler) and from the `PeekMessage` pre-dispatch loop (for the
   COM modal-loop pre-consumed case).
4. **Start callback**: the `start` callback drains pending messages before
   issuing the COM call, so stale paused/resume traffic from a previous cycle
   is handled first.

Several operations block the calling thread until Dragon signals completion:

### execScript

1. `exec_script()` validates the script via `IDgnSSvcInterpreterW::CheckScript`, then calls `ExecuteScript` (or `ExecuteScriptWithListResults` if args are provided).
2. The action sink's `ExecutionDone` posts `WM_EXECUTION` to the hidden window.
3. `_sync_op` pumps messages via `MsgWaitForMultipleObjects` + `PeekMessage` until triggered or timeout.

### recognitionMimic

1. `recognition_mimic()` pushes a `_MessageEntry(WM_MIMICDONE, clientCode)` onto the message stack.
2. `message_loop` drains pending messages (dispatching any leftover `WM_PAUSED → Resume` from a previous cycle), then calls `RecognitionMimic` via the `start` callback.
3. The engine sink's `MimicDone` posts `WM_MIMICDONE` to the hidden window with `wParam=clientCode`, `lParam=0` (success) or non-zero (failure).
4. `message_loop` pumps messages via `MsgWaitForMultipleObjects` + `PeekMessage` until the entry is triggered (matching on `WM_MIMICDONE` + `clientCode`).
5. If the first attempt fails and `_resume_count` increased (proving Dragon was paused from the audio-restart race), a retry is issued with a new client code. Genuine grammar mismatches propagate immediately.

See [Consecutive recognitionMimic](technical-limitations.md#consecutive-recognitionmimic-with-active-microphone) for the race condition details.

### playString / playEvents

1. `NatlinkCOM.play_string()` or `play_events()` calls `IDgnSSvcOutputEventW::PlayString` or `PlayEvents`.
2. DNS 16+ passes `dwNotify=1` as the final argument to request notification.
3. The action sink's `PlaybackDone` method is called by Dragon.
4. The calling thread waits on `_playback_done` event.
5. On legacy DLLs (DNS < 15), playback is fire-and-forget (no dwNotify support).

### inputFromFile

1. `_testFileName` validates the file exists and has a legal extension (`.utd`, `.utt`, `.utb`, `.wav`, `.nwv`). A re-entrancy guard prevents nested `inputFromFile` calls (Dragon supports only one active audio source).
2. `NatlinkCOM.input_from_file()` calls `IDgnSRAudioFileSourceW::LoadFile` then starts playback.
3. The engine sink's `AttribChanged2(dwCode)` fires both
   `signal(WM_ATTRIBCHANGED, dwCode)` — used by `pump.message_loop` for
   sync-op completion — and `dispatch(self._dispatch_attrib_changed,
   dwCode, channel=WM_ATTRIBCHANGED_WORK)` for the Python-side
   `on_attrib_changed` callback.
4. `pump()` waits on the event handle via `MsgWaitForMultipleObjects` until signaled or timeout (5 min).

## Shutdown

### Clean Exit via Shutdown Event

The launcher shuts down cleanly without `os._exit()`. The sequence:

1. **Signal** — an external process or UI action calls `request_shutdown()`,
   which opens and sets the `NatlinkShutdown` named event.
2. **Pump returns** — `pump()` returns index `0` (shutdown), and the
   `if rc == _SHUTDOWN: return` branch exits `_pump_loop`.
3. **`_teardown(launcher, natlink)`** runs:
   - `launcher.stop_monitor()`
   - `natDisconnect()` if still connected
   - `stop_provider(provider)` on the active UI provider (if any)
   - `launcher.close_handles()` releases all four event handles.
4. **Process exits normally** — `run()` returns, atexit runs
   `_atexit_disconnect` as a safety net, the process exits.

### natDisconnect Teardown

When `natDisconnect()` is called (either during shutdown or explicitly
by user code):

1. **`conn.begin_shutdown()`** — flips `_shutting_down=True` so the
   connection's `defer_*` routers and hidden-window `dispatch()` reject
   new work at the source. Ensures sink callbacks fired during teardown
   unwind cleanly instead of racing the queue clear in `_hidden_wnd.destroy()`.
2. **Set phase `idle`** — the UI provider updates immediately (COM
   teardown may block if Dragon is gone).
3. **Disable COM timer** if any timer callback is registered.
4. **Stop all active loaders** — calls `stop()` on each.
5. **Set disconnect event** — `_state._disconnect_event_handle` (Win32
   manual-reset event) is set, unblocking `waitForSpeech`.
6. **Unregister sinks** — `backend.unregister_sinks()` stops Dragon from
   sending callbacks. Must happen before releasing COM interfaces to
   prevent deadlocks from in-flight RPC callbacks.
7. **Clear callback slots** — `_callbacks.unregister_all()` (runs
   *after* `unregister_sinks` so in-flight callbacks still have the
   slots they need to call `Resume`).
8. **Teardown logging** — removes log handlers, restores stdout/stderr.
9. **Tear down objects** — unloads all grammar objects, destroys
   dictation objects.
10. **`backend.disconnect()`** — `DragonConnection.disconnect()` releases
    all COM interface references in the correct order, releases
    `IServiceProvider`. The marshal DLL is registered once per process
    and never revoked.
11. **`_state.reset()`** — clears all registries, resets
    `_disconnect_event_handle`, releases the `NatlinkConnectionActive`
    mutex.
