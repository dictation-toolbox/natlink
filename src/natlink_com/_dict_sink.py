"""Dictation notification sink for Dragon text change callbacks.

Implements two COM interfaces on a single object:
  - IVDct0NotifySinkW: Dictation callbacks (TextChanged, PhraseFinish, etc.)
  - IDgnGetSinkFlags: Tells Dragon which dictation callbacks we want

Created per-DictObj and registered via IVoiceDictation0W::Register.

C++: "When a recognition occurs we usually get either a TextChanged or a
TextSelChanged callback.  Although because of a coding bug (?) we get
both when a \"Scratch That\" command occurs."
-- Joel Gould, DictationObject.cpp (CVDct0NotifySink class comment)
"""

import contextlib
import ctypes
import logging

log = logging.getLogger("natlink.com.sink.dict")
# Per-edit text change events fire on every keystroke-equivalent; route
# them through a child logger so they can be silenced independently.
_text_log = log.getChild("text_changed")

from ._com_helpers import get_dragon_error_message as _get_dragon_error_message
from ._dspeech_constants import (
    DGNDICTSINKFLAG_SENDTEXTCHANGED,
    DGNDICTSINKFLAG_SENDTEXTSELCHANGED,
    DGNDICTSINKFLAG_SENDJITPAUSE,
)

from ._com_helpers import lazy_com_factory


def _build_sink_class():
    """Build the DictSink COMObject class."""
    from comtypes import COMObject
    from ._tlb import get_tlb; tlb = get_tlb()
    IVDct0NotifySinkW = tlb.IVDct0NotifySinkW
    IDgnVDctNotifySink = tlb.IDgnVDctNotifySink
    IDgnGetSinkFlags = tlb.IDgnGetSinkFlags

    class DictSink(COMObject):
        """Per-DictObj notification sink.

        Implements three interfaces (matches C++ CVDct0NotifySink):
          - IVDct0NotifySinkW: standard SAPI dictation callbacks
          - IDgnVDctNotifySink: Dragon-specific (JITPause, etc.)
          - IDgnGetSinkFlags: tells Dragon which callbacks we want
        """
        _com_interfaces_ = [IVDct0NotifySinkW, IDgnVDctNotifySink, IDgnGetSinkFlags]

        def __init__(self, dict_handle, connection=None):
            super().__init__()
            self._dict_handle = dict_handle
            self._text_iface = None  # IVDct0TextW, set after registration
            self._dict_obj = None    # ComDictObj, set after registration
            self._connection = connection

        # --- IDgnGetSinkFlags ---

        def IDgnGetSinkFlags_SinkFlagsGet(self, p0):
            # C++: "Dragon NaturallySpeaking allows sink object to have a
            # separate interface called IDgnGetSinkFlags.  That interface
            # implements a single function which is call by Drgaon
            # NaturallySpeaking when the sink is first registered.
            # if IDgnGetSinkFlags exists, SinkFlagsGet returns a list of
            # the notifications we want.  This interface is optional."
            # — Joel Gould, DictationObject.cpp (CVDct0NotifySink::SinkFlagsGet)
            return (DGNDICTSINKFLAG_SENDTEXTCHANGED |
                    DGNDICTSINKFLAG_SENDTEXTSELCHANGED |
                    DGNDICTSINKFLAG_SENDJITPAUSE)

        # --- IVDct0NotifySinkW ---

        def IVDct0NotifySinkW_Command(self, p0):
            return 0

        def IVDct0NotifySinkW_TextSelChanged(self):
            # C++: "We get this callback if a recognition has caused the
            # selection to change within the internal buffer without a
            # corresponding change in the text."
            # — Joel Gould, DictationObject.cpp (CVDct0NotifySink::TextSelChanged)
            _text_log.debug("TextSelChanged(handle=%d)", self._dict_handle)
            try:
                self._handle_text_sel_changed()
            except Exception:
                log.exception("Error in TextSelChanged handler")
            return 0

        def IVDct0NotifySinkW_TextChanged(self, dwReason):
            # C++: "We get this callback if a recognition has caused the
            # text to change within the internal buffer.  The parameter
            # (a reason code) is not currently used in Dragon
            # NaturallySpeaking and can be ignored."
            # "We ignore the reason code.  It is not set by NatSpeak"
            # — Joel Gould, DictationObject.cpp (CVDct0NotifySink::TextChanged,
            #   CDictationObject::TextChanged)
            _text_log.debug("TextChanged(reason=%d, handle=%d)", dwReason, self._dict_handle)
            try:
                self._handle_text_changed()
            except Exception:
                log.exception("Error in TextChanged handler")
            return 0

        def IVDct0NotifySinkW_TextBookmarkChanged(self, p0):
            return 0

        def IVDct0NotifySinkW_PhraseStart(self):
            return 0

        def IVDct0NotifySinkW_PhraseFinish(self, p0, p1):
            return 0

        def IVDct0NotifySinkW_PhraseHypothesis(self, p0, p1):
            return 0

        def IVDct0NotifySinkW_UtteranceBegin(self):
            return 0

        def IVDct0NotifySinkW_UtteranceEnd(self):
            return 0

        def IVDct0NotifySinkW_VUMeter(self, p0):
            return 0

        def IVDct0NotifySinkW_AttribChanged(self, p0):
            return 0

        def IVDct0NotifySinkW_Interference(self, p0):
            return 0

        def IVDct0NotifySinkW_Training(self, p0):
            return 0

        def IVDct0NotifySinkW_Dictating(self, p0, p1):
            return 0

        def IVDct0NotifySinkW_Reserved15(self, p0):
            return 0

        # --- IDgnVDctNotifySink ---

        def IDgnVDctNotifySink_ErrorHappened(self, p0):
            msg = _get_dragon_error_message(p0)
            if msg:
                log.error("DictSink ErrorHappened: %s", msg)
            else:
                log.error("DictSink ErrorHappened")
            return 0

        def IDgnVDctNotifySink_WarningHappened(self, p0):
            msg = _get_dragon_error_message(p0)
            if msg:
                log.info("DictSink WarningHappened: %s", msg)
            else:
                log.info("DictSink WarningHappened")
            return 0

        def IDgnVDctNotifySink_JITPause(self):
            """Just-in-time pause for dictation.

            C++: "We get this callback when recognition is about to start
            but before the voice dictation object has activated its
            grammars.  This allows us to make sure we are in sync with the
            internal buffer."
            -- Joel Gould, DictationObject.cpp (CVDct0NotifySink::JITPause)
            """
            log.debug("DictSink JITPause(handle=%d)", self._dict_handle)
            try:
                conn = self._connection
                cb = conn.on_dict_begin if conn else None
                if cb:
                    from ._win32 import get_current_module
                    cb(self._dict_handle, get_current_module())
            except Exception:
                log.exception("Error in JITPause handler")
            return 0

        def IDgnVDctNotifySink_HotKeyHappened(self, p0):
            return 0

        # --- Internal dispatch ---

        @contextlib.contextmanager
        def _lock_for_callback(self):
            """Lock the text buffer honoring ComDictObj's lock-count state.

            Prefer the obj's _auto_lock so we don't acquire/release a lock the
            user already holds.  Fall back to a direct lock only if the obj
            reference is missing (it is wired up right after registration).
            """
            dict_obj = getattr(self, "_dict_obj", None)
            if dict_obj is not None:
                with dict_obj._auto_lock():
                    yield
                return
            from ._dict_obj import _acquire_lock
            _acquire_lock(self._text_iface)
            try:
                yield
            finally:
                self._text_iface.UnLock()

        def _handle_text_sel_changed(self):
            """Selection changed without text change: lock, get sel, defer dispatch.

            C++: "compute the python results; note that there is no deleted
            region or changed text"
            -- Joel Gould, DictationObject.cpp (CDictationObject::TextSelChanged)

            C++ uses makeResultsCallback (deferred + pause_recog) for dictation
            text changes.  We match that: extract data on the RPC thread while
            the lock is held, then defer the callback to the main thread.
            """
            conn = self._connection
            cb = conn.on_dict_text_changed if conn else None
            if cb is None:
                return

            text_iface = self._text_iface
            if text_iface is None:
                return

            # Route through the obj's lock accounting so we never UnLock a lock
            # the user still holds (which would desync ComDictObj._lock_count).
            with self._lock_for_callback():
                sel_start, sel_count = text_iface.TextSelGet()
                sel_end = sel_start + sel_count

            # "setting this will delay recognition at the start of the next
            # utterance until results are processed"
            # — Joel Gould, DragonCode.cpp (CDragonCode::makeResultsCallback)
            if conn is not None:
                conn.increment_pause_recog()
                conn.defer_dict_text_changed(
                    self._dict_handle, sel_start, sel_start,
                    "", sel_start, sel_end)

        def _handle_text_changed(self):
            """Process text change: lock, get changes, get text, defer dispatch.

            C++ uses makeResultsCallback (deferred + pause_recog) for dictation
            text changes.  We match that: extract data on the RPC thread while
            the lock is held, then defer the callback to the main thread.
            """
            conn = self._connection
            cb = conn.on_dict_text_changed if conn else None
            if cb is None:
                return

            text_iface = self._text_iface
            if text_iface is None:
                return

            # Route through the obj's lock accounting so we never UnLock a lock
            # the user still holds (which would desync ComDictObj._lock_count).
            with self._lock_for_callback():
                # C++: "Ask NatSpeak for what region of text changed"
                new_start, new_end, old_start, old_end = text_iface.GetChanges()

                new_text = ""
                if new_end > new_start:
                    from ._sdata import sdata_to_bytes
                    sdata = text_iface.TextGet(new_start, new_end - new_start)
                    raw = sdata_to_bytes(sdata)
                    if raw:
                        new_text = raw.decode("utf-16-le").rstrip("\x00")

                sel_start, sel_count = text_iface.TextSelGet()
                sel_end = sel_start + sel_count

            # "setting this will delay recognition at the start of the next
            # utterance until results are processed"
            # — Joel Gould, DragonCode.cpp (CDragonCode::makeResultsCallback)
            if conn is not None:
                conn.increment_pause_recog()
                conn.defer_dict_text_changed(
                    self._dict_handle, old_start, old_end,
                    new_text, sel_start, sel_end)

        def _do_dict_text_changed(self, dict_handle, del_start, del_end,
                                  new_text, sel_start, sel_end):
            """Fire dictation text change callback on the main thread (deferred).

            Matches C++ onSendResults: makeCallback + resetPauseRecog.
            """
            try:
                conn = self._connection
                cb = conn.on_dict_text_changed if conn else None
                if cb:
                    cb(dict_handle, del_start, del_end,
                       new_text, sel_start, sel_end)
            except Exception:
                log.exception("Error in deferred dictation text change")
            finally:
                conn = self._connection
                if conn is not None:
                    conn.reset_pause_recog()

    return DictSink


create_dict_sink = lazy_com_factory(_build_sink_class)
