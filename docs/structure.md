# Project Structure

```
natlink/
+-- src/
|   +-- natlink/                    # Drop-in replacement package
|   |   +-- __init__.py             # Re-export + legacy active_loader interception
|   |
|   +-- natlink_compat/            # Compatibility layer (headless core)
|   |   +-- __init__.py            # Public API, single-provider registration, action functions
|   |   +-- _actions.py            # Action functions (dragon, loader, config, mic)
|   |   +-- _callbacks.py          # Global callback registration/dispatch (slot-drift guard in register_all)
|   |   +-- _cli.py                # CLI interface (natlink start/stop/info)
|   |   +-- _dict_obj.py           # DictObj (wraps ComDictObj)
|   |   +-- _exceptions.py         # NatError and 12 subclasses, com_call helper
|   |   +-- _gram_obj.py           # GramObj (wraps ComGramObj)
|   |   +-- _res_obj.py            # ResObj (wraps ComResObj)
|   |   +-- _state.py              # Global connection state; Win32 disconnect event handle
|   |   +-- _loaders.py            # Loader registry, discovery, and lifecycle
|   |   +-- _loader_protocol.py    # LoaderProtocol (runtime-checkable)
|   |   +-- _ui_protocol.py        # UIProvider protocol, NatlinkState, phase constants, dispatch helpers (set_phase, notify_ui, notify_text)
|   |   +-- _launcher.py           # Launcher class (event handles + monitor), run(), _wait_and_connect, _pump_loop, _teardown
|   |   +-- _playstring.py         # playString / playEvents helpers
|   |   +-- _speech.py             # Speech-related functions (mic, mimic, etc.)
|   |   +-- _users.py              # User management functions
|   |   +-- _vocabulary.py         # Vocabulary/word functions
|   |   +-- _system.py             # System info functions
|   |   +-- _monitor.py            # Dragon process monitor (session-scoped, no module globals)
|   |   +-- _helpers.py            # Shared helper utilities
|   |   +-- _lifecycle.py          # natConnect(*, discovered_loaders=...) / natDisconnect / waitForSpeech
|   |   +-- _logging_setup.py      # Log file init + notify_text handler + redirect
|   |   +-- _logging_control.py    # Runtime logging presets + per-category level API
|   |   +-- _win32.py              # Shared Win32 DLL handles and constants
|   |   +-- _legacy.py             # Legacy API shims
|   |
|   +-- natlink_com/              # Direct COM backend
|   |   +-- __init__.py            # Public re-exports: NatlinkCOM, NatlinkCOMError, dispatch/signal, etc.
|   |   +-- _config.py             # natlink.ini management + Dragon auto-detection + [Launch]python
|   |   +-- _ini_file.py           # Thin get/set helpers over ConfigParser
|   |   +-- _launcher.py           # Low-level primitives (COM probing, Dragon-wait hooks, mutex, event names)
|   |   +-- _com_bridge.py         # NatlinkCOM: high-level COM API
|   |   +-- _connection.py         # DragonConnection: COM lifecycle, callback slots, defer_* routers, begin_shutdown()
|   |   +-- _marshaling.py         # Marshal DLL registration (per-process)
|   |   +-- _sendinput.py          # SendInput fallback for playString/playEvents
|   |   +-- _guids.py              # COM GUIDs and CLSIDs
|   |   +-- _errors.py             # NatlinkCOMError
|   |   +-- _gram_obj.py           # ComGramObj: grammar object
|   |   +-- _grammar_sink.py       # ISRGramNotifySinkW; routes via conn.defer_send_results / defer_phrase_hypo
|   |   +-- _res_obj.py            # ComResObj: recognition result object
|   |   +-- _dict_obj.py           # ComDictObj: dictation object
|   |   +-- _dict_sink.py          # IDgnVDctNotifySinkW; routes via conn.defer_dict_text_changed
|   |   +-- _engine_sink.py        # IDgnSREngineNotifySinkW; signal+dispatch split, completion_channels()
|   |   +-- _action_sink.py        # IDgnSSvcActionNotifySinkW; signal() completions for playback/execScript
|   |   +-- grammar_compiler.py    # SAPI 4 + Dragon grammar compiler
|   |   +-- _grammar_parser.py     # Lark-based parser for SAPI 4.0 grammar syntax
|   |   +-- _dragon.py             # Dragon start/stop/restart/status + profile save
|   |   +-- _pump.py               # Win32 message pump, message_loop, trigger_message, timer
|   |   +-- _hidden_wnd.py         # Hidden COM window; dispatch() (closure queue) / signal() (sync-op completions)
|   |   +-- _lexicon.py            # Vocabulary operations (ILexPronounceW, IDgnLexWordW)
|   |   +-- _speech_ops.py         # Sync speech operations (mimic, playString, execScript)
|   |   +-- _user_ops.py           # User/speaker management (select, create, training)
|   |   +-- _win32.py              # Win32 helpers (clipboard, cursor, screen, module info)
|   |   +-- _sdata.py              # SDATA struct helpers (build/parse COM data blobs)
|   |   +-- _com_helpers.py        # COM helper utilities (force_release, addref_raw, etc.)
|   |   +-- _dspeech_constants.py  # DGNSR* codes, sink flags
|   |   +-- _speech_constants.py   # ISRNSAC_* legacy notify codes
|   |   +-- _tlb.py                # Vendored type library wrapper loader
|   |   +-- _gen_v13_v14.py        # Vendored comtypes wrappers (DNS 13 / DPI 14)
|   |   +-- _gen_v15_v16.py        # Vendored comtypes wrappers (DPI 15 / DPI 16)
|   |   +-- *.idl, *.tlb, *.dll    # IDL sources, type libraries, and marshal DLLs
|   |
|   +-- natlink_ui/               # Default UI (separate namespace, same package)
|       +-- __init__.py            # UIProvider + UI-owned install/uninstall entry points
|       +-- _window.py             # NatlinkWindow: tray + output window + UI thread; WM_UPDATE_TRAY / WM_DESTROY_SAFE trampolines
|       +-- _stream_redirect.py    # sys.stdout/stderr → notify_text
|       +-- _config.py             # natlink_ui.ini management
|       +-- _shortcuts.py          # Desktop/startup shortcut management
|       +-- _win32.py              # Win32 definitions (own copy — clean edge)
|       +-- icons/                 # Icon assets
|
+-- tests/                         # Test suite
+-- scripts/                       # Developer scripts (build, docs)
+-- examples/                      # Usage examples
+-- .claude/agents/                # Subagent definitions (ownership + shared rules)
+-- CMakeLists.txt                 # CMake build for marshal DLLs
+-- pyproject.toml                 # Package metadata; import-linter three-layer contract
+-- docs/                          # Documentation
```

## Dependency Direction

```
natlink → natlink_compat → natlink_com → Dragon COM
               ↑
          natlink_ui (optional, discovered via entry point)
```

`natlink_com` never imports from `natlink_compat` or `natlink_ui`.
`natlink_compat` never imports from `natlink_ui` except in
`_launcher.py` as an optional fallback when no `natlink.ui_provider`
entry point loads.

`natlink_ui` imports from `natlink_compat` for protocols, state types,
and action functions. It is the default implementation of the `UIProvider`
protocol — third parties replace it by registering their own
`natlink.ui_provider` entry point.

Only one UI provider is active at a time. External shells such as
Electron implement `UIProvider` and register instead of
the default tray UI.

For details on each package's design and responsibilities, see [Architecture](architecture.md).
