"""test_grammar_format.py - Live Dragon validation of grammar binary format.

Systematically tests grammar features from simple to complex, comparing
output from three compilers (our standalone, natlinkcore, dragonfly).

All tests require Dragon running and use the live_connection fixture.

Run one level at a time:
    pytest tests/test_grammar_format.py -v -m online -k "Level00"
"""

import struct
import threading
import time

import pytest

from natlink_com.grammar_compiler import (
    GrammarCompiler,
    compile_dictation_grammar,
    compile_grammar,
    compile_select_grammar,
    parse_grammar_binary)

def natlinkcore_compile(spec: str) -> bytes:
    """Compile via natlinkcore (skips test if not installed)."""
    gramparser = pytest.importorskip("natlinkcore.gramparser")
    parser = gramparser.GramParser(spec)
    parser.doParse()
    parser.checkForErrors()
    return gramparser.packGrammar(parser)
from _helpers import do_mimic, extract_words, clear_edit
pytestmark = pytest.mark.online


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def gram(live_connection):
    """Provide a fresh GramObj that auto-unloads on teardown."""
    import natlink_compat as natlink

    grams = []

    def _make():
        g = natlink.GramObj()
        grams.append(g)
        return g

    yield _make

    for g in grams:
        try:
            g.unload()
        except Exception:
            pass


class CallbackCollector:
    """Collect recognition results from a grammar callback."""

    def __init__(self):
        self.results = []
        self.event = threading.Event()

    def __call__(self, *args):
        """Called as beginCallback / resultsCallback by natlink."""
        # resultsCallback signature: (wordsAndNums, resObj)
        # beginCallback signature: (moduleInfo)
        # We only care about resultsCallback (2 args with words)
        if len(args) >= 2 and isinstance(args[0], (list, tuple)):
            words = extract_words(args[0])
            self.results.append(words)
            self.event.set()

    def wait(self, timeout=5.0):
        self.event.wait(timeout)

    def reset(self):
        self.results.clear()
        self.event.clear()


# ---------------------------------------------------------------------------
# Helper: load + activate + mimic + verify
# ---------------------------------------------------------------------------

def _load_and_test(gram_factory, binary, rule_name, mimic_words,
                   expected_words=None):
    """Load a compiled grammar, activate, mimic, verify callback.

    Returns the CallbackCollector for additional assertions.
    """
    import natlink_compat as natlink

    if expected_words is None:
        expected_words = [w.lower() for w in mimic_words]

    g = gram_factory()
    cb = CallbackCollector()
    g.load(binary)
    g.setResultsCallback(cb)
    g.activate(rule_name, 0)
    # Exclusive: Dragon only considers this grammar while active, so
    # the mimic can't be stolen by dictation or a sibling test grammar.
    try:
        g.setExclusive(True)
    except Exception:
        pass

    try:
        do_mimic(mimic_words, pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0, (
            f"No recognition results for mimic {mimic_words!r} "
            f"with rule {rule_name!r}"
        )
        assert cb.results[-1] == expected_words, (
            f"Expected {expected_words!r}, got {cb.results[-1]!r}"
        )
    finally:
        try:
            g.setExclusive(False)
        except Exception:
            pass
        try:
            g.deactivate(rule_name)
        except Exception:
            pass

    return cb


def _test_with_all_compilers(gram_factory, spec, rule_name, mimic_words,
                             expected_words=None):
    """Test a grammar spec with our compiler and natlinkcore."""
    # Our compiler (ANSI)
    ours = compile_grammar(spec, encoding="ansi")
    _load_and_test(gram_factory, ours, rule_name, mimic_words,
                   expected_words)

    # natlinkcore
    ref = natlinkcore_compile(spec)

    # Cross-validate bytecode
    if ours != ref:
        from natlink_com.grammar_compiler import compare_grammars
        diffs = compare_grammars(ours, ref, "ansi", "ansi")
        raise AssertionError(
            f"Bytecode mismatch for: {spec!r}\n"
            f"  Ours:  {ours.hex()}\n"
            f"  Ref:   {ref.hex()}\n"
            f"  Diffs: {diffs or 'byte-level only'}"
        )

    _load_and_test(gram_factory, ref, rule_name, mimic_words,
                   expected_words)


# ===================================================================
# Level 0: Encoding & Format Baseline
# ===================================================================

class TestLevel00_Encoding:
    """Resolve ANSI vs WCHAR and format variations."""

    def test_00a_ansi_loads(self, gram):
        """Known-working baseline: ANSI grammar (natlinkcore output)."""
        binary = natlinkcore_compile("<r> exported = hello ;")
        _load_and_test(gram, binary, "r", ["hello"])

    @pytest.mark.xfail(reason=(
        "FINDING: WCHAR without SRHDRFLAG_UNICODE (bit 0) loads but "
        "recognition fails. Dragon defaults to ANSI when flag=0. "
        "Doc §2 is WRONG about Dragon ignoring the flag."
    ))
    def test_00b_wchar_loads(self, gram):
        """Does Dragon accept UTF-16LE strings without UNICODE flag?"""
        binary = compile_grammar("<r> exported = hello ;", encoding="wchar")
        _load_and_test(gram, binary, "r", ["hello"])

    def test_00c_wchar_with_unicode_flag(self, gram):
        """WCHAR + SRHDRFLAG_UNICODE (bit 0) set."""
        binary = compile_grammar("<r> exported = hello ;", encoding="wchar")
        # Patch flags to set bit 0
        binary = binary[:4] + struct.pack("L", 1) + binary[8:]
        _load_and_test(gram, binary, "r", ["hello"])

    def test_00d_our_ansi_loads(self, gram):
        """Our standalone compiler ANSI output loads."""
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        _load_and_test(gram, binary, "r", ["hello"])

    def test_00e_empty_chunks_present(self, gram):
        """Grammar with all 5 chunk types emitted (some empty)."""
        # Build a grammar with empty import and list chunks
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        # Insert empty chunk 5 (imports) and chunk 6 (lists) before chunk 2
        # Find where chunk 2 starts
        pos = 8  # after header
        chunks_before = bytearray()
        chunks_after = bytearray()
        found_first = False
        while pos < len(binary):
            cid, csize = struct.unpack_from("LL", binary, pos)
            chunk = binary[pos : pos + 8 + csize]
            if cid == 4:
                # After exports, insert empty import + list chunks
                chunks_before += chunk
                # Empty chunk 5 (0 bytes data)
                chunks_before += struct.pack("LL", 5, 0)
                # Empty chunk 6 (0 bytes data)
                chunks_before += struct.pack("LL", 6, 0)
                found_first = True
            else:
                if found_first:
                    chunks_after += chunk
                else:
                    chunks_before += chunk
            pos += 8 + csize

        modified = binary[:8] + bytes(chunks_before) + bytes(chunks_after)
        _load_and_test(gram, modified, "r", ["hello"])

    def test_00f_empty_chunks_omitted(self, gram):
        """Grammar with only non-empty chunks (natlinkcore style)."""
        binary = natlinkcore_compile("<r> exported = hello ;")
        # Verify no chunk 5 or 6
        pos = 8
        chunk_ids = []
        while pos < len(binary):
            cid, csize = struct.unpack_from("LL", binary, pos)
            chunk_ids.append(cid)
            pos += 8 + csize
        assert 5 not in chunk_ids
        assert 6 not in chunk_ids
        _load_and_test(gram, binary, "r", ["hello"])


# ===================================================================
# Level 1: Single Word
# ===================================================================

class TestLevel01_SingleWord:

    def test_01a_single_word(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello ;", "r", ["hello"])


# ===================================================================
# Level 2: Sequences
# ===================================================================

class TestLevel02_Sequences:

    def test_02a_two_words(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello world ;", "r", ["hello", "world"])

    def test_02b_three_words(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = one two three ;", "r",
            ["one", "two", "three"])


# ===================================================================
# Level 3: Alternatives
# ===================================================================

class TestLevel03_Alternatives:

    def test_03a_two_choices_first(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello | goodbye ;", "r", ["hello"])

    def test_03a_two_choices_second(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello | goodbye ;", "r", ["goodbye"])

    def test_03b_three_choices(self, gram):
        spec = "<r> exported = hello | goodbye | hey ;"
        for word in ["hello", "goodbye", "hey"]:
            _test_with_all_compilers(
                gram, spec, "r", [word])


# ===================================================================
# Level 4: Optional
# ===================================================================

class TestLevel04_Optional:

    def test_04a_optional_at_end_with(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello [world] ;", "r",
            ["hello", "world"])

    def test_04a_optional_at_end_without(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello [world] ;", "r",
            ["hello"])

    def test_04b_optional_at_start(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = [please] help ;", "r",
            ["help"])

    def test_04c_optional_in_middle(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello [dear] world ;", "r",
            ["hello", "world"])


# ===================================================================
# Level 5: Repeat
# ===================================================================

class TestLevel05_Repeat:

    def test_05a_simple_repeat(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello+ ;", "r",
            ["hello"])

    def test_05a_simple_repeat_twice(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello+ ;", "r",
            ["hello", "hello"])

    def test_05b_repeat_in_sequence(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = say hello+ ;", "r",
            ["say", "hello"])


# ===================================================================
# Level 6: Two-Operation Combinations
# ===================================================================

class TestLevel06_Combinations:

    def test_06a_alt_in_seq(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = (hello | goodbye) world ;", "r",
            ["hello", "world"])

    def test_06b_alt_of_seqs(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello world | goodbye earth ;", "r",
            ["hello", "world"])

    def test_06c_seq_plus_optional(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = please [kindly] help ;", "r",
            ["please", "help"])

    def test_06d_optional_of_alt(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = [hello | goodbye] ;", "r",
            ["hello"])

    def test_06e_alt_with_optional(self, gram):
        _test_with_all_compilers(
            gram, "<r> exported = hello [world] | goodbye ;", "r",
            ["goodbye"])


# ===================================================================
# Level 7: Private Rule References
# ===================================================================

class TestLevel07_RuleRefs:

    def test_07a_simple_private(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = <greet> ; <greet> = hello ;",
            "r", ["hello"])

    def test_07b_private_with_alt(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = <greet> world ; <greet> = hello | hi ;",
            "r", ["hello", "world"])

    def test_07c_rule_chain(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = <a> ; <a> = <b> ; <b> = hello ;",
            "r", ["hello"])

    def test_07d_shared_private(self, gram):
        spec = (
            "<r1> exported = <g> world ;\n"
            "<r2> exported = <g> earth ;\n"
            "<g> = hello | hi ;"
        )
        binary = compile_grammar(spec, encoding="ansi")
        _load_and_test(gram, binary, "r1", ["hello", "world"])

        binary2 = compile_grammar(spec, encoding="ansi")
        _load_and_test(gram, binary2, "r2", ["hi", "earth"])


# ===================================================================
# Level 8: Dynamic Lists
# ===================================================================

class TestLevel08_Lists:

    def test_08a_single_list(self, gram):
        import natlink_compat as natlink

        spec = "<r> exported = open {files} ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("files", "readme")
        g.activate("r", 0)

        do_mimic(["open", "readme"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0, "No results for list grammar"
        assert cb.results[-1] == ["open", "readme"]
        g.deactivate("r")

    def test_08b_list_in_sequence(self, gram):
        spec = "<r> exported = open {files} now ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("files", "readme")
        g.activate("r", 0)

        do_mimic(["open", "readme", "now"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0
        assert cb.results[-1] == ["open", "readme", "now"]
        g.deactivate("r")

    def test_08c_multiple_lists(self, gram):
        spec = "<r> exported = {verb} {noun} ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("verb", "open")
        g.appendList("noun", "file")
        g.activate("r", 0)

        do_mimic(["open", "file"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0
        assert cb.results[-1] == ["open", "file"]
        g.deactivate("r")

    def test_08d_list_in_alt(self, gram):
        spec = "<r> exported = open {files} | close {files} ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("files", "readme")
        g.activate("r", 0)

        do_mimic(["close", "readme"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0
        assert cb.results[-1] == ["close", "readme"]
        g.deactivate("r")

    def test_08e_list_in_optional(self, gram):
        spec = "<r> exported = hello [{extras}] ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("extras", "world")
        g.activate("r", 0)

        # Mimic without the optional list word
        do_mimic(["hello"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0
        assert cb.results[-1] == ["hello"]
        g.deactivate("r")


# ===================================================================
# Level 9: Imported Rules / Dragon Built-ins
# ===================================================================

class TestLevel09_Imports:

    def test_09a_dgndictation(self, gram):
        spec = (
            "<dgndictation> imported ;\n"
            "<r> exported = say <dgndictation> ;"
        )
        _test_with_all_compilers(
            gram, spec, "r", ["say", "hello"])

    def test_09b_dgnwords(self, gram):
        spec = (
            "<dgnwords> imported ;\n"
            "<r> exported = spell <dgnwords> ;"
        )
        _test_with_all_compilers(
            gram, spec, "r", ["spell", "hello"])

    def test_09c_dgnletters(self, gram):
        spec = (
            "<dgnletters> imported ;\n"
            "<r> exported = letter <dgnletters> ;"
        )
        # Dragon returns spelled letters in format "a\spelling-letter\a"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.activate("r", 0)

        do_mimic(["letter", "a"], pause=1.5)
        cb.wait(timeout=8.0)

        assert len(cb.results) > 0, "No results for dgnletters"
        # First word should be "letter", second is Dragon's letter format
        assert cb.results[-1][0] == "letter"
        assert "a" in cb.results[-1][1]  # Contains "a" in some format
        g.deactivate("r")

    def test_09d_mixed_import_local(self, gram):
        spec = (
            "<dgndictation> imported ;\n"
            "<r> exported = <cmd> | <dgndictation> ;\n"
            "<cmd> = stop | cancel ;"
        )
        _test_with_all_compilers(
            gram, spec, "r", ["stop"])


# ===================================================================
# Level 10: Multiple Exported Rules
# ===================================================================

class TestLevel10_MultiExport:

    def test_10a_two_independent_exports(self, gram):
        spec = "<r1> exported = alpha ; <r2> exported = bravo ;"
        binary = compile_grammar(spec, encoding="ansi")

        # Activate r1, mimic alpha
        _load_and_test(gram, binary, "r1", ["alpha"])

    def test_10a_second_export(self, gram):
        spec = "<r1> exported = alpha ; <r2> exported = bravo ;"
        binary = compile_grammar(spec, encoding="ansi")

        _load_and_test(gram, binary, "r2", ["bravo"])

    def test_10b_exports_sharing_private(self, gram):
        spec = (
            "<r1> exported = <g> one ;\n"
            "<r2> exported = <g> two ;\n"
            "<g> = hello | hi ;"
        )
        binary = compile_grammar(spec, encoding="ansi")
        _load_and_test(gram, binary, "r1", ["hello", "one"])

    def test_10c_activate_deactivate(self, gram):
        """Load both rules, activate/deactivate them."""
        import natlink_compat as natlink

        spec = "<r1> exported = alpha ; <r2> exported = bravo ;"
        binary = compile_grammar(spec, encoding="ansi")

        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)

        # Activate r1 only
        g.activate("r1", 0)
        do_mimic(["alpha"], pause=1.5)
        cb.wait(timeout=8.0)
        assert len(cb.results) > 0
        assert cb.results[-1] == ["alpha"]

        # Switch to r2
        g.deactivate("r1")
        cb.reset()
        g.activate("r2", 0)
        do_mimic(["bravo"], pause=1.5)
        cb.wait(timeout=8.0)
        assert len(cb.results) > 0
        assert cb.results[-1] == ["bravo"]

        g.deactivate("r2")


# ===================================================================
# Level 11: Three-Level Nesting
# ===================================================================

class TestLevel11_DeepNesting:

    def test_11a_opt_in_alt_in_seq(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = hello (world | [dear] earth) ;",
            "r", ["hello", "earth"])

    def test_11b_alt_in_opt_in_seq(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = please [hello | goodbye] world ;",
            "r", ["please", "world"])

    def test_11c_seq_in_opt_in_alt(self, gram):
        _test_with_all_compilers(
            gram,
            "<r> exported = [hello world] | goodbye ;",
            "r", ["goodbye"])

    def test_11d_list_in_opt_in_seq(self, gram):
        spec = "<r> exported = open [{files}] now ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("files", "readme")
        g.activate("r", 0)

        # Mimic without optional list item
        do_mimic(["open", "now"], pause=1.5)
        cb.wait(timeout=8.0)
        assert len(cb.results) > 0
        assert cb.results[-1] == ["open", "now"]
        g.deactivate("r")


# ===================================================================
# Level 12: Real-World Patterns
# ===================================================================

class TestLevel12_RealWorld:

    def test_12a_command_target_modifier(self, gram):
        spec = "<r> exported = (open | close | save) {files} [now | later] ;"
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.appendList("files", "readme")
        g.activate("r", 0)

        do_mimic(["open", "readme", "now"], pause=1.5)
        cb.wait(timeout=8.0)
        assert len(cb.results) > 0
        assert cb.results[-1] == ["open", "readme", "now"]
        g.deactivate("r")

    def test_12b_navigation(self, gram):
        spec = (
            "<r> exported = go (up | down | left | right) [<count>] ;\n"
            "<count> = one | two | three ;"
        )
        _test_with_all_compilers(
            gram, spec, "r", ["go", "up"])

    def test_12c_mixed_dictation_command(self, gram):
        spec = (
            "<dgndictation> imported ;\n"
            "<r> exported = type <dgndictation> ;"
        )
        _test_with_all_compilers(
            gram, spec, "r", ["type", "hello"])


# ===================================================================
# Level 13: Other Grammar Types
# ===================================================================

class TestLevel13_OtherTypes:

    def test_13a_dictation_grammar_loads(self, gram):
        """Minimal dictation grammar (8 bytes) loads without error."""
        binary = compile_dictation_grammar()
        g = gram()
        g.load(binary)
        # Just loading without error is the test
        g.unload()

    def test_13b_dictation_activate(self, gram):
        """Dictation recognition via a CFG grammar with <dgndictation> element.

        A standalone dictation grammar (type=2) doesn't produce results via
        recognitionMimic. Mimic needs a CFG rule to route through. So we use
        a CFG grammar that wraps <dgndictation> as its only content — this is
        the "dictation element grammar" pattern.
        """
        spec = "<dgndictation> imported ;\n<r> exported = <dgndictation> ;"
        _test_with_all_compilers(
            gram, spec, "r", ["hello", "world"])

    def test_13c_select_grammar_loads(self, gram):
        """SELECT grammar loads without error."""
        binary = compile_select_grammar(["select"], "through")
        g = gram()
        g.load(binary)
        g.unload()

    def test_13d_select_with_text(self, gram, editwin_proc):
        """SELECT grammar: setSelectText + mimic recognizes selection.

        VALIDATED: setSelectText is sufficient — no live window needed.
        Both "select X" and "select X through Y" work via mimic.

        The EDIT window must be cleared first — if it contains text from
        previous tests, Dragon may try to match against the window text
        instead of the programmatic setSelectText buffer.
        """
        import time

        # Clear EDIT window to avoid interference with SELECT matching
        _, edit_hwnd = editwin_proc
        clear_edit(edit_hwnd)

        binary = compile_select_grammar(["select"], "through")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.setSelectText("hello world this is a test")
        g.activate("", 0)
        time.sleep(0.5)  # Let Dragon register the SELECT grammar

        try:
            # Simple selection: "select hello"
            # Dragon occasionally drops SELECT results; retry with full reload.
            for attempt in range(3):
                if attempt > 0:
                    cb.reset()
                    g.deactivate("")
                    g.unload()
                    time.sleep(0.5)
                    g.load(binary)
                    g.setResultsCallback(cb)
                    g.setSelectText("hello world this is a test")
                    g.activate("", 0)
                    time.sleep(0.5)
                do_mimic(["select", "hello"], pause=2.0)
                cb.wait(timeout=8.0)
                if cb.results:
                    break
            assert len(cb.results) > 0, "SELECT mimic produced no results"
            assert cb.results[-1] == ["select", "hello"]

            # Range selection: "select hello through world"
            cb.reset()
            do_mimic(["select", "hello", "through", "world"], pause=2.0)
            cb.wait(timeout=8.0)
            assert len(cb.results) > 0, "SELECT through mimic produced no results"
            assert cb.results[-1] == ["select", "hello", "through", "world"]
        finally:
            g.deactivate("")

    def test_13e_select_getSelectInfo(self, gram, editwin_proc):
        """ResObj.getSelectInfo returns word indices for SELECT recognition.

        "The recognizer call to the select information requires that you
        pass in the GUID of the grammar.  We go to the grammar to get
        the GUID.  The Python programmer will have passed in the grammar
        pointer." — Joel Gould, ResultObject.cpp (getSelectInfo)
        """
        import time

        _, edit_hwnd = editwin_proc
        clear_edit(edit_hwnd)

        binary = compile_select_grammar(["select"], "through")
        g = gram()
        select_info = []

        def results_cb(words_and_nums, res_obj):
            words = extract_words(words_and_nums)
            try:
                start, end = res_obj.getSelectInfo(g, 0)
                select_info.append((words, start, end))
            except Exception as e:
                select_info.append((words, "ERROR", str(e)))

        g.load(binary)
        g.setResultsCallback(results_cb)
        g.setSelectText("hello world this is a test")
        g.activate("", 0)
        time.sleep(0.5)

        try:
            for attempt in range(3):
                if attempt > 0:
                    select_info.clear()
                    g.deactivate("")
                    g.unload()
                    time.sleep(0.5)
                    g.load(binary)
                    g.setResultsCallback(results_cb)
                    g.setSelectText("hello world this is a test")
                    g.activate("", 0)
                    time.sleep(0.5)
                do_mimic(["select", "hello"], pause=2.0)
                time.sleep(3.0)
                if select_info:
                    break

            assert len(select_info) > 0, "SELECT mimic produced no results"
            words, start, end = select_info[-1]
            assert words == ["select", "hello"], f"Unexpected words: {words}"
            assert start != "ERROR", f"getSelectInfo failed: {end}"
            # Returns character offsets into the select text buffer.
            # "hello" spans chars 0..5 in "hello world this is a test"
            assert isinstance(start, int) and isinstance(end, int), \
                f"Expected (int, int), got ({type(start).__name__}, {type(end).__name__})"
            assert start == 0, f"Expected start=0 for 'hello', got {start}"
            assert end == 5, f"Expected end=5 for 'hello', got {end}"
        finally:
            g.deactivate("")


# ===================================================================
# Level 14: Binary Format Variations
# ===================================================================

class TestLevel14_FormatVariations:

    def test_14a_chunks_in_reverse_order(self, gram):
        """Emit chunks in reverse order (3, 2, 4) — does Dragon accept?"""
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        # Collect chunks
        chunks = {}
        pos = 8
        while pos < len(binary):
            cid, csize = struct.unpack_from("LL", binary, pos)
            chunks[cid] = binary[pos : pos + 8 + csize]
            pos += 8 + csize

        # Reassemble in reverse order: 3, 2, 4
        reordered = binary[:8]  # SRHEADER
        for cid in [3, 2, 4]:
            if cid in chunks:
                reordered += chunks[cid]

        _load_and_test(gram, reordered, "r", ["hello"])

    def test_14b_chunk2_before_chunk4(self, gram):
        """Words chunk before exports chunk."""
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        chunks = {}
        pos = 8
        while pos < len(binary):
            cid, csize = struct.unpack_from("LL", binary, pos)
            chunks[cid] = binary[pos : pos + 8 + csize]
            pos += 8 + csize

        reordered = binary[:8]
        for cid in [2, 4, 3]:
            if cid in chunks:
                reordered += chunks[cid]

        _load_and_test(gram, reordered, "r", ["hello"])

    def test_14c_redundant_wrapping(self, gram):
        """Single word wrapped in START(SEQ)...END(SEQ).

        FINDING: Dragon may accept or reject redundant wrapping.
        """
        c = GrammarCompiler()
        c.parse("<r> exported = hello ;")
        # Override rule definition to add redundant wrapping
        c.rule_defines["r"] = [("start", 1), ("word", 1), ("end", 1)]
        binary = c.emit("ansi")

        g = gram()
        try:
            g.load(binary)
            cb = CallbackCollector()
            g.setResultsCallback(cb)
            g.activate("r", 0)
            do_mimic(["hello"], pause=1.5)
            cb.wait(timeout=8.0)
            assert len(cb.results) > 0
            assert cb.results[-1] == ["hello"]
            print("  FINDING: Dragon ACCEPTS redundant SEQ wrapping")
            g.deactivate("r")
        except Exception as e:
            print(f"  FINDING: Dragon REJECTS redundant SEQ wrapping: {e}")

    def test_14d_no_wrapping(self, gram):
        """Single word with NO sequence wrapper (already the default)."""
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        parsed = parse_grammar_binary(binary)
        # Verify no START/END in the rule definition
        symbols = parsed["chunks"][3][0]["symbols"]
        assert symbols == [("word", 1)], "Single word should have no wrapping"

        _load_and_test(gram, binary, "r", ["hello"])

    def test_14e_unknown_chunk_id(self, gram):
        """Extra chunk with unknown ID — does Dragon skip it?

        FINDING: Dragon rejects grammars with unknown chunks.
        """
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        # Append an unknown chunk at the end
        unknown_chunk = struct.pack("LL", 0x9999, 4) + b"\x00" * 4
        modified = binary + unknown_chunk

        g = gram()
        try:
            g.load(modified)
            cb = CallbackCollector()
            g.setResultsCallback(cb)
            g.activate("r", 0)
            do_mimic(["hello"], pause=1.5)
            cb.wait(timeout=8.0)
            print("  FINDING: Dragon ACCEPTS unknown chunks (skips them)")
            g.deactivate("r")
        except Exception as e:
            print(f"  FINDING: Dragon REJECTS unknown chunks: {e}")

    def test_14f_dgnsrckcfg_header(self, gram):
        """Dragon REJECTS 0x1014 extension chunk (DGNSRCKCFG_HEADER).

        VALIDATED: Dragon treats 0x1014 (grammar metadata) the same as
        unknown chunk IDs — "grammar specification is in error".
        These chunks are only used internally by Dragon's voice command
        wizard, not accepted via programmatic GrammarLoad.
        """
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")

        # Build minimal DGNSRCKCFG_HEADER:
        #   dwSize(4) + szApplication(64 = WCHAR[32]) + szState(64 = WCHAR[32])
        app_name = "TestApp".encode("utf-16-le").ljust(64, b"\x00")
        state_name = "default".encode("utf-16-le").ljust(64, b"\x00")
        block_size = 4 + 64 + 64  # 132 bytes
        block = struct.pack("L", block_size) + app_name + state_name
        chunk_1014 = struct.pack("LL", 0x1014, len(block)) + block

        modified = binary + chunk_1014

        g = gram()
        try:
            g.load(modified)
            g.unload()
            pytest.fail("Expected Dragon to reject 0x1014 chunk")
        except Exception:
            pass  # Expected: Dragon rejects this

    @pytest.mark.skip(reason=(
        "VALIDATED: 0x1016 (DGNSRCKCFG_LISTS) CRASHES Dragon — hangs COM "
        "indefinitely during GrammarLoad, then kills natspeak.exe. "
        "Dragon extension chunks are NOT accepted via programmatic loading."
    ))
    def test_14g_dgnsrckcfg_lists(self, gram):
        """Dragon CRASHES on 0x1016 extension chunk (DGNSRCKCFG_LISTS).

        VALIDATED (2026-02-16): Loading a grammar with 0x1016 causes
        Dragon's COM to hang indefinitely during GrammarLoad, and
        ultimately kills the natspeak.exe process entirely.  Unlike 0x1014
        which returns an error immediately, 0x1016 is catastrophically
        destructive.

        This test is permanently skipped to avoid killing Dragon.
        """
        pass


# ===================================================================
# Level 15: Header Flags
# ===================================================================

class TestLevel15_HeaderFlags:

    def _with_flags(self, flags, gram):
        """Test a simple grammar with specific header flags."""
        binary = compile_grammar("<r> exported = hello ;", encoding="ansi")
        binary = binary[:4] + struct.pack("L", flags) + binary[8:]
        _load_and_test(gram, binary, "r", ["hello"])

    def test_15a_flags_zero(self, gram):
        """Baseline: flags=0 (already validated by all other tests)."""
        self._with_flags(0, gram)

    def test_15b_dontusenoise(self, gram):
        """DGNSRHDRFLAG_DONTUSENOISE (bit 28)."""
        self._with_flags(1 << 28, gram)

    def test_15c_uselmscore(self, gram):
        """DGNSRHDRFLAG_USELMSCORE (bit 29)."""
        self._with_flags(1 << 29, gram)

    def test_15d_languagemodelon(self, gram):
        """DGNSRHDRFLAG_LANGUAGEMODELON (bit 31)."""
        self._with_flags(1 << 31, gram)


# ===================================================================
# Level 16: Edge Cases & Error Conditions
# ===================================================================

class TestLevel16_EdgeCases:

    def test_16a_quoted_words(self, gram):
        """Multi-word token in quotes.

        Note: "hello world" is a single entry in the word table.
        Mimic sends words separately, so we mimic ["hello world"]
        as a single word. Dragon may or may not match it.
        """
        spec = '<r> exported = "hello world" ;'
        binary = compile_grammar(spec, encoding="ansi")
        g = gram()
        cb = CallbackCollector()
        g.load(binary)
        g.setResultsCallback(cb)
        g.activate("r", 0)

        # Try mimicking the multi-word token as a single string
        do_mimic(["hello world"], pause=1.5)
        cb.wait(timeout=5.0)
        if cb.results:
            print(f"  FINDING: Quoted multi-word recognized: {cb.results[-1]}")
        else:
            print("  FINDING: Quoted multi-word not matched by mimic "
                  "(Dragon may need exact single-token match)")
        g.deactivate("r")

    def test_16b_special_chars(self, gram):
        """Words with apostrophes."""
        spec = "<r> exported = don't | it's ;"
        binary = compile_grammar(spec, encoding="ansi")
        _load_and_test(gram, binary, "r", ["don't"])

    def test_16c_long_word_list(self, gram):
        """Stress test: grammar with 50+ alternatives."""
        words = " | ".join(f"word{i}" for i in range(50))
        spec = f"<r> exported = {words} ;"
        binary = compile_grammar(spec, encoding="ansi")
        # Just test that it loads and one word works
        _load_and_test(gram, binary, "r", ["word0"])

    def test_16d_mismatched_start_end(self, gram):
        """Deliberately malformed binary — should Dragon reject it?"""
        c = GrammarCompiler()
        c.parse("<r> exported = hello ;")
        # Override: START without matching END
        c.rule_defines["r"] = [("start", 1), ("word", 1)]
        binary = c.emit("ansi")

        g = gram()
        try:
            g.load(binary)
            # If load succeeds, that's interesting — record it
            print("  NOTE: Dragon accepted mismatched START/END")
            g.unload()
        except Exception as e:
            # Expected: Dragon should reject malformed grammars
            print(f"  NOTE: Dragon rejected mismatched START/END: {e}")

    def test_16e_unknown_chunk_id_only(self, gram):
        """Grammar with ONLY an unknown chunk (no standard chunks)."""
        header = struct.pack("LL", 0, 0)  # SRHEADER
        unknown = struct.pack("LL", 0x9999, 4) + b"\x00" * 4
        binary = header + unknown

        g = gram()
        try:
            g.load(binary)
            print("  NOTE: Dragon accepted grammar with only unknown chunk")
            g.unload()
        except Exception as e:
            print(f"  NOTE: Dragon rejected grammar with only unknown chunk: {e}")

    def test_16f_duplicate_word_ids(self, gram):
        """Same word registered twice in chunk 2 with different IDs."""
        # Build manually: header + exports + words (hello=1, hello=2) + rules
        header = struct.pack("LL", 0, 0)

        # Chunk 4: export "r" = 1
        r_bytes = b"r\x00"
        r_padded = (len(r_bytes) + 3) & ~3
        export_entry = struct.pack("LL%ds" % r_padded, r_padded + 8, 1, r_bytes)
        chunk4 = struct.pack("LL", 4, len(export_entry)) + export_entry

        # Chunk 2: "hello"=1, "hello"=2 (duplicate!)
        h_bytes = b"hello\x00"
        h_padded = (len(h_bytes) + 3) & ~3
        word1 = struct.pack("LL%ds" % h_padded, h_padded + 8, 1, h_bytes)
        word2 = struct.pack("LL%ds" % h_padded, h_padded + 8, 2, h_bytes)
        chunk2 = struct.pack("LL", 2, len(word1) + len(word2)) + word1 + word2

        # Chunk 3: rule 1 = WORD(1)
        sym = struct.pack("HHL", 3, 0, 1)  # WORD, prob=0, id=1
        rule = struct.pack("LL", 8 + len(sym), 1) + sym
        chunk3 = struct.pack("LL", 3, len(rule)) + rule

        binary = header + chunk4 + chunk2 + chunk3

        g = gram()
        try:
            g.load(binary)
            print("  NOTE: Dragon accepted duplicate word IDs")
            g.unload()
        except Exception as e:
            print(f"  NOTE: Dragon rejected duplicate word IDs: {e}")
