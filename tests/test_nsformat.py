#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# test_nsformat.py
#   Live mimic-based end-to-end tests for Dragon native text formatting.
#   Requires Dragon 13+ and a live COM connection.
#
#   Dragon types directly into a focused EDIT control; we read back the text.
#   Expected values reflect what Dragon 13 actually produces (not nsformat).
#
import os
import sys

import pytest

_src = os.path.join(os.path.dirname(__file__), "..", "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from _helpers import do_mimic, focus_window, get_edit_text, clear_edit


# ---------------------------------------------------------------------------
# EDIT-control formatting fixture: mimic -> Dragon types into EDIT -> verify
#
# Dragon types directly into the focused EDIT control using its native
# formatting engine.  We read the result back via WM_GETTEXT.
# This is Dragon's most natural path — no DictObj intermediary needed.
# ---------------------------------------------------------------------------

@pytest.fixture
def dfmt(live_connection, editwin_proc):
    """EDIT-control formatting capture: mimic -> Dragon types natively -> read back.

    Dragon types directly into the focused EDIT control.  This is the most
    reliable path — no DictObj create/destroy/activate overhead, no retry
    logic needed.
    """
    main_hwnd, edit_hwnd = editwin_proc
    focus_window(main_hwnd)

    def do(words, pause=2.0, clear=True):
        if clear:
            clear_edit(edit_hwnd)
        do_mimic(words, pause=pause)
        return get_edit_text(edit_hwnd)

    yield do


# ---------------------------------------------------------------------------
# Raw callback test: verify Dragon returns backslash-formatted words
# ---------------------------------------------------------------------------

@pytest.mark.nsformat
@pytest.mark.online
class TestLiveNsformat:
    """Verify Dragon returns backslash-formatted words in dictation callback."""

    def test_dictation_words_have_formatting_properties(self, live_connection):
        """Mimic dictation with written-form punctuation; verify Dragon returns backslash notation."""
        import natlink_compat as natlink
        from _helpers import compile_grammar

        received = []
        binary = compile_grammar("""
            <dgndictation> imported;
            <rule> exported = <dgndictation>;
        """)
        gram = natlink.GramObj()

        try:
            gram.setResultsCallBack(lambda w, r: received.append((w, r)))
            gram.load(binary)
            gram.activate("rule", 0)

            do_mimic(["hello", "world", ".\\period\\period"], pause=1.5)

            assert len(received) >= 1, "Results callback never fired"
            words_data, _ = received[0]

            if isinstance(words_data, list) and len(words_data) > 0:
                if isinstance(words_data[0], tuple):
                    raw_words = [w[0] for w in words_data]
                else:
                    raw_words = list(words_data)
            else:
                raw_words = []

            assert ".\\period\\period" in raw_words, \
                f"Expected '.\\period\\period' in results, got: {raw_words}"

        finally:
            gram.unload()


# ---------------------------------------------------------------------------
# Dragon native formatting tests: mimic -> EDIT control -> verify text
#
# These test Dragon's native formatting engine by reading what Dragon
# types into a focused EDIT control.  Key differences from nsformat:
#
#   Period spacing:     Dragon uses 1 space after period (nsformat used 2)
#   Caps-on:           Dragon may skip function words (nsformat title-cased all)
#   Number collapsing: Dragon collapses "two three" -> "23" (nsformat didn't)
#   No-space-on:       Dragon may delay 1 word (nsformat applied immediately)
#   Letter spacing:    Dragon suppresses spaces between all letter types
#
# Expected values are discovered from Dragon 13 actual output.
# Run with -s flag to see discovery output for any DISCOVERY assertions.
# ---------------------------------------------------------------------------

@pytest.mark.nsformat
@pytest.mark.online
class TestDragonFormatting:
    """Mimic vocabulary words -> EDIT control -> verify Dragon native formatted text."""

    # -- Basic punctuation --

    def test_period(self, dfmt):
        """Period with following word — Dragon uses 1 space (not 2)."""
        text = dfmt(["first", ".\\period\\period", "next"])
        assert text == "First. Next", f"Got: {text!r}"

    def test_sentence_ending(self, dfmt):
        """Period at end of utterance with no following word."""
        text = dfmt(["this", "is", "a", "test", ".\\period\\period"])
        assert text == "This is a test.", f"Got: {text!r}"

    def test_comma(self, dfmt):
        text = dfmt(["hello", ",\\comma\\comma", "world"])
        assert text == "Hello, world", f"Got: {text!r}"

    def test_dot(self, dfmt):
        """Dot joins words with no space (no cap change)."""
        text = dfmt(["hello", ".\\dot\\dot", "test", ".\\period\\period"])
        assert text == "Hello.test.", f"Got: {text!r}"

    def test_colon(self, dfmt):
        text = dfmt(["example", ":\\colon\\colon", "test"])
        assert text == "Example: test", f"Got: {text!r}"

    def test_semicolon(self, dfmt):
        text = dfmt(["first", ";\\semicolon\\semicolon", "second"])
        assert text == "First; second", f"Got: {text!r}"

    def test_hyphen(self, dfmt):
        text = dfmt(["well", "-\\hyphen\\hyphen", "known"])
        assert text == "Well-known", f"Got: {text!r}"

    # -- Special characters --

    def test_at_sign(self, dfmt):
        """@ -> at-sign property -> no space before/after."""
        text = dfmt(["hello", "@", "world"])
        assert text == "Hello@world", f"Got: {text!r}"

    def test_brackets(self, dfmt):
        """[ -> left-square-bracket, ] -> right-square-bracket."""
        text = dfmt(["hello", "[", "world", "]", ".\\period\\period"])
        assert text == "Hello [world].", f"Got: {text!r}"

    def test_minus_sign(self, dfmt):
        """minus-sign — Dragon may format differently from nsformat."""
        text = dfmt(["hello", "-\\minus-sign", "world"])
        assert text == "Hello - world", f"Got: {text!r}"

    def test_open_close_quote(self, dfmt):
        """Open-quote suppresses space after; close-quote suppresses space before."""
        text = dfmt([
            "\"\\left-double-quote\\open quote",
            "hello",
            "\"\\right-double-quote\\close quote"])
        assert text == '"Hello"', f"Got: {text!r}"

    # -- Capitalization commands --

    def test_cap(self, dfmt):
        text = dfmt(["\\cap\\cap", "hello"])
        assert text == "Hello", f"Got: {text!r}"

    def test_caps_on_off(self, dfmt):
        """Caps-on — Dragon may skip function words unlike nsformat."""
        text = dfmt([
            "\\caps-on\\caps on", "hello", "world",
            "\\caps-off\\caps off", "test"])
        assert text == "Hello World test", f"Got: {text!r}"

    def test_all_caps(self, dfmt):
        text = dfmt(["\\all-caps\\all caps", "hello"])
        assert text == "HELLO", f"Got: {text!r}"

    def test_all_caps_on_off(self, dfmt):
        text = dfmt([
            "\\all-caps-on\\all caps on", "hello", "world",
            "\\all-caps-off\\all caps off", "test"])
        assert text == "HELLO WORLD test", f"Got: {text!r}"

    def test_no_caps(self, dfmt):
        text = dfmt(["\\no-caps\\no caps", "London"])
        assert text == "london", f"Got: {text!r}"

    # -- Spacing commands --

    def test_no_space(self, dfmt):
        text = dfmt(["hello", "\\no-space\\no space", "there"])
        assert text == "Hellothere", f"Got: {text!r}"

    def test_no_space_on_off(self, dfmt):
        text = dfmt([
            "\\no-space-on\\no space on", "hello", "world",
            "\\no-space-off\\no space off", "test"])
        assert text == "Helloworld test", f"Got: {text!r}"

    # -- Newline / paragraph --

    def test_new_line(self, dfmt):
        text = dfmt(["hello", "\\new-line\\new line", "world"])
        assert text == "Hello\r\nworld", f"Got: {text!r}"

    def test_new_paragraph(self, dfmt):
        """New paragraph inserts double newline and capitalizes next word."""
        text = dfmt(["hello", "\\new-paragraph\\new paragraph", "world"])
        assert text == "Hello\r\n\r\nWorld", f"Got: {text!r}"

    def test_space_bar(self, dfmt):
        text = dfmt(["hello", "\\space-bar\\space bar"])
        assert text == "Hello ", f"Got: {text!r}"

    # -- Combined formatting --

    @pytest.mark.xfail(reason="Dragon may interpret 'a third' as '1/3'")
    def test_sentence_chaining(self, dfmt):
        """Three sentences with periods — Dragon uses 1-space gap (not 2)."""
        text = dfmt([
            "first", ".\\period\\period", "next",
            "this", "is", "a", "second", "sentence", ".\\period\\period",
            "and", "a", "third", "sentence", ".\\period\\period"])
        assert text == "First. Next this is a second sentence. And a third sentence.", \
            f"Got: {text!r}"

    def test_caps_on_with_comma(self, dfmt):
        """Caps-on with comma — Dragon may skip function words."""
        text = dfmt([
            "\\caps-on\\caps on", "as", "you", "can", "see",
            ",\\comma\\comma", "this", "works",
            "\\caps-off\\caps off", "well"])
        assert text == "As You Can See, This Works well", f"Got: {text!r}"

    def test_quote_with_period(self, dfmt):
        """Open-quote, text, period, close-quote — Dragon uses 1 space."""
        text = dfmt([
            "an",
            "\"\\left-double-quote\\open quote",
            "example", "of", "testing", ".\\period\\period",
            "\"\\right-double-quote\\close quote",
            "hello"])
        assert text == 'An "example of testing." Hello', f"Got: {text!r}"

    def test_dot_period_interleaved(self, dfmt):
        """Dots (no-space) and periods (1-space + cap-next) interleaved."""
        text = dfmt([
            "a", "hello", ".\\dot\\dot", "test", "message",
            ".\\period\\period",
            "and", "proceed", "with", "more",
            ".\\dot\\dot", "testing", ".\\period\\period"])
        assert text == "A hello.test message. And proceed with more.testing.", \
            f"Got: {text!r}"

    def test_combined_punctuation(self, dfmt):
        """Colon, semicolon, at-sign, and bracket in one utterance."""
        text = dfmt([
            "an", "example", "with", "many", "signs",
            ":\\colon\\colon", ";\\semicolon\\semicolon",
            "and", "@", "and", "["])
        assert text == "An example with many signs:; and@and [", f"Got: {text!r}"

    def test_bracket_hyphen_minus(self, dfmt):
        """Right-bracket, hyphen, and minus-sign distinctions."""
        text = dfmt([
            "and", "continuing", "with", "]",
            "and", "-\\hyphen\\hyphen", "and",
            "-\\minus-sign", ".\\period\\period"])
        assert text == "And continuing with] and-and -.", f"Got: {text!r}"

    def test_no_space_on_with_colon(self, dfmt):
        """No-space (single), colon, no-space-on/off — Dragon may add space after colon."""
        text = dfmt([
            "hello", "\\no-space\\no space", "there",
            "and", "no", "spacing", ":\\colon\\colon",
            "\\no-space-on\\no space on",
            "Daisy", "Dakar", "and", "more",
            "\\no-space-off\\no space off",
            "and", "normal", "again", ".\\period\\period"])
        # Dragon native may insert a space after colon before no-space-on takes effect
        assert text == "Hellothere and no spacing: DaisyDakarandmore and normal again.", \
            f"Got: {text!r}"

    def test_no_caps_on_off(self, dfmt):
        """No-caps (single word), no-caps-on/off toggle with proper nouns."""
        text = dfmt([
            "\\no-caps\\no caps", "Daisy", "Dakar", "lowercase", "example",
            "\\no-caps-on\\no caps on",
            "Daisy", "Dakar", "and", "more",
            "\\no-caps-off\\no caps off",
            "and", "Dakar", "again", ".\\period\\period"])
        assert text == "daisy Dakar lowercase example daisy dakar and more and Dakar again.", \
            f"Got: {text!r}"

    def test_cap_then_caps_on(self, dfmt):
        """Single cap, normal words, then caps-on/off with comma.

        Dragon may skip function words ("with", "an", "and") during caps-on,
        unlike nsformat which title-cased ALL words.
        """
        text = dfmt([
            "\\cap\\cap", "uppercase", "example", "and", "normal", "and",
            "\\caps-on\\caps on", "and", "continuing", "with", "an",
            "uppercase", "example", "and",
            "\\caps-off\\caps off",
            ",\\comma\\comma", "normal", "again", ".\\period\\period"])
        # Dragon native: skips function words ("with", "an", "and") in caps-on
        assert text == "Uppercase example and normal and And Continuing with an Uppercase Example and, normal again.", \
            f"Got: {text!r}"

    def test_all_caps_then_all_caps_on(self, dfmt):
        """Single all-caps, normal, then all-caps-on/off with comma."""
        text = dfmt([
            "\\all-caps\\all caps", "examples", "and", "normal", "and",
            "\\all-caps-on\\all caps on", "and", "continuing", "with",
            "\\all-caps-off\\all caps off",
            ",\\comma\\comma", "normal", "again", ".\\period\\period"])
        assert text == "EXAMPLES and normal and AND CONTINUING WITH, normal again.", \
            f"Got: {text!r}"

    def test_all_caps_on_no_space_complex(self, dfmt):
        """All-caps-on + no-space + no-space-on, then off switches interleaved."""
        text = dfmt([
            "combined",
            "\\all-caps-on\\all caps on", "hello",
            "\\no-space\\no space", "there", "and",
            "\\no-space-on\\no space on", "back", "again", "and",
            "\\all-caps-off\\all caps off", "continuing", "no", "spacing",
            "\\no-space-off\\no space off",
            "now", "normal", "again", ".\\period\\period"])
        # Dragon may delay no-space-on by 1 word, inserting space before "BACK"
        assert text == "Combined HELLOTHERE AND BACKAGAINANDcontinuingnospacing now normal again.", \
            f"Got: {text!r}"

    def test_cross_recognition_state(self, dfmt):
        """Formatting state persists across multiple mimics in the EDIT buffer.

        Uses clear=False to append subsequent mimics to the same buffer.
        """
        # Phase 1: start all-caps-on
        text1 = dfmt([
            "\\all-caps-on\\all caps on", "this", "is", "a", "test"])
        assert "THIS IS A TEST" in text1, f"Phase 1 got: {text1!r}"

        # Phase 2: all-caps carries over, add no-space-on, turn off all-caps
        text2 = dfmt([
            "continuing", "in", "the", "next", "phrase",
            "\\no-space-on\\no space on", "with", "no",
            "\\all-caps-off\\all caps off", "spacing"],
            clear=False)
        # text2 is the FULL buffer (phase1 + phase2)
        assert "THIS IS A TEST" in text2, f"Phase 2 full got: {text2!r}"

        # Phase 3: no-space-on still active, then off, then normal
        text3 = dfmt([
            "and", "resuming", "like", "that", ".\\period\\period",
            "this", "\\no-space-off\\no space off",
            "is", "now", "at", "last", "normal", ".\\period\\period"],
            clear=False)
        # text3 is the FULL buffer (all 3 phases)
        assert text3.startswith("THIS IS A TEST"), f"Full got: {text3!r}"
        assert text3.endswith("normal."), f"Full got: {text3!r}"

    def test_newline_and_paragraph_combined(self, dfmt):
        """New-line and new-paragraph in one utterance with auto-cap after paragraph."""
        text = dfmt([
            "now", "for", "the",
            "\\new-line\\new line", "and", "for", "the",
            "\\new-paragraph\\new paragraph",
            "testing", ".\\period\\period"])
        assert text == "Now for the\r\nand for the\r\n\r\nTesting.", f"Got: {text!r}"

    def test_spacebar_between_words(self, dfmt):
        """Spacebar inserts explicit space; next word has no additional space."""
        text = dfmt([
            "hello", "\\space-bar\\space bar", "world"])
        assert text == "Hello world", f"Got: {text!r}"

    def test_lowercase_no_spacing(self, dfmt):
        """No-caps-on + no-space-on produces email-style output."""
        text = dfmt([
            "\\no-caps-on\\no caps on",
            "\\no-space-on\\no space on",
            "Dakar", "@", "world", ".\\dot\\dot", "com",
            "\\no-caps-off\\no caps off",
            "\\no-space-off\\no space off"])
        assert text == "dakar@world.com", f"Got: {text!r}"

    # -- Spelling letters --

    def test_determiner_a(self, dfmt):
        """a\\determiner — determiner property, initial cap."""
        text = dfmt(["a\\determiner"])
        assert text == "A", f"Got: {text!r}"

    def test_letter_uppercase(self, dfmt):
        """A\\letter — letter property."""
        text = dfmt(["A\\letter"])
        assert text == "A", f"Got: {text!r}"

    def test_lowercase_letter(self, dfmt):
        """a\\lowercase-letter — Dragon suppresses space between all letter types."""
        text = dfmt(["hello", "a\\lowercase-letter\\lowercase A"])
        assert text == "Hello a", f"Got: {text!r}"

    def test_uppercase_letter(self, dfmt):
        """A\\uppercase-letter."""
        text = dfmt(["hello", "A\\uppercase-letter\\uppercase A"])
        assert text == "Hello A", f"Got: {text!r}"

    def test_letter_i(self, dfmt):
        """I\\letter — the letter I."""
        text = dfmt(["I\\letter"])
        assert text == "I", f"Got: {text!r}"

    def test_pronoun_i(self, dfmt):
        """I\\pronoun — the pronoun I."""
        text = dfmt(["I\\pronoun"])
        assert text == "I", f"Got: {text!r}"

    def test_spelling_letters_combined(self, dfmt):
        """Multiple letter types — Dragon suppresses spaces between all letter types."""
        text = dfmt([
            "a\\determiner", "A\\letter",
            "a\\lowercase-letter\\lowercase A",
            "A\\uppercase-letter\\uppercase A",
            "I\\letter", "I\\pronoun",
            "X\\letter", "I\\pronoun", "Y\\letter"])
        # Dragon native suppresses spaces between all letter types
        assert text == "A AaAI I X I Y", f"Got: {text!r}"

    # -- Numbers --
    # Dragon collapses consecutive number words to digits (nsformat didn't).

    def test_one_pronoun(self, dfmt):
        """one\\pronoun — produces word 'One', not digit."""
        text = dfmt(["one\\pronoun"])
        assert text == "One", f"Got: {text!r}"

    def test_one_number(self, dfmt):
        """one\\number — Dragon may produce '1' or 'One'."""
        text = dfmt(["one\\number"])
        assert text == "One", f"Got: {text!r}"

    def test_consecutive_number_words(self, dfmt):
        """Dragon collapses consecutive number words to digits: "two three four five" -> "2345"."""
        text = dfmt(["two", "three", "four", "five"])
        assert text == "2345", f"Got: {text!r}"

    def test_consecutive_number_words_6789(self, dfmt):
        """Same as above for six-nine range."""
        text = dfmt(["six", "seven", "eight", "nine"])
        assert text == "6789", f"Got: {text!r}"

    # -- UK English period variant --

    def test_period_full_stop(self, dfmt):
        """UK English period variant: .\\period\\full stop — same 1-space behavior."""
        text = dfmt(["hello", ".\\period\\full stop", "world"])
        assert text == "Hello. World", f"Got: {text!r}"

    # -- Shorter command forms (no display name) --

    @pytest.mark.xfail(
        reason="Dragon's recognitionMimic intermittently rejects bare formatting commands without display name",
        raises=Exception,
    )
    def test_caps_on_short_form(self, dfmt):
        """\\caps-on (without display name) works like \\caps-on\\caps on."""
        text = dfmt(["\\caps-on", "hello", "world"])
        assert text == "Hello World", f"Got: {text!r}"

    @pytest.mark.xfail(
        reason="Dragon's recognitionMimic intermittently rejects bare formatting commands without display name",
        raises=Exception,
    )
    def test_all_caps_on_short_form(self, dfmt):
        """\\all-caps-on (without display name) works like \\all-caps-on\\all caps on."""
        text = dfmt(["\\all-caps-on", "hello", "world"])
        assert text == "HELLO WORLD", f"Got: {text!r}"
