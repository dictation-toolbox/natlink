import re


# ---------------------------------------------------------------------------
# Lexing routines
#
# A Vocola 2.8+ pseudo-token is defined be one of the following:
#
#     ( ) [ ] | , = ; := :
#
#     a quotation using "s or 's where the delimiter may be escaped by
#       doubling it; e.g., 'can''t' for can't
#
#     an unterminated quotation: as above but with the final delimiter
#        replaced with a newline
#
#     a bare word: a sequence of one or more unquoted characters that
#       may not include the following characters or a colon at the
#       end:
#         ( ) [ ] | , = ' " # \s
#
#   The longest pseudo-token starting at a given location is always
# preferred (e.g., := over :).  Pseudo-tokens may be separated by
# whitespace (\s*) and #-to-end-of-line comments (#.*$).  Any program
# plus a newline can be divided up into a sequence of such
# pseudo-tokens.
#
#
#   Pseudo-tokens are converted into actual tokens by converting
# maximal subsequences of pseudo-tokens that do not contain the ;
# pseudo-token or contain the : pseudo-token except at the end into
# context statement tokens.  The text of the context statement token
# is the entire text (including any interleaving whitespace and
# comments!) from the start of the first pseudo-token of the
# subsequence to the end of the : pseudo-token.  Thus, for example,
# "foo; b ar:err:(dd)" tokenizes into foo, ;, b ar:err:, (, dd, and ),
# with "b ar:err:" being a single context statement token.  Finally,
# a EOF token is added at the end.
#
#   This handling of context statements is baroque to say the least,
# but is necessary to ensure sufficient backward compatibility with
# the original syntax, which treats whitespace in context statements
# (only) as significant.  We expect to depreciate context statements
# in the future in favor of more sane syntax.
#
#   Backward compatibility note: originally, the final : of a context
# statement had to be followed by whitespace (\s); this allowed bare
# words to end in a : so long as they were not followed by whitespace.
# We have chosen to remove this undesirable whitespace sensitivity by
# outlawing such bare words.  Instead, we treat such input as the end
# of a context statement.
#


##
## Dividing up the input into tokens:
##

Singles      = r'()\[\],|;='

  # characters not allowed anywhere in a bare word:
Excluded     = r'\s\#\'\"' + Singles

#
# Every string ending with a newline can be divided into a continuous
# series of these, with each pseudo token being as greedy as possible.
#
# Exception: whitespace (including comments) at the end of the string
# doesn't match.
#
Pseudo_token = r'(?x) '                                                  + \
               r' \s* (?: \#.*\n \s* )* '                                + \
               r' ( [^:'+Excluded+r']+ (?: :+ [^:'+Excluded+r']+ )* '    + \
               r' | ['+Singles+r'] '                                     + \
               r' | \" [^\"\n]* (?: \"\" [^\"\n]* )* [\"\n] '            + \
               r' | \' [^\'\n]* (?: \'\' [^\'\n]* )* [\'\n] '            + \
               r' | := '                                                 + \
               r' | :+ [^:'+Excluded+r']+ (?: :+ [^:'+Excluded+r']+ )* ' + \
               r' | : '                                                  + \
               r' )'

Pseudo       = re.compile(Pseudo_token)


Token_properties = {}

  # token_properties should have definitions for:
  #   ( ) [ ] | , = ; := : ' " \n b EOF
  # where b denotes a bare word and \n an unterminated quotation
def initialize_tokenizer(token_properties):
    global Token_properties

    properties = token_properties
    for i in xrange(0,256):
        c = chr(i)
        token_properties[c + ':']  = token_properties[':']
        token_properties[c + '"']  = token_properties['"']
        token_properties[c + "'"]  = token_properties["'"]
        token_properties[c + "\n"] = token_properties["\n"]

    Token_properties = properties

  # requires: text ends in a newline
  # requires: initialize_tokenizer(-) has already been called
def tokenize(text):  # -> [[kind, token text, offset in text of token start]*]
    global Token_properties, Pseudo
    properties               = Token_properties
    token_bare_properties    = properties["b"]
    token_context_properties = properties[":"]
    pseudo                   = Pseudo

    tokens          = []
    start           = 0
    statement_start = 0
    while True:
        match = pseudo.match(text, start)
        if not match:
            tokens.append([properties["EOF"], "", len(text)])
            return tokens

        start = match.end(0)
        token = match.group(1)
        kind  = properties.get(token[-2:], token_bare_properties)
        tokens.append([kind, token, match.start(1)])

        if token == ";":
            statement_start = len(tokens)
        elif kind == token_context_properties:
            beginning = tokens[statement_start][2]
            token     = text[beginning:start]
            tokens[statement_start:] = [[kind, token, beginning]]
            statement_start = len(tokens)


##
## Loading the tokens of a string for processing:
##

  # (initial) tokenizer state:
Text          = ""
Tokens        = []
Offset        = -1  # uninitialized state for implementation error detection
Peeks         = 0
Scan_limit    = 0
Scan_newlines = 0


  # requires: initialize_token_properties(-) has already been called
def load_tokens(text):
    global Text, Offset, Peeks, Tokens, Scan_limit, Scan_newlines

    if text[-1:] != "\n": text += "\n"

    Text          = text
    Tokens        = tokenize(text)

    Offset        = 0
    Peeks         = 0
    Scan_limit    = 0
    Scan_newlines = 0


##
## Moving through the list of tokens:
##

def peek(kind):
    global Tokens, Offset, Peeks
    Peeks |= kind
    return Tokens[Offset][0] & kind

def eat(kind= -1):
    global Tokens, Offset, Peeks

    if not (Tokens[Offset][0] & kind):
        Peeks |= kind
        syntax_error(Peeks, Tokens[Offset][0], Tokens[Offset][1],
                     get_current_position())

    Peeks   = 0
    Offset += 1
    return Tokens[Offset-1][1]

def get_current_position():
    global Text, Offset, Tokens
    if Offset == -1:
        implementation_error("get_current_position() called before open_text")
    return [Text, Offset, Tokens[Offset][2]]

def get_last_position():
    global Text, Offset, Tokens
    if Offset < 1:
        implementation_error("get_last_position() called before open_text/eat")
    return [Text, Offset-1, Tokens[Offset-1][2]]

def adjust_position(position, amount):
    text, tokens_offset, text_offset = position
    return [text, tokens_offset, text_offset+amount]

  # requires: load_tokens(-) has not been called since this position was captured
def rewind(position):
    global Offset
    Offset = position[1]
    Peeks  = 0


##
## Getting information about positions:
##

def get_line_number(position):
    global Text, Scan_limit, Scan_newlines

    text, dummy, text_offset = position

    if text is Text:                  # compare by pointer values
        if text_offset < Scan_limit:
            Scan_limit = Scan_newlines = 0
        Scan_newlines += text[Scan_limit:text_offset].count("\n")
        Scan_limit = text_offset
        return Scan_newlines + 1

    return text[:text_offset].count("\n")+ 1

def get_column_number(position):
    text, dummy, text_offset = position

    last_newline = text.rfind("\n", 0, text_offset)
    line_start = last_newline + 1

    return text_offset - line_start

  # returns line without it's terminating newline:
def get_line(position):
    text, dummy, text_offset = position

    last_newline = text.rfind("\n", 0, text_offset)
    line_start = last_newline + 1

    line_end = text.find("\n", line_start)

    return text[line_start:line_end]

def point_to_position(position):
    line   = get_line(position)
    column = get_column_number(position)

    line   = line.replace("\t", " ")
    before = line[0:column]

    line   = make_visible(line)
    before = make_visible(before)

    limit = 65
    post  = 15
    if len(line) > limit:
        fringe = "..."
        if len(before)+1 > limit-post:
            while len(before)+len(fringe)+1 > limit-post:
                line   = line[1:]
                before = before[1:]
            line   = fringe + line
            before = fringe + before
        if len(line) > limit:
            line = line[:limit-len(fringe)] + "..."

    result  = line + "\n"
    #result += before + "^\n"
    result += " "*len(before) + "^\n"

    return result

def make_visible(text):
    result = ""
    for char in text:
        c = ord(char)
        if c < 32:
            result += "^" + chr(ord('@')+c)
        else:
            result += char
    return result

##
## Decorating tokens with properties:
##

TOKEN_BARE_WORD    = 0x1
TOKEN_DOUBLE_WORD  = 0x2
TOKEN_SINGLE_WORD  = 0x4
TOKEN_LPAREN       = 0x8
TOKEN_RPAREN       = 0x10
TOKEN_LBRACKET     = 0x20
TOKEN_RBRACKET     = 0x40
TOKEN_BAR          = 0x80
TOKEN_COMMA        = 0x100
TOKEN_SEMICOLON    = 0x200
TOKEN_EQUALS       = 0x400
TOKEN_COLON_EQUALS = 0x800
TOKEN_CONTEXT      = 0x1000
TOKEN_ILLEGAL_WORD = 0x2000
TOKEN_EOF          = 0x4000

TOKEN_TERM         = 0x10000
TOKEN_ACTION       = 0x20000
TOKEN_WORD         = 0x40000


def initialize_token_properties():
    properties = {}

    properties["("]   = TOKEN_LPAREN       |TOKEN_TERM
    properties[")"]   = TOKEN_RPAREN

    properties["["]   = TOKEN_LBRACKET     |TOKEN_TERM
    properties["]"]   = TOKEN_RBRACKET

    properties["|"]   = TOKEN_BAR
    properties[","]   = TOKEN_COMMA
    properties[";"]   = TOKEN_SEMICOLON
    properties["="]   = TOKEN_EQUALS
    properties[":="]  = TOKEN_COLON_EQUALS

    properties[":"]   = TOKEN_CONTEXT
    properties["b"]   = TOKEN_BARE_WORD    |TOKEN_TERM |TOKEN_ACTION |TOKEN_WORD
    properties['"']   = TOKEN_DOUBLE_WORD  |TOKEN_TERM |TOKEN_ACTION |TOKEN_WORD
    properties["'"]   = TOKEN_SINGLE_WORD  |TOKEN_TERM |TOKEN_ACTION |TOKEN_WORD
    properties["\n"]  = TOKEN_ILLEGAL_WORD
    properties["EOF"] = TOKEN_EOF

    initialize_tokenizer(properties)

def decode_token_kinds(kind):
    result = []

    if kind & TOKEN_ACTION:       result.append("an action")
    if kind & TOKEN_TERM:         result.append("a term")
    if kind & TOKEN_WORD:         result.append("a word")

    if kind & TOKEN_LPAREN:       result.append("'('")
    if kind & TOKEN_RPAREN:       result.append("')'")

    if kind & TOKEN_LBRACKET:     result.append("'['")
    if kind & TOKEN_RBRACKET:     result.append("']'")

    if kind & TOKEN_BAR:          result.append("'|'")
    if kind & TOKEN_COMMA:        result.append("','")
    if kind & TOKEN_SEMICOLON:    result.append("';'")
    if kind & TOKEN_EQUALS:       result.append("'='")
    if kind & TOKEN_COLON_EQUALS: result.append("':='")

    if kind & TOKEN_CONTEXT:      result.append("a context statement")

    if kind & TOKEN_BARE_WORD:    result.append("an unquoted word")
    if kind & TOKEN_DOUBLE_WORD:  result.append("a double quoted word")
    if kind & TOKEN_SINGLE_WORD:  result.append("a single quoted word")

    if kind & TOKEN_ILLEGAL_WORD: result.append("an unterminated quotation")
    if kind & TOKEN_EOF:          result.append("end of file")

    if len(result) <= 2:
        return " or ".join(result)
    else:
        return (", ".join(result[:-1])) + ", or " + result[-1]


##
## Handling syntax errors:
##

def syntax_error(wanted, found, found_text, position):
    if found == TOKEN_ILLEGAL_WORD:
        log_error("Unterminated quotation: " + found_text[:-1],
                  get_current_position())
        raise SyntaxError("Unterminated quotation: " + found_text[:-1])

    advice = ""
    if (wanted&TOKEN_RPAREN):
        advice += "    Did you forget a ')' or have an extra'('?\n"
    if (wanted&TOKEN_ACTION):
        advice += "    Did you forget a ';' at the end of your (last) statement?\n"
        if (wanted&TOKEN_BAR):
            advice += "    Did you forget a '|' at the end of your " + \
                      "(last) alternative?\n"

    if wanted & TOKEN_TERM:
        wanted &= ~(TOKEN_LPAREN|TOKEN_LBRACKET|TOKEN_BARE_WORD|
                    TOKEN_DOUBLE_WORD|TOKEN_SINGLE_WORD)
    if wanted & TOKEN_ACTION:
        wanted &= ~(TOKEN_BARE_WORD|TOKEN_DOUBLE_WORD|TOKEN_SINGLE_WORD)
    if wanted & TOKEN_WORD:
        wanted &= ~(TOKEN_BARE_WORD|TOKEN_DOUBLE_WORD|TOKEN_SINGLE_WORD)

    found &= ~(TOKEN_TERM | TOKEN_ACTION | TOKEN_WORD)

    message = "Wanted " + decode_token_kinds(wanted) + \
        " but found " + decode_token_kinds(found)

    log_error(message, position, advice)
    raise SyntaxError(message)


##
## Saving and restoring the token state:
##

Token_state_stack = []

  # requires: initialize_token_properties(-) has already been called
def open_text(text):
    global Token_state_stack, Text, Tokens, Offset, Peeks, Scan_limit
    global Scan_newlines
    token_state = [Text, Tokens, Offset, Peeks, Scan_limit, Scan_newlines]
    Token_state_stack.append(token_state)

    load_tokens(text)

def close_text():
    global Token_state_stack, Text, Tokens, Offset, Peeks, Scan_limit, Scan_newlines
    token_status = Token_state_stack.pop()
    Text, Tokens, Offset, Peeks, Scan_limit, Scan_newlines = token_status
