"""Lark-based parser for SAPI 4.0 grammar syntax.

Replaces the hand-rolled tokenizer + recursive descent parser with a
declarative grammar definition.  Produces the same internal representation
that GrammarCompiler.emit() consumes.

The grammar syntax (from the SAPI 4 spec §8):
    <rule> exported = hello world | goodbye ;
    <other> = [optional] (group | alt) word+ ;
    <imp> imported ;
"""

from lark import Lark, Transformer, v_args

from .grammar_compiler import (
    SEQ_CODE, ALT_CODE, REP_CODE, OPT_CODE, GrammarError, Definition,
)

# Lark grammar — replaces _Tokenizer (70 lines) + _parse_* (120 lines)
_GRAMMAR = r"""
start: rule_def+

rule_def: "<" NAME ">" "exported" "=" expr ";"   -> rule_exported
        | "<" NAME ">" "=" expr ";"              -> rule_private
        | "<" NAME ">" "imported" ";"            -> rule_imported

expr: seq ("|" seq)*

seq: atom+

atom: WORD                                       -> atom_word
    | QUOTED                                     -> atom_word
    | "<" NAME ">"                               -> atom_rule
    | "{" NAME "}"                               -> atom_list
    | "(" expr ")"                               -> atom_group
    | "[" expr "]"                               -> atom_optional
    | atom "+"                                   -> atom_repeat

NAME: /[a-zA-Z0-9_\-]+/
WORD: /[a-zA-Z0-9_\-'\\]+/
QUOTED: "\"" /[^"]*/ "\""
      | "'" /[^']*/ "'"

%ignore /\s+/
%ignore /#[^\n]*/
"""

_parser = None
_parser_lock = __import__("threading").Lock()


def _get_parser():
    global _parser
    if _parser is None:
        with _parser_lock:
            if _parser is None:
                _parser = Lark(_GRAMMAR, parser="lalr")
    return _parser


class _CompilerTransformer(Transformer):
    """Transform lark parse tree into GrammarCompiler internal state."""

    def __init__(self):
        super().__init__()
        self.known_rules = {}
        self.known_words = {}
        self.known_lists = {}
        self.next_rule = 1
        self.next_word = 1
        self.next_list = 1
        self.export_rules = {}
        self.import_rules = {}
        self.rule_defines = {}

    def _get_rule_id(self, name):
        if name not in self.known_rules:
            self.known_rules[name] = self.next_rule
            self.next_rule += 1
        return self.known_rules[name]

    def _get_word_id(self, word):
        if word not in self.known_words:
            self.known_words[word] = self.next_word
            self.next_word += 1
        return self.known_words[word]

    def _get_list_id(self, name):
        if name not in self.known_lists:
            self.known_lists[name] = self.next_list
            self.next_list += 1
        return self.known_lists[name]

    # --- Rule definitions ---

    def rule_exported(self, items):
        name = str(items[0])
        defn = items[1]
        rule_id = self._get_rule_id(name)
        if name in self.import_rules:
            raise GrammarError(f"Rule {name!r} already imported")
        if name in self.rule_defines:
            raise GrammarError(f"Rule {name!r} already defined")
        self.rule_defines[name] = defn
        self.export_rules[name] = rule_id

    def rule_private(self, items):
        name = str(items[0])
        defn = items[1]
        self._get_rule_id(name)
        if name in self.import_rules:
            raise GrammarError(f"Rule {name!r} already imported")
        if name in self.rule_defines:
            raise GrammarError(f"Rule {name!r} already defined")
        self.rule_defines[name] = defn

    def rule_imported(self, items):
        name = str(items[0])
        rule_id = self._get_rule_id(name)
        if name in self.rule_defines:
            raise GrammarError(f"Rule {name!r} already defined")
        self.import_rules[name] = rule_id

    # --- Expressions ---

    def expr(self, items) -> Definition:
        if len(items) == 1:
            return items[0]
        result = [("start", ALT_CODE)]
        for item in items:
            result.extend(item)
        result.append(("end", ALT_CODE))
        return result

    def seq(self, items) -> Definition:
        if len(items) == 1:
            return items[0]
        result = [("start", SEQ_CODE)]
        for item in items:
            result.extend(item)
        result.append(("end", SEQ_CODE))
        return result

    # --- Atoms ---

    def atom_word(self, items) -> Definition:
        word = str(items[0])
        # Strip quotes if present
        if (word.startswith('"') and word.endswith('"')) or \
           (word.startswith("'") and word.endswith("'")):
            word = word[1:-1]
        return [("word", self._get_word_id(word))]

    def atom_rule(self, items) -> Definition:
        return [("rule", self._get_rule_id(str(items[0])))]

    def atom_list(self, items) -> Definition:
        return [("list", self._get_list_id(str(items[0])))]

    def atom_group(self, items) -> Definition:
        return items[0]  # parentheses don't add structure

    def atom_optional(self, items) -> Definition:
        return [("start", OPT_CODE)] + items[0] + [("end", OPT_CODE)]

    def atom_repeat(self, items) -> Definition:
        return [("start", REP_CODE)] + items[0] + [("end", REP_CODE)]

    def start(self, items):
        pass  # rule_* methods build state directly


def _preallocate_ids_in_source_order(tree, t):
    """Walk the tree in source order to allocate IDs matching the old parser.

    The old hand-rolled parser allocates IDs as it scans left-to-right:
    first the rule definition name, then all references in its body,
    then the next rule definition, etc.  Lark's bottom-up transformer
    visits children before parents.  This pre-pass restores encounter order.
    """
    for child in tree.children:
        if not hasattr(child, 'data'):
            continue
        if child.data in ('rule_exported', 'rule_private', 'rule_imported'):
            # Allocate definition name first
            t._get_rule_id(str(child.children[0]))
            # Then walk expression body for references
            _walk_expr_for_ids(child, t)


def _walk_expr_for_ids(node, t):
    """Recursively walk expression nodes to allocate word/rule/list IDs."""
    if not hasattr(node, 'data'):
        return
    if node.data == 'atom_word':
        word = str(node.children[0])
        if (word.startswith('"') and word.endswith('"')) or \
           (word.startswith("'") and word.endswith("'")):
            word = word[1:-1]
        t._get_word_id(word)
    elif node.data == 'atom_rule':
        t._get_rule_id(str(node.children[0]))
    elif node.data == 'atom_list':
        t._get_list_id(str(node.children[0]))
    else:
        for child in node.children:
            if hasattr(child, 'data'):
                _walk_expr_for_ids(child, t)


def parse(text: str) -> _CompilerTransformer:
    """Parse grammar text and return the transformer with populated state.

    The returned object has: known_rules, known_words, known_lists,
    export_rules, import_rules, rule_defines — same fields as GrammarCompiler.
    """
    try:
        tree = _get_parser().parse(text)
    except Exception as e:
        raise GrammarError(str(e)) from e

    t = _CompilerTransformer()
    _preallocate_ids_in_source_order(tree, t)
    t.transform(tree)
    return t
