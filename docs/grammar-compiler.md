# Grammar Compiler

## Overview

`natlink_com.grammar_compiler` is a pure-Python compiler that converts grammar specifications into SAPI 4 binary format with Dragon extensions. It compiles CFG (context-free grammar), dictation, and Dragon SELECT grammars without a running Dragon instance.

## Location

```
src/natlink_com/grammar_compiler.py
```

## Usage

### From Python

```python
from natlink_com.grammar_compiler import GrammarCompiler

compiler = GrammarCompiler()

# Define a grammar
compiler.set_language(0x0409)  # English US
compiler.add_export("MyCommand", 1)
compiler.add_rule(1, [
    ("start", 1),  # SEQ_CODE
    ("word", compiler.add_word("hello")),
    ("word", compiler.add_word("world")),
    ("end", 1),
])

# Compile to binary
binary = compiler.compile()
```

### Grammar Types

- **CFG** (type 0): Context-free grammars with rules, words, lists, imports, and exports
- **Dictation** (type 2): Free-form dictation grammar
- **SELECT** (type 10): Dragon-specific selection grammar

### Binary Format

The compiler produces binary data conforming to the SAPI 4.0 grammar format:

- 12-byte header: type (DWORD), flags (DWORD), total size (DWORD)
- Chunks: Language (1), Words (2), Rules (3), Exports (4), Imports (5), Lists (6)
- Each chunk: ID (DWORD), size (DWORD), data

Strings can be encoded as ANSI or WCHAR (UTF-16LE) depending on the grammar flags.

### Standalone Testing

The grammar compiler has its own test suite that runs without Dragon:

```
uv run pytest tests/test_grammar_compiler.py tests/test_grammar_format.py -v
```
