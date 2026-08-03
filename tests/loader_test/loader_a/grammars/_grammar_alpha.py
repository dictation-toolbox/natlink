"""Test grammar Alpha — self-loads on import."""
import natlink
from natlink_com.grammar_compiler import compile_grammar

GRAMMAR_SPEC = """
<alpha> exported = test alpha;
"""

_gram = natlink.GramObj()
_binary = compile_grammar(GRAMMAR_SPEC)
_gram.load(_binary)
_gram.activate("alpha", 0)
print("Grammar alpha loaded and activated")


def unload():
    _gram.unload()
