"""grammar_compiler.py - SAPI 4 + Dragon grammar compiler.

A pure-Python compiler based on docs/grammar_binary_format.md.
Supports CFG, dictation, and Dragon SELECT grammars with both
ANSI and WCHAR (UTF-16LE) string encoding.  No Dragon needed.
"""

import re
import struct
from locale import getpreferredencoding
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Operation codes (for START/END symbols)
SEQ_CODE = 1   # SRCFGO_SEQUENCE
ALT_CODE = 2   # SRCFGO_ALTERNATIVE
REP_CODE = 3   # SRCFGO_REPEAT
OPT_CODE = 4   # SRCFGO_OPTIONAL

# Symbol types
SYM_START = 1  # SRCFG_STARTOPERATION
SYM_END = 2    # SRCFG_ENDOPERATION
SYM_WORD = 3   # SRCFG_WORD
SYM_RULE = 4   # SRCFG_RULE
SYM_LIST = 6   # SRCFG_LIST

# Chunk IDs
CHUNK_LANGUAGE = 1
CHUNK_WORDS = 2
CHUNK_RULES = 3
CHUNK_EXPORTS = 4
CHUNK_IMPORTS = 5
CHUNK_LISTS = 6

# Element type name → symbol type number (for binary emission)
_ELEM_TYPE_MAP = {"start": SYM_START, "end": SYM_END, "word": SYM_WORD,
                  "rule": SYM_RULE, "list": SYM_LIST}

# Type alias for rule definitions: list of (type_str, value) tuples
Definition = List[Tuple[str, int]]


class GrammarError(Exception):
    """Raised on grammar syntax errors."""


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

class _Tokenizer:
    """Simple tokenizer for grammar text syntax (§8 of the spec)."""

    WORD = "word"
    RULE = "rule"
    LIST = "list"
    EQUALS = "="
    SEMI = ";"
    PIPE = "|"
    PLUS = "+"
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    EXPORTED = "exported"
    IMPORTED = "imported"
    EOF = "eof"

    _SINGLE = {"=": EQUALS, ";": SEMI, "|": PIPE, "+": PLUS,
               "(": LPAREN, ")": RPAREN, "[": LBRACKET, "]": RBRACKET}

    def __init__(self, text: str):
        self.tokens: List[Tuple[str, str]] = []
        self._tokenize(text)
        self._idx = 0

    def _tokenize(self, text: str):
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]

            # Whitespace
            if ch in " \t\r\n":
                i += 1
                continue

            # Line comments
            if ch == "#":
                while i < n and text[i] != "\n":
                    i += 1
                continue

            # Rule reference <name>
            if ch == "<":
                try:
                    j = text.index(">", i + 1)
                except ValueError:
                    raise GrammarError(
                        f"Unterminated rule reference at position {i}")
                self.tokens.append((self.RULE, text[i + 1 : j]))
                i = j + 1
                continue

            # List reference {name}
            if ch == "{":
                try:
                    j = text.index("}", i + 1)
                except ValueError:
                    raise GrammarError(
                        f"Unterminated list reference at position {i}")
                self.tokens.append((self.LIST, text[i + 1 : j]))
                i = j + 1
                continue

            # Quoted word
            if ch in ('"', "'"):
                try:
                    j = text.index(ch, i + 1)
                except ValueError:
                    raise GrammarError(
                        f"Unterminated quoted string at position {i}")
                self.tokens.append((self.WORD, text[i + 1 : j]))
                i = j + 1
                continue

            # Single-character operators
            if ch in self._SINGLE:
                self.tokens.append((self._SINGLE[ch], ch))
                i += 1
                continue

            # Bare word (may contain letters, digits, _, -, ', \)
            m = re.match(r"[a-zA-Z0-9_\-'\\]+", text[i:])
            if m:
                word = m.group(0)
                if word == "exported":
                    self.tokens.append((self.EXPORTED, word))
                elif word == "imported":
                    self.tokens.append((self.IMPORTED, word))
                else:
                    self.tokens.append((self.WORD, word))
                i += len(word)
                continue

            raise GrammarError(
                f"Unexpected character at position {i}: {text[i]!r}"
            )
        self.tokens.append((self.EOF, ""))

    def peek(self) -> Tuple[str, str]:
        return self.tokens[self._idx]

    def next(self) -> Tuple[str, str]:
        tok = self.tokens[self._idx]
        self._idx += 1
        return tok

    def expect(self, ttype: str) -> str:
        tok = self.next()
        if tok[0] != ttype:
            raise GrammarError(
                f"Expected {ttype}, got {tok[0]} ({tok[1]!r})"
            )
        return tok[1]


# ---------------------------------------------------------------------------
# Parser + Compiler
# ---------------------------------------------------------------------------

class GrammarCompiler:
    """Parses grammar text and emits SAPI 4.0 binary."""

    def __init__(self):
        self.known_rules: Dict[str, int] = {}
        self.known_words: Dict[str, int] = {}
        self.known_lists: Dict[str, int] = {}
        self.next_rule = 1
        self.next_word = 1
        self.next_list = 1
        self.export_rules: Dict[str, int] = {}
        self.import_rules: Dict[str, int] = {}
        self.rule_defines: Dict[str, Definition] = {}

    # -- ID allocation (encounter-order, 1-based) --

    def _get_rule_id(self, name: str) -> int:
        if name not in self.known_rules:
            self.known_rules[name] = self.next_rule
            self.next_rule += 1
        return self.known_rules[name]

    def _get_word_id(self, word: str) -> int:
        if word not in self.known_words:
            self.known_words[word] = self.next_word
            self.next_word += 1
        return self.known_words[word]

    def _get_list_id(self, name: str) -> int:
        if name not in self.known_lists:
            self.known_lists[name] = self.next_list
            self.next_list += 1
        return self.known_lists[name]

    # -- Recursive-descent parser --

    def parse(self, text: str):
        """Parse grammar text into internal structures."""
        tok = _Tokenizer(text)
        while tok.peek()[0] != _Tokenizer.EOF:
            self._parse_rule(tok)

    def _parse_rule(self, tok: _Tokenizer):
        """Parse: <name> [exported] = expr ; | <name> imported ;"""
        tt, name = tok.next()
        if tt != _Tokenizer.RULE:
            raise GrammarError(f"Expected rule name, got {tt} ({name!r})")

        rule_id = self._get_rule_id(name)

        tt2, _ = tok.peek()

        # Imported rule
        if tt2 == _Tokenizer.IMPORTED:
            tok.next()
            tok.expect(_Tokenizer.SEMI)
            if name in self.rule_defines:
                raise GrammarError(
                    f"Rule {name!r} already defined, cannot import"
                )
            self.import_rules[name] = rule_id
            return

        # Exported or private rule
        exported = False
        if tt2 == _Tokenizer.EXPORTED:
            tok.next()
            exported = True

        tok.expect(_Tokenizer.EQUALS)
        definition = self._parse_expr(tok)
        tok.expect(_Tokenizer.SEMI)

        if name in self.import_rules:
            raise GrammarError(
                f"Rule {name!r} already imported, cannot define"
            )
        if name in self.rule_defines:
            raise GrammarError(f"Rule {name!r} already defined")

        self.rule_defines[name] = definition
        if exported:
            self.export_rules[name] = rule_id

    def _parse_expr(self, tok: _Tokenizer) -> Definition:
        """Alternatives: expr2 (| expr2)*"""
        items = [self._parse_expr2(tok)]
        while tok.peek()[0] == _Tokenizer.PIPE:
            tok.next()
            items.append(self._parse_expr2(tok))

        if len(items) == 1:
            return items[0]

        result: Definition = [("start", ALT_CODE)]
        for item in items:
            result.extend(item)
        result.append(("end", ALT_CODE))
        return result

    def _parse_expr2(self, tok: _Tokenizer) -> Definition:
        """Sequence: expr3 expr3 ..."""
        items = [self._parse_expr3(tok)]
        while tok.peek()[0] in (
            _Tokenizer.WORD, _Tokenizer.RULE, _Tokenizer.LIST,
            _Tokenizer.LPAREN, _Tokenizer.LBRACKET,
        ):
            items.append(self._parse_expr3(tok))

        if len(items) == 1:
            return items[0]

        result: Definition = [("start", SEQ_CODE)]
        for item in items:
            result.extend(item)
        result.append(("end", SEQ_CODE))
        return result

    def _parse_expr3(self, tok: _Tokenizer) -> Definition:
        """Repeat: expr4+"""
        item = self._parse_expr4(tok)
        if tok.peek()[0] == _Tokenizer.PLUS:
            tok.next()
            return [("start", REP_CODE)] + item + [("end", REP_CODE)]
        return item

    def _parse_expr4(self, tok: _Tokenizer) -> Definition:
        """Atom: word, <rule>, {list}, (expr), [expr]"""
        tt, val = tok.peek()

        if tt == _Tokenizer.WORD:
            tok.next()
            return [("word", self._get_word_id(val))]

        if tt == _Tokenizer.RULE:
            tok.next()
            return [("rule", self._get_rule_id(val))]

        if tt == _Tokenizer.LIST:
            tok.next()
            return [("list", self._get_list_id(val))]

        if tt == _Tokenizer.LPAREN:
            tok.next()
            expr = self._parse_expr(tok)
            tok.expect(_Tokenizer.RPAREN)
            return expr

        if tt == _Tokenizer.LBRACKET:
            tok.next()
            expr = self._parse_expr(tok)
            tok.expect(_Tokenizer.RBRACKET)
            return [("start", OPT_CODE)] + expr + [("end", OPT_CODE)]

        raise GrammarError(f"Unexpected token: {tt} ({val!r})")

    # -- Binary emission --

    def emit(self, encoding: str = "ansi") -> bytes:
        """Emit SAPI 4.0 binary.

        encoding: "ansi" for 8-bit strings, "wchar" for UTF-16LE
        """
        parts = [struct.pack("LL", 0, 0)]  # SRHEADER: type=CFG, flags=0

        if self.export_rules:
            parts.append(self._emit_name_chunk(CHUNK_EXPORTS, self.export_rules, encoding))
        if self.import_rules:
            parts.append(self._emit_name_chunk(CHUNK_IMPORTS, self.import_rules, encoding))
        if self.known_lists:
            parts.append(self._emit_name_chunk(CHUNK_LISTS, self.known_lists, encoding))
        if self.known_words:
            parts.append(self._emit_name_chunk(CHUNK_WORDS, self.known_words, encoding))
        if self.rule_defines:
            parts.append(self._emit_rules_chunk())

        return b"".join(parts)

    def _padded_name_bytes(self, name: str, encoding: str) -> Tuple[int, bytes]:
        """Return (padded_len, packed_name_bytes) for a name-table entry.

        For ANSI: matches natlinkcore formula ``(len(word) + 4) & 0xFFFC``
        where ``word`` is the encoded bytes *without* null terminator and the
        ``%ds`` struct format zero-pads to ``padded_len``.

        For WCHAR: ``byteLen = (wcslen+1)*2``, ``paddedLen = (byteLen+3)&~3``.
        """
        if encoding == "wchar":
            raw = name.encode("utf-16-le")  # without null
            byte_len = len(raw) + 2  # +2 for null WCHAR
            padded_len = (byte_len + 3) & ~3
        else:
            raw = name.encode(getpreferredencoding())  # without null
            padded_len = (len(raw) + 4) & 0xFFFC
        # Return padded_len and the raw bytes (struct.pack %ds will zero-pad)
        return padded_len, raw

    def _emit_name_chunk(self, chunk_id: int, names: Dict[str, int],
                         encoding: str) -> bytes:
        """Emit a name-table chunk (types 2, 4, 5, 6)."""
        entries = []
        total = 0
        for name, num in names.items():
            padded_len, raw = self._padded_name_bytes(name, encoding)
            entry = struct.pack(
                "LL%ds" % padded_len, padded_len + 8, num, raw
            )
            entries.append(entry)
            total += padded_len + 8
        return struct.pack("LL", chunk_id, total) + b"".join(entries)

    def _emit_rules_chunk(self) -> bytes:
        """Emit chunk 3 (rule definitions)."""
        entries = []
        total = 0
        for name, definition in self.rule_defines.items():
            rule_id = self.known_rules[name]
            symbols = b""
            for elem_type, value in definition:
                symbols += struct.pack(
                    "HHL", _ELEM_TYPE_MAP[elem_type], 0, value
                )
            rule_size = 8 + len(symbols)
            entries.append(struct.pack("LL", rule_size, rule_id) + symbols)
            total += rule_size
        return struct.pack("LL", CHUNK_RULES, total) + b"".join(entries)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_grammar(spec: str, *, encoding: str = "ansi") -> bytes:
    """Compile a grammar spec string to SAPI 4.0 binary.

    encoding: "ansi" for 8-bit strings, "wchar" for UTF-16LE
    """
    from ._grammar_parser import parse
    t = parse(spec)
    # Transplant parsed state into the emitter
    compiler = GrammarCompiler()
    compiler.known_rules = t.known_rules
    compiler.known_words = t.known_words
    compiler.known_lists = t.known_lists
    compiler.export_rules = t.export_rules
    compiler.import_rules = t.import_rules
    compiler.rule_defines = t.rule_defines
    compiler.next_rule = t.next_rule
    compiler.next_word = t.next_word
    compiler.next_list = t.next_list
    return compiler.emit(encoding)


def compile_dictation_grammar() -> bytes:
    """Return the minimal 8-byte dictation grammar (type=2, flags=0)."""
    return struct.pack("LL", 2, 0)


def compile_select_grammar(
    select_words: Optional[List[str]] = None,
    through_word: str = "through",
) -> bytes:
    """Compile a SELECT grammar (type 10).

    Uses ANSI encoding to match the existing _helpers.compile_select_grammar.
    """
    if select_words is None:
        select_words = ["select"]

    def _pack_chunk(chunk_type: int, words: List[str]) -> bytes:
        entries = []
        total = 0
        for word in words:
            encoded = word.encode("latin-1")
            padded = (len(encoded) + 4) & 0xFFFC
            entries.append(struct.pack("LL%ds" % padded, padded + 8, 0, encoded))
            total += padded + 8
        return struct.pack("LL", chunk_type, total) + b"".join(entries)

    parts = [struct.pack("LL", 10, 0)]  # SRHEADER: type=SELECT, flags=0
    parts.append(_pack_chunk(0x1017, select_words))
    if through_word:
        parts.append(_pack_chunk(0x1018, [through_word]))
    return b"".join(parts)


# ---------------------------------------------------------------------------
# Binary Grammar Parser (for cross-validation tests)
# ---------------------------------------------------------------------------

def parse_grammar_binary(data: bytes, encoding: str = "ansi") -> dict:
    """Parse a SAPI 4.0 grammar binary back into a structured dict.

    Returns::

        {
            "type": int,          # 0=CFG, 2=Dictation, 10=SELECT
            "flags": int,
            "chunks": {
                chunk_id: <content>,
            },
        }

    For name-table chunks (2, 4, 5, 6), content is a dict {name: id}.
    For chunk 3 (rules), content is a list of
    {"rule_id": int, "symbols": [(type_str, value), ...]}.
    """
    if len(data) < 8:
        raise ValueError("Data too short for SRHEADER")

    dtype, dflags = struct.unpack_from("LL", data, 0)
    result = {"type": dtype, "flags": dflags, "chunks": {}}
    pos = 8

    while pos < len(data):
        if pos + 8 > len(data):
            break
        chunk_id, chunk_size = struct.unpack_from("LL", data, pos)
        pos += 8
        chunk_data = data[pos : pos + chunk_size]
        pos += chunk_size

        if chunk_id in (CHUNK_WORDS, CHUNK_EXPORTS, CHUNK_IMPORTS, CHUNK_LISTS):
            result["chunks"][chunk_id] = _parse_name_chunk(
                chunk_data, encoding
            )
        elif chunk_id == CHUNK_RULES:
            result["chunks"][chunk_id] = _parse_rules_chunk(chunk_data)
        else:
            # Unknown/extension chunk — store raw bytes
            result["chunks"][chunk_id] = chunk_data

    return result


def _parse_name_chunk(data: bytes, encoding: str) -> Dict[str, int]:
    """Parse a name-table chunk into {name: id}."""
    names: Dict[str, int] = {}
    pos = 0
    while pos < len(data):
        entry_size, entry_num = struct.unpack_from("LL", data, pos)
        name_bytes = data[pos + 8 : pos + entry_size]
        # Decode the name (strip padding/nulls)
        if encoding == "wchar":
            # UTF-16LE: find the first null WCHAR
            raw = name_bytes
            name = raw.decode("utf-16-le").rstrip("\x00")
        else:
            name = name_bytes.rstrip(b"\x00").decode(getpreferredencoding())
        names[name] = entry_num
        pos += entry_size
    return names


# Reverse map: symbol type number → type string
_SYM_TYPE_REV = {v: k for k, v in _ELEM_TYPE_MAP.items()}


def _parse_rules_chunk(data: bytes) -> list:
    """Parse chunk 3 (rule definitions) into a list of rule dicts."""
    rules = []
    pos = 0
    while pos < len(data):
        rule_size, rule_id = struct.unpack_from("LL", data, pos)
        symbols = []
        sym_pos = pos + 8
        while sym_pos < pos + rule_size:
            wtype, wprob, dwvalue = struct.unpack_from("HHL", data, sym_pos)
            type_str = _SYM_TYPE_REV.get(wtype, f"unknown({wtype})")
            symbols.append((type_str, dwvalue))
            sym_pos += 8
        rules.append({"rule_id": rule_id, "symbols": symbols})
        pos += rule_size
    return rules


def compare_grammars(a: bytes, b: bytes, encoding_a: str = "ansi",
                     encoding_b: str = "ansi") -> List[str]:
    """Compare two grammar binaries structurally.

    Returns a list of differences (empty = identical structure).
    """
    diffs = []
    pa = parse_grammar_binary(a, encoding_a)
    pb = parse_grammar_binary(b, encoding_b)

    if pa["type"] != pb["type"]:
        diffs.append(f"type: {pa['type']} vs {pb['type']}")
    if pa["flags"] != pb["flags"]:
        diffs.append(f"flags: {pa['flags']} vs {pb['flags']}")

    all_chunks = set(pa["chunks"]) | set(pb["chunks"])
    for cid in sorted(all_chunks):
        ca = pa["chunks"].get(cid)
        cb = pb["chunks"].get(cid)
        if ca is None:
            diffs.append(f"chunk {cid}: missing in A")
            continue
        if cb is None:
            diffs.append(f"chunk {cid}: missing in B")
            continue

        if cid == CHUNK_RULES:
            # Compare rules structurally
            if len(ca) != len(cb):
                diffs.append(
                    f"chunk {cid}: {len(ca)} rules vs {len(cb)} rules"
                )
                continue
            for i, (ra, rb) in enumerate(zip(ca, cb)):
                if ra["rule_id"] != rb["rule_id"]:
                    diffs.append(
                        f"chunk {cid} rule {i}: id {ra['rule_id']} vs {rb['rule_id']}"
                    )
                if ra["symbols"] != rb["symbols"]:
                    diffs.append(
                        f"chunk {cid} rule {i}: symbols differ\n"
                        f"  A: {ra['symbols']}\n  B: {rb['symbols']}"
                    )
        elif isinstance(ca, dict) and isinstance(cb, dict):
            # Name-table chunks: compare name→id mappings
            if ca != cb:
                diffs.append(f"chunk {cid}: {ca} vs {cb}")
        else:
            if ca != cb:
                diffs.append(f"chunk {cid}: raw data differs")

    return diffs
