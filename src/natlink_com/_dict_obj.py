"""ComDictObj — wraps IVoiceDictation0W + IVDct0TextW + IDgnVDctTextW.

Provides the DictObj interface that natlink_compat wraps to present
the original natlink C extension API.
"""

import contextlib
import ctypes
import logging
import time
from typing import List, Tuple

from ._com_helpers import (cotaskmem_free, next_object_handle,
                           release_raw, wrap_comtypes)
from ._errors import NatlinkCOMError, ERR_BAD_WINDOW, ERR_WRONG_STATE
from ._sdata import sdata_to_bytes

log = logging.getLogger("natlink.com.dictation")

# E_PENDING — Lock() returns this when another thread holds the lock
E_PENDING = -2147483638  # 0x8000000A signed


class _VDCTBOOKMARK(ctypes.Structure):
    _fields_ = [
        ("dwID", ctypes.c_ulong),
        ("dwPosn", ctypes.c_ulong),
    ]


class ComDictObj:
    """Wraps a Dragon dictation object.

    Lifecycle:
      1. NatlinkCOM.create_dictation() builds this with pre-registered interfaces
      2. User calls activate(hwnd) to bind to a window
      3. Text manipulation via set_text/get_text/etc. (auto-locks if needed)
      4. User calls deactivate() then destroy()
    """

    def __init__(self, voice_dict, text_iface, dgn_text, sink,
                 tlb=None, connection=None):
        """
        Args:
            voice_dict: comtypes IVoiceDictation0W pointer.
            text_iface: comtypes IVDct0TextW pointer.
            dgn_text: comtypes IDgnVDctTextW pointer (or None).
            sink: DictSink COMObject (prevent GC).
        """
        self._handle = next_object_handle()
        self._voice_dict = voice_dict
        self._text = text_iface
        self._dgn_text = dgn_text
        self._sink = sink
        self._tlb = tlb
        self._connection = connection
        self._lock_count = 0
        self._BM = tlb.VDCTBOOKMARK if tlb else _VDCTBOOKMARK

    @contextlib.contextmanager
    def _auto_lock(self):
        """Acquire the text buffer lock if not already held by the user.

        C++: "This utility class will make sure that the text object is
        locked when we access it.  When created, this object calls Lock
        but only if we know that we are not locked.  Then when this object
        is deleted because it goes out of scope, the lock is released."
        — Joel Gould, DictationObject.cpp (CGrabLock class comment)

        Per-method comment: "if the Python program did not lock the buffer
        then we gran the lock for the duration of this routine"
        [sic — "gran" for "grab"]
        """
        need_lock = self._lock_count == 0
        if need_lock:
            _acquire_lock(self._text)
        try:
            yield
        finally:
            if need_lock:
                self._text.UnLock()

    @property
    def handle(self):
        return self._handle

    def _mustbe_usable(self, func):
        """C++ MUSTBEUSABLE macro — check dictation object is still usable."""
        if self._voice_dict is None:
            raise NatlinkCOMError(func,
                error_message=f"This dictation object is no longer usable "
                              f"(calling {func})")

    def activate(self, window_handle=0):
        """Activate dictation for a window.

        Matches C++ CDictationObject::activate:
          MUSTBEUSABLE + IsWindow check + IVoiceDictation0::Activate(hWnd)
        """
        self._mustbe_usable("activate")
        if window_handle and not ctypes.windll.user32.IsWindow(window_handle):
            # C++: errBadWindow, "The handle %d does not refer to an existing window"
            raise NatlinkCOMError("activate", error_type=ERR_BAD_WINDOW,
                error_message=f"The handle {window_handle} does not refer "
                              f"to an existing window")
        self._voice_dict.Activate(window_handle)
        log.debug("Dictation activated (hwnd=%d)", window_handle)

    def deactivate(self):
        """Deactivate dictation.

        Matches C++ CDictationObject::deactivate:
          MUSTBEUSABLE + IVoiceDictation0::Deactivate()
        """
        self._mustbe_usable("deactivate")
        self._voice_dict.Deactivate()
        log.debug("Dictation deactivated")

    def set_lock(self, state):
        """Lock or unlock the text buffer.

        Matches C++ CDictationObject::setLock:
          MUSTBEUSABLE + Lock()/UnLock() with E_PENDING retry.
          errWrongState if unlock when not locked.
        """
        self._mustbe_usable("setLock")
        if self._text is None:
            raise NatlinkCOMError("set_lock",
                error_message="This dictation object is no longer usable "
                              "(calling setLock)")
        if state:
            _acquire_lock(self._text)
            self._lock_count += 1
        else:
            if self._lock_count <= 0:
                # C++: errWrongState, "The dictation object was not locked"
                raise NatlinkCOMError("set_lock", error_type=ERR_WRONG_STATE,
                    error_message="The dictation object was not locked")
            self._text.UnLock()
            self._lock_count -= 1

    def _compute_length(self):
        """Compute text buffer length.

        C++: "There is no call in NatSpeak to get the length of the
        internal buffer.  To compute the length, we get all the text in
        the window and measure its length.  Ugly and slow."
        "This function can only be called when a lock is in effect."
        — Joel Gould, DictationObject.cpp (computeLength)

        C++: "as an optimization, we do not have to get all the text,
        just from the end of the selection"
        """
        sel_start, sel_count = self._text.TextSelGet()
        end_pos = sel_start + sel_count
        sdata = self._text.TextGet(end_pos, 0x7FFFFFFF)
        raw = sdata_to_bytes(sdata)
        remaining = len(raw.decode("utf-16-le").rstrip("\x00")) if raw else 0
        return end_pos + remaining

    def _compute_range(self, start, end):
        """Convert natlink (start, end) to COM (start, count).

        C++: "This function converts a Python nStart,nEnd pair into a
        nStart,nCount pair.  In general we are very forgiving of the Python
        input mimicing the behavior of the slicing operation."
        — Joel Gould, DictationObject.cpp (computeRange)

        - Negative start/end -> offset from buffer length (Python slice semantics)
        - end < start -> count = 0
        - 0x7FFFFFFF end -> 0x7FFFFFFF count (to end of buffer)

        Must be called while locked (computeLength needs TextSelGet).
        """
        if end == 0x7FFFFFFF:
            # Large sentinel: C++ computes count = end - start normally
            if start < 0:
                length = self._compute_length()
                start = length + start
            return start, 0x7FFFFFFF - start

        length = -1  # lazy compute, matching C++

        if start < 0:
            length = self._compute_length()
            start = length + start

        if end < 0:
            if length == -1:
                length = self._compute_length()
            end = length + end

        if end < start:
            count = 0
        else:
            count = end - start

        return start, count

    def get_length(self):
        """Get text buffer length.

        No direct API — uses TextSelGet + TextGet trick from C++ original:
        get selection position, then count chars from there to end.
        """
        self._mustbe_usable("getLength")
        with self._auto_lock():
            return self._compute_length()

    def set_text(self, text, start, end):
        """Replace text in the buffer.

        IVDct0TextW::TextSet(start, count, text, reason=0).
        Natlink convention uses (start, end); COM API uses (start, count).
        Supports negative indices (offset from end), matching C++ computeRange.
        """
        self._mustbe_usable("setText")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            self._text.TextSet(start, count, text, 0)

    def get_text(self, start, end):
        """Get text from the buffer.

        IVDct0TextW::TextGet(start, length) -> SDATA.
        C++: "we sometimes return NULL when we mean an empty string"
        — Joel Gould, DictationObject.cpp (getText)
        Supports negative indices (offset from end), matching C++ computeRange.
        """
        self._mustbe_usable("getText")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            if count == 0:
                return ""
            sdata = self._text.TextGet(start, count)
            raw = sdata_to_bytes(sdata)
            return raw.decode("utf-16-le").rstrip("\x00") if raw else ""

    def set_text_sel(self, start, end):
        """Set text selection / cursor position.

        IVDct0TextW::TextSelSet(start, count).
        Lock required for cross-process; conditional on user lock state.
        Supports negative indices (offset from end), matching C++ computeRange.
        """
        self._mustbe_usable("setTextSel")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            self._text.TextSelSet(start, count)

    def get_text_sel(self):
        """Get text selection range.

        IVDct0TextW::TextSelGet() -> (start, count).
        C++: "convert start,count into start,end"
        — Joel Gould, DictationObject.cpp (getTextSel)
        Lock required for cross-process; conditional on user lock state.
        """
        self._mustbe_usable("getTextSel")
        with self._auto_lock():
            sel_start, sel_count = self._text.TextSelGet()
            return (sel_start, sel_start + sel_count)

    def move_text(self, start, end, dest, flags=0):
        """Move a text range within the dictation buffer."""
        self._mustbe_usable("moveText")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            self._text.TextMove(start, count, dest, flags)

    def remove_text(self, start, end, flags=0):
        """Remove a text range from the dictation buffer."""
        self._mustbe_usable("removeText")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            self._text.TextRemove(start, count, flags)

    def hint_text(self, text):
        """Provide dictation hint text."""
        self._mustbe_usable("hintText")
        with self._auto_lock():
            self._text.Hint(text)

    def set_words(self, text):
        """Set the dictation word sequence."""
        self._mustbe_usable("setWords")
        with self._auto_lock():
            self._text.Words(text)

    def set_auto_lock(self, state):
        """Set Dragon's dictation autolock mode."""
        self._mustbe_usable("setAutoLock")
        self._text.AutoLockSet(bool(state))

    def get_auto_lock(self):
        """Get Dragon's dictation autolock mode."""
        self._mustbe_usable("getAutoLock")
        return bool(self._text.AutoLockGet())

    def add_bookmark(self, bookmark_id, position):
        """Add a dictation bookmark."""
        self._mustbe_usable("addBookmark")
        with self._auto_lock():
            bookmark = self._BM(int(bookmark_id), int(position))
            hr = getattr(self._text, "_IVDct0TextW__com_BookmarkAdd")(
                ctypes.byref(bookmark))
            if hr < 0:
                raise NatlinkCOMError("IVDct0TextW::BookmarkAdd", hr=hr)

    def remove_bookmark(self, bookmark_id):
        """Remove a dictation bookmark by id."""
        self._mustbe_usable("removeBookmark")
        with self._auto_lock():
            self._text.BookmarkRemove(int(bookmark_id))

    def move_bookmark(self, bookmark_id, position):
        """Move a dictation bookmark to a new text position."""
        self._mustbe_usable("moveBookmark")
        with self._auto_lock():
            self._text.BookmarkMove(int(bookmark_id), int(position))

    def query_bookmark(self, bookmark_id):
        """Fetch a dictation bookmark as `(id, position)`."""
        self._mustbe_usable("queryBookmark")
        with self._auto_lock():
            bookmark = self._BM()
            hr = getattr(self._text, "_IVDct0TextW__com_BookmarkQuery")(
                int(bookmark_id), ctypes.byref(bookmark))
            if hr < 0:
                raise NatlinkCOMError("IVDct0TextW::BookmarkQuery", hr=hr)
            return (int(bookmark.dwID), int(bookmark.dwPosn))

    def enum_bookmarks(self, start_id=0, count=0x7FFFFFFF) -> List[Tuple[int, int]]:
        """Enumerate dictation bookmarks as `(id, position)` tuples."""
        self._mustbe_usable("enumBookmarks")
        with self._auto_lock():
            bookmark_ptr = ctypes.POINTER(self._BM)()
            actual = ctypes.c_ulong(0)
            hr = getattr(self._text, "_IVDct0TextW__com_BookmarkEnum")(
                int(start_id), int(count),
                ctypes.byref(bookmark_ptr), ctypes.byref(actual))
            if hr < 0:
                raise NatlinkCOMError("IVDct0TextW::BookmarkEnum", hr=hr)
            if not bookmark_ptr or actual.value == 0:
                return []
            try:
                return [
                    (int(bookmark_ptr[i].dwID), int(bookmark_ptr[i].dwPosn))
                    for i in range(actual.value)
                ]
            finally:
                cotaskmem_free(bookmark_ptr)

    def get_results_object(self, start_id=0, count=1):
        """Fetch dictation results as `(actual_start, actual_count, ComResObj)`."""
        self._mustbe_usable("getResultsObject")
        with self._auto_lock():
            actual_start = ctypes.c_ulong(0)
            actual_count = ctypes.c_ulong(0)
            result_unknown = ctypes.c_void_p()
            hr = getattr(self._text, "_IVDct0TextW__com_ResultsGet")(
                int(start_id), int(count),
                ctypes.byref(actual_start),
                ctypes.byref(actual_count),
                ctypes.byref(result_unknown))
            if hr < 0:
                raise NatlinkCOMError("IVDct0TextW::ResultsGet", hr=hr)
            if not result_unknown.value:
                return (int(actual_start.value), int(actual_count.value), None)
            import comtypes
            from ._res_obj import ComResObj

            wrapped = wrap_comtypes(result_unknown.value, comtypes.IUnknown)
            release_raw(result_unknown.value)
            return (
                int(actual_start.value),
                int(actual_count.value),
                ComResObj(wrapped, tlb=self._tlb, connection=self._connection),
            )

    def _require_dgn_text(self, caller):
        """Guard for methods requiring IDgnVDctTextW."""
        self._mustbe_usable(caller)
        if self._dgn_text is None:
            raise NatlinkCOMError(caller,
                                  error_message="No IDgnVDctTextW interface")

    def set_visible_text(self, start, end):
        """Set the visible text range.

        C++: "This is a Dragon specific function so we use a different
        interface" — Joel Gould, DictationObject.cpp (setVisibleText)
        IDgnVDctTextW::VisibleTextSet(start, count).
        Lock via IVDct0TextW required for cross-process.
        Supports negative indices (offset from end), matching C++ computeRange.
        """
        self._require_dgn_text("setVisibleText")
        with self._auto_lock():
            start, count = self._compute_range(start, end)
            self._dgn_text.VisibleTextSet(start, count)

    def get_visible_text(self):
        """Get the visible text range.

        IDgnVDctTextW::VisibleTextGet() -> (start, count).
        C++: "convert start,count into start,end"
        — Joel Gould, DictationObject.cpp (getVisibleText)
        Lock via IVDct0TextW required for cross-process.
        """
        self._require_dgn_text("getVisibleText")
        with self._auto_lock():
            start, count = self._dgn_text.VisibleTextGet()
            return (start, start + count)

    def get_that(self):
        """Get Dragon's current correction target range."""
        self._require_dgn_text("getThat")
        with self._auto_lock():
            start, count = self._dgn_text.ThatGet()
            return (start, start + count)

    def correction_dialog(self, use_default=True, flags=0):
        """Open Dragon's correction dialog for the current dictation context."""
        self._require_dgn_text("correctionDialog")
        with self._auto_lock():
            self._dgn_text.CorrectionDialog(bool(use_default), flags)

    def recent_buffer_commit(self):
        """Commit the recent Dragon dictation buffer."""
        self._require_dgn_text("recentBufferCommit")
        with self._auto_lock():
            self._dgn_text.RecentBufferCommit()

    def destroy(self, connection=None):
        """Release all COM references."""
        from ._com_helpers import force_release
        if connection is not None:
            connection.unregister_dict_sink(self._handle)
        if self._voice_dict is not None:
            try:
                self._voice_dict.Deactivate()
            except Exception:
                pass
        self._sink = None
        try:
            force_release(self._dgn_text)
            force_release(self._text)
            force_release(self._voice_dict)
        finally:
            self._dgn_text = None
            self._text = None
            self._voice_dict = None
            self._lock_count = 0
        log.debug("Dictation object destroyed (handle=%d)", self._handle)


def create_dictation(conn):
    """Create a dictation object.

    1. QueryService(DgnVDct) -> IVoiceDictation0W
    2. Create DictSink (IVDct0NotifySinkW + IDgnGetSinkFlags)
    3. IVoiceDictation0W::Register(sink)
    4. QI for IVDct0TextW, IDgnVDctTextW
    5. Return ComDictObj wrapping everything
    """
    from ._dict_sink import create_dict_sink

    tlb = conn.tlb
    if tlb is None:
        raise NatlinkCOMError("create_dictation", error_message="Not connected")

    voice_dict = conn.create_voice_dict()
    sink = create_dict_sink(0, connection=conn)

    iid = tlb.IVDct0NotifySinkW._iid_
    voice_dict.Register("NatLink", "", None, "", sink, iid, 0)

    text_iface = voice_dict.QueryInterface(tlb.IVDct0TextW)

    dgn_text = None
    try:
        dgn_text = voice_dict.QueryInterface(tlb.IDgnVDctTextW)
    except Exception:
        log.debug("No IDgnVDctTextW interface (visible text not available)")

    dict_obj = ComDictObj(
        voice_dict, text_iface, dgn_text, sink, tlb=tlb, connection=conn)

    sink._dict_handle = dict_obj.handle
    sink._text_iface = text_iface
    sink._dict_obj = dict_obj
    conn.register_dict_sink(dict_obj.handle, sink)

    log.debug("Created dictation object (handle=%d)", dict_obj.handle)
    return dict_obj


def _acquire_lock(text_iface):
    """Acquire IVDct0TextW lock, retrying on E_PENDING.

    "It is possible that the Lock call will return E_PENDING if the
    VoiceDictation object is busy with another thread.  In that case,
    the correct behavior is to sleep a little and then try again."
    — Joel Gould, DictationObject.cpp (CGrabLock::setLock)

    C++ loops indefinitely, but we add a timeout because Dragon is in a
    separate process — a hung or crashed Dragon would never release the
    lock, freezing the Python thread forever.
    """
    deadline = time.monotonic() + 10.0  # 10 seconds — generous for transient E_PENDING
    while True:
        try:
            text_iface.Lock()
            return
        except Exception as e:
            # comtypes raises COMError; check for E_PENDING
            if hasattr(e, 'hresult') and e.hresult == E_PENDING:
                if time.monotonic() > deadline:
                    raise NatlinkCOMError("Lock",
                        error_message="Timed out waiting for dictation lock "
                        "(Dragon may be unresponsive)")
                time.sleep(0.02)
                continue
            raise
