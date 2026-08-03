"""Test grammar Charlie — self-loads on import."""
import natlink
from natlink_com.grammar_compiler import compile_grammar

GRAMMAR_SPEC = """
<charlie> exported = test charlie;
"""

_gram = natlink.GramObj()
_binary = compile_grammar(GRAMMAR_SPEC)
_gram.load(_binary)
_gram.activate("charlie", 0)
print("Grammar charlie loaded and activated")


def unload():
    _gram.unload()
