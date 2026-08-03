"""_state.py - Global singleton holding natlink session state.

All mutable state lives here so that __init__.py functions and
wrapper objects share a single source of truth.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, List, Optional, TYPE_CHECKING
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from natlink_com import NatlinkCOM

log = logging.getLogger("natlink.compat")

# Inline to avoid circular import with _ui_protocol
_PHASE_IDLE = "idle"


class _NatlinkState:
    """Singleton that holds the COM backend and all registries."""

    def __init__(self):
        self.backend: Optional[NatlinkCOM] = None

        # Active loaders (multiple allowed; managed by _loaders.py)
        self.loader_registry: List = []  # List[_LoaderEntry]

        # Active UI provider (default tray/window shell or a replacement)
        self.ui_provider: Optional[object] = None
        self.phase: str = _PHASE_IDLE
        self.error_message: str = ""

        # Cached state for UI snapshots (avoids COM calls during callbacks)
        self.last_mic_state: str = ""
        self.last_user_name: str = ""
        self.last_user_dir: str = ""

        # Global callback stacks — multiple loaders can each register one.
        # Entries are _callbacks._CB records (fn + owning loader); kept as
        # ordered lists so dispatch fires in registration order.
        self.begin_callbacks: list = []
        self.change_callbacks: list = []
        self.timer_callbacks: list = []
        # Loader currently being started/stopped (set via
        # _callbacks.loader_registration). Callbacks registered while this is
        # set are tagged with that loader for precise per-loader teardown.
        self.registering_loader = None
        # Handle -> wrapper registries (populated by GramObj.load / DictObj).
        # These must not own object lifetime: the original C++ kept raw
        # pointers in linked lists, while Python refcount/dealloc triggered
        # GramObj/DictObj cleanup.
        self.grammar_registry: WeakValueDictionary[int, object] = WeakValueDictionary()
        self.dict_registry: WeakValueDictionary[int, object] = WeakValueDictionary()

        # Callback depth tracking (for getCallbackDepth() API)
        self.callback_depth = 0

        self.during_init: bool = False
        self.during_paused: bool = False
        self._pending_speaker = None      # (user, directory) or None
        self._pending_micstate = None     # mic_state string or None

        # Slow callback warning threshold (ms, 0=disabled)
        self.slow_callback_ms: int = 500

        # Win32 manual-reset event: signaled when natDisconnect starts so
        # waitForSpeech (legacy path) can wake via MsgWaitForMultipleObjects
        # instead of polling.
        from natlink_com._win32 import kernel32
        self._disconnect_event_handle: int = kernel32.CreateEventW(None, True, False, None)

        # Connection mutex handle (Win32)
        self._conn_mutex = None

        # True when the launcher owns the process + the shared connection
        # (issue #228). Gates re-entrant natConnect/natDisconnect from loaders
        # into no-ops. Process-scoped — NOT cleared by reset().
        self.launcher_active = False

        # Cached (name, enabled, running) loader tuples for UI menus/snapshots.
        # None = stale; recomputed by _actions.get_loader_states(). Owned here
        # so reset() can clear it directly without importing _actions
        # (avoids the compat -> actions -> state cycle).
        self.loader_states_cache = None
        self.loader_cache_lock = threading.Lock()

        self.lock = threading.Lock()

    @property
    def connected(self) -> bool:
        """Derived from backend — no separate flag to get out of sync."""
        return self.backend is not None

    @property
    def conn(self):
        """Current COM connection, or None. Thread-safe."""
        with self.lock:
            backend = self.backend
        return backend.conn if backend and backend.conn else None

    def cache_user_state(self, mic: str, user: str, user_dir: str):
        """Cache mic/user state for UI snapshots."""
        self.last_mic_state = mic
        self.last_user_name = user
        self.last_user_dir = user_dir

    def reset(self):
        """Clear all state (called on natDisconnect)."""
        log.info("Connection state: disconnected (reset)")
        self.backend = None
        self.begin_callbacks.clear()
        self.change_callbacks.clear()
        self.timer_callbacks.clear()
        self.grammar_registry.clear()
        self.dict_registry.clear()
        self.callback_depth = 0
        self.during_init = False
        self.during_paused = False
        self._pending_speaker = None
        self._pending_micstate = None
        self.slow_callback_ms = 500
        from natlink_com._win32 import kernel32
        kernel32.ResetEvent(self._disconnect_event_handle)
        self.phase = _PHASE_IDLE
        self.error_message = ""
        self.last_mic_state = ""
        self.last_user_name = ""
        self.last_user_dir = ""
        with self.loader_cache_lock:
            self.loader_states_cache = None
        if self._conn_mutex:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(self._conn_mutex)
            self._conn_mutex = None


# Module-level singleton
_state = _NatlinkState()
