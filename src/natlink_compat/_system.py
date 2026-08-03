"""_system.py - System info and utility functions."""

import struct
from typing import List, Optional, Sequence, Tuple

from ._helpers import _require_connected, _require_not_during_init, _require_not_paused, com_call
from ._state import _state
from natlink_com._dspeech_constants import DGNUTTFLG_DETECTUTT, DGNUTTFLG_REALTIME

# Re-entrancy guard for inputFromFile — matches C++ CInFunction/bInFunction.
# "We do not allow playback if we are already in the middle of playback.
# This is really a limitation of NatSpeak because there can only be one
# active file-based audio source."
# — Joel Gould, DragonCode.cpp (inputFromFile)
_in_input_from_file = False


def getClipboard() -> str:
    """Return the current contents of the clipboard as text.

    Returns an empty string if there is no text in the clipboard.
    """
    _require_connected()
    return com_call("getClipboard", _state.backend.get_clipboard)


def getCursorPos() -> Tuple[int, int]:
    """Return the current mouse cursor position as (x, y).

    (0, 0) is the upper left corner of the screen.
    """
    _require_connected()
    return com_call("getCursorPos", _state.backend.get_cursor_pos)


def getScreenSize() -> Tuple[int, int]:
    """Return the full screen size in pixels as (width, height).

    Can be used together with getCursorPos to keep the cursor on screen.
    """
    _require_connected()
    return com_call("getScreenSize", _state.backend.get_screen_size)


def getCurrentModule() -> Tuple[str, str, int]:
    """Return information about the currently active window.

    Returns:
        A tuple of (module_path, window_title, window_handle) where:

        - module_path is the full file name including path and extension,
        - window_title is the title of the currently active window,
        - window_handle is the Win32 HWND as an integer.

        Returns ``("", "", 0)`` if the current module cannot be determined.
    """
    _require_connected()
    return com_call("getCurrentModule", _state.backend.get_current_module)


def getCurrentUser() -> Tuple[str, str]:
    """Return information about the current Dragon user profile.

    Returns:
        A tuple of (user_name, speech_files_directory). If no user is
        loaded, user_name will be an empty string.
    """
    _require_connected()
    return com_call("getCurrentUser", _state.backend.get_current_user)


def getMicState() -> str:
    """Return the current microphone state.

    Returns one of ``'on'``, ``'off'``, ``'disabled'``, or ``'sleeping'``.
    """
    _require_connected()
    return com_call("getMicState", _state.backend.get_mic_state)


def setMicState(newState: str) -> None:
    """Change the microphone state.

    Args:
        newState: One of ``'on'`` (resume recognition), ``'off'`` (turn off),
            or ``'sleeping'`` (enter sleep mode).

    Raises:
        ValueError: If newState is not one of the accepted strings.
    """
    _require_connected()
    com_call("setMicState", _state.backend.set_mic_state, newState)


def inputFromFile(fileName: str, realtime: int = 0,
                  playlist: Sequence = None,
                  uttDetect: int = -1) -> None:
    """Cause Dragon to take its input from a wave file.

    Supported file extensions: ``.wav``, ``.utt``, ``.utd``, ``.utb``, ``.nwv``.

    Args:
        fileName: Path to the audio file.
        realtime: If non-zero (1), slow playback to simulate real-time
            recognition.
        playlist: Optional list of utterance indices to play (zero-based).
            Only valid for UTT, UTD and NWV files (not WAV). Can contain
            single integers or ``(start, end)`` range tuples.
        uttDetect: Utterance detection mode. ``1`` forces detection on,
            ``0`` forces it off, ``-1`` (default) auto-detects (on for WAV
            files, off for others which are assumed pre-segmented).

    Warning:
        Due to bugs in Dragon, this function can sometimes cause a crash:

        - Specifying an utterance number not present in the input file
          can cause Dragon to hang (SDAPI error, function will not return).
        - On some DNS versions (e.g. DNS 15+), calling this with a WAV
          file path can cause a fatal process crash.

    Raises:
        ValueError: If the file is missing or has an unsupported extension.
    """
    _require_connected()
    _require_not_during_init("inputFromFile")
    _require_not_paused("inputFromFile")

    global _in_input_from_file
    if _in_input_from_file:
        from ._exceptions import NatError
        raise NatError("inputFromFile cannot be reentered, "
                       "input is already active")
    _in_input_from_file = True
    try:
        _inputFromFile_impl(fileName, realtime, playlist, uttDetect)
    finally:
        _in_input_from_file = False


_VALID_EXTENSIONS = {'.utd', '.utt', '.utb', '.wav', '.nwv'}


def _testFileName(fileName):
    """Validate audio file before sending to Dragon.

    Matches C++ CDragonCode::testFileName — checks file exists and has
    a legal extension (.utd, .utt, .utb, .wav, .nwv).
    """
    import os
    from ._exceptions import NatError, ValueError
    if not fileName:
        raise ValueError("inputFromFile: empty filename")
    if not os.path.isfile(fileName):
        raise NatError(
            f"The file named {fileName} does not exist or cannot be opened "
            f"(calling natlink.inputFromFile)")
    ext = os.path.splitext(fileName)[1].lower()
    if ext not in _VALID_EXTENSIONS:
        raise NatError(
            f"The file named {fileName} does not have a legal extension "
            f"(calling natlink.inputFromFile)")


def _inputFromFile_impl(fileName, realtime, playlist, uttDetect):
    _testFileName(fileName)

    # Compute flags
    flags = 0
    is_wav = fileName.lower().endswith(('.wav', '.wave'))
    if uttDetect == 1 or (uttDetect != 0 and is_wav):
        flags |= DGNUTTFLG_DETECTUTT
    if realtime:
        flags |= DGNUTTFLG_REALTIME

    playlist_bytes = _build_playlist(playlist) if playlist else b""

    com_call(
        "inputFromFile",
        _state.backend.input_from_file,
        fileName,
        flags=flags,
        playlist=playlist_bytes,
    )


def getCallbackDepth() -> int:
    """Return the current callback nesting depth.

    Returns 0 when not inside a callback (e.g. during initialization).
    Returns 1 for a basic callback, and higher values for nested callbacks
    (e.g. calling recognitionMimic from within a callback).

    This is used by natlinkmain to avoid reloading Python modules during
    nested callbacks.
    """
    return _state.callback_depth


def _build_playlist(playlist):
    """Convert a playlist sequence into raw DWORD-pair bytes.

    Each item is either (start, end) or a single sample offset
    (treated as a single-sample range).
    """
    if not isinstance(playlist, (list, tuple)):
        raise TypeError("inputFromFile requires a play list of integers")

    buf = bytearray()
    for item in playlist:
        if isinstance(item, (list, tuple)):
            if len(item) != 2:
                raise TypeError(
                    "the ranges in the play list passed to inputFromFile must contain integers")
            try:
                start = int(item[0])
                end = int(item[1])
            except Exception as exc:
                raise TypeError(
                    "the ranges in the play list passed to inputFromFile must contain integers") from exc
            if start > end:
                raise TypeError(
                    "end point less than start point in the play list passed to inputFromFile")
            buf += struct.pack("<II", start, end)
        else:
            try:
                value = int(item)
            except Exception as exc:
                raise TypeError(
                    "the play list passed to inputFromFile must contain integers") from exc
            buf += struct.pack("<II", value, value)
    return bytes(buf)
