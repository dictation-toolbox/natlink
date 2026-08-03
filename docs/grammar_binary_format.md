# Dragon NaturallySpeaking Grammar Binary Format

This document describes the binary grammar format accepted by Dragon
NaturallySpeaking via the SAPI 4.0 `ISRCentral::GrammarLoad()` COM method.
It is sufficient to build a grammar compiler in any language.

The format is derived from the Microsoft SAPI 4.0 specification with Dragon (Nuance) extensions. This Represents best effort with an LLM to implement and document.

---

## 1  Grammar Types

Dragon supports three grammar types, distinguished by the first DWORD of the
binary blob (the header type field):

| Header type | dwType | Purpose |
|-------------|-------:|---------|
| CFG | 0 | Command grammars — structured rules with words, lists, alternatives |
| Dictation | 2 | Free-form speech recognition |
| SELECT | 10 | Select-and-say word lists (Dragon-only) |

When calling `ISRCentral::GrammarLoad()`, the caller passes an `SRGRMFMT`
enum value as the first parameter.  This must match the `dwType`:

| `dwType` | `SRGRMFMT` to pass |
|---------:|--------------------|
| 0 | `SRGRMFMT_CFGNATIVE` (0x8000) — preferred; fall back to `SRGRMFMT_CFG` (0x0000) if the engine rejects it |
| 2 | `SRGRMFMT_DICTATION` (0x0002) |
| 10 | `SRGRMFMT_DRAGONNATIVE1` (0x8101) |

See §15 for the full `SRGRMFMT` enum.

This document focuses on the **CFG format** (type 0), which is what grammar
compilers produce.  Dictation and SELECT are covered in §12 and §13.

---

## 2  String Encoding

All SAPI 4.0 grammar structures have ANSI (A) and Unicode (W) variants.
Dragon accepts **both** encodings:

- **ANSI (8-bit)**: Use locale-preferred encoding (cp1252 on Western Windows).
  Set `dwFlags = 0`.  This is what natlinkcore and dragonfly produce.
- **Unicode (UTF-16LE)**: All strings are null-terminated `WCHAR` (2 bytes per
  character).  Set `SRHDRFLAG_UNICODE` (bit 0) in `dwFlags`.

**IMPORTANT — validated live (2026-02-16):** Dragon 13 does **NOT** auto-detect
the string encoding.  `dwFlags` bit 0 controls interpretation:

| `dwFlags` bit 0 | String encoding expected |
|:----------------:|--------------------------|
| 0 (clear) | ANSI (8-bit) |
| 1 (set) | Unicode (UTF-16LE WCHAR) |

If you emit WCHAR strings but leave bit 0 clear, grammars load and activate
without error but **recognition silently fails** — Dragon interprets the
UTF-16LE bytes as ANSI, producing garbled word entries that never match.

For maximum compatibility, use **ANSI with `dwFlags = 0`**.

---

## 3  Overall Binary Layout

All multi-byte integers are **little-endian**.  All strings are
null-terminated and **padded to a 4-byte boundary** (ANSI or WCHAR per §2).

```
┌──────────────────────────────────────┐
│ SRHEADER  (8 bytes)                  │
├──────────────────────────────────────┤
│ SRCHUNK   Exported rules  (type 4)   │  ← optional
├──────────────────────────────────────┤
│ SRCHUNK   Imported rules  (type 5)   │  ← optional
├──────────────────────────────────────┤
│ SRCHUNK   Lists           (type 6)   │  ← optional
├──────────────────────────────────────┤
│ SRCHUNK   Words           (type 2)   │  ← optional
├──────────────────────────────────────┤
│ SRCHUNK   Rule defs       (type 3)   │  ← optional
├──────────────────────────────────────┤
│ (Dragon extension chunks, if any)    │  ← optional
└──────────────────────────────────────┘
```

**Validated live (2026-02-16):**
- Chunks may appear in **any order** — Dragon accepts chunks 3,2,4 and 2,4,3.
- Chunks with zero entries **may be omitted** (natlinkcore style) or
  **emitted as empty** 8-byte headers (dragonfly style) — both work.
- Dragon **rejects unknown chunk IDs** (e.g., 0x9999) with `GrammarError`.

---

## 4  SRHEADER

```
Offset  Size   Field      Value
──────  ────   ─────      ─────
0x00    4      dwType     0 = CFG, 2 = Dictation, 10 = SELECT
0x04    4      dwFlags    Bitfield (see §10); use 0 for standard grammars
```

### SDATA — Passing the Binary Blob

`GrammarLoad()` receives the grammar as an `SDATA` structure:

```c
typedef struct {
    DWORD dwSize;   // Byte count of the entire binary blob
    BYTE *pData;    // Pointer to the SRHEADER
} SDATA;
```

---

## 5  SRCHUNK Envelope

Every chunk starts with an 8-byte header:

```
Offset  Size   Field         Description
──────  ────   ─────         ───────────
0x00    4      dwChunkID     Chunk type identifier (see table below)
0x04    4      dwChunkSize   Byte count of data AFTER this 8-byte header
```

### Standard Chunk IDs (SAPI 4.0)

| ID | Constant | Content |
|---:|----------|---------|
| 1 | `SRCK_LANGUAGE` | Language declaration (not needed for grammar compilation) |
| 2 | `SRCKCFG_WORDS` | Word table |
| 3 | `SRCKCFG_RULES` | Rule definitions (symbol arrays) |
| 4 | `SRCKCFG_EXPORTRULES` | Exported (public) rule names |
| 5 | `SRCKCFG_IMPORTRULES` | Imported rule names |
| 6 | `SRCKCFG_LISTS` | Dynamic list names |

### Dragon Extension Chunk IDs

| ID | Constant | Content |
|---:|----------|---------|
| 0x1014 | `DGNSRCKCFG_HEADER` | Grammar name + application metadata |
| 0x1015 | `DGNSRCKCFG_VCMDCOMMAND` | Voice-command rule descriptions |
| 0x1016 | `DGNSRCKCFG_LISTS` | Serialized list word data |

---

## 6  Name-Table Chunks (types 2, 4, 5, 6)

These four chunk types share an identical entry format.  Each chunk is a
packed array of variable-length entries:

```
Per entry:
Offset  Size   Field      Description
──────  ────   ─────      ───────────
0x00    4      dwSize     Total bytes of this entry (incl. dwSize + dwNum + name)
0x04    4      dwNum      1-based ID
0x08    var    szName     Null-terminated string (ANSI or WCHAR per §2), padded to 4-byte boundary
```

Each name must appear **exactly once** within its chunk.  IDs must be unique
and sequential starting from 1.

**Validated live (2026-02-16):** Dragon accepts duplicate word IDs in chunk 2
(same word registered twice with different IDs) without error.

### String Padding

Names are null-terminated strings, padded so that `dwSize` is a multiple of 4.

**For WCHAR (UTF-16LE) strings:**

```
byteLen   = (wcslen(name) + 1) * 2       // +1 for null terminator, *2 for WCHAR
paddedLen = (byteLen + 3) & ~3            // round up to 4-byte boundary
dwSize    = 8 + paddedLen                 // 8 = sizeof(dwSize) + sizeof(dwNum)
```

Example: the word `"hello"` (5 WCHARs) →
`byteLen = 12`, `paddedLen = 12`, `dwSize = 20`.

Example: the rule name `"greeting"` (8 WCHARs) →
`byteLen = 18`, `paddedLen = 20`, `dwSize = 28`.

**For ANSI (8-bit) strings:**

```
paddedLen = (strlen(name) + 4) & 0xFFFC    // +1 null +3 round, mask to 4-byte
dwSize    = 8 + paddedLen
```

Example: the word `"hello"` (5 bytes) →
`paddedLen = 8`, `dwSize = 16`.

### Chunk 4 — Exported Rules

Lists rules that are **public** (can be activated by name via
`ISRGramCommon::Activate()`).  Only exported rules are visible to Dragon.

### Chunk 5 — Imported Rules

Lists rules that are **imported** from other grammars or are Dragon built-in
rules (see §9).

### Chunk 6 — Lists

Lists the names of **dynamic lists**.  Lists start empty after grammar load;
words are added at runtime via `ISRGramCFG::ListAppend()`.

### Chunk 2 — Words

Lists all **terminal words** referenced by rule definitions.  Each unique word
gets a 1-based ID.  The same word appearing in multiple rules is stored once.

---

## 7  Rule Definitions Chunk (type 3)

This chunk contains all rule definitions.  Each rule is a header followed by
an array of 8-byte symbols:

```
Per rule:
Offset  Size   Field       Description
──────  ────   ─────       ───────────
0x00    4      dwSize      Total bytes (header + all symbols)
0x04    4      dwRuleID    1-based rule ID (matches exported/imported ID)
0x08    8*N    symbols[]   Array of SRCFGSYMBOL (see below)
```

Only **defined** rules appear here.  Exported rules must have a definition.
Imported rules must NOT — Dragon provides them internally.

### SRCFGSYMBOL (8 bytes each)

```
Offset  Size   Field        Description
──────  ────   ─────        ───────────
0x00    2      wType        Symbol type (see table)
0x02    2      wProbability See note below; always set to 0
0x04    4      dwValue      Meaning depends on wType
```

**wProbability**: The SAPI 4.0 specification intended this for weighted
alternatives — a higher value would bias recognition toward that branch.
Dragon NaturallySpeaking **ignores this field**.  Always set it to 0.

### Symbol Types

| wType | Constant | dwValue meaning |
|------:|----------|-----------------|
| 1 | `SRCFG_STARTOPERATION` | Operation code (see below) |
| 2 | `SRCFG_ENDOPERATION` | Same operation code as matching START |
| 3 | `SRCFG_WORD` | Word ID (1-based, from chunk 2) |
| 4 | `SRCFG_RULE` | Rule ID (1-based) |
| 5 | `SRCFG_WILDCARD` | Defined by SAPI 4.0 but **not supported by Dragon** — do not emit |
| 6 | `SRCFG_LIST` | List ID (1-based, from chunk 6) |

### Operation Codes (for START/END symbols)

| Code | Constant | Grammar construct |
|-----:|----------|-------------------|
| 1 | `SRCFGO_SEQUENCE` | Juxtaposition: `A B C` |
| 2 | `SRCFGO_ALTERNATIVE` | Choice: `A \| B \| C` |
| 3 | `SRCFGO_REPEAT` | One-or-more: `A+` |
| 4 | `SRCFGO_OPTIONAL` | Zero-or-one: `[A]` |

START and END symbols always appear in matched pairs.  They nest like
parentheses.  Every START must have a corresponding END with the same
operation code.

**Validated live (2026-02-16):** Dragon rejects grammars with mismatched
START/END pairs (e.g., START without matching END) with `GrammarError`.

### Wrapping Conventions

These are not format requirements — Dragon accepts any valid nesting — but
following them minimizes binary size.  **Validated live:** Dragon accepts both
redundant wrapping (single word in START(SEQ)...END(SEQ)) and no wrapping
(bare word with no START/END).

- A **sequence** of 2+ items is wrapped in START(1)...END(1).
- An **alternative** of 2+ items is wrapped in START(2)...END(2).
- A single item need not be wrapped in a redundant START/END pair.

Example: `hello [world]` compiles to:

```
START sequence  (wType=1, dwValue=1)
WORD "hello"    (wType=3, dwValue=1)
START optional  (wType=1, dwValue=4)
WORD "world"    (wType=3, dwValue=2)
END optional    (wType=2, dwValue=4)
END sequence    (wType=2, dwValue=1)
```

---

## 8  Grammar Text Syntax

This BNF-like text format is a conventional authoring syntax for Dragon CFG
grammars.  Dragon does not parse this text — it only accepts the binary
format described above.  A compiler translates this text (or any equivalent
representation) into binary.

### Statements

```
<ruleName> exported = expression ;     // Public rule (activatable)
<ruleName> = expression ;              // Private rule (internal only)
<ruleName> imported ;                  // Imported from elsewhere
```

### Expressions

Operators listed from highest to lowest precedence.  These precedence rules
govern how the text is parsed; the binary output uses explicit START/END
nesting with no ambiguity.

| Precedence | Syntax | Meaning |
|:----------:|--------|---------|
| 1 (highest) | `word` | Bare word (alphanumeric, `-`, `_`) |
| 1 | `"quoted word"` or `'quoted word'` | Word with spaces/special chars |
| 1 | `<ruleName>` | Rule reference |
| 1 | `{listName}` | Dynamic list reference |
| 1 | `( expr )` | Grouping |
| 1 | `[ expr ]` | Optional (emits START/END with OPTIONAL op) |
| 2 | `expr +` | Repeat (1 or more) |
| 3 | `expr expr` | Sequence (implicit, no operator) |
| 4 (lowest) | `expr \| expr` | Alternative |

### Comments

Lines beginning with `#` are comments.

### Valid Identifiers

Rule names and list names: `[a-zA-Z0-9_-]+` (case-sensitive).

### Examples

```
# Simple command grammar
<command> exported = open <target> ;
<target> = file | folder | window ;

# With optional and repeat
<dictate> exported = please [type] {words}+ ;

# Imported Dragon built-in
<dgndictation> imported ;
<mixed> exported = command <dgndictation> ;
```

---

## 9  Dragon Built-in Rules

These rule names can be imported without a definition.  Dragon provides
them internally:

| Rule name | Purpose |
|-----------|---------|
| `dgndictation` | Free-form dictation (equivalent to `(<dgnwords> \| "\\(noise)")+`) |
| `dgnwords` | All words in the active vocabulary |
| `dgnletters` | Spelling alphabet — recognized words come back in format `a\spelling-letter\a` |

Import them with: `<dgndictation> imported ;`

**Validated live (2026-02-16):** All three built-in rules load and recognize
correctly when imported.  `dgnletters` returns words with
`\spelling-letter\` markup (e.g., `a\spelling-letter\a`), not plain letters.

---

## 10  Dragon Header Flags

The `dwFlags` field in SRHEADER is a bitfield.  Standard SAPI 4.0 defines
bit 0; Dragon adds bits 26-31:

| Bit | Constant | Effect |
|----:|----------|--------|
| 0 | `SRHDRFLAG_UNICODE` | Grammar uses WCHAR strings (**required** for WCHAR grammars — see §2) |
| 26 | `DGNSRHDRFLAG_STATICXYZGRAMMAR` | Grammar is not dynamically modified |
| 27 | `DGNSRHDRFLAG_DONTUSESTATEWORDS` | Ignore state-specific word lists |
| 28 | `DGNSRHDRFLAG_DONTUSENOISE` | Reject noise/silence matches |
| 29 | `DGNSRHDRFLAG_USELMSCORE` | Use language model scoring |
| 30 | `DGNSRHDRFLAG_ADDTODICTSTATE` | Merge grammar into dictation state |
| 31 | `DGNSRHDRFLAG_LANGUAGEMODELON` | Enable language model |

For most command grammars (ANSI encoding), `dwFlags = 0` is correct.

**Validated live (2026-02-16):** Bits 28, 29, and 31 are all accepted by
Dragon without error.  Recognition still works with any combination of these
flags set.  Specific behavioral differences (e.g., noise rejection, LM
scoring) were not measured in these tests.

---

## 11  Dragon Extension Chunks

### DGNSRCKCFG_HEADER (0x1014) — Grammar Metadata

Associates a grammar with a specific application and window state.  Dragon
uses this for automatic context-sensitive grammar activation.

```
Offset  Size   Field                Description
──────  ────   ─────                ───────────
0x00    4      dwSize               Total block size
0x04    64     szApplication        Application name (WCHAR[32])
0x44    64     szState              Window state name (WCHAR[32])
0x84    var    abData               Arbitrary extension data (4-byte aligned)
```

The VCMDNAME sub-structure (szApplication + szState) identifies the target
application context.  `VCMD_APPLEN` and `VCMD_STATELEN` are both 32 WCHARs
(64 bytes each).

This chunk is not required for programmatic grammar loading.  Dragon's
voice command wizard generates it for its own grammar management.

### DGNSRCKCFG_VCMDCOMMAND (0x1015) — Voice Command Metadata

Per-rule description and action strings used by Dragon's command browser
UI.  Not required for programmatic grammar loading.

### DGNSRCKCFG_LISTS (0x1016) — Serialized List Words

> **Do not emit this chunk.** Validated 2026-02-16 against Dragon 13: a grammar
> containing 0x1016 hangs COM indefinitely inside `GrammarLoad` and then kills
> the `natspeak.exe` process. Unlike 0x1014, which fails cleanly with an error,
> this is destructive. Dragon extension chunks are not accepted via programmatic
> loading — populate lists with `ListAppend()` after load instead. The
> regression test is permanently skipped for this reason
> (`tests/test_grammar_format.py::test_14g_dgnsrckcfg_lists`).

The layout below is recorded for completeness — for reading grammars produced
elsewhere, not for generating them.  The chunk contains one or more entries:

```
Offset  Size   Field       Description
──────  ────   ─────       ───────────
0x00    4      dwSize      Total block size
0x04    4      dwListNum   List ID (matches chunk 6 entry)
0x08    var    abData      Array of SRWORD entries (same format as chunk 2)
```

---

## 12  Dictation Grammars (type 2)

Dictation grammars use `SRHEADER.dwType = 2` and are loaded with
`SRGRMFMT_DICTATION`.  They differ from CFG in several ways:

- **No rule definitions** — Dragon provides the language model internally.
- **No chunks required** — the binary is just an 8-byte SRHEADER.
- **Activation requires NULL rule name** — pass NULL (not a string) to
  `ISRGramCommon::Activate()`.
- **Context control** — use `ISRGramDictation::Context(before, after)` to set
  surrounding text for better predictions.

Minimal dictation grammar binary (8 bytes):

```
02 00 00 00  00 00 00 00      dwType=2 (Dictation), dwFlags=0
```

Dragon extends dictation via `IDgnSRGramDictation`:

| Method | Purpose |
|--------|---------|
| `Words(SDATA, DWORD)` | Set context-specific word hints |
| `RecentBufferFlush()` | Clear pending audio buffer |
| `RecentBufferCommit()` | Confirm pending audio |
| `CommittedFlush()` | Clear committed audio |

---

## 13  SELECT Grammars (type 10, Dragon-only)

SELECT grammars enable select-and-say: the user says an intro phrase, one or
more words from a dynamic list, and an optional end phrase.

`SRHEADER.dwType = 10`, loaded with `SRGRMFMT_DRAGONNATIVE1` (0x8101).

### SELECT Chunk IDs

| ID | Constant | Content |
|---:|----------|---------|
| 0x1017 | `DGNSRCKSELECT_INTROPHRASES` | Phrases preceding the selection (e.g., "select") |
| 0x1018 | `DGNSRCKSELECT_THRUWORD` | Separator word (e.g., "through") |
| 0x1019 | `DGNSRCKSELECT_ENDPHRASES` | Phrases following the selection |
| 0x1020 | `DGNSRCKSELECT_WORDS` | The selectable word list |

The internal format of these chunks is proprietary to Dragon and not
documented in the SAPI 4.0 specification.  SELECT grammars are typically
managed entirely through the `IDgnSRGramSelect` COM interface rather than
by constructing the binary directly.

### IDgnSRGramSelect Methods

| Method | Purpose |
|--------|---------|
| `WordsSet(SDATA)` | Replace all words |
| `WordsInsert(DWORD, SDATA)` | Insert at position |
| `WordsDelete(DWORD, DWORD)` | Delete range |
| `WordsChange(DWORD, DWORD, SDATA)` | Replace range |
| `WordsGet(PSDATA)` | Retrieve current words |

---

## 14  Runtime Grammar Control

After loading, the grammar object exposes several COM interfaces for runtime
control.  These are not part of the binary format, but are essential for using
grammars.

### Loading (ISRCentral)

```c
HRESULT GrammarLoad(SRGRMFMT fmt, SDATA data, PVOID pNotifySink,
                    IID iidNotify, LPUNKNOWN *ppGramObj);
```

The `pNotifySink` parameter is an `ISRGramNotifySink` implementation.  Dragon
calls its methods when recognition events occur:

| Callback | When |
|----------|------|
| `BookMark(DWORD)` | A previously-set bookmark is reached in the audio stream |
| `Paused()` | Grammar is auto-paused after recognition (if `bAutoPause` was TRUE) |
| `PhraseFinish(DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN)` | A phrase was recognized — `LPUNKNOWN` is the result object |
| `PhraseHypothesis(DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN)` | Partial hypothesis during recognition |
| `PhraseStart(QWORD)` | Speech detected, recognition starting |
| `Reevaluate(LPUNKNOWN)` | Result re-evaluation completed |
| `Training(DWORD)` | Training status update |
| `UnArchive(LPUNKNOWN)` | Grammar un-archived |

### Activation (ISRGramCommon)

```c
HRESULT Activate(HWND hWnd, BOOL bAutoPause, PCWSTR pszRuleName);
HRESULT Deactivate(PCWSTR pszRuleName);
```

- CFG grammars: activate by exported rule name.
- Dictation grammars: pass NULL for rule name.
- `hWnd` scopes recognition to a window (0 = global).

### Dynamic Lists (ISRGramCFG)

```c
HRESULT ListAppend(PCWSTR pszListName, SDATA words);
HRESULT ListRemove(PCWSTR pszListName, SDATA words);
HRESULT ListSet(PCWSTR pszListName, SDATA words);
HRESULT ListGet(PCWSTR pszListName, PSDATA pWords);
```

The `words` SDATA contains packed SRWORD entries (same variable-length format
as chunk 2 name-table entries).

### Exclusive Mode (IDgnSRGramCommon — Dragon extension)

```c
HRESULT SpecialGrammar(BOOL bExclusive);
```

When TRUE, only this grammar is active — all other grammars are suppressed.
Useful for modal dialogs or dedicated voice-control modes.

---

## 15  All SRGRMFMT Constants

The complete set of grammar format enum values:

| Value | Constant | Description |
|------:|----------|-------------|
| 0x0000 | `SRGRMFMT_CFG` | Standard CFG grammar |
| 0x0001 | `SRGRMFMT_LIMITEDDOMAIN` | Limited domain grammar |
| 0x0002 | `SRGRMFMT_DICTATION` | Dictation grammar |
| 0x8000 | `SRGRMFMT_CFGNATIVE` | Native (compiled) CFG — preferred for Dragon |
| 0x8001 | `SRGRMFMT_LIMITEDDOMAINNATIVE` | Native limited domain |
| 0x8002 | `SRGRMFMT_DICTATIONNATIVE` | Native dictation |
| 0x8101 | `SRGRMFMT_DRAGONNATIVE1` | Dragon SELECT grammar |
| 0x8102 | `SRGRMFMT_DRAGONNATIVE2` | Reserved |
| 0x8103 | `SRGRMFMT_DRAGONNATIVE3` | Reserved |

---

## 16  Complete Binary Example

Grammar text:

```
<greeting> exported = hello [world] ;
```

### ID Assignments

- Words: `hello` = 1, `world` = 2
- Rules: `greeting` = 1 (exported)

### Hex Dump (156 bytes) — WCHAR variant

This example uses UTF-16LE with `SRHDRFLAG_UNICODE` set.  The more common
ANSI variant (used by natlinkcore/dragonfly) would be shorter, with 8-bit
strings and `dwFlags = 0`.

```
# SRHEADER (8 bytes)
00000000  00 00 00 00  00 00 00 00                              type=CFG, flags=0

# Chunk 4: Exported rules (8 + 28 = 36 bytes)
00000008  04 00 00 00  1C 00 00 00                              chunkID=4, dataSize=28
00000010  1C 00 00 00  01 00 00 00                              entrySize=28, ruleID=1
00000018  67 00 72 00  65 00 65 00  74 00 69 00  6E 00 67 00   L"greeting"
00000028  00 00 00 00                                           null WCHAR + 2 pad

# Chunk 2: Words (8 + 40 = 48 bytes)
0000002C  02 00 00 00  28 00 00 00                              chunkID=2, dataSize=40
00000034  14 00 00 00  01 00 00 00                              entrySize=20, wordID=1
0000003C  68 00 65 00  6C 00 6C 00  6F 00 00 00                L"hello" + null
00000048  14 00 00 00  02 00 00 00                              entrySize=20, wordID=2
00000050  77 00 6F 00  72 00 6C 00  64 00 00 00                L"world" + null

# Chunk 3: Rule definitions (8 + 56 = 64 bytes)
0000005C  03 00 00 00  38 00 00 00                              chunkID=3, dataSize=56
00000064  38 00 00 00  01 00 00 00                              ruleSize=56, ruleID=1
0000006C  01 00 00 00  01 00 00 00                              START sequence (op=1)
00000074  03 00 00 00  01 00 00 00                              WORD "hello" (id=1)
0000007C  01 00 00 00  04 00 00 00                              START optional (op=4)
00000084  03 00 00 00  02 00 00 00                              WORD "world" (id=2)
0000008C  02 00 00 00  04 00 00 00                              END optional (op=4)
00000094  02 00 00 00  01 00 00 00                              END sequence (op=1)
```

In the SRCFGSYMBOL entries, `wType` occupies the first 2 bytes and
`wProbability` (always 0) the next 2, so `01 00 00 00` reads as
`wType=0x0001, wProbability=0x0000`.

---

## 17  C Structure Reference

These are the C struct definitions from the SAPI 4.0 headers (`speech.h` and
`dspeech.h`).  All structs are the Unicode (W) variants.  ANSI (A) variants
replace `WCHAR` with `CHAR`.

```c
// Binary blob passed to GrammarLoad()
typedef struct {
    DWORD dwSize;       // Total byte count
    BYTE *pData;        // Pointer to SRHEADER
} SDATA;

// File header — first 8 bytes of every grammar
typedef struct {
    DWORD dwType;       // 0=CFG, 2=Dictation, 10=SELECT
    DWORD dwFlags;      // Bitfield (see §10)
} SRHEADER;

// Chunk envelope
typedef struct {
    DWORD dwChunkID;    // Chunk type (see §5)
    DWORD dwChunkSize;  // Byte count of data after this 8-byte header
    BYTE  avInfo[];     // Variable-length data
} SRCHUNK;

// Word entry (chunk 2)
typedef struct {
    DWORD dwSize;       // Total entry size
    DWORD dwWordNum;    // 1-based word ID
    WCHAR szWord[];     // Null-terminated, 4-byte padded
} SRWORDW;

// Exported rule entry (chunk 4)
typedef struct {
    DWORD dwSize;       // Total entry size
    DWORD dwRuleNum;    // 1-based rule ID
    WCHAR szString[];   // Null-terminated rule name, 4-byte padded
} SRCFGXRULEW;

// Imported rule entry (chunk 5)
typedef struct {
    DWORD dwSize;       // Total entry size
    DWORD dwRuleNum;    // 1-based rule ID
    WCHAR szString[];   // Null-terminated rule name, 4-byte padded
} SRCFGIMPRULEW;

// List entry (chunk 6)
typedef struct {
    DWORD dwSize;       // Total entry size
    DWORD dwListNum;    // 1-based list ID
    WCHAR szString[];   // Null-terminated list name, 4-byte padded
} SRCFGLISTW;

// Rule definition header (chunk 3)
typedef struct {
    DWORD dwSize;       // Total size (this header + all symbols)
    DWORD dwUniqueID;   // 1-based rule ID
    // Followed by array of SRCFGSYMBOL
} SRCFGRULE;

// Symbol within a rule definition
typedef struct {
    WORD  wType;        // 1=START, 2=END, 3=WORD, 4=RULE, 5=WILDCARD, 6=LIST
    WORD  wProbability; // Always 0 (Dragon ignores this field)
    DWORD dwValue;      // ID or operation code
} SRCFGSYMBOL;

// Dragon grammar metadata (chunk 0x1014)
typedef struct {
    DWORD  dwSize;              // Total block size
    WCHAR  szApplication[32];   // VCMD_APPLEN
    WCHAR  szState[32];         // VCMD_STATELEN
    BYTE   abData[];            // Extension data (4-byte aligned)
} DGNSRCFGHEADER;

// Dragon serialized list (chunk 0x1016)
typedef struct {
    DWORD dwSize;       // Total block size
    DWORD dwListNum;    // List ID (matches chunk 6)
    BYTE  abData[];     // Array of SRWORD entries
} DGNSRCFGLIST;

// Recognition notification sink (passed to GrammarLoad)
DECLARE_INTERFACE_(ISRGramNotifySink, IUnknown) {
    STDMETHOD (BookMark)        (THIS_ DWORD) PURE;
    STDMETHOD (Paused)          (THIS) PURE;
    STDMETHOD (PhraseFinish)    (THIS_ DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN) PURE;
    STDMETHOD (PhraseHypothesis)(THIS_ DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN) PURE;
    STDMETHOD (PhraseStart)     (THIS_ QWORD) PURE;
    STDMETHOD (Reevaluate)      (THIS_ LPUNKNOWN) PURE;
    STDMETHOD (Training)        (THIS_ DWORD) PURE;
    STDMETHOD (UnArchive)       (THIS_ LPUNKNOWN) PURE;
};
```

---

## 18  Implementation Checklist

To build a grammar compiler that targets Dragon:

1. Parse your grammar into rules, words, lists, and symbol sequences.
2. Assign 1-based IDs to each unique word, rule, and list.
3. Emit SRHEADER: `{dwType=0, dwFlags=0}`.
4. Emit chunk 4 (exported rules) — one entry per public rule.
5. Emit chunk 5 (imported rules) — one entry per imported rule.
6. Emit chunk 6 (lists) — one entry per dynamic list.
7. Emit chunk 2 (words) — one entry per unique word.
8. Emit chunk 3 (rule definitions) — one SRCFGRULE per defined rule,
   each containing an array of SRCFGSYMBOL.
9. Pass the resulting byte buffer to `ISRCentral::GrammarLoad()` as an
   SDATA with the appropriate SRGRMFMT constant.
10. Implement `ISRGramNotifySink` to receive recognition callbacks.

Key constraints (all validated live against Dragon 13):

- Strings: Use ANSI (8-bit) with `dwFlags=0`, or WCHAR (UTF-16LE) with
  `SRHDRFLAG_UNICODE` (bit 0) set.  Both are padded to 4-byte boundaries.
- All DWORDs and WORDs are little-endian.
- START/END symbols must be properly nested and matched (Dragon rejects
  mismatched pairs).
- Exported rules must also appear in chunk 3 with a definition.
- Imported rules must NOT appear in chunk 3 (Dragon provides them).
- Each name must be unique within its chunk; IDs are sequential from 1.
- `wProbability` must be 0 (Dragon ignores it).
- `SRCFG_WILDCARD` (wType=5) is defined by the spec but not supported by
  Dragon — do not emit it.
- Do NOT include unknown chunk IDs — Dragon rejects them.
- Chunk order is flexible; empty chunks may be omitted or included.
