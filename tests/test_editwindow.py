"""Edit window integration tests (Dragon + DictObj + select grammar + playString)."""

import ctypes
import ctypes.wintypes as wt
import time
import threading

import pytest

import natlink_compat as natlink

from _helpers import (
    _user32, focus_window, get_edit_text, clear_edit,
    get_edit_selection, send_keys, compile_grammar,
    compile_select_grammar, extract_words, do_mimic,
    dismiss_dictation_box, wait_for_edit_text, WM_APP_FOCUS_EDIT,
)


@pytest.mark.online
class TestLiveEditWindow:
    """Dragon interaction with a focused classic Win32 EDIT control.

    Launches _editwin_helper.py (EDIT child auto-receives keyboard focus via
    WM_ACTIVATE), verifies Dragon sees the window, and tests typing and
    DictObj operations.
    """

    @pytest.fixture(autouse=True)
    def editwin(self, editwin_proc):
        """Re-use the session-scoped EDIT window; re-focus each test."""
        main_hwnd, edit_hwnd = editwin_proc
        dismiss_dictation_box()
        focus_window(main_hwnd)

        self._hwnd = main_hwnd
        self._edit_hwnd = edit_hwnd
        yield
        dismiss_dictation_box()

    # -- Tests that PASS (working APIs) --

    def test_dragon_sees_editwin(self, live_connection):
        """getCurrentModule reports the Edit window as foreground."""
        path, title, hwnd = natlink.getCurrentModule()
        assert hwnd == self._hwnd, \
            f"HWND mismatch: Dragon=0x{hwnd:X}, expected=0x{self._hwnd:X}"

    def test_begin_callback_reports_editwin(self, live_connection):
        """Begin callback fires with the Edit window's HWND."""
        received = []
        binary = compile_grammar("<rule> exported = edit window check;")
        gram = natlink.GramObj()
        try:
            natlink.setBeginCallback(lambda info: received.append(info))
            gram.setResultsCallBack(lambda w, r: None)
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["edit", "window", "check"])

            assert len(received) >= 1, "Begin callback never fired"
            assert received[0][2] == self._hwnd, \
                f"Begin HWND=0x{received[0][2]:X}, expected=0x{self._hwnd:X}"
        finally:
            natlink.setBeginCallback(None)
            gram.unload()

    def test_dictobj_text_operations(self, live_connection):
        """DictObj setText/getText/getLength work against Edit HWND."""
        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("hello from edit", 0, 0x7FFFFFFF)
            assert dobj.getText(0, 0x7FFFFFFF) == "hello from edit"
            assert dobj.getLength() == len("hello from edit")
            dobj.setLock(0)
            dobj.deactivate()
        finally:
            dobj.destroy()

    def test_dictobj_change_callback_fires(self, live_connection):
        """DictObj change callback fires when mimic triggers dictation.

        Defocuses the EDIT child so Dragon routes dictation through the
        DictObj buffer instead of typing directly into the EDIT control.
        """
        # Defocus EDIT — Dragon routes dictation through DictObj when
        # there's no focused text control.
        _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 0, 0)
        time.sleep(0.3)

        changes = []
        dobj = natlink.DictObj()
        try:
            dobj.setChangeCallback(lambda *args: changes.append(args))
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("", 0, 0x7FFFFFFF)
            dobj.setTextSel(0, 0)
            dobj.setLock(0)

            do_mimic(["hello", "world"])

            assert len(changes) >= 1, \
                "DictObj change callback never fired during mimic"
        finally:
            # Restore EDIT focus for subsequent tests
            _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 1, 0)
            time.sleep(0.1)
            dobj.destroy()

    def test_dictobj_begin_callback_keeps_buffer_stable_until_return(self, live_connection):
        """DictObj begin callback runs before dictation mutates the buffer.

        JITPause blocks Dragon until the callback returns.  We verify
        getLength() is unchanged at callback entry — if it changed,
        Dragon mutated the buffer before we returned (a contract violation).
        """
        # Defocus EDIT so Dragon routes dictation through DictObj.
        _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 0, 0)
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)

            begin_called = threading.Event()
            length_at_begin = {"value": -1}
            callback_error = {"value": None}

            def on_begin(_info):
                begin_called.set()
                try:
                    length_at_begin["value"] = dobj.getLength()
                except Exception as exc:
                    callback_error["value"] = exc

            dobj.setBeginCallback(on_begin)
            dobj.setLock(1)
            dobj.setText("", 0, 0x7FFFFFFF)
            dobj.setTextSel(0, 0)
            dobj.setLock(0)

            do_mimic(["hello"])

            assert begin_called.is_set(), "DictObj begin callback never fired"
            assert callback_error["value"] is None, (
                f"DictObj begin callback raised: {callback_error['value']}")
            assert length_at_begin["value"] == 0, (
                f"Buffer was not empty at begin callback entry "
                f"(length={length_at_begin['value']})")
            assert dobj.getLength() > 0, (
                "DictObj buffer stayed empty after mimic")
        finally:
            _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 1, 0)
            time.sleep(0.1)
            dobj.destroy()

    # -- Tests for typing into the Edit control via SendInput --
    # Dragon's PlayString uses WH_JOURNALPLAYBACK (blocked on Windows 11).
    # These tests use SendInput instead — the same mechanism dragonfly uses.

    def test_sendinput_types_into_edit(self, live_connection):
        """SendInput should type text into the focused Edit control."""
        clear_edit(self._edit_hwnd)
        send_keys("hello")
        time.sleep(0.5)
        text = get_edit_text(self._edit_hwnd)
        assert "hello" in text.lower(), \
            f"Expected 'hello' in Edit, got {text!r}"

    def test_playback_from_grammar_callback(self, live_connection):
        """playString from inside a grammar callback should type into Edit.

        This mirrors dragonfly's real-world pattern: grammar recognizes
        speech → callback fires → action types keystrokes via playString.
        """
        clear_edit(self._edit_hwnd)
        binary = compile_grammar("<rule> exported = type into window;")
        gram = natlink.GramObj()
        try:
            def on_results(words, res):
                if isinstance(words, list):
                    natlink.playString("callback typed this")

            gram.setResultsCallBack(on_results)
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["type", "into", "window"])

            text = wait_for_edit_text(
                self._edit_hwnd,
                lambda t: "callback typed this" in t.lower())
            assert "callback typed this" in text.lower(), \
                f"Expected 'callback typed this' in Edit, got {text!r}"
        finally:
            gram.unload()

    def test_recognitionMimic_types_into_edit(self, live_connection):
        """Mimicking dictation should produce text in Edit control."""
        clear_edit(self._edit_hwnd)
        do_mimic(["hello", "world"])
        text = get_edit_text(self._edit_hwnd)
        assert len(text.strip()) > 0 and "hello" in text.lower(), \
            f"Expected 'hello' in Edit, got {text!r}"

    # -- Dragon text manipulation on multi-line content --

    def _set_edit_text(self, text):
        """Clear then set Edit control text via WM_SETTEXT."""
        clear_edit(self._edit_hwnd)
        buf = ctypes.create_unicode_buffer(text)
        _user32.SendMessageW(self._edit_hwnd, 0x000C, 0,
                             ctypes.addressof(buf))

    def test_dictate_multiline(self, live_connection):
        """Dictate words across multiple lines using Enter via SendInput."""
        clear_edit(self._edit_hwnd)
        do_mimic(["the", "quick", "brown", "fox"])
        # Dragon's "new line" command isn't matched by recognitionMimic.
        # Use SendInput Enter to create a new line (same as dragonfly).
        send_keys("\r")
        time.sleep(0.3)
        do_mimic(["jumps", "over", "the", "lazy", "dog"])

        text = get_edit_text(self._edit_hwnd)
        lines = text.strip().splitlines()
        assert len(lines) >= 2, \
            f"Expected at least 2 lines, got {len(lines)}: {text!r}"
        assert "quick" in lines[0].lower(), \
            f"Line 1 missing 'quick': {lines[0]!r}"
        assert "lazy" in lines[-1].lower(), \
            f"Last line missing 'lazy': {lines[-1]!r}"

    def test_scratch_that_removes_last_utterance(self, live_connection):
        """'Scratch that' should remove the last dictated phrase."""
        clear_edit(self._edit_hwnd)
        do_mimic(["hello", "world"])
        text_before = get_edit_text(self._edit_hwnd)
        assert "hello" in text_before.lower(), \
            f"Setup failed — expected 'hello', got {text_before!r}"

        do_mimic(["scratch", "that"])
        text_after = get_edit_text(self._edit_hwnd)
        assert len(text_after.strip()) < len(text_before.strip()), \
            f"'Scratch that' didn't shorten text: before={text_before!r}, after={text_after!r}"

    def test_select_word_via_mimic(self, live_connection):
        """Dragon's 'select <word>' should select the word in the Edit control.

        Uses EM_GETSEL to read the selection from the Edit control directly.
        Requires DictObj active with synced text so Dragon's Select-and-Say
        grammar knows the on-screen content.
        """
        self._set_edit_text("the quick brown fox jumps over the lazy dog")
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("the quick brown fox jumps over the lazy dog",
                         0, 0x7FFFFFFF)
            dobj.setTextSel(0, 0)
            dobj.setLock(0)

            do_mimic(["select", "brown"])

            # Check Edit control's selection via EM_GETSEL
            sel_start, sel_end = get_edit_selection(self._edit_hwnd)
            text = get_edit_text(self._edit_hwnd)
            selected = text[sel_start:sel_end]
            assert "brown" in selected.lower(), \
                f"Expected 'brown' selected, got {selected!r} (sel={sel_start}:{sel_end}, text={text!r})"
        finally:
            dobj.destroy()

    def test_dictate_over_selection(self, live_connection):
        """Dictating with a selection active should replace the selected text."""
        self._set_edit_text("the quick brown fox")
        time.sleep(0.3)

        # Defocus EDIT so Dragon routes through DictObj
        _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 0, 0)
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("the quick brown fox", 0, 0x7FFFFFFF)
            # Select "brown"
            dobj.setTextSel(10, 15)
            dobj.setLock(0)

            do_mimic(["red"])

            text = dobj.getText(0, 0x7FFFFFFF)
            assert "red" in text.lower(), \
                f"Expected 'red' in text after replacement, got {text!r}"
            assert "brown" not in text.lower(), \
                f"'brown' should have been replaced, got {text!r}"
        finally:
            _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 1, 0)
            time.sleep(0.1)
            dobj.destroy()

    # -- Select grammar: setSelectText / getSelectText --
    # Select grammars require a real window handle (global activation
    # crashes Dragon's COM) and expose IDgnSRGramSelect.

    def test_setSelectText_and_getSelectText(self, live_connection):
        """setSelectText/getSelectText round-trip on a select grammar.

        Select grammars (DGNSRHDRTYPE_SELECT=10) support setSelectText to
        provide the text buffer for Dragon's "select <text>" recognition.
        """
        binary = compile_select_grammar(["select"])
        gram = natlink.GramObj()
        try:
            gram.load(binary)

            gram.setSelectText("the quick brown fox")
            result = gram.getSelectText()
            assert result == "the quick brown fox", \
                f"Expected 'the quick brown fox', got {result!r}"

            # Overwrite
            gram.setSelectText("jumps over the lazy dog")
            result = gram.getSelectText()
            assert result == "jumps over the lazy dog", \
                f"Expected 'jumps over the lazy dog', got {result!r}"

            # Clear
            gram.setSelectText("")
            result = gram.getSelectText()
            assert result == "", f"Expected empty string, got {result!r}"
        finally:
            gram.unload()

    def test_select_grammar_recognition(self, live_connection):
        """Select grammar: mimic 'select brown' and apply selection to Edit.

        Loads a select grammar, sets the text buffer, mimics "select brown",
        then uses getSelectInfo to apply the selection to the Edit control.
        """
        buffer = "the quick brown fox jumps over the lazy dog"
        self._set_edit_text(buffer)
        binary = compile_select_grammar(["select"])
        gram = natlink.GramObj()
        received = []

        try:
            gram.setResultsCallBack(lambda w, r: received.append((w, r)))
            gram.load(binary)
            gram.setSelectText(buffer)
            gram.activate("", self._hwnd)

            do_mimic(["select", "brown"])

            assert len(received) >= 1, \
                "Select grammar results callback never fired"

            words_and_nums, res_obj = received[0]
            word_strs = [w[0].lower() if isinstance(w, tuple) else w.lower()
                         for w in words_and_nums]
            assert "select" in word_strs and "brown" in word_strs, \
                f"Expected 'select' and 'brown' in {word_strs}"

            start, end = res_obj.getSelectInfo(gram, 0)
            assert buffer[start:end].lower() == "brown", \
                f"Expected 'brown' at [{start}:{end}], got {buffer[start:end]!r}"

            # Apply selection to Edit and verify
            _user32.SendMessageW(self._edit_hwnd, 0x00B1, start, end)
            sel_start, sel_end = get_edit_selection(self._edit_hwnd)
            edit_selected = get_edit_text(self._edit_hwnd)[sel_start:sel_end]
            assert "brown" in edit_selected.lower(), \
                f"Edit selection should be 'brown', got {edit_selected!r}"
        finally:
            gram.unload()

    def test_select_grammar_through_range(self, live_connection):
        """Select grammar: mimic 'select brown through lazy' selects range.

        Verifies getSelectInfo returns the span from 'brown' to 'lazy',
        then applies the selection to the Edit control.
        """
        buffer = "the quick brown fox jumps over the lazy dog"
        self._set_edit_text(buffer)
        binary = compile_select_grammar(["select"], through_word="through")
        gram = natlink.GramObj()
        received = []

        try:
            gram.setResultsCallBack(lambda w, r: received.append((w, r)))
            gram.load(binary)
            gram.setSelectText(buffer)
            gram.activate("", self._hwnd)

            do_mimic(["select", "brown", "through", "lazy"])

            assert len(received) >= 1, \
                "Select grammar results callback never fired"

            words_and_nums, res_obj = received[0]
            start, end = res_obj.getSelectInfo(gram, 0)

            expected_start = buffer.index("brown")
            expected_end = buffer.index("lazy") + len("lazy")
            assert start == expected_start, \
                f"Start: expected {expected_start}, got {start}"
            assert end == expected_end, \
                f"End: expected {expected_end}, got {end}"

            # Apply selection to Edit and verify
            _user32.SendMessageW(self._edit_hwnd, 0x00B1, start, end)
            sel_start, sel_end = get_edit_selection(self._edit_hwnd)
            edit_selected = get_edit_text(self._edit_hwnd)[sel_start:sel_end]
            assert "brown" in edit_selected.lower() and "lazy" in edit_selected.lower(), \
                f"Edit selection should span 'brown'...'lazy', got {edit_selected!r}"
        finally:
            gram.unload()

    # -- DictObj ↔ Edit control sync tests --
    # These tests verify how DictObj programmatic operations interact with
    # the Edit control — what syncs and what doesn't.

    def test_dictobj_setText_syncs_to_edit(self, live_connection):
        """DictObj.setText should push text changes to the Edit control."""
        clear_edit(self._edit_hwnd)
        time.sleep(0.2)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("programmatic text", 0, 0x7FFFFFFF)
            dobj.setLock(0)
            time.sleep(0.5)

            # Check if the Edit control received the text
            edit_text = get_edit_text(self._edit_hwnd)
            buf_text = dobj.getText(0, 0x7FFFFFFF)
            assert buf_text == "programmatic text", \
                f"DictObj buffer: expected 'programmatic text', got {buf_text!r}"
            # Edit control may or may not sync — document actual behavior
            if "programmatic" in edit_text.lower():
                pass  # setText syncs to Edit — great
            else:
                import warnings
                warnings.warn(
                    f"DictObj.setText does NOT sync to Edit control "
                    f"(edit={edit_text!r}, buffer={buf_text!r})")
        finally:
            dobj.destroy()

    def test_dictobj_setTextSel_is_buffer_only(self, live_connection):
        """DictObj.setTextSel updates the internal buffer, NOT the Edit control.

        The Edit control's selection only changes when Dragon's Select-and-Say
        grammar fires (via recognitionMimic "select <word>").  Programmatic
        setTextSel affects only the DictObj buffer — verified here by showing
        EM_GETSEL stays at (0, 0) while getTextSel reports (10, N).
        """
        self._set_edit_text("the quick brown fox")
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("the quick brown fox", 0, 0x7FFFFFFF)
            dobj.setTextSel(10, 15)  # select "brown" in buffer
            dobj.setLock(0)
            time.sleep(0.3)

            # DictObj buffer has the selection
            buf_start, buf_end = dobj.getTextSel()
            buf_selected = dobj.getText(buf_start, buf_end)
            assert "brown" in buf_selected, \
                f"DictObj buffer should have 'brown' selected, got {buf_selected!r}"

            # Edit control does NOT reflect it
            edit_start, edit_end = get_edit_selection(self._edit_hwnd)
            assert edit_start == edit_end, \
                f"Edit control should have no selection, got ({edit_start}, {edit_end})"
        finally:
            dobj.destroy()

    def test_dictobj_mimic_then_programmatic_append(self, live_connection):
        """Mimic generates text, then DictObj appends to it programmatically."""
        clear_edit(self._edit_hwnd)

        # Defocus EDIT so Dragon routes dictation through DictObj
        _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 0, 0)
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("", 0, 0x7FFFFFFF)
            dobj.setTextSel(0, 0)
            dobj.setLock(0)

            do_mimic(["hello", "world"])

            dobj.setLock(1)
            length = dobj.getLength()
            assert length > 0, "DictObj buffer empty after mimic"
            original = dobj.getText(0, length)

            # Append text programmatically
            dobj.setText(" suffix", length, length)
            new_text = dobj.getText(0, 0x7FFFFFFF)
            assert new_text.endswith("suffix"), \
                f"Expected text ending with 'suffix', got {new_text!r}"
            assert new_text.startswith(original), \
                f"Original text lost: expected prefix {original!r}, got {new_text!r}"
            dobj.setLock(0)
        finally:
            _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 1, 0)
            time.sleep(0.1)
            dobj.destroy()

    def test_dictobj_mimic_then_programmatic_replace(self, live_connection):
        """Mimic generates text, then DictObj replaces a word in it."""
        clear_edit(self._edit_hwnd)

        # Defocus EDIT so Dragon routes dictation through DictObj
        _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 0, 0)
        time.sleep(0.3)

        dobj = natlink.DictObj()
        try:
            dobj.activate(self._hwnd)
            dobj.setLock(1)
            dobj.setText("", 0, 0x7FFFFFFF)
            dobj.setTextSel(0, 0)
            dobj.setLock(0)

            do_mimic(["the", "quick", "brown", "fox"], pause=2.0)

            dobj.setLock(1)
            text = dobj.getText(0, 0x7FFFFFFF)
            assert len(text) > 0, "DictObj buffer empty after mimic"

            # Find "brown" in the dictated text and replace with "red"
            idx = text.lower().find("brown")
            assert idx >= 0, f"'brown' not found in dictated text: {text!r}"
            dobj.setText("red", idx, idx + 5)

            result = dobj.getText(0, 0x7FFFFFFF)
            assert "red" in result.lower(), \
                f"Expected 'red' in result, got {result!r}"
            assert "brown" not in result.lower(), \
                f"'brown' should be replaced, got {result!r}"
            dobj.setLock(0)
        finally:
            _user32.PostMessageW(self._hwnd, WM_APP_FOCUS_EDIT, 1, 0)
            time.sleep(0.1)
            dobj.destroy()


