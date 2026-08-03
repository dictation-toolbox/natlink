# Technical Limitations

## Cross-Process Pronunciation Lookup

`getWordProns()` returns empty pronunciations when called cross-process. Dragon's server-side stub DLL (`dd10sapi.dll`) has `ExprEvalRoutines=NULL`, so the `size_is(p4/2)` expression in `ILexPronounceW::Get` evaluates to 0 on the return path. The pronunciation buffer is sent to Dragon correctly, but zero bytes are marshaled back.

Word flags and part-of-speech are unaffected (they use `size_is(p8)` with no divider).

This is maybe a fundamental limitation of Dragon's cross-process COM — their server-side stub cannot evaluate the `/2` expression. There is no workaround without replacing Dragon's stub DLL.

## Windows 11 playString / playEvents

Dragon uses `WH_JOURNALPLAYBACK` hooks to inject keystrokes. Windows 10 1607+
blocks these hooks due to User Interface Privilege Isolation (UIPI).

**DNS 16**: Works around the hook failure internally via `IDgnSSvcOutputEventW`.
The COM backend blocks on `PlaybackDone` via the action sink before returning.

**DNS 13**: Natlink bypasses Dragon's broken playback and uses Win32 `SendInput`
directly (`_sendinput.py`). This is detected automatically at connect time --
when `supports_dw_notify` is False and Windows version >= 10, `playString` and
`playEvents` route through `SendInput` instead of Dragon's
`IDgnSSvcOutputEvent::PlayString`.

The `SendInput` implementation (`_sendinput.py`, inspired by
[dtactions/vocola_sendkeys](https://github.com/dictation-toolbox/dtactions/tree/master/src/dtactions/vocola_sendkeys))
supports:
- Plain text: `playString("hello")` types each character via `VkKeyScanW`
- Named keys: `playString("{Enter}")`, `playString("{Tab}")`
- Modifiers: `playString("{Ctrl+a}")`, `playString("{Shift+Left_10}")`
- Repeat counts: `playString("{Right_5}")`
- playEvents: converts `HOOK_EVENTMSG` structs to `SendInput` keyboard events

**Limitation**: `execScript('SendKeys "abc"')` still fails on DNS 13 + Windows 11
because Dragon's scripting engine does its own keystroke injection via journal
hooks. Use `playString("abc")` instead (routed through `SendInput`).

### Diagnosis

If SendInput is active, natlink log shows:
```
PlayString(N chars) via SendInput
```

If Dragon's path is used and fails, natlink log shows:
```
PlaybackAborted(code=N, hr=0x00000000) -- if DNS 13 on Windows 10/11, journal hooks are blocked by the OS
```

## Dragon Version Differences

| Feature | DNS 13-14 | DNS 15-16 |
|---------|-----------|-----------|
| PlayString/PlayEvents | 5 params, fire-and-forget | 6 params (+ dwNotify), waits for done |
| PlayString on Win 11 | Broken (journal hooks blocked) | Works (internal fallback) |
| SRRESWORDNODE | 64 bytes | 72 bytes (+ qwSilenceDuration) |
| 32-bit proxy/stub | vcmshl.dll (/Oi) + dd10midl.dll | dd10midl.dll (/Oicf) |
| Marshal DLL variant | marshal64_v13_v14.dll | marshal64_v15_v16.dll |

The correct variant is selected automatically based on the installed Dragon version.

## Consecutive recognitionMimic with Active Microphone

When the microphone is on and processing audio, consecutive `recognitionMimic`
calls can fail with `MimicFailed` even though the grammar is loaded and active.
This is a Dragon limitation that occurs both in-process (original C++ natlink)
and out-of-process. The original C++ code reports `errMimicFailed` and returns
FALSE with no recovery.

### Root Cause

Dragon has an internal threading race between its recognition thread and the
Paused/Resume cycle. When `RecognitionMimic` is issued while Dragon's
recognition thread is still processing an audio-restart pause from the
previous utterance, the recognition thread may attempt to set up the mimic
before `Resume` has taken effect — even when `Resume` is called correctly.

Dragon log signature:
```
S2: mimic found after pause
S2: Pending utt due to mimic.
S2: Performing RecognitionMimic...
S2: Error: no utt in setup recognizer
S2: Warning: Paused Key 10370 not found
```

### Solution: Resume-Gated Retry for recognitionMimic

`recognition_mimic` (`_speech_ops.py`) improves on the C++ original with a
resume-gated retry to handle Dragon's internal threading race:

- If the first attempt fails AND `_resume_count` increased (proving a
  `Resume` was called during the attempt), retry once with a new client code.
  By the second attempt, Dragon's recognition thread has settled.
- Genuine grammar mismatches (no `Resume` fired) propagate immediately
  without retry.
