"""Test grammar Bravo — self-loads on import."""
import natlink
from natlink_com.grammar_compiler import compile_grammar

GRAMMAR_SPEC = """
<bravo> exported = test bravo;
"""

_gram = natlink.GramObj()
_binary = compile_grammar(GRAMMAR_SPEC)
_gram.load(_binary)
_gram.activate("bravo", 0)
print("Grammar bravo loaded and activated")


def unload():
    _gram.unload()
