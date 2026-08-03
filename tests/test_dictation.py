"""DictObj lifecycle tests (offline + live)."""

import pytest

import natlink_compat as natlink
from natlink_compat._state import _state
from natlink_compat._exceptions import WrongState


class TestDictObjOffline:

    def setup_method(self):
        _state.reset()

    def test_activate_raises_without_connection(self):
        dobj = natlink.DictObj()
        with pytest.raises(WrongState):
            dobj.activate(0)

    def test_setText_raises_without_connection(self):
        dobj = natlink.DictObj()
        with pytest.raises(WrongState):
            dobj.setText("text", 0, 100)

    def test_getText_raises_without_connection(self):
        dobj = natlink.DictObj()
        with pytest.raises(WrongState):
            dobj.getText(0, 100)

    def test_deactivate_without_create_is_noop(self):
        dobj = natlink.DictObj()
        dobj.deactivate()  # should not raise

    def test_callback_setters_work_without_connection(self):
        dobj = natlink.DictObj()
        dobj.setBeginCallback(lambda x: None)
        dobj.setChangeCallback(lambda *a: None)
        assert dobj._begin_callback is not None
        assert dobj._change_callback is not None
        dobj.setBeginCallback(None)
        dobj.setChangeCallback(None)
        assert dobj._begin_callback is None
        assert dobj._change_callback is None


@pytest.mark.online
class TestLiveDictation:

    def test_full_lifecycle(self, live_connection):
        """Create, activate, set text, get text, deactivate."""
        dobj = natlink.DictObj()
        try:
            dobj.activate(0)
            dobj.setLock(1)
            dobj.setText("Hello world", 0, 0x7FFFFFFF)
            text = dobj.getText(0, 0x7FFFFFFF)
            assert text == "Hello world"
            length = dobj.getLength()
            assert length == 11
            dobj.setLock(0)
            dobj.deactivate()
        finally:
            dobj.destroy()

    def test_setText_replace_range(self, live_connection):
        """setText(text, start, end) replaces the [start, end) range."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("the quick brown fox", 0, 0x7FFFFFFF)
            dobj.setText("slow", 4, 9)
            assert dobj.getText(0, 0x7FFFFFFF) == "the slow brown fox"
            dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_getText_subrange(self, live_connection):
        """getText(start, end) reads a subrange of the buffer."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("the quick brown fox", 0, 0x7FFFFFFF)
            assert dobj.getText(4, 9) == "quick"
            assert dobj.getText(10, 19) == "brown fox"
            dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_setTextSel_and_getTextSel(self, live_connection):
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("Some text", 0, 0x7FFFFFFF)
            dobj.setTextSel(2, 6)
            start, end = dobj.getTextSel()
            assert start == 2
            assert end == 6
            dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_callbacks(self, live_connection):
        dobj = natlink.DictObj()
        begin_cb = lambda info: None
        change_cb = lambda *args: None
        dobj.setBeginCallback(begin_cb)
        dobj.setChangeCallback(change_cb)
        assert dobj._begin_callback is begin_cb
        assert dobj._change_callback is change_cb
        try:
            dobj.activate(0)
            dobj.deactivate()
        finally:
            dobj.destroy()
        assert dobj._begin_callback is None
        assert dobj._change_callback is None

    def test_multiple_dictation_objects(self, live_connection):
        """Multiple DictObj instances can coexist."""
        d1 = natlink.DictObj()
        d2 = natlink.DictObj()
        try:
            d1.activate(0)
            d2.activate(0)
            d1.setLock(1)
            d1.setText("First", 0, 0x7FFFFFFF)
            d2.setLock(1)
            d2.setText("Second", 0, 0x7FFFFFFF)
            assert d1.getText(0, 0x7FFFFFFF) == "First"
            assert d2.getText(0, 0x7FFFFFFF) == "Second"
            d1.setLock(0)
            d2.setLock(0)
        finally:
            d1.destroy()
            d2.destroy()

    def test_auto_lock(self, live_connection):
        """Methods auto-lock if user hasn't called setLock(1)."""
        dobj = natlink.DictObj()
        try:
            dobj.setText("auto lock test", 0, 0x7FFFFFFF)
            assert dobj.getText(0, 0x7FFFFFFF) == "auto lock test"
            assert dobj.getLength() == 14
        finally:
            dobj.destroy()

    def test_negative_indices(self, live_connection):
        """Negative indices offset from the end."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("hello world", 0, 0x7FFFFFFF)
            assert dobj.getText(0, -5) == "hello "
            assert dobj.getText(-5, 0x7FFFFFFF) == "world"
            dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_autolock_set_get(self, live_connection):
        """setAutoLock / getAutoLock round-trip."""
        dobj = natlink.DictObj()
        try:
            dobj.setAutoLock(1)
            assert dobj.getAutoLock() is True
            dobj.setAutoLock(0)
            assert dobj.getAutoLock() is False
        finally:
            dobj.destroy()

    def test_visible_text_set_get(self, live_connection):
        """setVisibleText / getVisibleText round-trip."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("the quick brown fox jumps", 0, 0x7FFFFFFF)
            dobj.setVisibleText(4, 19)
            start, end = dobj.getVisibleText()
            assert start == 4
            assert end == 19
            dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_hint_text(self, live_connection):
        """hintText call completes (may return E_INVALIDARG on DNS 13)."""
        from natlink_compat._exceptions import NatError
        dobj = natlink.DictObj()
        try:
            dobj.activate(0)
            try:
                dobj.hintText("email")
            except NatError:
                # DNS 13 may not support Hint — E_INVALIDARG is acceptable
                pass
            dobj.deactivate()
        finally:
            dobj.destroy()

    def test_get_that(self, live_connection):
        """getThat returns a (start, end) tuple."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            dobj.setText("some text", 0, 0x7FFFFFFF)
            dobj.setLock(0)
            result = dobj.getThat()
            assert isinstance(result, tuple)
            assert len(result) == 2
        finally:
            dobj.destroy()

    def test_recent_buffer_commit(self, live_connection):
        """recentBufferCommit completes without error."""
        dobj = natlink.DictObj()
        try:
            dobj.recentBufferCommit()  # should not raise
        finally:
            dobj.destroy()

    def test_bookmark_lifecycle(self, live_connection):
        """addBookmark / queryBookmark / moveBookmark / removeBookmark.

        DNS 13 may return E_NOTIMPL for bookmark operations — test
        verifies the call reaches Dragon without RPC errors.
        """
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            try:
                dobj.setText("bookmark test text", 0, 0x7FFFFFFF)
                try:
                    dobj.addBookmark(42, 5)
                except Exception as exc:
                    pytest.skip(f"Bookmarks not supported: {exc}")
                bm_id, bm_pos = dobj.queryBookmark(42)
                assert bm_id == 42
                assert bm_pos == 5
                dobj.moveBookmark(42, 10)
                bm_id2, bm_pos2 = dobj.queryBookmark(42)
                assert bm_pos2 == 10
                dobj.removeBookmark(42)
            finally:
                dobj.setLock(0)
        finally:
            dobj.destroy()

    def test_enum_bookmarks(self, live_connection):
        """enumBookmarks returns a list of (id, position) tuples."""
        dobj = natlink.DictObj()
        try:
            dobj.setLock(1)
            try:
                dobj.setText("enum test", 0, 0x7FFFFFFF)
                try:
                    dobj.addBookmark(1, 0)
                except Exception as exc:
                    pytest.skip(f"Bookmarks not supported: {exc}")
                dobj.addBookmark(2, 4)
                bookmarks = dobj.enumBookmarks()
                assert len(bookmarks) >= 2
                ids = [bm[0] for bm in bookmarks]
                assert 1 in ids
                assert 2 in ids
                dobj.removeBookmark(1)
                dobj.removeBookmark(2)
            finally:
                dobj.setLock(0)
        finally:
            dobj.destroy()
