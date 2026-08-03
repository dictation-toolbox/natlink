# Gap Analysis vs Reference (2026-07-31)

Four-domain comparison of this rewrite against `Reference/natlink-master/NatlinkSource` (C++),
`Reference/natlinkcore`, and the major consumers (dragonfly, Vocola2, unimacro, Caster).

**Verification status.** Every P0 claim below was independently re-verified with offline repros
(see "Verification round 2"). All 9 audited claims CONFIRMED, none refuted; the `error_type`
defect is *larger* than first reported (22 of 35 sites wrong, not ~19). The grammar compiler was
additionally differential-fuzzed against the reference `gramparser` over 343 cases — the binary
emitter is byte-perfect, but the *parser's* accept/reject behavior diverges (new findings, §P0-9
and §P1-18). One claim (P0-1, choice-0 rule numbers) requires live Dragon and is still pending.

**Overall verdict:** the architecture is sound and coverage is nearly complete. All 36 C++
module-level functions exist, all 13 exception classes exist, the binary grammar format is
byte-compatible with `gramparser.packGrammar`, the hard pause/resume machinery is faithfully
ported, and hosting the reference `natlinkcore.loader` as a plugin preserves its reload/error
isolation semantics. Only **one symbol is missing outright** across the entire consumer sweep
(`setTrayIcon`). The real gaps cluster in four themes:

1. **Exception fidelity** — wrong `error_type` codes and bare `NatError` where C++ raised
   specific subclasses; consumers catch specific classes.
2. **Single-slot → multi-slot callback translation** — `None`-clears-all and teardown paths
   break loader coexistence.
3. **Result-object semantics** — swallowed `OutOfRange`, and choice-0 rule numbers sourced
   from `dwWordNum` instead of `dwCFGParse`.
4. **Legacy strings/affordances** consumers depend on (dragonfly string-matches error text).

---

## P0 — breaks real consumers at runtime

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 1 | **CONFIRMED ON LIVE DRAGON — choice-0 "rule numbers" are word IDs, not rule numbers.** We return `SRWORDW.dwWordNum` where C++ returns `dwCFGParse` from the results graph (`ResultObject.cpp:193-199`). | `natlink_com/_grammar_sink.py:94`, `_res_obj.py:106-107,471-487` | **Every rule-based callback is broken.** See the measurement below. Fix = route choice 0 through `BestPathWord`/`GetWordNode` like choice>0. |
| 2 | **`setTrayIcon` missing entirely** (C++: `DragonCode.cpp:3575-3703`). | nowhere in `src/` | `AttributeError` in unimacro `_repeat` repeating mode, tray-icon grammars, natlinkcore `_mouse` sample. Stub in `_legacy.py` removes the crash; real impl goes through the UI provider. |
| 3 | **Compat ResObj swallows errors** — `getResults`/`getWords`/`getWordInfo` catch and return `None` instead of raising `OutOfRange`/`NatError`. | `natlink_compat/_res_obj.py:28-68` | The ubiquitous `while 1: ... except natlink.OutOfRange: break` idiom (unimacro `_oops`, samples) gets `None` → TypeError downstream. `error_type=6` mapping already exists. |
| 4 | ~~**Systematic wrong `error_type` codes** → wrong exception classes~~ — **FIXED**. 22 of 35 raise sites carried a wrong code: bad grammar → OutOfRange instead of **BadGrammar** (natlinkutils catches BadGrammar on load); existing user → SyntaxError instead of **UserExists**; invalid word → BadWindow instead of **InvalidWord**; VALUEOUTOFRANGE → BadGrammar instead of **OutOfRange**. | natlink_com | All 35 sites now use named `ERR_*` constants from `_errors.py`, ordinal-identical to `Exceptions.h:14-33`, so the magic numbers that caused this cannot recur. |
| 5 | ~~**`setBeginCallback(None)` (and Change/Timer) clears ALL loaders' callbacks**~~ — **FIXED**, clears are now scoped to the calling package. | `natlink_compat/_callbacks.py` | Verified callers of the module-level form: dragonfly's timer (`backend_natlink/timer.py:61`) and natlinkcore's `natlinktimer` (`:284`, `:377`), both `setTimerCallback(None, 0)` — so a dragonfly timer shutting down stopped natlinkcore's timers too. **Correction:** earlier revisions also cited dragonfly's `disconnect()` and `natlinkutils`, but those call `gramObj.setBeginCallback(None)` — a per-grammar API that never reaches this list — and natlinkcore's `finish()`, which does not exist in the installed 5.4.1. |
| 6 | ~~**Disabling/removing a loader doesn't stick**~~ — **MOSTLY RETRACTED.** `remove_loader` not calling `_remove_callbacks_for` is a **deliberate contract**, pinned by two tests asserting it is not called (`test_stop_and_stop_all`, `test_unload_all_loaded_modules_does_not_guess_callback_cleanup`): frameworks own their own teardown and natlink must not guess. The `finish()` half was a category error — that method exists only in `Reference/natlinkcore` (5.4.2.dev6), not in the installed 5.4.1, which has neither `stop()` nor `finish()`, so `unload_all_loaded_modules()` is the correct call. | `natlink_compat/_loaders.py` | What remains is **unverified**: whether a tray toggle-off actually leaves natlinkcore's begin callback registered so the next utterance reloads. Never tested. Becomes live if 5.4.2 ships a `finish()`. |
| 7 | **`natlinkstatus` crashes on missing `HKLM\Software\Natlink` registry key** — nothing in this repo writes it. | reference `loader.py:633-637` expectation | `getDNSVersion`/`getNatlinkStatusDict` → uncaught `FileNotFoundError`; hits unimacro `_control` status and Vocola immediately. Provision at `natlink-ui install`, or shim. |
| 8 | **`natlink.active_loader = None` registers a None loader** — module `__setattr__` intercept has no None guard. | `src/natlink/__init__.py:24-30`, `_loaders.py:392-402` | a loader clearing `active_loader` pollutes the registry; `get_loaders()` returns `[None]`. Also `active_loader` **getter** returns `loaders[0]` regardless of owner. Repro confirmed: registry becomes `[_LoaderEntry(loader=None, name='NoneType')]`. |
| 9 | **Our parser rejects non-ASCII bare words** — ASCII-only `WORD`/`NAME` terminals. Reference uses `str.isalpha()`, so any Unicode letter works bare. | `natlink_com/_grammar_parser.py:39-40` | `<r> exported = démo;` → `GrammarError: No terminal defined for 'é'`. **Breaks 5 shipped sample macros** (natlinkcore `_samplehypothesis.py`, `_sample1/2/3/5.py`). Found by differential fuzzing; quoted `"café"` works on both sides. |
| 10 | **No `checkForErrors` equivalent anywhere in `src/`** — natlinkutils always runs doParse + checkForErrors + packGrammar. | `natlink_com/grammar_compiler.py` | We silently compile grammars with **undefined rule references** (emitting dangling rule IDs to Dragon) and with no exported rules. Callers migrating to `compile_grammar` lose the whole validation layer. |
| 11 | **PROVEN ON LIVE DRAGON — `inputFromFile` can never succeed.** It waits on `conn.playback_done` (`_speech_ops.py:352-355`), but **no `SetEvent` call in `src/` ever signals that handle** — Dragon's `PlaybackDone` posts `WM_PLAYBACK` instead (`_action_sink.py:62`). | `natlink_com/_speech_ops.py:352-355`, `_connection.py:114-118` | Measured: a valid WAV against a connected Dragon raised `inputFromFile timed out (5min)` after **exactly 300.0s**. Two completion mechanisms coexist — `message_loop`+message-entry (playString/execScript/mimic) and `pump(h_event)` — and `input_from_file` is the sole caller on the event path that nothing feeds. Residue of an incomplete event→message migration; sibling `conn.mimic_done` is created, exposed as a property, and read by nobody. **Invisible to the suite because every `inputFromFile` test mocks `backend.input_from_file`.** Fix = wait on `WM_PLAYBACK` via `push_message_entry`/`message_loop` like the other sync ops, and delete both dead events. |

| 12 | ~~**`faulthandler.enable()` in the `finally` of hidden-window creation aborts the whole connection**~~ — **FIXED**. It writes to `sys.stderr` and needs a real file descriptor. | `natlink_com/_hidden_wnd.py:222-224` | Any host whose `sys.stderr` lacks a descriptor — pytest's capture, a GUI shell, **or natlinkcore's own `redirect_output`** — raised `io.UnsupportedOperation: fileno` out of `create()`, failing `natConnect` entirely. Restoring a debug aid now never propagates. This was the true cause of the suite's ~192 setup errors (not the `fileno` defect in P1-13b, which is real but separate). |
| 13 | ~~**Connection mutex handle is clobbered, permanently poisoning the process**~~ — **FIXED**. `_establish_com_connection` assigned `CreateMutexW`'s result over `_state._conn_mutex` *before* testing `ERROR_ALREADY_EXISTS`. | `natlink_compat/_lifecycle.py:138-146` | When a stale handle was still open, the create returned a **second** handle to the same named object; the ALREADY_EXISTS branch closed only that new handle and nulled the field, **leaking the original**. The mutex then stayed held for the life of the process and every later `natConnect` — including natlink's own reconnect-after-Dragon-died path — failed with `ConnectionInUse`. Proven by instrumenting the handle lifecycle: `created=816` → later `prev=816, created=904 err=183` → 904 closed, 816 orphaned → every subsequent attempt `err=183`. Now releases a stale handle first and only publishes on success. |

## P1 — behavioral divergences with clear consumer impact

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 9 | **Legacy error strings** — dragonfly string-matches `"Calling GramObj.load is not allowed before calling natConnect"` (engine.py:232) and the playEvents variant to trigger auto-connect fallbacks. | `natlink_compat/_gram_obj.py:48`, `_helpers.py:10` | Emit per-function `"Calling {name} is not allowed before calling natConnect"` to restore fallbacks. |
| 10 | **`waitForSpeech` negative timeout hangs forever** — deadline only computed `if timeout_ms > 0`; C++ auto-closed after \|timeout\| ms. Also no dialog at all (standalone dfly-loader loses its exit affordance), and silent return when disconnected (C++ raised). | `natlink_compat/_lifecycle.py:403-435` | Fix deadline; document/replace dialog. |
| 11 | **`playString` flags dropped on DNS13/Win10 SendInput path** — shift/ctrl/upper flags never reach `send_dragon_keys`. C++ always forwarded flags (`DragonCode.cpp:2023-2042`). | `natlink_com/_speech_ops.py:180-186` | Grammars using `playString(s, flags)` get unmodified keys on the primary supported config. |
| 12 | **execScript syntax errors raise bare `NatError`**, not `natlink.SyntaxError` (C++ `DragonCode.cpp:2425-2428`; our own docstring promises SyntaxError). Same class of gap: training WrongState/ValueError sites, setMicState ValueError, getWordInfo flags ValueError, inputFromFile ValueError. | `natlink_com/_speech_ops.py:271-274`, `_user_ops.py:331-375`, `_com_bridge.py:131`, `_lexicon.py:277-279`, `natlink_compat/_system.py:154-161` | Vocola/dragonfly catch `natlink.SyntaxError` around execScript. |
| 13 | **print redirect requires natlinkcore installed** — `_logging_setup.py:349-354` imports `natlinkcore.redirect_output`; in-repo `natlink_ui/_stream_redirect.py:87` is dead code (no callers). | natlink_compat / natlink_ui | dragonfly-only installs: grammar `print()` never reaches the messages window. |
| 13b | ~~**`natConnect` breaks `sys.stdout`/`sys.stderr.fileno()` process-wide**~~ — **FIXED**. natlinkcore's `FakeTextIO.fileno()` raises `NotImplementedError` (`redirect_output.py:28`) and we install `NewStdout`/`NewStderr` on connect, even when `discovered_loaders=[]`. | `_logging_setup.py` | Before connect `sys.stderr.fileno()` → `2`; after, it raised — breaking `subprocess(..., stderr=sys.stderr)`, logging handlers wanting an fd, and any C-level consumer. Now delegates to the stream being replaced. Note `natlink_ui/_stream_redirect.py` is **implemented and unit-tested** (`tests/test_stream_redirect.py`) but wired into no production path. |
| 14 | **Two different files named `natlink.ini`** — ours `%LOCALAPPDATA%\natlink\natlink.ini` (`NATLINK_SETTINGS_DIR`); natlinkcore's `~/.natlink/natlink.ini` (`NATLINK_SETTINGSDIR`, no underscore). Our `save_config` strips comments if pointed at theirs. | `natlink_com/_config.py:17-21` vs reference `config.py:229-250` | High confusion for existing users; consider renaming ours or unifying. |
| 15 | **Shared COM timer interval** — multi-owner timer list, last-set `nMilliseconds` wins for all loaders. | `natlink_compat/_callbacks.py:568-575` | Two loaders with different intervals fight. |
| 16 | **ResObj from `DictObj.getResultsObject` returns `[]` for choice 0** — created without words, cached-words fast path short-circuits before graph query. | `natlink_com/_dict_obj.py:377`, `_res_obj.py:106-107` | Fall through to `BestPathWord` when `_words` empty. |
| 17 | **`_HRESULT_MAP` values mostly wrong** vs speech.h (GRAMMARERROR, VALUEOUTOFRANGE, SPEAKEREXISTS, nonexistent 0x80040032) and effectively dead — `NatlinkCOMError.error_type` defaults 0, so `_raise_for_com_error` never consults it. | `natlink_compat/_exceptions.py:70-129` | Fix values, default `error_type=None`. |

## P2 — lower priority / polish

- **`ConnectionInUse` not exported** from `natlink_compat.__init__` (`_exceptions.py:33`) — only catchable as NatError.
- **No callable-type validation** on callback setters (C++ raised TypeError; `pythwrap.cpp:325-329`).
- **Attrib-change events during init dropped** instead of deferred-and-replayed (`_callbacks.py:582-583`; mitigated by `_cache_initial_state`). Nested-callback deferral itself is faithful.
- **Begin callbacks skipped when `getCurrentModule` fails** — C++ substituted `("","",0)` and still fired (`DragonCode.cpp:793-796` vs `_callbacks.py:644`).
- **MimicDone diagnostic text lost** — C++ extracted IDgnError text; ours raises fixed message (`_engine_sink.py:187-202`).
- **Missing NOTDURING guards** — natConnect/natDisconnect callable from inside a paused callback (C++ refused; `DragonCode.cpp:1685,1862`).
- **inputFromFile playlist parsed then silently dropped** (`_speech_ops.py:347-351`); missing-file raises NatError not ValueError.
- **`GramObj.load` on already-loaded grammar silently reloads** (C++ hard-errored, `GrammarObject.cpp:224-229`); str decoded latin-1 vs C++ UTF-8.
- **`DictObj()` lazy construction** — succeeds while disconnected (C++ raised in ctor).
- **Results callback fired with `[]`** when word extraction fails (C++ skipped callback entirely).
- **Sink always wraps/defers result objects** even with no results callback (C++ skipped; perf, extra cross-process traffic).
- **natlinkcore can refuse to start yet register as running** (`loader.py:542-554` bails after setting `active_loader`); tray shows running with zero grammars.
- **Logger clobber hazard** if `natlinkstatus` imported before `loader.run()` (`setup_logger` strips handlers).
- **`ensure_natlinkcore_logging`** exported and documented but never called.
- **displayText `logText` arg** (Dragon-log copy) not implemented.
- **getCursorPos OSError** surfaces as misleading "connection lost" NatError (`_exceptions.py:163-164`).
- **natlinkcore log_level=DEBUG** won't show DEBUG in window (UI handler pinned at INFO, `_loaders.py:217`).

---

## Verification round 3 — LIVE ON DRAGON (P0-1 resolved)

Probe: `tests/manual_probe_cfgparse.py`. Grammar with two exported rules, `now` shared by both:

```
<ruleOne> exported = hello world now;
<ruleTwo> exported = goodbye now;
```

| Mimic | What callbacks deliver (ours) | Real `dwCFGParse` (graph) |
|---|---|---|
| "hello world now" (ruleOne) | hello→**1**, world→**2**, now→**3** | hello→**1**, world→**1**, now→**1** |
| "goodbye now" (ruleTwo) | goodbye→**4**, now→**3** | goodbye→**2**, now→**2** |

**The graph is self-consistent and correct:** every word matched by ruleOne carries 1, every word
matched by ruleTwo carries 2 — that is what a CFG parse/rule number means.

**Ours is a word table index.** The clincher is the shared word: `now` reports **3 in both
mimics**, even though it matched a different rule each time. A rule number cannot be invariant
across two different rules. The values 1/2/3/4 are simply `hello`/`world`/`now`/`goodbye` in
grammar word order.

Confirmed end-to-end — the raw callback payload dragonfly and `natlinkutils.GrammarBase`
receive was `[('goodbye', 4), ('now', 3)]`. `ruleMap` decoding, `gotResults_<rule>` dispatch, and
dragonfly's rule decoding all consume these numbers, so rule-based grammars dispatch on garbage.
Severity upgraded from "needs verification" to **confirmed P0**.

### Other P0/P1 claims confirmed live in the same run

- **P0-3**: `compat getResults(50)` → `None` (C++ raised `OutOfRange`); underlying
  `NatlinkCOMError` carried `error_type=3` (BadGrammar) instead of 6. Both halves confirmed live.
- **P1-12**: `execScript("...(((")` → bare `NatError`, not `natlink.SyntaxError`.
- **§2.3**: `activate(rule, 0x00DEAD00)` → bare `NatError`, not `BadWindow`.
- Cosmetic: both errors above report `HRESULT 0x00000000` — a success code printed in an error
  message, because these raise sites pass no `hr`.

## The connection defect that blocked all live testing (fixed)

Live verification was blocked for hours by `CoCreateInstance(DgnSite)` failing with
`0x80080005`; the project's own `tests/test_minimal.py` failed identically, so this was not
probe-specific. Root cause and fix, both in `natlink_com/_connection.py`:

1. **Missing `CLSCTX_ACTIVATE_32_BIT_SERVER`.** Dragon is a 32-bit `LocalServer32`. The 64-bit
   registry view holds an `AppID` for DgnSite with an empty `DllSurrogate` (natlink's historical
   `dgnSiteSurrogate` registration — cf. `Reference/natlink-master/NatlinkSource/dgnSiteSurrogate.rgs`);
   the clean registration lives only in the 32-bit view. A 64-bit client using plain
   `CLSCTX_LOCAL_SERVER` resolves to the 64-bit entry, COM tries to launch a server that cannot
   exist, and activation fails with `CO_E_SERVER_EXEC_FAILURE` — spawning a stray `natspeak.exe`
   on every attempt. Measured directly: `LOCAL_SERVER` → `CO_E_SERVER_EXEC_FAILURE`,
   `LOCAL_SERVER|ACTIVATE_32_BIT_SERVER` → **S_OK**, `…|ACTIVATE_64_BIT_SERVER` →
   `REGDB_E_CLASSNOTREG`. This is machine-state dependent, which is why it appears intermittently.
2. **Both COM HRESULT constants were wrong** (same mis-transcription pattern as the `error_type`
   cluster). Per `winerror.h`: `CO_E_BAD_PATH=0x80080004`, `CO_E_SERVER_EXEC_FAILURE=0x80080005`,
   `CO_E_OBJSRV_RPC_FAILURE=0x80080006`. We had `_CO_E_OBJSRV_RPC_FAILURE=0x80080005` and
   `_CO_E_SERVER_EXEC_FAILURE=0x80080004`, so the retry loop retried on
   `CO_E_SERVER_EXEC_FAILURE` and would **never** retry the genuinely transient
   `CO_E_OBJSRV_RPC_FAILURE` that Joel Gould's comment (`DragonCode.cpp:1518`) exists to work
   around. It also mislabeled every failure in the logs.

After the fix: `tests/test_minimal.py` → **13 passed**; `test_grammar.py` + `test_mimic.py` →
**32 passed**; full suite → **472 passed**. The remaining 192 suite errors are all the
two further defects found by chasing them down (§P0-12 and §P0-13), both since fixed.

---

## Verification round 2 — adversarial re-check + differential fuzzing

### Adversarial verification of the P0 claims

Nine claims re-derived independently from source with offline repros. **All CONFIRMED, none
refuted, no severity overstated.** Corrections to the first-round report:

- **The `error_type` defect is bigger than reported: 22 of 35 raise sites map to the wrong
  exception class** (13 correct). The complete audited table lives below. Notably the Python
  comments at each site *cite the correct C++ class* (e.g. `_dict_obj.py:101` says "C++:
  errBadWindow" then passes `10`=ValueError) — intent was right, the numbers were
  mis-transcribed individually. No single alternative enum explains them.
- `active_loader` getter returning `loaders[0]` is technically true but *observably* returns
  `None` once a loader clears it, so the read-back is coincidentally correct; the real
  damage is the phantom `NoneType` entry visible to `get_loaders()` and the UI.
- `_HRESULT_MAP` is worse than reported: beyond the three known-bad values, SRERR_INVALIDRULE,
  SRERR_INVALIDWINDOW, SRERR_INVALIDINTERFACE and SRERR_GRAMMARTOOCOMPLEX are all wrong, and
  `SRERR_INVALIDWORD 0x80040032` doesn't exist in speech.h. Only SRERR_INVALIDLIST, E_INVALIDARG
  and E_FAIL are right. **`natlink_com/_speech_constants.py:116-156` already has every correct
  value** — `_exceptions.py` simply doesn't use it.

#### Complete error_type audit (22 wrong of 35)

| Our site | Condition | Ours | C++ | 
|---|---|---|---|
| `_dict_obj.py:102` | activate: bad hwnd | ValueError | **BadWindow** |
| `_dict_obj.py:136` | setLock: not locked | UserExists | **WrongState** |
| `_gram_obj.py:166` | load: INVALIDCHAR | BadWindow | **InvalidWord** |
| `_gram_obj.py:170` | load: GRAMMARERROR | OutOfRange | **BadGrammar** |
| `_gram_obj.py:254` | activate: INVALIDRULE | ValueError | **UnknownName** |
| `_gram_obj.py:259` | activate: GRAMMARTOOCOMPLEX | OutOfRange | **BadGrammar** |
| `_gram_obj.py:264` | activate: RULEALREADYACTIVE | UserExists | **WrongState** |
| `_gram_obj.py:287` | deactivate: RULENOTACTIVE | UserExists | **WrongState** |
| `_gram_obj.py:409` | appendList: INVALIDCHAR | BadWindow | **InvalidWord** |
| `_lexicon.py:422` | addWord: INVALIDTEXTCHAR | BadWindow | **InvalidWord** |
| `_lexicon.py:446` | deleteWord: INVALIDTEXTCHAR | BadWindow | **InvalidWord** |
| `_lexicon.py:618` | getWordProns: INVALIDTEXTCHAR | BadWindow | **InvalidWord** |
| `_res_obj.py:118` | getResults: VALUEOUTOFRANGE | BadGrammar | **OutOfRange** |
| `_res_obj.py:151` | getWordInfo: VALUEOUTOFRANGE | BadGrammar | **OutOfRange** |
| `_res_obj.py:248` | correction: INVALIDCHAR | BadWindow | **InvalidWord** |
| `_res_obj.py:291` | getSelectInfo: VALUEOUTOFRANGE | BadGrammar | **OutOfRange** |
| `_res_obj.py:296` | getSelectInfo: NOTASELECTGRAMMAR | UserExists | **WrongType** |
| `_res_obj.py:301` | getSelectInfo: DOESNOTMATCHGRAMMAR | UserExists | **BadGrammar** |
| `_user_ops.py:113` | selectUser: E_INVALIDARG | BadWindow | **InvalidWord** |
| `_user_ops.py:159` | createUser: E_INVALIDARG | BadWindow | **InvalidWord** |
| `_user_ops.py:163` | createUser: SPEAKEREXISTS | SyntaxError | **UserExists** |
| `_user_ops.py:167,187` | createUser: base model/topic | BadGrammar | **OutOfRange** |

Correct already: `_gram_obj.py:379,388,400,413,478,492`; `_lexicon.py:250,451,485`;
`_res_obj.py:206`; `_speech_ops.py:143`; `_user_ops.py:105`.

### Differential fuzzing: grammar compiler vs reference gramparser

343 cases — 46 hand-written (every construct), 26 invalid, 12 lexical probes, 59 real-world
gramSpecs AST-extracted from unimacro/natlinkcore/Vocola2, 200 random (seed 20260731).

**The binary emitter is perfect: 300/300 mutually-accepted cases byte-identical.** Chunk order,
ID allocation order, dword padding, cp1252 encoding, symbol streams — all match, including
é/ü padding, 60-rule ID ordering, shared words across rules, and `exported` used as a word.
Error parity holds on 23 invalid grammars.

All divergence is at the **acceptance layer**:

| Divergence | Who's wrong | Impact |
|---|---|---|
| Non-ASCII bare words rejected by ours | **Ours** (vs reference *and* our own docs) | P0-9 above — breaks 5 shipped macros |
| Empty quoted word `""` accepted by ours | **Ours** — emits a nameless word entry | Dragon receives a word with an all-padding name |
| `a++` accepted (nested repeat), duplicate imports accepted, multi-line quoted words accepted | Ours (permissive) | Bytes still well-formed; grammars that build here won't load on stock natlinkcore |
| Bare `-` `_` `'` `\` in words: reference rejects, ours accepts | **Reference** deviates from its own docstring for `-`/`_`; ours exceeds both for `'`/`\` | Portability asymmetry — policy decision |
| No `checkForErrors` layer | **Ours** | P0-10 above |

---

## Verified-faithful (no action)

- Pause/resume engine semantics end-to-end: JIT-paused deferral, `pause_recog` increment on
  PhraseFinish post, deferred-cookie processing, ExecutionStatus unpause, mimic's up-front
  `resetPauseRecog`, Resume-always-in-finally, `during_paused` guards, timer skip at depth>0,
  sink flags.
- Callback ordering: global begin → trigger_load → per-grammar `gotBegin` in the same
  utterance; change-callback deferral inside callbacks with pending replay.
- Binary grammar format byte-compatible with `gramparser.packGrammar` (chunk order, padding,
  SELECT/dictation headers, the intentional dwSize bug reproduction).
- Select-and-say trio (`setSelectText`/`getSelectText`/`getSelectInfo`) complete; grammar-GUID
  plumbing equivalent to C++ pointer identity.
- Dictation lock nesting, `computeRange` slice semantics, TextChanged arg tuples.
- Result-object lifetime tracking and pre-disconnect release.
- All dragonfly/Vocola/Caster module-level calls present and signature-compatible.

## Deliberate divergences to keep documented

Launcher-owned connection with no-op natConnect/natDisconnect + `ConnectionInUse` mutex
(issue #228) — dragonfly standalone `engine.connect()` conflicts with a running launcher;
multi-loader registry replacing the NatlinkMain singleton; UIProvider replacing
`setMessageWindow`'s second-thread window; SendInput bypass of Dragon's journal hooks;
timeouts on all sync ops; getWave→bytes; getWordInfo pronunciation fallback (ILexPronounceW
marshaling break); mimic retry-on-paused-race; extra vocabulary enumeration APIs.

## Suggested fix order

1. ~~**`error_type` sweep**~~ — **DONE.** All 35 sites converted to named `ERR_*` constants;
   22 wrong values corrected against `Exceptions.h`. Still outstanding from this item: the
   `_HRESULT_MAP` rewrite and `NatlinkCOMError.error_type` default → `None` (P1-17).
2. **Unicode bare words in the parser** (P0-9) — breaks shipped sample macros today, and the fuzz
   harness gives an immediate regression check. Add `checkForErrors` equivalent (P0-10) alongside.
3. **Compat ResObj**: raise instead of returning `None` (P0-3); graph fallback for empty `_words` (P1-16).
4. **Callback ownership**: scope `None`-clears to owner (P0-5); fix `remove_loader` teardown incl.
   None-guard the `active_loader` setter + owner-aware getter (P0-8).
5. **`setTrayIcon`** stub → UI-provider impl (P0-2); legacy error strings (P1-9).
6. Registry key provisioning for natlinkstatus (P0-7); `waitForSpeech` deadline (P1-10);
   playString flags on SendInput path (P1-11); wire up `_stream_redirect` (P1-13).
7. **Live-verify P0-1** (choice-0 `dwWordNum` vs `dwCFGParse`) — still outstanding; needs a
   working Dragon COM connection. Probe script exists and is ready to run.

## Version dispatch across four Dragon versions

Dragon ships in four supported majors — **DNS 13, DPI 14, DPI 15, DPI 16** — and the repo carries
two IDL/TLB/marshal variants. The history shows the grouping is **inherited and empirically
grounded**, not invented here:

- **2015-11-05 `952086f`** (quintijn) — DNS 14 support in the original natlink was a **three-line
  change**: add the install path, add `14` to the version list. No interface change. 13 and 14 are
  interface-identical.
- **2021-10-19 `be1d962`** (fusentasticus) — the C++ build began producing **two** pyd variants,
  `natlink1314_pyd` (`DRAGON_VERSION=1314`) and `natlink15_pyd` (`DRAGON_VERSION=15`), with the
  installer picking one. The `{13,14}` vs `{15,…}` split originates here.
- **2023-03-06 `d9ddaf3`** — renamed the macro to `LEGACY`, and extended the non-legacy build to
  cover DPI 16 ("define filename for Dragon 15, 16 pyd").

**What the split actually tracks.** The only version conditional in the entire C++ header set is a
single struct field:

```c
#if LEGACY == 0   //  DPI => v15
    QWORD   qwSilenceDuration;
#endif
```

in the word-node struct (`dspeech.h:304`, `speech.h:573`). That is the whole basis for `v13_v14`
vs `v15_v16`, and it is a sound one.

**Corrected: DPI 15 does *not* issue malformed calls.** An earlier revision of this document
claimed DPI 15 lands in an "impossible cell" producing a `TypeError`, because the TLB/marshal
split is at 15 while `supports_dw_notify` splits at 16. **That was wrong and is retracted.**
Measured against live Dragon 13, comtypes accepts the required `[in]` params and optionally the
`[out]` slot:

| variant | `PlayString` | accepted arg counts |
|---|---|---|
| v13_v14 | 4 `in` + 1 `out` | 4 or 5 (6 → TypeError) |
| v15_v16 | 5 `in` + 1 `out` | 5 or 6 |

`_speech_ops.py:199` passes **5** on the legacy branch, which is valid for both variants — and on
v15_v16 the 5th argument binds to `p5` (`dwNotify`) as `0`, i.e. exactly the fire-and-forget
behaviour that branch intends. `:195` passes **6** on the dwNotify branch, valid only on v15_v16,
which is the only variant that branch can reach. All four versions are consistent.

**What remains genuinely open:**

1. **The two IDLs contradict each other on when `dwNotify` appeared.**
   `dragon_interfaces_v13_v14.idl:9` says "no dwNotify — **added in DNS 15**";
   `dragon_interfaces_v15_v16.idl:4` says "includes dwNotify … **for DNS 16+**";
   `_connection.py:769-771` says DNS 15 has it in the TLB but ignores it. The SDK header
   (`dspeech.h:456`) declares `PlayString` with **no** `dwNotify` for every version, and the
   v15_v16 IDL notes the extra parameter is "not in SDK headers" — so it was reverse-engineered.
   At most one comment is right; nothing in the repo resolves it, and it needs DPI 15/16 hardware.
2. **DPI 15 on Windows 10+ never uses Dragon's own PlayString.** `_use_sendinput`
   (`_speech_ops.py:155-159`) returns True for any non-16 Dragon on Win10+, so 15 always routes
   through SendInput. That substitution was reasoned about for DNS 13's blocked journal hooks; it
   was never decided for 15, it just falls out of `supports_dw_notify` doubling as "is this 16".
3. **One boolean answers three questions** — TLB arity, whether Dragon honours dwNotify, and
   whether the OS needs the SendInput workaround. The arity coincidence above is load-bearing but
   undocumented: the same source line means "fill the out slot" on v13_v14 and "dwNotify=0" on
   v15_v16. A `DragonProfile` naming the three separately would make that explicit rather than
   incidental.

## Still-open investigation threads

- **P0-1 live verification — BLOCKED on environment, not on the probe.** The probe is written and
  ready (compares cached `SRPHRASEW.dwWordNum` against `BestPathWord`/`GetWordNode` →
  `dwCFGParse` on the same result object across two distinct exported rules, via two mimics).
  Every `CoCreateInstance(DgnSite)` on this machine currently fails with **0x80080005
  CO_E_SERVER_EXEC_FAILURE**, including `pytest tests/test_minimal.py` — so it is not specific to
  the probe. Dragon itself is healthy (profile loaded, DragonBar in Normal mode); its log shows
  our activation arriving as `(Anti-elevation) Delegating COM activation from IL=2 PID=…` with no
  matching `Activation has been successfully delegated` line.
  Hypotheses tested and **refuted**: modal wizard blocking the server (dismissed, no change);
  multiple stale Dragon instances (cleaned to a single pid, no change); detached-subprocess launch
  context (relaunched via shell `Start-Process`, no change). Note that each failed activation
  attempt spawns another `natspeak.exe` stub, so repeated retries accumulate zombie processes —
  clean them up before re-testing. Next candidates: DCOM/marshal registration state for the
  64-bit client, or a machine reboot.
- **Out-of-process robustness audit** (Dragon dying mid-COM-call, STA reentrancy/deadlock,
  refcount leaks on crash paths, reconnect races, SDATA lifetime) — not yet performed. This is
  the failure class the in-process C++ original never had, so the reference offers no guidance.
- **Unswept consumers** — voicecode, re-tools, dragonfly-scripts; plus usage counts for
  `playString` flags and the `except OutOfRange` idiom to firm up P1-11/P0-3 severity.
