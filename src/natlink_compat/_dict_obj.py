"""_dict_obj.py - DictObj: Dragon voice dictation interface.

Note: DictObj uses lowercase b in Callback (setBeginCallback etc.),
unlike GramObj which uses capital B (setBeginCallBack).
"""

import logging
from typing import Callable, List, Optional, Tuple

from natlink_com import ComDictObj as _ComDictObj

from ._state import _state
from ._exceptions import com_call as _com_call

log = logging.getLogger("natlink.compat")


class DictObj:
    """Dictation object — wraps Dragon's voice dictation COM interface."""

    def __init__(self):
        self._com_dict: Optional[_ComDictObj] = None
        self._begin_callback: Optional[Callable] = None
        self._change_callback: Optional[Callable] = None

    def _ensure_created(self):
        """Lazy-create the dictation object on first use."""
        with _state.lock:
            if self._com_dict is not None:
                return
            backend = _state.backend
            if backend is None:
                from ._exceptions import WrongState
                raise WrongState("natlink is not connected")
            self._com_dict = _com_call("DictObj.create", backend.create_dictation)
            from ._callbacks import current_owner_package
            self._owner_pkg = current_owner_package()
            _state.dict_registry[self._com_dict.handle] = self

    def activate(self, window: int) -> None:
        """Activate dictation for the given window."""
        self._ensure_created()
        _com_call("DictObj.activate", self._com_dict.activate, window_handle=window)

    def deactivate(self) -> None:
        """Deactivate dictation."""
        if self._com_dict is None:
            return
        _com_call("DictObj.deactivate", self._com_dict.deactivate)

    def setBeginCallback(self, callback: Optional[Callable]) -> None:
        """Set the begin callback (note: lowercase b)."""
        if callback is not None and not callable(callback):
            raise TypeError("parameter must be callable")
        self._begin_callback = callback

    def setChangeCallback(self, callback: Optional[Callable]) -> None:
        """Set the change callback (note: lowercase b)."""
        if callback is not None and not callable(callback):
            raise TypeError("parameter must be callable")
        self._change_callback = callback

    def setLock(self, state: int) -> None:
        """Lock or unlock the dictation text buffer."""
        self._ensure_created()
        _com_call("DictObj.setLock", self._com_dict.set_lock, bool(state))

    def getLength(self) -> int:
        """Get the length of the dictation text."""
        self._ensure_created()
        return _com_call("DictObj.getLength", self._com_dict.get_length)

    def setText(self, text: str, start: int, end: int = 0x7FFFFFFF) -> None:
        """Set text in the dictation buffer."""
        self._ensure_created()
        _com_call("DictObj.setText", self._com_dict.set_text, text, start, end)

    def getText(self, start: int, end: int = 0x7FFFFFFF) -> str:
        """Get text from the dictation buffer."""
        self._ensure_created()
        return _com_call("DictObj.getText", self._com_dict.get_text, start, end)

    def setTextSel(self, start: int, end: int = 0x7FFFFFFF) -> None:
        """Set text selection range."""
        self._ensure_created()
        _com_call("DictObj.setTextSel", self._com_dict.set_text_sel, start, end)

    def getTextSel(self) -> Tuple[int, int]:
        """Get text selection range."""
        self._ensure_created()
        return _com_call("DictObj.getTextSel", self._com_dict.get_text_sel)

    def moveText(self, start: int, end: int, dest: int, flags: int = 0) -> None:
        """Move text within the dictation buffer."""
        self._ensure_created()
        _com_call("DictObj.moveText", self._com_dict.move_text, start, end, dest, flags)

    def removeText(self, start: int, end: int, flags: int = 0) -> None:
        """Remove text from the dictation buffer."""
        self._ensure_created()
        _com_call("DictObj.removeText", self._com_dict.remove_text, start, end, flags)

    def hintText(self, text: str) -> None:
        """Provide dictation hint text."""
        self._ensure_created()
        _com_call("DictObj.hintText", self._com_dict.hint_text, text)

    def setWords(self, text: str) -> None:
        """Set the dictation word sequence."""
        self._ensure_created()
        _com_call("DictObj.setWords", self._com_dict.set_words, text)

    def setAutoLock(self, state: int) -> None:
        """Set dictation autolock mode."""
        self._ensure_created()
        _com_call("DictObj.setAutoLock", self._com_dict.set_auto_lock, bool(state))

    def getAutoLock(self) -> bool:
        """Get dictation autolock mode."""
        self._ensure_created()
        return _com_call("DictObj.getAutoLock", self._com_dict.get_auto_lock)

    def addBookmark(self, bookmarkId: int, position: int) -> None:
        """Add a dictation bookmark."""
        self._ensure_created()
        _com_call("DictObj.addBookmark",
                  self._com_dict.add_bookmark, bookmarkId, position)

    def removeBookmark(self, bookmarkId: int) -> None:
        """Remove a dictation bookmark by id."""
        self._ensure_created()
        _com_call("DictObj.removeBookmark",
                  self._com_dict.remove_bookmark, bookmarkId)

    def moveBookmark(self, bookmarkId: int, position: int) -> None:
        """Move a dictation bookmark."""
        self._ensure_created()
        _com_call("DictObj.moveBookmark",
                  self._com_dict.move_bookmark, bookmarkId, position)

    def queryBookmark(self, bookmarkId: int) -> Tuple[int, int]:
        """Fetch a bookmark as `(id, position)`."""
        self._ensure_created()
        return _com_call("DictObj.queryBookmark",
                         self._com_dict.query_bookmark, bookmarkId)

    def enumBookmarks(self, startId: int = 0,
                      count: int = 0x7FFFFFFF) -> List[Tuple[int, int]]:
        """Enumerate bookmarks as `(id, position)` tuples."""
        self._ensure_created()
        return _com_call("DictObj.enumBookmarks",
                         self._com_dict.enum_bookmarks, startId, count)

    def getResultsObject(self, startId: int = 0, count: int = 1):
        """Fetch dictation results as `(actualStart, actualCount, ResObj|None)`."""
        self._ensure_created()
        actual_start, actual_count, res_obj = _com_call(
            "DictObj.getResultsObject",
            self._com_dict.get_results_object,
            startId, count,
        )
        if res_obj is None:
            return (actual_start, actual_count, None)
        from ._res_obj import ResObj
        return (actual_start, actual_count, ResObj(res_obj))

    def setVisibleText(self, start: int, end: int = 0x7FFFFFFF) -> None:
        """Set visible text range."""
        self._ensure_created()
        _com_call(
            "DictObj.setVisibleText", self._com_dict.set_visible_text, start, end)

    def getVisibleText(self) -> Tuple[int, int]:
        """Get visible text range."""
        self._ensure_created()
        return _com_call("DictObj.getVisibleText", self._com_dict.get_visible_text)

    def getThat(self) -> Tuple[int, int]:
        """Get Dragon's current correction target range."""
        self._ensure_created()
        return _com_call("DictObj.getThat", self._com_dict.get_that)

    def correctionDialog(self, useDefault: int = 1, flags: int = 0) -> None:
        """Open Dragon's correction dialog."""
        self._ensure_created()
        _com_call("DictObj.correctionDialog",
                  self._com_dict.correction_dialog, bool(useDefault), flags)

    def recentBufferCommit(self) -> None:
        """Commit the recent dictation buffer."""
        self._ensure_created()
        _com_call("DictObj.recentBufferCommit", self._com_dict.recent_buffer_commit)

    def destroy(self):
        """Clean up the dictation object.

        Order matches C++ ``CDictationObject::destroy``: Release the COM
        pointer first, null it out, then remove from the registry.
        Raises on COM failure; ``__del__`` catches separately so
        finalization never propagates out.
        """
        if self._com_dict is not None:
            handle = self._com_dict.handle
            log.debug("Destroying dictation object (handle=%d)", handle)
            conn = _state.backend.conn if _state.backend else None
            _com_call("DictObj.destroy", self._com_dict.destroy, conn)
            self._com_dict = None
            with _state.lock:
                _state.dict_registry.pop(handle, None)
        self._begin_callback = None
        self._change_callback = None

    def __del__(self):
        if self._com_dict is not None:
            try:
                self.destroy()
            except Exception:
                log.debug("Dictation cleanup in __del__ failed", exc_info=True)
