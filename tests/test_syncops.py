"""Live tests for synchronous blocking operations.

All four operations now block until their completion callback fires:
  - playString  (PlaybackDone via IDgnSSvcActionNotifySink)
  - playEvents  (PlaybackDone via IDgnSSvcActionNotifySink)
  - execScript  (ExecutionDone via IDgnSSvcActionNotifySink)
  - recognitionMimic (MimicDone via IDgnSREngineNotifySinkW)
  - inputFromFile (DGNSRAC_PLAYBACKDONE via AttribChanged2)
"""

import os
import time

import pytest

import natlink_compat as natlink
from natlink_compat._exceptions import MimicFailed

from _helpers import (
    focus_window, get_edit_text, clear_edit, dismiss_dictation_box,
    get_edit_selection, send_keys, compile_grammar, do_mimic,
    wait_for_edit_text,
)


# ---------------------------------------------------------------------------
# playString
# ---------------------------------------------------------------------------

@pytest.mark.online
class TestPlayString:
    """playString delivers keystrokes via Dragon's COM interface."""

    @pytest.fixture(autouse=True)
    def editwin(self, editwin_proc, live_connection):
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)
        self._hwnd = main_hwnd
        self._edit_hwnd = edit_hwnd
        yield

    def test_plain_text(self):
        """Plain text should type into the edit control."""
        natlink.playString("hello")
        assert "hello" in get_edit_text(self._edit_hwnd).lower()

    def test_enter_key(self):
        """{Enter} should insert a newline."""
        natlink.playString("line1{Enter}line2")
        text = wait_for_edit_text(
            self._edit_hwnd, lambda t: "line1" in t and "line2" in t)
        assert "line1" in text and "line2" in text

    def test_backspace(self):
        """{Backspace} should delete the previous character."""
        natlink.playString("abc{Backspace}")
        text = get_edit_text(self._edit_hwnd)
        assert "ab" in text
        assert "abc" not in text

    def test_ctrl_a_selects_all(self):
        """{Ctrl+a} should select all text."""
        send_keys("some text")
        time.sleep(0.2)
        natlink.playString("{Ctrl+a}")
        sel = get_edit_selection(self._edit_hwnd)
        assert sel[0] != sel[1], f"Expected selection, got: {sel}"


# ---------------------------------------------------------------------------
# playEvents
# ---------------------------------------------------------------------------

@pytest.mark.online
class TestPlayEvents:
    """playEvents delivers HOOK_EVENTMSG triples via Dragon's COM interface."""

    @pytest.fixture(autouse=True)
    def editwin(self, editwin_proc, live_connection):
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)
        self._hwnd = main_hwnd
        self._edit_hwnd = edit_hwnd
        yield

    def test_empty_raises(self):
        """playEvents([]) should raise."""
        with pytest.raises(natlink.NatError):
            natlink.playEvents([])

    def test_keypress_arrives(self):
        """A down+up pair for 'a' (VK 0x41) should type into the edit control."""
        WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
        events = [(WM_KEYDOWN, 0x41, 0), (WM_KEYUP, 0x41, 0)]
        natlink.playEvents(events)
        assert "a" in get_edit_text(self._edit_hwnd).lower()

    def test_multiple_keys(self):
        """Multiple key events should all arrive in order."""
        WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
        events = []
        for vk in [0x48, 0x49]:  # H, I
            events.append((WM_KEYDOWN, vk, 0))
            events.append((WM_KEYUP, vk, 0))
        natlink.playEvents(events)
        assert "hi" in get_edit_text(self._edit_hwnd).lower()

    def test_shift_key(self):
        """Shift+A should produce uppercase 'A'."""
        WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
        events = [
            (WM_KEYDOWN, 0x10, 0),  # Shift down
            (WM_KEYDOWN, 0x41, 0),  # A down
            (WM_KEYUP, 0x41, 0),    # A up
            (WM_KEYUP, 0x10, 0),    # Shift up
        ]
        natlink.playEvents(events)
        assert "A" in get_edit_text(self._edit_hwnd)


# ---------------------------------------------------------------------------
# execScript
# ---------------------------------------------------------------------------

@pytest.mark.online
class TestExecScript:
    """execScript runs Dragon scripting commands synchronously."""

    def test_set_microphone(self, live_connection):
        """execScript SetMicrophone should change mic state."""
        original = natlink.getMicState()
        try:
            natlink.setMicState("sleeping")
            time.sleep(0.3)

            natlink.execScript("SetMicrophone 3")
            time.sleep(0.3)
            assert natlink.getMicState() == "sleeping"

            natlink.execScript("SetMicrophone 0")
            time.sleep(0.3)
            assert natlink.getMicState() == "off"

            natlink.execScript("SetMicrophone 1")
            time.sleep(0.3)
            assert natlink.getMicState() == "on"
        finally:
            natlink.setMicState(original)

    def test_invalid_command_raises(self, live_connection):
        """An invalid scripting command should raise NatError."""
        with pytest.raises(natlink.NatError):
            natlink.execScript("ThisIsNotAValidDragonCommand_XYZ123")

    def test_send_keys_types_into_edit(self, editwin_proc, live_connection):
        """SendKeys via execScript should type into the focused edit window.

        Skipped on DNS 13 + Windows 10/11: Dragon's SendKeys script command
        uses journal hooks which the OS blocks, and Dragon shows an error dialog.
        """
        import sys
        from natlink_compat._state import _state
        if sys.getwindowsversion().major >= 10 and not _state.backend._conn.supports_dw_notify:
            pytest.skip("DNS 13 SendKeys blocked by Windows 10/11 journal hook restriction")
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)
        natlink.execScript('SendKeys "abc"')
        # SendKeys is async — poll until keystrokes arrive
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            if "abc" in get_edit_text(edit_hwnd).lower():
                break
            time.sleep(0.1)
        dismiss_dictation_box()
        assert "abc" in get_edit_text(edit_hwnd).lower()


# ---------------------------------------------------------------------------
# recognitionMimic
# ---------------------------------------------------------------------------

@pytest.mark.online
class TestRecognitionMimic:
    """recognitionMimic injects words into the recognition engine."""

    def test_basic_mimic(self, live_connection):
        """Mimic a simple phrase and verify the results callback fires."""
        received = []
        binary = compile_grammar("<rule> exported = sync ops mimic test ;")
        gram = natlink.GramObj()
        try:
            gram.setResultsCallback(lambda w, r: received.append(w))
            gram.load(binary)
            gram.activate("rule", 0)
            do_mimic(["sync", "ops", "mimic", "test"])
            assert len(received) >= 1, "Results callback never fired"
        finally:
            gram.unload()

    def test_mimic_types_into_edit(self, editwin_proc, live_connection):
        """Mimic 'hello' — text should appear in edit AND callback should fire."""
        main_hwnd, edit_hwnd = editwin_proc
        focus_window(main_hwnd)
        clear_edit(edit_hwnd)

        received = []
        binary = compile_grammar("<rule> exported = mimic edit observer ;")
        gram = natlink.GramObj()

        try:
            gram.setResultsCallback(lambda w, r: received.append(w))
            gram.load(binary, allResults=1)
            gram.activate("rule", 0)

            natlink.recognitionMimic(["hello"])

            text = get_edit_text(edit_hwnd)
            assert "hello" in text.lower(), \
                f"Expected 'hello' in edit, got: {text!r}"
            assert len(received) >= 1, "Results callback never fired"
        finally:
            gram.unload()
            time.sleep(0.3)

    def test_invalid_words_raise(self, live_connection):
        """Mimic with nonsense words should raise MimicFailed."""
        with pytest.raises(MimicFailed):
            natlink.recognitionMimic(["xzqwvbn_not_a_word_99"])


# ---------------------------------------------------------------------------
# inputFromFile
# ---------------------------------------------------------------------------

@pytest.mark.online
class TestInputFromFile:
    """inputFromFile plays audio into the recognizer synchronously."""

    _WAV = os.path.join(os.path.dirname(__file__), "Recording_mono22k.wav")

    @pytest.fixture(autouse=True)
    def _check_wav(self):
        if not os.path.isfile(self._WAV):
            pytest.skip(f"Test wav file not found: {self._WAV}")

    def test_nonexistent_file_raises(self, live_connection):
        """inputFromFile with a bogus path should raise NatError."""
        with pytest.raises(natlink.NatError):
            natlink.inputFromFile("C:\\nonexistent_test_audio_xyz.wav")

    def test_wav_completes(self, live_connection):
        """inputFromFile with a real wav returns promptly.

        The duration is the assertion. This waited on an event nothing ever
        signalled, so it could only ever burn its full 5-minute timeout and
        raise -- and was marked experimental, which deselects it by default,
        so the failure stayed hidden. A wall-clock bound is what catches that
        class of regression; "returns without error" would not.
        """
        started = time.monotonic()
        natlink.inputFromFile(self._WAV)
        elapsed = time.monotonic() - started
        assert elapsed < 60, (
            f"inputFromFile took {elapsed:.0f}s -- it is waiting on something "
            f"that never fires and running out its timeout")

    @pytest.mark.experimental
    def test_getWave_from_audio(self, live_connection):
        """getWave returns audio bytes from a real recognition (not mimic).

        Opt-in: unlike test_wav_completes, this depends on Dragon actually
        recognising the WAV, which is not deterministic across a long session
        -- it passes alone and in small groups but not reliably after the full
        suite has run. That is what "experimental" is for. test_wav_completes
        only measures that inputFromFile returns, so it stays in the default
        suite where it guards the timeout regression.

        Loads a dictation grammar, plays a WAV via inputFromFile, and
        verifies the ResObj from the results callback has wave data.
        Exercises ISRResMemory::LockSet (preserves audio buffer).
        """
        from natlink_com.grammar_compiler import compile_dictation_grammar
        wave_data = []

        gram = natlink.GramObj()
        gram.load(compile_dictation_grammar(), allResults=1)
        gram.activate("", 0)
        gram.setResultsCallback(lambda w, r: wave_data.append(r.getWave()))

        try:
            natlink.inputFromFile(self._WAV)
        finally:
            gram.setResultsCallback(None)
            gram.deactivate("")
            gram.unload()

        assert wave_data, "No results callback fired during inputFromFile"
        assert isinstance(wave_data[0], bytes)
        assert len(wave_data[0]) > 100, f"Wave too small: {len(wave_data[0])} bytes"
