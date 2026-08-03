"""natlink compatibility adapter — re-exports the full API.

Pure-Python package that wraps natlink_com to provide the exact
original natlink C extension API surface.  Install as ``natlink``
so existing grammars and natlinkcore work unchanged.

Exports:
  - 38 module-level functions
  - 3 classes: GramObj, ResObj, DictObj
  - 13 exceptions: NatError + 12 subclasses
"""

from ._lifecycle import natConnect, natDisconnect, isNatSpeakRunning, waitForSpeech
from ._callbacks import setBeginCallback, setChangeCallback, setTimerCallback
from ._ui_protocol import (UIProvider, NatlinkState,
    PHASE_IDLE, PHASE_WAITING_FOR_DRAGON, PHASE_CONNECTING,
    PHASE_LOADING_PROFILE, PHASE_CONNECTED, PHASE_RESTARTING,
    PHASE_INACTIVE, PHASE_ERROR)
from ._actions import (
    is_dragon_running, start_dragon, stop_dragon, restart_dragon, dragon_status,
    reload_grammars, toggle_loader, get_loader_states,
    toggle_auto_launch, is_auto_launch_enabled,
    set_mic, exit_natlink, set_inactive,
    stop_provider,
)
from ._logging_control import (
    list_log_categories, get_log_category,
    set_log_level, reset_log_level, reset_log_levels,
    list_log_presets, apply_log_preset,
)
from ._speech import playString, playEvents, execScript, recognitionMimic
from ._ui_protocol import notify_text
from ._legacy import setMessageWindow, setTrayIcon, displayText
from ._system import (getClipboard, getCursorPos, getScreenSize, getCurrentModule,
                      getCurrentUser, getMicState, setMicState, inputFromFile, getCallbackDepth)
from ._users import (getAllUsers, createUser, openUser, saveUser, getUserTraining, getTrainingMode, startTraining, finishTraining)
from ._vocabulary import (
    getWordInfo, addWord, deleteWord, setWordInfo, getWordProns,
    enumerateWords, enumeratePrefixWords, getWordFromPrefix, getWordFromPron,
)
from ._logging_setup import ensure_natlinkcore_logging
from ._loader_protocol import LoaderProtocol, is_loader

def set_ui_provider(provider) -> None:
    """Register or replace the active UI provider."""
    from ._state import _state
    if not isinstance(provider, UIProvider):
        raise TypeError(f"provider must implement UIProvider protocol, got {type(provider)}")
    previous = _state.ui_provider
    _state.ui_provider = provider
    if previous is not None and previous is not provider:
        try:
            stop_provider(previous)
        except Exception:
            pass


def clear_ui_provider() -> None:
    """Unregister and stop the active UI provider, if any."""
    from ._state import _state
    provider = _state.ui_provider
    _state.ui_provider = None
    if provider is not None:
        try:
            stop_provider(provider)
        except Exception:
            pass


def get_ui_provider():
    """Get the active UIProvider, or None."""
    from ._state import _state
    return _state.ui_provider


def is_configured() -> bool:
    """Check if natlink.ini exists (Dragon detected, config written)."""
    from natlink_com._config import _CONFIG_FILE
    return _CONFIG_FILE.is_file()


def get_config_dir():
    """Return the directory containing natlink.ini."""
    from natlink_com._config import _CONFIG_DIR
    return _CONFIG_DIR


def configure():
    """Detect Dragon and write natlink.ini. Returns the ConfigParser."""
    from natlink_com._config import setup_config
    return setup_config()


def configure_runtime():
    """Detect Dragon and write natlink.ini. Returns the ConfigParser."""
    return configure()


def get_config_path():
    """Return the path to natlink.ini."""
    from natlink_com._config import get_config_path as _get
    return _get()


def load_config():
    """Load natlink.ini (read-only). Returns ConfigParser."""
    from natlink_com._config import load_config as _load
    return _load()


def get_log_path():
    """Return the path to the natlink log file."""
    from ._logging_setup import _resolve_log_path
    return _resolve_log_path()


def remove_runtime_config() -> None:
    """Remove natlink.ini if it exists."""
    get_config_path().unlink(missing_ok=True)


def get_dragon_log_dir():
    """Return the most relevant Dragon log directory, or None."""
    import os

    from natlink_com._launcher import dragon_log_dir, find_dragon_log

    cfg = load_config()
    version = cfg.get("dragon", "version", fallback="16")
    base = dragon_log_dir(version)
    if not base.is_dir():
        return None
    # Newest, not first: directory order puts the install-time SYSTEM log
    # ahead of the live profile one, so opening "the Dragon log" handed the
    # user a file that had not changed since installation.
    newest = find_dragon_log(version)
    return newest.parent if newest else base


def get_programdata_dir():
    """Return PROGRAMDATA as a Path."""
    import os
    from pathlib import Path

    return Path(os.environ.get("PROGRAMDATA", ""))


def run():
    """Run the headless launcher (pump loop + UI provider discovery)."""
    from ._launcher import run as _run
    _run()


from ._loaders import (add_loader, remove_loader, reload_loader,
                       get_loaders, get_running_loaders,
                       get_grammars_for, get_dictation_objects_for,
                       release_objects_for)
# Re-exports of natlink_com seams so the UI imports through the compat layer
# rather than reaching into natlink_com directly (preserves the layer boundary).
from natlink_com import (
    msgbox, MB_ICONERROR, MB_ICONWARNING, MB_ICONQUESTION, MB_YESNO, IDYES, IDNO,
    IniFile, print_config, request_shutdown,
)
from ._gram_obj import GramObj
from ._res_obj import ResObj
from ._dict_obj import DictObj
from ._exceptions import (
    NatError,
    InvalidWord,
    UnknownName,
    OutOfRange,
    MimicFailed,
    BadGrammar,
    WrongState,
    BadWindow,
    SyntaxError,
    UserExists,
    ValueError,
    DataMissing,
    WrongType,
)

__all__ = [
    # Functions
    "natConnect", "natDisconnect", "isNatSpeakRunning",
    "waitForSpeech",
    "setBeginCallback", "setChangeCallback", "setTimerCallback",
    "set_ui_provider", "clear_ui_provider", "get_ui_provider",
    "is_configured", "get_config_dir", "get_config_path", "get_log_path",
    "load_config", "configure", "configure_runtime", "remove_runtime_config",
    "get_dragon_log_dir", "get_programdata_dir", "run",
    "UIProvider", "NatlinkState",
    # Actions
    "is_dragon_running", "start_dragon", "stop_dragon", "restart_dragon",
    "reload_grammars", "toggle_loader", "get_loader_states",
    "toggle_auto_launch", "is_auto_launch_enabled",
    "list_log_categories", "get_log_category",
    "set_log_level", "reset_log_level", "reset_log_levels",
    "list_log_presets", "apply_log_preset",
    "set_mic", "exit_natlink", "set_inactive",
    "PHASE_IDLE", "PHASE_WAITING_FOR_DRAGON", "PHASE_CONNECTING",
    "PHASE_LOADING_PROFILE", "PHASE_CONNECTED", "PHASE_RESTARTING",
    "PHASE_INACTIVE", "PHASE_ERROR",
    "playString", "playEvents", "execScript",
    "recognitionMimic", "notify_text", "displayText",
    # Legacy shims — must be in __all__ or `import natlink` cannot
    # reach them and _legacy.py fails at the one job it has.
    "setMessageWindow", "setTrayIcon",
    "dragon_status", "stop_provider",
    "getClipboard", "getCursorPos", "getScreenSize",
    "getCurrentModule", "getCurrentUser",
    "getMicState", "setMicState",
    "inputFromFile", "getCallbackDepth",
    "getAllUsers", "createUser", "openUser", "saveUser",
    "getUserTraining", "getTrainingMode", "startTraining", "finishTraining",
    "getWordInfo", "addWord", "deleteWord", "setWordInfo", "getWordProns",
    "enumerateWords", "enumeratePrefixWords", "getWordFromPrefix", "getWordFromPron",
    "ensure_natlinkcore_logging",
    # Loader management
    "LoaderProtocol", "is_loader", "add_loader", "remove_loader",
    "reload_loader", "get_loaders", "get_running_loaders",
    "get_grammars_for", "get_dictation_objects_for",
    "release_objects_for",
    # natlink_com seams re-exported for the UI layer
    "msgbox", "MB_ICONERROR", "MB_ICONWARNING", "MB_ICONQUESTION", "MB_YESNO",
    "IDYES", "IDNO", "IniFile", "print_config", "request_shutdown",
    # Classes
    "GramObj", "ResObj", "DictObj",
    # Exceptions
    "NatError", "InvalidWord", "UnknownName", "OutOfRange",
    "MimicFailed", "BadGrammar", "WrongState", "BadWindow",
    "SyntaxError", "UserExists", "ValueError", "DataMissing", "WrongType",
]
