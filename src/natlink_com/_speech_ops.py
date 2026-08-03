"""Speech operations — playback, mimic, and script execution."""

import ctypes
import logging
import struct
import time

from ._errors import (NatlinkCOMError,
                      ERR_MIMIC_FAILED)
from ._pump import pump, push_message_entry, message_loop, _kernel32
from ._sdata import build_sdata as _build_sdata

log = logging.getLogger("natlink.com")


def _pack_mimic_words(words):
    """Pack words as null-terminated WCHAR strings for RecognitionMimic SDATA.

    Python equivalent of C++ ``packString()`` in DragonCode.cpp.
    Format: word1\\0word2\\0word3\\0 ... padded to 4-byte boundary.
    Each character is 2 bytes (UTF-16LE WCHAR).
    """
    parts = []
    for word in words:
        # Null-terminated UTF-16LE string
        parts.append((word + "\x00").encode("utf-16-le"))
    raw = b"".join(parts)
    # Pad to 4-byte boundary
    padded_size = (len(raw) + 3) & ~3
    raw += b"\x00" * (padded_size - len(raw))
    return raw


def _sync_op(conn, client_code_fn, wm_msg, label, start, timeout_ms=10000):
    """Run a sync operation matching C++ messageLoop pattern.

    push_message_entry -> start callback (dispatch pending + COM call) -> message_loop.
    lParam: 0 = success, non-zero = abort/error.  Error message (if any)
    is attached via signal(data=...) and retrieved here via
    ``take_signal_data(wm_msg, code)`` after message_loop returns.

    Design note from DragonCode.cpp (Notes about nested callbacks):
    "NatSpeak is free to call into this code whenever we are in a Windows
    message loop."  During the message loop wait, Dragon may fire additional
    COM callbacks (PhraseFinish, Paused, etc.) which can re-enter Python.
    "The user needs to be aware that when they do a playString, execScript
    or recognitionMimic, another Python callback is possible."
    """
    from . import _hidden_wnd
    code = client_code_fn()
    entry = push_message_entry(wm_msg, code)

    lparam = message_loop(entry, timeout_ms, label,
                          start=lambda c=code: start(c))

    if lparam is None:
        raise NatlinkCOMError(label, error_message=f"{label} timed out")
    if lparam != 0:
        error_msg = _hidden_wnd.take_signal_data(wm_msg, code)
        if not error_msg:
            error_msg = f"Error returned from {label}"
        raise NatlinkCOMError(label, error_message=error_msg)
    return code


def recognition_mimic(conn, client_code_fn, words):
    """Mimic a recognition with the given word list.  Blocks until MimicDone.

    IDgnSREngineControlW::RecognitionMimic(DWORD count, SDATA data, DWORD clientCode)

    SDATA contains null-terminated WCHAR strings concatenated together,
    padded to 4-byte boundary.

    The C++ original calls resetPauseRecog() before starting the mimic
    so any pending PhraseFinish processing is flushed — otherwise the
    mimic's recognition cannot start (Dragon won't restart the
    recognition loop until PhraseFinish processing is complete).
    See DragonCode.cpp, CDragonCode::recognitionMimic.
    """
    ctl = conn.engine_ctl
    tlb = conn.tlb
    if ctl is None:
        raise NatlinkCOMError("recognition_mimic", error_message="No engine control")

    # Pack words as null-terminated WCHAR strings
    packed = _pack_mimic_words(words)

    # Build SDATA — _buf prevents GC while sdata.pData is live
    sdata, _buf = _build_sdata(tlb, packed)

    conn.reset_pause_recog()

    from . import _hidden_wnd

    # STA out-of-process: Dragon may still be paused from the previous
    # recognition cycle (audio-restart Paused RPC not yet delivered).
    # If RecognitionMimic arrives while Dragon is paused, Dragon returns
    # MimicDone with error ("no utt in setup recognizer").
    #
    # Recovery: message_loop's start callback dispatches any pending
    # WM_PAUSED → Resume, then issues RecognitionMimic.  If the Paused
    # RPC hadn't landed yet (LRPC latency), the first attempt fails.
    # We retry ONLY if a Resume was called between attempts (proving
    # Dragon was paused).  If no Resume fired, the failure is genuine.
    #
    # "each request to NatSpeak will have a different request number so we
    # can match up ExecutionDone callbacks."
    # — DragonCode.cpp, CDragonCode::recognitionMimic
    # (N.B. The C++ comment says "ExecutionDone" but means MimicDone —
    # copy-paste from execScript in the original source.)
    resume_before = conn._resume_count
    code = client_code_fn()
    entry = push_message_entry(_hidden_wnd.WM_MIMICDONE, code)

    lparam = message_loop(entry, 60000, "mimic",
                          start=lambda c=code: ctl.RecognitionMimic(
                              len(words), sdata, c))

    if lparam is None:
        raise NatlinkCOMError("recognition_mimic",
                              error_message="MimicDone not received within 60s")
    if lparam == 0:
        log.debug("RecognitionMimic(%d words) OK", len(words))
        return

    # First attempt failed.  Retry only if Dragon was paused — a Resume
    # between attempts proves the race condition, not a grammar mismatch.
    if conn._resume_count > resume_before:
        log.debug("MIMIC: failed with Resume detected (paused race), retrying")
        code = client_code_fn()
        entry = push_message_entry(_hidden_wnd.WM_MIMICDONE, code)

        lparam = message_loop(entry, 60000, "mimic",
                              start=lambda c=code: ctl.RecognitionMimic(
                                  len(words), sdata, c))

        if lparam is None:
            raise NatlinkCOMError("recognition_mimic",
                                  error_message="MimicDone not received within 60s")
        if lparam == 0:
            log.debug("RecognitionMimic(%d words) OK", len(words))
            return

    raise NatlinkCOMError("recognition_mimic", error_type=ERR_MIMIC_FAILED,
                          error_message="MimicDone reported failure (no matching grammar)")


def _use_sendinput(conn):
    """True if we should bypass Dragon's PlayString and use SendInput directly.

    DNS 13 on Windows 10+ uses journal hooks (WH_JOURNALPLAYBACK) that the
    OS blocks. DNS 16 handles this internally. We detect the combination
    and route through our SendInput implementation instead.
    """
    if conn.supports_dw_notify:
        return False  # DNS 16 — Dragon handles it
    import sys
    win_ver = sys.getwindowsversion()
    return win_ver.major >= 10


def play_string(conn, client_code_fn, keys, flags=0):
    """Send keystrokes via Dragon.  Blocks until keystrokes are delivered.

    DNS 16+: Uses dwNotify=1 so Dragon fires PlaybackDone, then pumps
    the Win32 message queue (MsgWaitForMultipleObjects) until the callback
    arrives — the same approach original natlink used in-process.

    DNS 13 on Windows 10/11: Bypasses Dragon's broken journal hooks and
    uses Win32 SendInput directly via _sendinput module.

    DNS 13 on older Windows: Fire-and-forget through Dragon.

    "each request to NatSpeak will have a different request number so we
    can match up PlaybackDone callbacks."
    — Joel Gould, DragonCode.cpp (playString)
    """
    if not keys:
        return  # Dragon doesn't fire PlaybackDone for empty strings

    if _use_sendinput(conn):
        from ._sendinput import send_dragon_keys
        send_dragon_keys(keys)
        # Yield to let the target window's thread process the input queue.
        time.sleep(0.05)
        log.debug("PlayString(%d chars) via SendInput", len(keys))
        return

    oe = conn.output_event
    if oe is None:
        raise NatlinkCOMError("play_string", error_message="No output event interface")

    from . import _hidden_wnd
    if conn.supports_dw_notify:
        _sync_op(conn, client_code_fn, _hidden_wnd.WM_PLAYBACK, "playString",
                 start=lambda c: oe.PlayString(keys, flags, 0xFFFFFFFF, c, 0, 1))
        time.sleep(0.03)
    else:
        code = client_code_fn()
        oe.PlayString(keys, flags, 0xFFFFFFFF, code, 0)
        pump()
    log.debug("PlayString(%d chars, flags=0x%X)", len(keys), flags)


def play_events(conn, client_code_fn, buffer):
    """Play keyboard/mouse events.  Blocks until delivery completes.

    DNS 16+: Uses dwNotify=1 + message pump wait (same as play_string).
    DNS 13 on Windows 10/11: Bypasses Dragon, uses SendInput directly.
    DNS 13 on older Windows: Fire-and-forget through Dragon.

    buffer: packed HOOK_EVENTMSG structs (3 DWORDs each: message, paramL, paramH)
    """
    event_size = 12  # 3 DWORDs = 12 bytes
    if len(buffer) == 0:
        raise NatlinkCOMError("play_events",
                              error_message="Empty event buffer")
    if len(buffer) % event_size != 0:
        raise NatlinkCOMError("play_events",
                              error_message=f"Buffer size {len(buffer)} not a multiple of {event_size}")

    if _use_sendinput(conn):
        from ._sendinput import send_events
        send_events(buffer)
        time.sleep(0.05)
        log.debug("PlayEvents(%d events) via SendInput", len(buffer) // event_size)
        return

    oe = conn.output_event
    if oe is None:
        raise NatlinkCOMError("play_events", error_message="No output event interface")
    count = len(buffer) // event_size

    # Build array of HOOK_EVENTMSG structs
    tlb = conn.tlb
    EventArray = tlb.HOOK_EVENTMSG * count
    events = EventArray()
    for i in range(count):
        msg, paramL, paramH = struct.unpack_from("<III", buffer, i * event_size)
        events[i].message = msg
        events[i].paramL = paramL
        events[i].paramH = paramH

    # "each request to NatSpeak will have a different request number so we
    # can match up PlaybackDone callbacks."
    # — DragonCode.cpp, CDragonCode::playEvents
    from . import _hidden_wnd
    if conn.supports_dw_notify:
        _sync_op(conn, client_code_fn, _hidden_wnd.WM_PLAYBACK, "playEvents",
                 start=lambda c: oe.PlayEvents(count, events, 0xFFFFFFFF, c, 1))
        time.sleep(0.03)
    else:
        code = client_code_fn()
        oe.PlayEvents(count, events, 0xFFFFFFFF, code)
        pump()
    log.debug("PlayEvents(%d events)", count)


def exec_script(conn, client_code_fn, command, args=None, comment=""):
    """Execute a Dragon scripting command.  Blocks until ExecutionDone fires.

    Without args: IDgnSSvcInterpreterW::ExecuteScript
    With args:    IDgnSSvcInterpreterW::ExecuteScriptWithListResults
        Dragon substitutes %1, %2, ... in the script at execution time.
    """
    interp = conn.interpreter
    if interp is None:
        raise NatlinkCOMError("exec_script", error_message="No interpreter interface")
    # "Although this is optional, if we check the script syntax first, we
    # can report errors in a cleaner way."
    # — DragonCode.cpp, CDragonCode::execScript
    error_code, line_number = interp.CheckScript(command, 0, 0)
    if error_code:
        raise NatlinkCOMError("exec_script",
                              error_message=f"Script error {error_code} at line {line_number}")
    from . import _hidden_wnd

    def _do_exec(code):
        # "if there are list parameters, we use this form.  The list
        # parameters need to be passed in a single buffer separated with
        # terminators" — DragonCode.cpp, CDragonCode::execScript
        if args:
            packed = _pack_mimic_words(args)
            buf = (ctypes.c_ubyte * len(packed))(*packed)
            ec, ln = interp.ExecuteScriptWithListResults(
                command, len(packed), buf, 0, 0, comment, code)
        else:
            ec, ln = interp.ExecuteScript(command, 0, 0, comment, code)
        if ec:
            raise NatlinkCOMError("exec_script",
                                  error_message=f"Script error {ec} at line {ln}")

    _sync_op(conn, client_code_fn, _hidden_wnd.WM_EXECUTION, "execScript",
             start=_do_exec, timeout_ms=60000)
    log.debug("ExecuteScript OK")


def name_from_key(conn, key, flags=0, state=0, layout=0):
    """Resolve a Dragon key specifier into its textual name."""
    oe = conn.output_event
    if oe is None:
        raise NatlinkCOMError("name_from_key",
                              error_message="No output event interface")
    needed = ctypes.c_ulong(64)
    buf = ctypes.create_unicode_buffer(needed.value)
    hr = getattr(oe, "_IDgnSSvcOutputEventW__com_NameFromKey")(
        key, flags, state, layout, buf, ctypes.byref(needed))
    if hr < 0:
        raise NatlinkCOMError("IDgnSSvcOutputEventW::NameFromKey", hr=hr)
    if needed.value > len(buf) and needed.value > 0:
        buf = ctypes.create_unicode_buffer(needed.value)
        hr = getattr(oe, "_IDgnSSvcOutputEventW__com_NameFromKey")(
            key, flags, state, layout, buf, ctypes.byref(needed))
        if hr < 0:
            raise NatlinkCOMError("IDgnSSvcOutputEventW::NameFromKey", hr=hr)
    return buf.value


_input_from_file_active = False


def input_from_file(conn, path, flags=0, playlist=b""):
    """Play audio from a file into the recognizer.

    IDgnSRAudioFileSourceW: FileNameSet, PlayListSet, EnableSet, FileClose.
    Blocks until playback completes (DGNSRAC_PLAYBACKDONE notification).

    Reentrancy guard matches C++: "We do not allow playback if we are
    already in the middle of playback.  This is really a limitation of
    NatSpeak because there can only be one active file-based audio source."
    — Joel Gould, DragonCode.cpp (inputFromFile)
    """
    global _input_from_file_active
    if _input_from_file_active:
        raise NatlinkCOMError("input_from_file",
                              error_message="inputFromFile can not be reentered, "
                              "input is already active")
    afs = conn.audio_file_source
    if afs is None:
        raise NatlinkCOMError("input_from_file",
                              error_message="No audio file source interface")

    _input_from_file_active = True
    started = False
    try:
        afs.FileNameSet(flags, path)

        if playlist:
            log.warning("PlayListSet not available cross-process "
                        "(Dragon omits it from W-variant marshal); "
                        "playlist ignored, playing entire file")

        # Completion arrives as AttribChanged2(DGNSRAC_PLAYBACKDONE), which
        # _engine_sink turns into signal(WM_ATTRIBCHANGED, dwCode) — the same
        # message-entry mechanism playString/execScript/mimic use. Waiting on
        # a Win32 event instead would block until the timeout, since nothing
        # signals one. Push the entry before EnableSet so an immediate
        # completion is caught by message_loop's pre-consumed check.
        from . import _hidden_wnd
        from ._dspeech_constants import DGNSRAC_PLAYBACKDONE
        entry = push_message_entry(_hidden_wnd.WM_ATTRIBCHANGED,
                                   DGNSRAC_PLAYBACKDONE)
        afs.EnableSet(True)
        started = True
        if message_loop(entry, 300000, "inputFromFile") is None:  # 5min
            raise NatlinkCOMError("inputFromFile",
                                  error_message="inputFromFile timed out (5min)")

        log.debug("inputFromFile completed: %s", path)
    finally:
        # Always disable/close the file source once EnableSet(True) succeeded,
        # so a pump timeout/error does not leave Dragon's file-audio source
        # active.
        if started:
            try:
                afs.EnableSet(False)
                afs.FileClose()
            except Exception:
                log.exception("inputFromFile cleanup failed")
        _input_from_file_active = False
