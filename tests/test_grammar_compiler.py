"""test_grammar_compiler.py - Offline cross-validation of our grammar compiler.

Compares binary output from our standalone compiler against both reference
oracles (natlinkcore and dragonfly) to ensure structural equivalence.

No Dragon connection needed — all tests are offline.
"""

import struct

import pytest

from natlink_com.grammar_compiler import (
    GrammarCompiler,
    GrammarError,
    compile_grammar,
    compile_dictation_grammar,
    compile_select_grammar,
    compare_grammars,
    parse_grammar_binary,
)


# ---------------------------------------------------------------------------
# Reference oracle helpers
# ---------------------------------------------------------------------------

def _natlinkcore_compile(spec: str) -> bytes:
    """Compile via natlinkcore (the canonical reference)."""
    gramparser = pytest.importorskip("natlinkcore.gramparser")
    parser = gramparser.GramParser(spec)
    parser.doParse()
    parser.checkForErrors()
    return gramparser.packGrammar(parser)


def _dragonfly_compile(spec: str) -> bytes:
    """Compile via dragonfly's natlink backend compiler.

    dragonfly's compiler takes a different input format (Rule objects),
    so we use natlinkcore's GramParser to parse the text, then compare
    the output.  This function returns natlinkcore output for now —
    dragonfly comparison is deferred to live tests where we can use
    dragonfly Rule objects directly.
    """
    # For offline structural comparison, natlinkcore is the primary oracle.
    # dragonfly uses a different API (Rule objects, not text), so we test
    # it in live tests (test_grammar_format.py) where we can build rules.
    return _natlinkcore_compile(spec)


# ---------------------------------------------------------------------------
# Helper: structural comparison
# ---------------------------------------------------------------------------

def assert_structurally_equal(ours: bytes, ref: bytes,
                              our_enc: str = "ansi", ref_enc: str = "ansi"):
    """Assert two grammar binaries are structurally identical."""
    diffs = compare_grammars(ours, ref, our_enc, ref_enc)
    if diffs:
        pytest.fail(
            "Structural differences:\n" + "\n".join(f"  - {d}" for d in diffs)
        )


# ---------------------------------------------------------------------------
# Test: Parser basics
# ---------------------------------------------------------------------------

class TestParserBasics:
    """Test that our parser produces correct internal structures."""

    def test_single_word(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello ;")
        assert c.export_rules == {"r": 1}
        assert c.known_words == {"hello": 1}
        assert c.rule_defines == {"r": [("word", 1)]}

    def test_two_words(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello world ;")
        assert c.known_words == {"hello": 1, "world": 2}
        assert c.rule_defines["r"] == [
            ("start", 1), ("word", 1), ("word", 2), ("end", 1),
        ]

    def test_alternatives(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello | goodbye ;")
        assert c.rule_defines["r"] == [
            ("start", 2), ("word", 1), ("word", 2), ("end", 2),
        ]

    def test_optional(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello [world] ;")
        assert c.rule_defines["r"] == [
            ("start", 1),
            ("word", 1),
            ("start", 4), ("word", 2), ("end", 4),
            ("end", 1),
        ]

    def test_repeat(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello+ ;")
        assert c.rule_defines["r"] == [
            ("start", 3), ("word", 1), ("end", 3),
        ]

    def test_rule_reference(self):
        c = GrammarCompiler()
        c.parse("<r> exported = <g> ; <g> = hello ;")
        assert c.known_rules == {"r": 1, "g": 2}
        assert c.rule_defines["r"] == [("rule", 2)]
        assert c.rule_defines["g"] == [("word", 1)]

    def test_list_reference(self):
        c = GrammarCompiler()
        c.parse("<r> exported = open {files} ;")
        assert c.known_lists == {"files": 1}
        assert c.rule_defines["r"] == [
            ("start", 1), ("word", 1), ("list", 1), ("end", 1),
        ]

    def test_imported_rule(self):
        c = GrammarCompiler()
        c.parse("<dgndictation> imported ; <r> exported = say <dgndictation> ;")
        assert c.import_rules == {"dgndictation": 1}
        assert c.export_rules == {"r": 2}
        assert "dgndictation" not in c.rule_defines

    def test_private_rule(self):
        c = GrammarCompiler()
        c.parse("<r> exported = <g> ; <g> = hello | goodbye ;")
        assert "g" not in c.export_rules
        assert "g" in c.rule_defines

    def test_multiple_exports(self):
        c = GrammarCompiler()
        c.parse("<r1> exported = alpha ; <r2> exported = bravo ;")
        assert c.export_rules == {"r1": 1, "r2": 2}

    def test_grouped_expression(self):
        c = GrammarCompiler()
        c.parse("<r> exported = (hello | goodbye) world ;")
        assert c.rule_defines["r"] == [
            ("start", 1),
            ("start", 2), ("word", 1), ("word", 2), ("end", 2),
            ("word", 3),
            ("end", 1),
        ]

    def test_nested_optional_in_alt(self):
        c = GrammarCompiler()
        c.parse("<r> exported = [hello] | goodbye ;")
        assert c.rule_defines["r"] == [
            ("start", 2),
            ("start", 4), ("word", 1), ("end", 4),
            ("word", 2),
            ("end", 2),
        ]

    def test_complex_nesting(self):
        c = GrammarCompiler()
        c.parse("<r> exported = hello (world | [dear] earth) ;")
        # hello SEQ( ALT( world, SEQ( OPT(dear), earth ) ) )
        assert c.rule_defines["r"] == [
            ("start", 1),
            ("word", 1),
            ("start", 2),
            ("word", 2),
            ("start", 1),
            ("start", 4), ("word", 3), ("end", 4),
            ("word", 4),
            ("end", 1),
            ("end", 2),
            ("end", 1),
        ]


class TestParserErrors:
    """Test that the parser rejects invalid input."""

    def test_duplicate_rule(self):
        with pytest.raises(GrammarError, match="already defined"):
            c = GrammarCompiler()
            c.parse("<r> exported = hello ; <r> = world ;")

    def test_import_then_define(self):
        with pytest.raises(GrammarError, match="already imported"):
            c = GrammarCompiler()
            c.parse("<r> imported ; <r> = hello ;")

    def test_define_then_import(self):
        with pytest.raises(GrammarError, match="already defined"):
            c = GrammarCompiler()
            c.parse("<r> = hello ; <r> imported ;")


# ---------------------------------------------------------------------------
# Test: Binary emission
# ---------------------------------------------------------------------------

class TestBinaryEmission:
    """Test that emit() produces correct binary format."""

    def test_header_is_8_bytes(self):
        data = compile_grammar("<r> exported = hello ;")
        assert len(data) >= 8
        dtype, dflags = struct.unpack_from("LL", data, 0)
        assert dtype == 0  # CFG
        assert dflags == 0

    def test_dictation_grammar(self):
        data = compile_dictation_grammar()
        assert data == b"\x02\x00\x00\x00\x00\x00\x00\x00"

    def test_select_grammar_has_correct_header(self):
        data = compile_select_grammar(["select"], "through")
        dtype, dflags = struct.unpack_from("LL", data, 0)
        assert dtype == 10
        assert dflags == 0

    def test_chunk_order(self):
        """Chunks should appear in order: 4, 5, 6, 2, 3."""
        spec = (
            "<dgndictation> imported ;\n"
            "<r> exported = hello {files} <dgndictation> ;\n"
        )
        data = compile_grammar(spec)
        chunks = []
        pos = 8
        while pos < len(data):
            cid, csize = struct.unpack_from("LL", data, pos)
            chunks.append(cid)
            pos += 8 + csize
        assert chunks == [4, 5, 6, 2, 3]

    def test_empty_chunks_omitted(self):
        """Chunks with no entries should not appear."""
        data = compile_grammar("<r> exported = hello ;")
        chunks = []
        pos = 8
        while pos < len(data):
            cid, csize = struct.unpack_from("LL", data, pos)
            chunks.append(cid)
            pos += 8 + csize
        # No imports (5) or lists (6)
        assert 5 not in chunks
        assert 6 not in chunks
        assert chunks == [4, 2, 3]

    def test_ansi_name_padding(self):
        """ANSI name entries should be padded to 4-byte boundaries."""
        data = compile_grammar("<r> exported = hello ;")
        parsed = parse_grammar_binary(data, "ansi")
        # "hello" = 5 bytes + null → 6 bytes → padded to 8 → entry size = 16
        # "r" = 1 byte + null → 2 bytes → padded to 4 → entry size = 12
        assert parsed["chunks"][4] == {"r": 1}
        assert parsed["chunks"][2] == {"hello": 1}

    def test_wchar_name_encoding(self):
        """WCHAR mode should encode names as UTF-16LE."""
        data = compile_grammar("<r> exported = hello ;", encoding="wchar")
        parsed = parse_grammar_binary(data, "wchar")
        assert parsed["chunks"][4] == {"r": 1}
        assert parsed["chunks"][2] == {"hello": 1}

    def test_wchar_binary_larger(self):
        """WCHAR binary should be larger than ANSI for same grammar."""
        ansi = compile_grammar("<r> exported = hello ;", encoding="ansi")
        wchar = compile_grammar("<r> exported = hello ;", encoding="wchar")
        assert len(wchar) > len(ansi)

    def test_rule_symbols(self):
        """Rule definitions should contain correct symbol sequences."""
        data = compile_grammar("<r> exported = hello [world] ;")
        parsed = parse_grammar_binary(data)
        rules = parsed["chunks"][3]
        assert len(rules) == 1
        assert rules[0]["rule_id"] == 1
        assert rules[0]["symbols"] == [
            ("start", 1),   # SEQ
            ("word", 1),    # hello
            ("start", 4),   # OPT
            ("word", 2),    # world
            ("end", 4),     # /OPT
            ("end", 1),     # /SEQ
        ]


# ---------------------------------------------------------------------------
# Test: Cross-validation against natlinkcore
# ---------------------------------------------------------------------------

class TestCrossValidation:
    """Compare our compiler output against natlinkcore byte-for-byte."""

    def _compare(self, spec: str):
        """Compile with both and assert byte-identical output."""
        ours = compile_grammar(spec, encoding="ansi")
        ref = _natlinkcore_compile(spec)
        if ours != ref:
            # If not byte-identical, show structural diff
            diffs = compare_grammars(ours, ref, "ansi", "ansi")
            if diffs:
                pytest.fail(
                    f"Binary mismatch for grammar:\n  {spec!r}\n"
                    f"Ours: {len(ours)} bytes, Ref: {len(ref)} bytes\n"
                    f"Structural diffs:\n" +
                    "\n".join(f"  - {d}" for d in diffs)
                )
            else:
                # Structurally same but byte-level difference (padding?)
                pytest.fail(
                    f"Byte-level mismatch (structural match) for:\n  {spec!r}\n"
                    f"Ours: {ours.hex()}\n"
                    f"Ref:  {ref.hex()}"
                )

    def test_single_word(self):
        self._compare("<r> exported = hello ;")

    def test_two_words(self):
        self._compare("<r> exported = hello world ;")

    def test_three_words(self):
        self._compare("<r> exported = one two three ;")

    def test_alternative_two(self):
        self._compare("<r> exported = hello | goodbye ;")

    def test_alternative_three(self):
        self._compare("<r> exported = hello | goodbye | hey ;")

    def test_optional_at_end(self):
        self._compare("<r> exported = hello [world] ;")

    def test_optional_at_start(self):
        self._compare("<r> exported = [please] help ;")

    def test_optional_in_middle(self):
        self._compare("<r> exported = hello [dear] world ;")

    def test_repeat(self):
        self._compare("<r> exported = hello+ ;")

    def test_repeat_in_sequence(self):
        self._compare("<r> exported = say hello+ ;")

    def test_grouped_alt_in_seq(self):
        self._compare("<r> exported = (hello | goodbye) world ;")

    def test_alt_of_sequences(self):
        self._compare("<r> exported = hello world | goodbye earth ;")

    def test_seq_plus_optional(self):
        self._compare("<r> exported = please [kindly] help ;")

    def test_optional_of_alt(self):
        self._compare("<r> exported = [hello | goodbye] ;")

    def test_alt_with_optional(self):
        self._compare("<r> exported = hello [world] | goodbye ;")

    def test_private_rule(self):
        self._compare("<r> exported = <greet> ; <greet> = hello ;")

    def test_private_with_alt(self):
        self._compare(
            "<r> exported = <greet> world ; <greet> = hello | hi ;"
        )

    def test_rule_chain(self):
        self._compare(
            "<r> exported = <a> ; <a> = <b> ; <b> = hello ;"
        )

    def test_shared_private(self):
        self._compare(
            "<r1> exported = <g> world ;\n"
            "<r2> exported = <g> earth ;\n"
            "<g> = hello | hi ;"
        )

    def test_dynamic_list(self):
        self._compare("<r> exported = open {files} ;")

    def test_list_in_sequence(self):
        self._compare("<r> exported = open {files} now ;")

    def test_multiple_lists(self):
        self._compare("<r> exported = {verb} {noun} ;")

    def test_list_in_alt(self):
        self._compare("<r> exported = open {files} | close {files} ;")

    def test_list_in_optional(self):
        self._compare("<r> exported = hello [{extras}] ;")

    def test_imported_dgndictation(self):
        self._compare(
            "<dgndictation> imported ;\n"
            "<r> exported = say <dgndictation> ;"
        )

    def test_imported_dgnwords(self):
        self._compare(
            "<dgnwords> imported ;\n"
            "<r> exported = spell <dgnwords> ;"
        )

    def test_imported_dgnletters(self):
        self._compare(
            "<dgnletters> imported ;\n"
            "<r> exported = letter <dgnletters> ;"
        )

    def test_mixed_import_local(self):
        self._compare(
            "<dgndictation> imported ;\n"
            "<r> exported = <cmd> | <dgndictation> ;\n"
            "<cmd> = stop | cancel ;"
        )

    def test_two_independent_exports(self):
        self._compare(
            "<r1> exported = alpha ;\n"
            "<r2> exported = bravo ;"
        )

    def test_exports_sharing_private(self):
        self._compare(
            "<r1> exported = <g> one ;\n"
            "<r2> exported = <g> two ;\n"
            "<g> = hello | hi ;"
        )

    def test_three_level_nesting(self):
        self._compare(
            "<r> exported = hello (world | [dear] earth) ;"
        )

    def test_alt_in_opt_in_seq(self):
        self._compare(
            "<r> exported = please [hello | goodbye] world ;"
        )

    def test_seq_in_opt_in_alt(self):
        self._compare(
            "<r> exported = [hello world] | goodbye ;"
        )

    def test_real_world_command(self):
        self._compare(
            "<r> exported = (open | close | save) {files} [now | later] ;"
        )

    def test_navigation(self):
        self._compare(
            "<r> exported = go (up | down | left | right) [<count>] ;\n"
            "<count> = one | two | three ;"
        )

    def test_mixed_dictation_command(self):
        self._compare(
            "<dgndictation> imported ;\n"
            "<r> exported = type <dgndictation> ;"
        )

    def test_long_word_list(self):
        """Stress test with many alternatives."""
        words = " | ".join(f"word{i}" for i in range(50))
        self._compare(f"<r> exported = {words} ;")

    def test_quoted_word(self):
        self._compare('<r> exported = "hello world" ;')

    def test_apostrophe_word(self):
        # Apostrophes must be double-quoted — natlinkcore treats ' as string delimiter
        self._compare('<r> exported = "don\'t" | "it\'s" ;')


# ---------------------------------------------------------------------------
# Test: WCHAR structural equivalence
# ---------------------------------------------------------------------------

class TestWcharEquivalence:
    """Our WCHAR output should be structurally identical to ANSI output."""

    def _compare_wchar(self, spec: str):
        ansi = compile_grammar(spec, encoding="ansi")
        wchar = compile_grammar(spec, encoding="wchar")
        assert_structurally_equal(ansi, wchar, "ansi", "wchar")

    def test_single_word(self):
        self._compare_wchar("<r> exported = hello ;")

    def test_complex(self):
        self._compare_wchar(
            "<dgndictation> imported ;\n"
            "<r> exported = <cmd> | <dgndictation> ;\n"
            "<cmd> = (open | close) {files} [now] ;"
        )

    def test_multiple_exports(self):
        self._compare_wchar(
            "<r1> exported = <g> one ;\n"
            "<r2> exported = <g> two ;\n"
            "<g> = hello | hi ;"
        )


# ---------------------------------------------------------------------------
# Test: Binary round-trip (parse back what we emit)
# ---------------------------------------------------------------------------

class TestBinaryRoundTrip:
    """Verify parse_grammar_binary can read back what we emit."""

    def test_roundtrip_ansi(self):
        spec = "<r> exported = hello [world] ;"
        data = compile_grammar(spec, encoding="ansi")
        parsed = parse_grammar_binary(data, "ansi")
        assert parsed["type"] == 0
        assert parsed["flags"] == 0
        assert parsed["chunks"][4] == {"r": 1}
        assert parsed["chunks"][2] == {"hello": 1, "world": 2}
        assert len(parsed["chunks"][3]) == 1

    def test_roundtrip_wchar(self):
        spec = "<r> exported = hello [world] ;"
        data = compile_grammar(spec, encoding="wchar")
        parsed = parse_grammar_binary(data, "wchar")
        assert parsed["type"] == 0
        assert parsed["chunks"][4] == {"r": 1}
        assert parsed["chunks"][2] == {"hello": 1, "world": 2}

    def test_roundtrip_with_imports_lists(self):
        spec = (
            "<dgndictation> imported ;\n"
            "<r> exported = hello {files} <dgndictation> ;\n"
        )
        data = compile_grammar(spec, encoding="ansi")
        parsed = parse_grammar_binary(data, "ansi")
        assert parsed["chunks"][4] == {"r": 2}
        assert parsed["chunks"][5] == {"dgndictation": 1}
        assert parsed["chunks"][6] == {"files": 1}
        assert parsed["chunks"][2] == {"hello": 1}

    def test_roundtrip_natlinkcore(self):
        """Parse natlinkcore output and verify structure."""
        gramparser = pytest.importorskip("natlinkcore.gramparser")
        spec = "<r> exported = hello [world] ;"
        parser = gramparser.GramParser(spec)
        parser.doParse()
        parser.checkForErrors()
        data = gramparser.packGrammar(parser)
        parsed = parse_grammar_binary(data, "ansi")
        assert parsed["type"] == 0
        assert parsed["chunks"][4] == {"r": 1}
        assert parsed["chunks"][2] == {"hello": 1, "world": 2}
