"""NatlinkCOM — direct COM backend for natlink."""

import ctypes
import itertools
import logging
from typing import List, Optional, Tuple

from ._connection import DragonConnection
from ._dict_obj import ComDictObj, create_dictation as _create_dictation
from ._dspeech_constants import HOOKERR_CANNOTINJECT, HOOKERR_INJECTFAILED
from ._errors import NatlinkCOMError
from ._gram_obj import ComGramObj, load_grammar as _load_grammar
from ._speech_constants import E_BUFFERTOOSMALL
from ._win32 import (
    get_clipboard, get_cursor_pos, get_screen_size,
    get_current_module, is_dragon_running,
)

# DGNMIC_* constants from dspeech.h
DGNMIC_DISABLED = 0
DGNMIC_OFF = 1
DGNMIC_ON = 2
DGNMIC_SLEEPING = 3

# Mic state code → string (matching C++ CDragonCode::getMicState switch)
MIC_STATE_MAP = {
    DGNMIC_DISABLED: "disabled",
    DGNMIC_OFF: "off",
    DGNMIC_ON: "on",
    DGNMIC_SLEEPING: "sleeping",
}

# String → mic state code (matching C++ CDragonCode::setMicState)
# Note: "disabled" is intentionally excluded — C++ does not accept it.
MIC_STRING_MAP = {"on": DGNMIC_ON, "off": DGNMIC_OFF, "sleeping": DGNMIC_SLEEPING}

from ._lexicon import (  # noqa: E402 — grouped with constants
    get_word_info as _get_word_info,
    add_word as _add_word, delete_word as _delete_word,
    set_word_info as _set_word_info, get_word_prons as _get_word_prons,
    enumerate_words as _enumerate_words,
    enumerate_prefix_words as _enumerate_prefix_words,
    get_word_from_prefix as _get_word_from_prefix,
    get_word_from_pron as _get_word_from_pron,
)

from . import _speech_ops
from . import _user_ops

from ._pump import pump, set_timer, kill_timer

log = logging.getLogger("natlink.com")



class NatlinkCOM:
    """Direct COM backend for natlink.

    Provides method names and signatures that natlink_compat wraps to
    present the original natlink C extension API surface.
    """

    def __init__(self):
        self._conn = DragonConnection()
        # Timer managed via module-level set_timer/kill_timer in _pump.py
        self._client_codes = itertools.count(1)

    def _next_client_code(self) -> int:
        return next(self._client_codes)

    # --- Connection ---

    def connect(self, launch: bool = True) -> None:
        if launch and not is_dragon_running():
            log.info("Dragon not running, attempting to launch...")
            from ._dragon import launch as launch_dragon
            launch_dragon()

        self._conn.connect()

    def unregister_sinks(self) -> None:
        self._conn.unregister_sinks()

    def disconnect(self) -> None:
        kill_timer()
        self._conn.disconnect()

    @property
    def conn(self):
        """The underlying DragonConnection (for callback slot wiring)."""
        return self._conn

    def is_dragon_running_remote(self) -> bool:
        return is_dragon_running()

    @property
    def dragon_version(self) -> Tuple[int, int, int]:
        return self._conn.dragon_version

    # --- Engine Control ---

    def get_mic_state(self) -> str:
        """Get the microphone state as a string.

        Matches C++ CDragonCode::getMicState:
          DGNMIC_DISABLED → "disabled"
          DGNMIC_OFF → "off"
          DGNMIC_ON → "on"
          DGNMIC_SLEEPING → "sleeping"
          unknown → "error"
        """
        ctl = self._conn.engine_ctl
        if ctl is None:
            raise NatlinkCOMError("get_mic_state", error_message="No engine control")
        wState = ctl.GetMicState()
        return MIC_STATE_MAP.get(wState, "error")

    def set_mic_state(self, state: str) -> None:
        """Set the microphone state.

        Matches C++ CDragonCode::setMicState:
          "on" → DGNMIC_ON, "off" → DGNMIC_OFF, "sleeping" → DGNMIC_SLEEPING
          Other values → error (C++ uses case-insensitive _stricmp)

        "change the microphone state here"
        — Joel Gould, DragonCode.cpp (setMicState)
        """
        ctl = self._conn.engine_ctl
        if ctl is None:
            raise NatlinkCOMError("set_mic_state", error_message="No engine control")
        code = MIC_STRING_MAP.get(state.lower())
        if code is None:
            raise NatlinkCOMError("set_mic_state",
                                  error_message=f"Invalid parameter '{state}' (calling setMicState)")
        log.info("→ SetMicState(%s)", state)
        ctl.SetMicState(code, 0)  # FALSE = don't persist
        pump()

    # --- Speaker ---

    def get_current_user(self) -> Tuple[str, str]:
        return _user_ops.get_current_user(self._conn)

    def get_all_users(self) -> List[str]:
        return _user_ops.get_all_users(self._conn)

    # --- Pure Python Utilities ---

    def get_clipboard(self) -> str:
        return get_clipboard()

    def get_cursor_pos(self) -> Tuple[int, int]:
        return get_cursor_pos()

    def get_screen_size(self) -> Tuple[int, int]:
        return get_screen_size()

    # Import the canonical transcriptions rather than restating the literals:
    # dspeech.h derives these from HOOKAPIERROR(x) = FACILITY_ITF | (x + 0x2000)
    # and SPEECHERROR(x) = FACILITY_ITF | (x + 0x200), which is easy to get
    # wrong by hand. A wrong value here fails silently -- the retry below never
    # fires and long module paths truncate at 520 chars.
    _E_BUFFERTOOSMALL_HOOK = E_BUFFERTOOSMALL
    _HOOKERR_INJECTFAILED = HOOKERR_INJECTFAILED
    _HOOKERR_CANNOTINJECT = HOOKERR_CANNOTINJECT

    # HRESULTs where Dragon's hook failed but the condition may be
    # temporary — return ("", "", 0) matching C++ behavior.
    _HOOK_SOFT_ERRORS = {_HOOKERR_INJECTFAILED, _HOOKERR_CANNOTINJECT}

    def get_current_module(self) -> Tuple[str, str, int]:
        """Get foreground window info: (module_path, window_title, hwnd).

        Matches C++ CDragonCode::getCurrentModule:
          1. GetForegroundWindow — null → ("", "", 0)
          2. GetWindowText for title
          3. IDgnExtModSupStringsW::GetWindowModuleFileName for module path
          4. Handle E_BUFFERTOOSMALL (retry with larger buffer)
          5. Handle HOOKERR_INJECTFAILED, HOOKERR_CANNOTINJECT,
             SRERR_INVALIDPARAM → ("", "", 0)

        "get the module name of the current foreground window; note that
        this operation is very complicated under Win32.  Fortunately,
        Dragon NaturallySpeaking has worked out all the details and has
        exposed the function for our use."
        — Joel Gould, DragonCode.cpp (getCurrentModule)

        Falls back to Win32 GetModuleFileNameExW if Dragon's hook interface
        is unavailable (our extension — C++ just returns empty).
        """
        ext = self._conn._ext_mod_strings
        if ext is None:
            return get_current_module()

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            # "This can happen if the current foreground window is closing."
            return ("", "", 0)

        # Get the caption of the current foreground window
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 512)
        title = buf.value

        try:
            # comtypes generates POINTER(c_ushort) for [out, size_is] wchar_t*,
            # so we must cast our unicode buffer to match.
            path_buf = ctypes.create_unicode_buffer(520)
            path_ptr = ctypes.cast(path_buf, ctypes.POINTER(ctypes.c_ushort))
            needed = ctypes.c_ulong(0)
            hr = getattr(ext, "_IDgnExtModSupStringsW__com_GetWindowModuleFileName")(
                hwnd, path_ptr, 520, ctypes.byref(needed))

            if (hr & 0xFFFFFFFF) == self._E_BUFFERTOOSMALL_HOOK:
                # "dwLength = dwNeeded + 1; ... retry"
                path_buf = ctypes.create_unicode_buffer(needed.value + 1)
                path_ptr = ctypes.cast(path_buf, ctypes.POINTER(ctypes.c_ushort))
                hr = getattr(ext, "_IDgnExtModSupStringsW__com_GetWindowModuleFileName")(
                    hwnd, path_ptr, needed.value + 1, ctypes.byref(needed))

            hr_unsigned = hr & 0xFFFFFFFF
            if hr_unsigned in self._HOOK_SOFT_ERRORS:
                # "This error sometimes happens when NatSpeak tries to get
                # the module name of the currently active module and fails
                # because the target module is busy or otherwise unable to
                # be accessed through the NatSpeak hooking mechanism.  This
                # condition may be temporary so retrying is always an option."
                # — Joel Gould, DragonCode.cpp (getCurrentModule)
                log.debug("GetWindowModuleFileName soft error: 0x%08X",
                          hr_unsigned)
                return ("", "", 0)

            if hr < 0:
                log.debug("GetWindowModuleFileName failed: 0x%08X, "
                          "using Win32 fallback", hr_unsigned)
                return get_current_module()

            return (path_buf.value, title, hwnd)
        except Exception:
            log.debug("GetWindowModuleFileName exception, using Win32 fallback",
                      exc_info=True)
            return get_current_module()

    # --- Message window ---

    def display_text(self, text: str, is_error: bool) -> None:
        if is_error:
            log.error("%s", text.rstrip())
        else:
            log.info("%s", text.rstrip())

    def set_timer_callback(self, has_callback: bool, ms: int = 0) -> None:
        kill_timer()
        if not has_callback or ms <= 0:
            return

        def _dispatch_timer():
            cb = self._conn.on_timer_dispatch
            if cb:
                cb()

        set_timer(ms, _dispatch_timer)

    # --- Grammar ---

    def grammar_load(self, data: bytes, all_results: bool = False,
                     hypothesis: bool = False) -> ComGramObj:
        return _load_grammar(self._conn, data, all_results, hypothesis)

    # --- Playback + Engine ---

    def recognition_mimic(self, words: List[str]) -> None:
        _speech_ops.recognition_mimic(self._conn, self._next_client_code, words)

    def play_string(self, keys: str, flags: int = 0) -> None:
        _speech_ops.play_string(self._conn, self._next_client_code, keys, flags)

    def play_events(self, buffer: bytes) -> None:
        _speech_ops.play_events(self._conn, self._next_client_code, buffer)

    def exec_script(self, command: str, args: list = None,
                    comment: str = "") -> None:
        _speech_ops.exec_script(self._conn, self._next_client_code, command, args, comment)

    def save_speaker(self) -> None:
        _user_ops.save_speaker(self._conn)

    # --- User Management ---

    def select_user(self, user: str) -> None:
        _user_ops.select_user(self._conn, user)

    def create_user(self, name: str, model: str = "", topic: str = "") -> None:
        _user_ops.create_user(self._conn, name, model, topic)

    # --- Vocabulary ---

    def get_word_info(self, word: str, flags: int = 0) -> Optional[int]:
        return _get_word_info(self._conn, word, flags)

    def add_word(self, word: str, pron: str = "", word_info: int = 0) -> bool:
        return _add_word(self._conn, word, pron, word_info)

    def delete_word(self, word: str) -> None:
        _delete_word(self._conn, word)

    def set_word_info(self, word: str, flags: int = 0) -> None:
        _set_word_info(self._conn, word, flags)

    def get_word_prons(self, word: str) -> Optional[List[str]]:
        return _get_word_prons(self._conn, word)

    def enumerate_words(self) -> List[str]:
        return _enumerate_words(self._conn)

    def enumerate_prefix_words(self, prefix: str) -> List[str]:
        return _enumerate_prefix_words(self._conn, prefix)

    def get_word_from_prefix(self, prefix: str, flags: int = 0, index: int = 0) -> str:
        return _get_word_from_prefix(self._conn, prefix, flags, index)

    def get_word_from_pron(self, pron: str, flags: int = 0, index: int = 0) -> str:
        return _get_word_from_pron(self._conn, pron, flags, index)

    # --- Training ---

    def get_user_training(self) -> Optional[str]:
        return _user_ops.get_user_training(self._conn)

    def get_training_mode(self) -> Tuple[str, int]:
        return _user_ops.get_training_mode(self._conn)

    def start_training_mode(self, mode: str) -> None:
        _user_ops.start_training_mode(self._conn, mode)

    def finish_training(self, process: bool = True) -> None:
        _user_ops.finish_training(self._conn, process)

    # --- Audio Input ---

    def input_from_file(self, path: str, flags: int = 0, playlist: bytes = b"") -> None:
        _speech_ops.input_from_file(self._conn, path, flags, playlist)

    # --- Dictation ---

    def create_dictation(self) -> ComDictObj:
        return _create_dictation(self._conn)
