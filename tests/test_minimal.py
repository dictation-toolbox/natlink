"""Minimal live regression suite — one test per feature, <30s total.

Covers: connection, system info, grammar load/activate/mimic, callbacks
(begin + results + timer + change), lists, dictation, vocabulary,
playString, playEvents, execScript.

Run:  py -m pytest tests/test_00_minimal.py -m online -v
"""

import time

import pytest

import natlink_compat as natlink
from natlink_compat._state import _state
from _helpers import compile_grammar, extract_words, do_mimic
from _helpers import focus_window, get_edit_text, clear_edit


# ── Connection ──────────────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestConnection:

    def test_connected(self, live_connection):
        assert _state.connected
        assert _state.backend is not None


# ── System info ─────────────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestSystemInfo:

    def test_queries(self, live_connection):
        name, directory = natlink.getCurrentUser()
        assert isinstance(name, str) and len(name) > 0

        path, title, hwnd = natlink.getCurrentModule()
        assert isinstance(hwnd, int)

        assert natlink.getMicState() in ("on", "off", "sleeping", "disabled")
        assert natlink.getScreenSize()[0] > 0
        assert isinstance(natlink.getCursorPos()[0], int)
        assert isinstance(natlink.getClipboard(), str)
        assert natlink.getCallbackDepth() == 0


# ── Grammar + mimic + callbacks ─────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestGrammarMimicCallbacks:

    @pytest.fixture(autouse=True, scope="class")
    def shared_grammar(self, live_connection):
        binary = compile_grammar(
            "<rule> exported = hello world;\n"
            "<depthrule> exported = check depth;\n"
            "<listrule> exported = open {files};"
        )
        cls = type(self)
        cls._gram = natlink.GramObj()
        cls._gram.load(binary)
        cls._gram.activate("rule", 0)
        cls._gram.activate("depthrule", 0)
        cls._gram.activate("listrule", 0)
        cls._gram.emptyList("files")
        cls._gram.appendList("files", "document")
        # Exclusive: mimic must route to this grammar even when
        # another window is foreground.
        try:
            cls._gram.setExclusive(True)
        except Exception:
            pass
        yield
        try:
            cls._gram.setExclusive(False)
        except Exception:
            pass
        cls._gram.unload()

    def test_mimic_with_callbacks(self):
        """Mimic fires begin then results with correct words + ResObj."""
        order = []
        begin_info = []
        result_data = []
        natlink.setBeginCallback(lambda info: (order.append("begin"), begin_info.append(info)))
        self._gram.setResultsCallback(lambda w, r: (order.append("results"), result_data.append((w, r))))
        try:
            do_mimic(["hello", "world"])
            assert len(begin_info) >= 1
            assert isinstance(begin_info[0], tuple) and len(begin_info[0]) == 3
            assert len(result_data) >= 1
            words = extract_words(result_data[0][0])
            assert "hello" in words and "world" in words
            assert order.index("begin") < order.index("results")
            # ResObj usable
            res = result_data[0][1]
            assert res.getResults(0) is not None
        finally:
            natlink.setBeginCallback(None)
            self._gram.setResultsCallback(None)

    def test_callback_depth(self):
        depths = []
        self._gram.setResultsCallback(
            lambda w, r: depths.append(natlink.getCallbackDepth()))
        try:
            do_mimic(["check", "depth"])
            assert depths and depths[0] >= 1
        finally:
            self._gram.setResultsCallback(None)

    def test_list_recognized(self):
        received = []
        self._gram.setResultsCallback(lambda w, r: received.append(w))
        try:
            do_mimic(["open", "document"])
            assert received
            assert extract_words(received[0]) == ["open", "document"]
        finally:
            self._gram.setResultsCallback(None)

    def test_getList(self):
        assert "document" in self._gram.getList("files")


# ── Timer callback ──────────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestTimerCallback:

    def test_fires(self, live_connection):
        from conftest import wait_for_callback
        hits = []
        natlink.setTimerCallback(lambda: hits.append(1), 100)
        try:
            wait_for_callback(lambda: len(hits) >= 2, timeout=3.0)
        finally:
            natlink.setTimerCallback(None, 0)
        assert len(hits) >= 2


# ── Change callback ─────────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestChangeCallback:

    def test_mic_change(self, live_connection):
        from conftest import wait_for_callback
        received = []
        natlink.setChangeCallback(lambda t, info: received.append((t, info)))
        original = natlink.getMicState()
        target = "on" if original != "on" else "off"
        try:
            natlink.setMicState(target)
            wait_for_callback(
                lambda: any(r[0] == "mic" for r in received), timeout=2.0)
            mic_events = [r for r in received if r[0] == "mic"]
            assert mic_events and mic_events[-1][1] == target
        finally:
            natlink.setChangeCallback(None)
            natlink.setMicState(original)
            time.sleep(0.3)


# ── Dictation object ───────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestDictation:

    def test_lifecycle(self, live_connection):
        dobj = natlink.DictObj()
        try:
            dobj.activate(0)
            dobj.setLock(1)
            dobj.setText("Hello world", 0, 0x7FFFFFFF)
            assert dobj.getText(0, 0x7FFFFFFF) == "Hello world"
            assert dobj.getLength() == 11
            dobj.setLock(0)
            dobj.deactivate()
        finally:
            dobj.destroy()


# ── Vocabulary ──────────────────────────────────────────────────────────

@pytest.mark.online
@pytest.mark.minimal
class TestVocabulary:

    _WORD = "natlinktestminimal"

    def test_word_lifecycle(self, live_connection):
        assert natlink.getWordInfo("hello") is not None
        assert natlink.getWordInfo(self._WORD) is None
        try:
            assert natlink.addWord(self._WORD) == 1
            assert natlink.getWordInfo(self._WORD) is not None
        finally:
            natlink.deleteWord(self._WORD)
        assert natlink.getWordInfo(self._WORD) is None


# ── Sync operations (LAST — playString poisons grammar activation) ─────

@pytest.mark.online
@pytest.mark.minimal
class TestPlayString:

    def test_types_text(self, editwin_proc, live_connection):
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)
        natlink.playString("hi")
        assert "hi" in get_edit_text(edit_hwnd).lower()


@pytest.mark.online
@pytest.mark.minimal
class TestPlayEvents:

    def test_keypress(self, editwin_proc, live_connection):
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)
        WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
        natlink.playEvents([(WM_KEYDOWN, 0x41, 0), (WM_KEYUP, 0x41, 0)])
        assert "a" in get_edit_text(edit_hwnd).lower()


@pytest.mark.online
@pytest.mark.minimal
class TestExecScript:

    def test_set_microphone(self, live_connection):
        original = natlink.getMicState()
        try:
            natlink.execScript("SetMicrophone 0")
            time.sleep(0.3)
            assert natlink.getMicState() == "off"
        finally:
            natlink.setMicState(original)
            time.sleep(0.3)
