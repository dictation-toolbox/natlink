"""_speech.py - Speech playback and scripting functions."""

import struct
from typing import List, Tuple

from ._helpers import _require_connected, _require_not_during_init, _require_not_paused, com_call
from ._state import _state
from ._playstring import expand_keys as _expand_playstring_keys


def _coerce_event_triples(events) -> bytes:
    if not isinstance(events, list):
        raise TypeError("the argument to playEvents must be a list of tuples")

    buf = bytearray()
    for ev in events:
        if not isinstance(ev, tuple):
            raise TypeError("the list passed to playEvents must contain tuples")
        try:
            msg = int(ev[0])
            wparam = int(ev[1]) if len(ev) > 1 else 0
            lparam = int(ev[2]) if len(ev) > 2 else 0
        except Exception as exc:
            raise TypeError("the list passed to playEvents must contain tuples") from exc
        buf += struct.pack("<III", msg, wparam, lparam)
    return bytes(buf)


def _coerce_exec_script_args(args):
    if args is None:
        return None
    if not isinstance(args, list):
        raise TypeError("the second argument to execScript must be a list of words")
    if not all(isinstance(word, str) for word in args):
        raise TypeError("the second argument to execScript must be a list of words")
    return args


def _coerce_mimic_words(args) -> List[str]:
    if len(args) == 0:
        raise TypeError("recognitionMimic requires at least 1 argument")

    if len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]):
        words = list(args[0])
    else:
        words = list(args)

    if not words:
        raise TypeError("recognitionMimic requires at least 1 argument")
    if not all(isinstance(word, str) for word in words):
        raise TypeError("all arguments passed to recognitionMimic must be strings")
    return words


def playString(keys: str, flags: int = 0) -> None:
    """Send keystrokes to the focused window in Dragon NaturallySpeaking format.

    The keys string uses Dragon's control-sequence syntax (sequences in braces).
    This function will not return until the last keystroke has been drained
    from the input queue.

    Args:
        keys: Keystroke string in Dragon NaturallySpeaking format.
        flags: Optional combination of modifier flags:

            - ``0x01`` — add SHIFT to the first character
            - ``0x02`` — add ALT to the first character
            - ``0x04`` — add CTRL to the first character
            - ``0x08`` — add RIGHT SHIFT to the first character
            - ``0x10`` — add RIGHT ALT to the first character
            - ``0x20`` — add RIGHT CTRL to the first character
            - ``0x40`` — use the extended keyboard version of the first char
            - ``0x100`` — defer termination until the event queue is drained
            - ``0x200`` — send system keys (uses low-level keyboard hook)
            - ``0x400`` — raise an exception if a shift key is held down
              (recommended with system keys)
            - ``0x10000`` — use scan codes when generating events
            - ``0x20000`` — uppercase the entire string
            - ``0x40000`` — lowercase the entire string
            - ``0x80000`` — uppercase the first character

    Note:
        **DNS 13 on Windows 10+**: Dragon's ``WH_JOURNALPLAYBACK`` hooks are
        blocked by User Interface Privilege Isolation (UIPI). Natlink
        automatically detects this and routes keystrokes through Win32
        ``SendInput`` instead. DNS 15-16 are unaffected (Dragon uses an
        internal fallback).
    """
    _require_connected()
    _require_not_during_init("playString")
    _require_not_paused("playString")
    keys = _expand_playstring_keys(keys)
    com_call("playString", _state.backend.play_string, keys, flags)


def playEvents(events: List[Tuple[int, ...]]) -> None:
    """Play a sequence of keyboard and mouse events.

    A more powerful alternative to playString that can play any sequence
    of Windows message events.

    Args:
        events: List of tuples, each containing (msg, wParam, lParam).
            Supported messages:

            - ``(0x100, keycode, repeat)`` — WM_KEYDOWN
            - ``(0x101, keycode, repeat)`` — WM_KEYUP
            - ``(0x104, keycode, repeat)`` — WM_SYSKEYDOWN
            - ``(0x105, keycode, repeat)`` — WM_SYSKEYUP
            - ``(0x200, x, y)`` — WM_MOUSEMOVE
            - ``(0x201, x, y)`` — WM_LBUTTONDOWN
            - ``(0x202, x, y)`` — WM_LBUTTONUP
            - ``(0x203, x, y)`` — WM_LBUTTONDBLCLK
            - ``(0x204, x, y)`` — WM_RBUTTONDOWN
            - ``(0x205, x, y)`` — WM_RBUTTONUP
            - ``(0x206, x, y)`` — WM_RBUTTONDBLCLK
            - ``(0x207, x, y)`` — WM_MBUTTONDOWN
            - ``(0x208, x, y)`` — WM_MBUTTONUP
            - ``(0x209, x, y)`` — WM_MBUTTONDBLCLK

    Note:
        **DNS 13 on Windows 10+**: Dragon's journal hooks are blocked by
        UIPI. Natlink converts keyboard events to Win32 ``SendInput`` calls
        automatically. Mouse events are passed through unchanged.
        DNS 15-16 are unaffected.
    """
    _require_connected()
    _require_not_during_init("playEvents")
    _require_not_paused("playEvents")
    com_call("playEvents", _state.backend.play_events, _coerce_event_triples(events))


def execScript(command: str, args: List[str] = None,
               comment: str = "") -> None:
    """Execute an arbitrary script using Dragon's built-in scripting language.

    Args:
        command: The script text to execute.
        args: Optional list of strings substituted for ``_arg1``, ``_arg2``,
            etc. in the script at execution time.
        comment: Optional comment displayed in error messages if the script
            fails (typically the command name).

    Raises:
        SyntaxError: If there is a syntax error in the script.

    Note:
        **DNS 13 on Windows 10+**: ``SendKeys`` commands inside Dragon
        scripts still fail because Dragon's scripting engine uses its own
        journal hook injection, which is blocked by UIPI. Use
        ``playString()`` instead (routed through ``SendInput``).
    """
    _require_connected()
    _require_not_during_init("execScript")
    _require_not_paused("execScript")
    com_call("execScript", _state.backend.exec_script, command, _coerce_exec_script_args(args), comment)


def recognitionMimic(*args) -> None:
    """Simulate the effect of a recognition.

    Pass in words representing the recognition results and Dragon will
    simulate the exact effect of having recognized that sequence. An error
    is raised if the words are unknown or represent an impossible recognition
    given the current system state.

    Accepts either a list or varargs::

        recognitionMimic(["hello", "world"])
        recognitionMimic("hello", "world")

    Raises:
        MimicFailed: If the phrase is not legal in the current context
            (not in an active grammar) or a word is invalid.
    """
    _require_connected()
    _require_not_during_init("recognitionMimic")
    _require_not_paused("recognitionMimic")
    com_call("recognitionMimic", _state.backend.recognition_mimic, _coerce_mimic_words(args))
