import re
import os

from vcl2py.ast import *
from vcl2py.lex import *
from vcl2py.log import *


def parse_input(in_file, in_folder, extension_functions, debug):
    global Input_name, In_folder, Extension_functions, Debug

    Input_name          = in_file
    In_folder           = in_folder
    Extension_functions = extension_functions
    Debug               = debug


    global Included_files, Include_stack_file, Include_stack_line
    global Functions, Function_definitions, Definitions, Statement_count
    global Forward_references, Last_include_position, Error_count
    global Should_emit_dictation_support, File_empty

    Definitions                   = {}
    Functions                     = {}
    Function_definitions          = {}

    Forward_references            = []
    Included_files                = []
    Include_stack_file            = []  # short names (relative to In_folder)
    Include_stack_line            = []
    Last_include_position         = None
    Error_count                   = 0
    File_empty                    = True
    Should_emit_dictation_support = False
    Statement_count               = 1

    return parse_file(in_file), Definitions, Function_definitions, Statement_count, Error_count, Should_emit_dictation_support, File_empty


# ---------------------------------------------------------------------------
# Parsing routines
#
#   The following grammar defines the Vocola 2 language:
# (note that a "menu" is called an "alternative set" in the documentation)
#
#     <statements> ::= <statement>*
#      <statement> ::= context_statement | <definition> | <function>
#                    | <directive> | <top_command>
#
#     <definition> ::= variable    ':=' <menu_body> ';'
#       <function> ::= <prototype> ':=' <action>*   ';'
#    <top_command> ::= <terms>      '=' <action>*   ';'
#      <directive> ::= bare_word [<word> [<word>]]  ';'
#
#          <terms> ::= <term>+
#           <term> ::= <word> | variable | range | <menu> | '[' <terms> ']'
#           <word> ::= quoted_word | bare_word
#
#         <action> ::= <word> | <call>
#           <call> ::= callName '(' <arguments> ')'
#      <arguments> ::= [<action>* (',' <action>*)*]
#
#           <menu> ::= '(' <menuBody> ')'
#       <menuBody> ::= <command> ('|' <command>)*
#        <command> ::= <terms> ['=' <action>*]
#
#      <prototype> ::= functionName '(' <formals> ')'
#        <formals> ::= [name (',' name)*]
#
# The terminals variable, range, callName, name, and functionName are
# simply synonyms for bare_word as far as the parser is concerned.
# Note that unterminated quotations do not occur in the above; this is
# because they are not legal Vocola 2.
#
#
#   The logically separate (integrated in practice) type checking pass
# enforces additional constraints including:
#
#            variable == <\w+>
#               range == \d+\.\.\d+
#                name == [a-zA-Z_]\w*
#        functionName == [a-zA-Z_]\w*
#            callName == [a-zA-Z_][\w.]*
#
#   context_statements may not contain normal '='s (e.g., not in a
#     quotation or a comment).
#
# The actual currently allowable directives are:
#
#      <directive> ::= ('include' word | '$set' word word) ';'
#
# There additional limitations on the complexity of menus; <<<>>>

# ---------------------------------------------------------------------------
# Built in Vocola functions with (minimum number of arguments, maximum
# number of arguments):

Vocola_functions = {
                     "Eval"         : [1,1],
                     "EvalTemplate" : [1,-1],
                     "If"           : [2,3],
                     "Repeat"       : [2,2],
                     "Unimacro"     : [1,1],
                     "When"         : [2,3],
                   }

# Vocola extensions with (extension_name, minimum_arguments, maximum_arguments,
# needs_flushing, module_name, function_name); initialized by
# read_extensions_file():

#Extension_functions = {}

# Built in Dragon functions with (minimum number of arguments,
# template of types of all possible arguments); template has one
# letter per argument with s denoting string and i denoting integer:

Dragon_functions = {
                     "ActiveControlPick" : [1,"s"],
                     "ActiveMenuPick"    : [1,"s"],
                     "AppBringUp"        : [1,"ssis"],
                     "AppSwapWith"       : [1,"s"],
                     "Beep"              : [0,""],
                     "ButtonClick"       : [0,"ii"],
                     "ClearDesktop"      : [0,""],
                     "ControlPick"       : [1,"s"],
                     "DdeExecute"        : [3,"sssi"],
                     "DdePoke"           : [4,"ssss"],
                     "DllCall"           : [3,"sss"],
                     "DragToPoint"       : [0,"i"],
                     "GoToSleep"         : [0,""],
                     "HeardWord"         : [1,"ssssssss"],  # max 8 words
                     "HTMLHelp"          : [2,"sss"],
                     "MenuCancel"        : [0,""],
                     "MenuPick"          : [1,"s"],
                     "MouseGrid"         : [0,"ii"],
                     "MsgBoxConfirm"     : [3,"sis"],
                     "PlaySound"         : [1,"s"],
                     "RememberPoint"     : [0,""],
                     "RunScriptFile"     : [1,"s"],
                     "SendKeys"          : [1,"s"],
                     "SendDragonKeys"    : [1,"s"],
                     "SendSystemKeys"    : [1,"si"],
                     "SetMicrophone"     : [0,"i"],
                     "SetMousePosition"  : [2,"iii"],
                     "SetNaturalText"    : [1,"i"],
                     "ShellExecute"      : [1,"siss"],
                     "ShiftKey"          : [0,"ii"],
                     "TTSPlayString"     : [0,"ss"],
                     "Wait"              : [1,"i"],
                     "WaitForWindow"     : [1,"ssi"],
                     "WakeUp"            : [0,""],
                     "WinHelp"           : [2,"sii"],
                    }

# parse_file returns a parse tree (list of statements), which includes in-line
# any statements from include files. Since parse_file is called recursively
# for include files, all code applying to the parse tree as a whole is
# executed in this routine.

def parse_file(in_file):    # returns a list of statements
    global Include_stack_file, Included_files

    short_name, canonical_path = canonicalize_in_file(in_file)
    Included_files.append(canonical_path)

    text = read_file(canonical_path)
    open_text(text)
    try:
        Include_stack_file.append(short_name)
        statements = parse_statements()
    finally:
        close_text()
        Include_stack_file.pop()

    return statements

def canonicalize_in_file(in_file):
    # allow \ as a file separator even on Linux:
    if os.sep == '/':
        in_file = in_file.replace('\\', '/')

    from_folder = In_folder
    if len(Include_stack_file) > 0:
        from_folder = os.path.dirname(os.path.join(In_folder,
                                                   Include_stack_file[-1]))

    in_path        = os.path.join(from_folder, in_file)
    canonical_path = os.path.realpath(os.path.abspath(in_path))

    short_name = in_file
    if not os.path.isabs(short_name):
        short_name = os.path.relpath(in_path, In_folder)

    return short_name, canonical_path

def read_file(in_file):
    global Last_include_position
    try:
        return open(in_file).read()
    except (IOError, OSError) as e:
        log_error("Unable to open or read '" + in_file + "'", # + ": " + str(e),
                  Last_include_position)
        return ""

# This is the main parsing loop.

def parse_statements():    # statements = (context | top_command | definition)*
    global Definitions, Formals, Include_stack_line, Last_include_position
    global Statement_count, Variable_terms

    statements = []
    while not peek(TOKEN_EOF):
        Variable_terms    = []  # used in error-checking
        Formals           = []  # None => any ref ok (environment variables)
        starting_position = get_current_position()
        try:
            statement = parse_statement()
        except (SyntaxError, RuntimeError) as e:
            # panic until after next ";":
            while not peek(TOKEN_EOF) and not peek(TOKEN_SEMICOLON):
                eat()
            if peek(TOKEN_SEMICOLON):
                eat(TOKEN_SEMICOLON)
            continue

        if statement["TYPE"] == "definition":
            name = statement["NAME"]
            if name in Definitions:
                log_error("Redefinition of <"+name+">", starting_position)
            Definitions[name] = statement
        elif statement["TYPE"] == "command":
            statement["NAME"] = str(Statement_count)
            Statement_count += 1

        #print unparse_statements([statement]),
        if statement["TYPE"] != "include":
            statements.append(statement)
        else:
            # Handle include file
            include_file = expand_variables(statement["ACTIONS"])
            if not already_included(include_file):
                # Save context, get statements from include file, restore
                Last_include_position = starting_position
                Include_stack_line.append(get_line_number(starting_position))
                #print "--> " + include_file
                statements.extend(parse_file(include_file))
                #print "<--"
                Include_stack_line.pop()

    return statements

def parse_statement():
    if peek(TOKEN_CONTEXT):
        return parse_context()
    if peek(TOKEN_LBRACKET|TOKEN_LPAREN|TOKEN_SINGLE_WORD|TOKEN_DOUBLE_WORD):
        return parse_top_command()


    start = get_current_position()
    peek(TOKEN_TERM)
    eat(TOKEN_BARE_WORD)

    # b ^ :=
    if peek(TOKEN_COLON_EQUALS):
        rewind(start); return parse_variable_definition()

    # b ^ w{0,2} ;  or  b ^ w{2} <term>  or b ^ w{0,2} =
    directive_arguments = 0
    while peek(TOKEN_WORD):
        eat()
        directive_arguments += 1
        if directive_arguments > 2:
            rewind(start); return parse_top_command()
    if peek(TOKEN_SEMICOLON):
        rewind(start); return parse_directive()
    if directive_arguments > 0:
        if not peek(TOKEN_LBRACKET|TOKEN_LPAREN):
            peek(TOKEN_TERM)
            eat(TOKEN_EQUALS)
        rewind(start); return parse_top_command()

    # b ^ <term> in unambiguous case  or  b ^ =
    if peek(TOKEN_LBRACKET|TOKEN_SINGLE_WORD|TOKEN_DOUBLE_WORD|TOKEN_EQUALS):
        rewind(start); return parse_top_command()


    peek(TOKEN_TERM)
    eat(TOKEN_LPAREN)
    # b( ^ <term>  or  b( ^ )  or  b( ^ b)  or  b( ^ b,  or  b( ^ b) :=
    if peek(TOKEN_RPAREN):
        rewind(start); return parse_function_definition()
    if peek(TOKEN_LBRACKET|TOKEN_SINGLE_WORD|TOKEN_DOUBLE_WORD|TOKEN_LPAREN):
        rewind(start); return parse_top_command()


    peek(TOKEN_TERM)
    eat(TOKEN_BARE_WORD)
    # b(b ^ <term>  or  b(b ^ |  or b(b ^ =  or  b(b ^ )  or  b(b ^ ,
    if peek(TOKEN_TERM|TOKEN_BAR|TOKEN_EQUALS):
        rewind(start); return parse_top_command()
    if peek(TOKEN_COMMA):
        rewind(start); return parse_function_definition()

    eat(TOKEN_RPAREN)
    # b(b) ^ <term>  or  b(b) ^ =  or b(b) ^ :=
    if peek(TOKEN_TERM|TOKEN_EQUALS):
        rewind(start); return parse_top_command()


    eat(TOKEN_COLON_EQUALS)
    rewind(start); return parse_function_definition()

def parse_context():    # context = chars* ('|' chars*)* ':'
    global Debug

    raw = eat(TOKEN_CONTEXT)[:-1]
    match = re.match(r'(?:[^=#]|#.*\n)*=', raw)
    if match:
        equal_position = adjust_position(get_last_position(),
                                         match.end(0) - 1)
        error("Context statements may not contain '='s", equal_position,
              "    Did you forget a ';' at the end of this statement?\n" +
              "    Did you forget to quote a word ending with ':'?\n")

    processed = ""
    for piece in re.findall(r'[^#]+|#.*\n', raw):
        if piece[:1] != "#": processed += piece.lower()
    strings = re.split(r'\s*\|\s*', processed.strip())
    if len(strings)== 0:
        strings = [""]

    statement            = {}
    statement["TYPE"]    = "context"
    statement["STRINGS"] = strings
    if Debug>=1: print_log(unparse_directive (statement), True)
    return statement

def parse_variable_definition():    # definition = variable ':=' menu_body ';'
    global Debug
    position = get_current_position()
    name = eat(TOKEN_BARE_WORD)
    if not re.match(r'<.*>$', name):
        error("Illegal variable '" + name +
              "': variables must start with '<' and end with '>'", position)
    name = name[1:-1]
    check_variable_name(name, position)
    if name == "_anything":
        error("Built-in list <_anything> is not redefinable", position)

    statement = {}
    statement["TYPE"] = "definition"
    statement["NAME"] = name
    eat(TOKEN_COLON_EQUALS)
    menu = parse_menu_body(TOKEN_SEMICOLON)
    eat(TOKEN_SEMICOLON)
    verify_referenced_menu(menu)
    statement["MENU"] = menu
    if Debug>=1: print_log(unparse_definition (statement), True)
    return statement

def check_variable_name(name, position):
    if not re.match(r'\w+$', name):
        error("Illegal variable name: <" + name + ">", position)

def parse_function_definition():   # function = prototype ':=' action* ';'
                                   # prototype = functionName '(' formals ')'
    global Debug, Formals, Function_definitions, Functions
    position = get_current_position()
    functionName = eat(TOKEN_BARE_WORD)
    if Debug>=2: print_log("Found user function:  " + functionName + "()")
    if not re.match(r'[a-zA-Z_]\w*$', functionName):
        error("Illegal user function name: " + functionName, position)

    eat(TOKEN_LPAREN)
    formals = parse_formals()
    eat(TOKEN_RPAREN)

    statement            = {}
    statement["TYPE"]    = "function"
    statement["NAME"]    = functionName
    statement["FORMALS"] = formals
    Formals              = formals # Used below in parse_formal_reference

    eat(TOKEN_COLON_EQUALS)
    statement["ACTIONS"] = parse_actions(TOKEN_SEMICOLON)
    eat(TOKEN_SEMICOLON)

    if functionName in Functions:
        error("Redefinition of " + functionName + "()", position)
    if functionName in Vocola_functions:
        error("Attempted redefinition of built-in function: " + functionName, position)
    Functions[functionName] = len(formals)  # remember number of formals
    Function_definitions[functionName] = statement
    if Debug>=1: print_log(unparse_function_definition (statement), True)
    return statement

def parse_formals():    # formals = [name (',' name)*]
    global Debug
    safe_formals = []
    if not peek(TOKEN_RPAREN):
        while True:
            formal = eat(TOKEN_BARE_WORD)
            if not re.match(r'[a-zA-Z_]\w*$', formal):
                error("Illegal formal name: '" + formal + "'", get_last_position())
            if Debug>=2: print_log("Found formal:  " + formal)
            safe_formals.append("_" + formal)
            if peek(TOKEN_COMMA):
                eat(TOKEN_COMMA)
            else:
                break
    return safe_formals

def parse_top_command():    # top_command = terms '=' action* ';'
    global Debug, File_empty
    statement = parse_command(TOKEN_SEMICOLON, True)
    eat(TOKEN_SEMICOLON)
    File_empty = False
    if Debug>=1: print_log(unparse_command (statement, True))
    return statement

def parse_directive():    # directive = ('include' word | '$set' word word) ';'
    global Debug, Formals, Variable_terms

    starting_position = get_current_position()
    directive         = eat(TOKEN_BARE_WORD)

    word_nodes = []
    while len(word_nodes) < 2 and not peek(TOKEN_SEMICOLON):
        peek(TOKEN_WORD)
        word_nodes.append(parse_word())
    before_semicolon = get_last_position();
    eat(TOKEN_SEMICOLON)

    statement = {}
    if directive == "include":
        if len(word_nodes) != 1:
            position = before_semicolon
            if len(word_nodes) == 0:
                position = get_last_position()
            error("Include directive requires one word: include filename;",
                  position)
        statement["TYPE"]    = "include"
        statement["TEXT"]    = word_nodes[0]["TEXT"]
        Variable_terms = []    # no # references are valid
        Formals        = None  # turn off formal reference checking
        statement["ACTIONS"] = split_out_references(word_nodes[0])
    elif directive == "$set":
        if len(word_nodes) != 2:
            error("$set directive requires 2 words: $set parameter value;",
                  get_last_position())
        statement["TYPE"] = "set"
        statement["KEY"]  = word_nodes[0]["TEXT"]
        statement["TEXT"] = word_nodes[1]["TEXT"]
    else:
        error("Unknown directive '" + directive + "'", starting_position)

    if Debug>=1: print_log(unparse_directive (statement), True)
    return statement

def parse_command(separators, needs_actions=False): # command = terms ['=' action*]
    global Include_stack_file, Variable_terms
    if needs_actions:
        terms = parse_terms(TOKEN_EQUALS)
    else:
        terms = parse_terms(separators | TOKEN_EQUALS)

    command          = {}
    command["TYPE"]  = "command"
    command["FILE"]  = Include_stack_file[-1]
    command["TERMS"] = terms

    # Count variable terms for range checking in parse_reference
    Variable_terms = get_variable_terms(terms)

    if needs_actions or peek(TOKEN_EQUALS):
        eat(TOKEN_EQUALS)
        command["ACTIONS"] = parse_actions(separators)

    command["LINE"] = get_line_number(get_current_position()) # line number is *last* line of command # <<<>>>
    return command

def parse_terms(separators):    # <terms> ::= (<term> | '[' <terms> ']')+
    starting_position = get_current_position()
    terms = []
    seen_non_optional = False
    while True:
        if peek(TOKEN_LBRACKET):
            optional = True
            optional_starting_position = get_current_position()
            eat(TOKEN_LBRACKET)
            optional_terms = parse_terms(TOKEN_RBRACKET)
            eat(TOKEN_RBRACKET)
            term             = {}
            term["TYPE"]     = "optionalterms"
            term["TERMS"]    = optional_terms
            term["POSITION"] = optional_starting_position
            if Debug>=2:
                print_log("Found optional term group:  " + unparse_term(term, True))
        else:
            optional = False
            term = parse_term()

        term["OPTIONAL"] = optional
        if (not optional): seen_non_optional = True
        terms.append(term)

        if peek(separators):
            break

    if not seen_non_optional:
        error("At least one term must not be optional",
              starting_position)
    else:
        return combine_terms(terms)

def parse_term():         # <term> ::= <word> | variable | range | <menu>
    global Debug, Definitions

    starting_position = get_current_position()
    peek(TOKEN_TERM)
    if peek(TOKEN_LPAREN):
        eat(TOKEN_LPAREN)
        term = parse_menu_body(TOKEN_RPAREN)
        term["POSITION"] = starting_position
        eat(TOKEN_RPAREN)
        if Debug>=2:
            print_log("Found menu:  " + unparse_menu(term, True))
        return term
    elif not peek(TOKEN_BARE_WORD):
        return parse_word()

    word  = eat(TOKEN_BARE_WORD)
    match = re.match(r'<(.*?)>$|(\d+)\.\.(\d+)$', word)
    if not match:
        term = parse_word1(word, starting_position)
    elif match.group(2):
        term = {}
        term["TYPE"] = "range"
        term["FROM"] = int(match.group(2))
        term["TO"]   = int(match.group(3))
        if Debug>=2:
            print_log("Found range:  " + match.group(2) + ".." + match.group(3))
    else:
        name = match.group(1)
        check_variable_name(name, starting_position)
        if name == "_anything":
            if Debug>=2: print_log("Found <_anything>")
            term = create_dictation_node()
        else:
            if Debug>=2: print_log("Found variable:  <" + name + ">")
            if name not in Definitions:
                add_forward_reference(name, starting_position)
            term = create_variable_node(name)

    term["POSITION"] = starting_position
    return term

def create_dictation_node():
    global Should_emit_dictation_support
    Should_emit_dictation_support = True
    term = {}
    term["TYPE"] = "dictation"
    return term

def parse_menu_body(separators):    # menuBody = command ('|' command)*
    commands = []
    while True:
        if peek(separators | TOKEN_BAR):
            error("Empty alternative (set)", get_current_position())
        commands.append(parse_command(separators | TOKEN_BAR))
        if peek(TOKEN_BAR):
            eat(TOKEN_BAR)
        else:
            break

    menu = {}
    menu["TYPE"]     = "menu"
    menu["COMMANDS"] = commands
    return menu

def parse_actions(separators):    # action = word | call
    actions = []
    while not peek(separators):
        kind = peek(TOKEN_ACTION|TOKEN_DOUBLE_WORD|TOKEN_SINGLE_WORD)
        if peek(TOKEN_BARE_WORD):
            word = eat(TOKEN_BARE_WORD)
            if peek(TOKEN_LPAREN):
                actions.append(parse_call(word))
                continue
            else:
                word_node = parse_word1(word, get_last_position())
        else:
            word_node = parse_word()
        actions += split_out_references(word_node)
    return actions

# expand in-string references (e.g. "{Up $1}") and unquote
# $'s (e.g., \$ -> $).
# returns a non-empty list of actions
def split_out_references(word_node):
    word              = word_node["TEXT"]
    starting_position = word_node["POSITION"]
    quote_char        = word_node["QUOTE_CHAR"]

    if word == "":
        return [word_node]

    raw     = quote_char  # raw word text seen so far
    actions = []

    # reference = '$' (number | name)
    for match in re.finditer(r'(.*?)(\Z|(?<!\\)\$(?:(\d+)|([a-zA-Z_]\w*)))',
                             word):
        normal = match.group(1)
        if normal != "":
            unescaped = normal.replace(r'\$','$')  # convert \$ to $
            position  = adjust_position(starting_position, len(raw))
            actions.append(create_word_node(unescaped, quote_char, position))
            raw += normal.replace(quote_char, quote_char+quote_char)
        if match.group(2) !=  None:
            position  = adjust_position(starting_position, len(raw))
            if match.group(3) != None:
                actions.append(create_reference_node(match.group(3),
                                                     position))
            elif match.group(4)!= None:
                actions.append(create_formal_reference_node(match.group(4),
                                                     position))
            raw += match.group(2)

    return actions

def create_reference_node(n, position):
    global Debug, Variable_terms
    if int(n) > len(Variable_terms):
        error("Reference '$" + n + "' out of range", position)
    term = Variable_terms[int(n) - 1]
    if term["TYPE"] == "menu": verify_referenced_menu(term)
    if Debug>=2: print_log("Found reference:  $" + n)
    action = {}
    action["TYPE"] = "reference"
    action["TEXT"] = n
    return action

def create_formal_reference_node(name, position):
    global Debug, Formals
    formal = "_" + name
    if Formals!=None and formal not in Formals:
        error("Reference to unknown formal '$" + name + "'", position)
    if Debug>=2: print_log("Found formal reference:  $" + name)
    action = {}
    action["TYPE"]     = "formalref"
    action["TEXT"]     = formal
    action["POSITION"] = position
    return action

def parse_call(callName):    # call = callName '(' arguments ')'
    global Debug, Dragon_functions, Extension_functions, Functions, Vocola_functions

    call_position = get_last_position()
    if Debug>=2: print_log("Found call:  " + callName + "()")
    if not re.match(r'[\w.]+$', callName):
        error("Illegal function call name: '" + callName + "'", call_position)

    action = {}
    action["TYPE"] = "call"
    action["TEXT"] = callName
    eat(TOKEN_LPAREN)
    action["ARGUMENTS"] = parse_arguments()
    eat(TOKEN_RPAREN)

    nActuals = len(action["ARGUMENTS"])
    if callName.find(".") != -1:
        if callName in Extension_functions:
            callFormals = Extension_functions[callName]
            lFormals = callFormals[0]
            uFormals = callFormals[1]
            action["CALLTYPE"] = "extension"
        else:
            error("Call to unknown extension '" + callName + "'", call_position)
    elif callName in Dragon_functions:
        callFormals = Dragon_functions[callName]
        lFormals =     callFormals[0]
        uFormals = len(callFormals[1])
        action["CALLTYPE"] = "dragon"
        action["ARGTYPES"] = callFormals[1]
    elif callName in Vocola_functions:
        callFormals = Vocola_functions[callName]
        lFormals = callFormals[0]
        uFormals = callFormals[1]
        action["CALLTYPE"] = "vocola"
    elif callName in Functions:
        lFormals = uFormals = Functions[callName]
        action["CALLTYPE"] = "user"
    else:
        error("Call to unknown function '" + callName + "'", call_position)

    if lFormals != -1 and nActuals < lFormals:
        error("Too few arguments passed to '" + callName +
              "' (minimum of " + str(lFormals) + " required)", call_position)
    if uFormals != -1 and nActuals > uFormals:
        error("Too many arguments passed to '" + callName +
              "' (maximum of " + str(uFormals) + " allowed)", call_position)

    return action

def parse_arguments():    # arguments = [action* (',' action*)*]
    arguments = []
    if not peek(TOKEN_RPAREN):
        while True:
            arguments.append(parse_actions(TOKEN_COMMA|TOKEN_RPAREN))
            if peek(TOKEN_COMMA):
                eat(TOKEN_COMMA)
            else:
                break

    return arguments

def parse_word():
    global Debug
    if peek(TOKEN_DOUBLE_WORD):
        quote_char ='"'
        word = eat(TOKEN_DOUBLE_WORD)[1:-1].replace('""', '"')
    elif peek(TOKEN_SINGLE_WORD):
        quote_char = "'"
        word = eat(TOKEN_SINGLE_WORD)[1:-1].replace("''", "'")
    else:
        quote_char = ""
        word = eat(TOKEN_BARE_WORD)
    if Debug>=2: print_log("Found word:  '" + word + "'")
    node = create_word_node(word, quote_char, get_last_position())
    return node

def parse_word1(bare_word, position):
    global Debug
    if Debug>=2: print_log("Found word:  '" + bare_word + "'")
    node = create_word_node(bare_word, "", position)
    node["POSITION"] = position
    return node


def implementation_error(error):
    log_error(error)
    raise RuntimeError(error)    # <<<>>>

def error(message, position, advice=""):
    log_error(message, position, advice)
    raise RuntimeError(message)    # <<<>>>

def log_error(message, position=None, advice=""):
    global Error_count, Input_name
    if Error_count==0: print_log("Converting " + Input_name)
    print_log(format_error_message(message, position, advice), True)
    Error_count += 1

def format_error_message(message, position=None, advice=""):
    global Include_stack_file, Include_stack_line

    if message[-1] == "\n":
        message = message[:-1]

    at_line = ""
    if position != None:
        at_line = " at line " + str(get_line_number(position))
    of_file = ""
    if len(Include_stack_file) > 1:
        of_file = " of " + Include_stack_file[-1]
    message = "  Error" + at_line + of_file + ":  " + message + "\n"

    indent = ""
    i = len(Include_stack_file)-2
    while i >= 0:
        file = Include_stack_file[i]
        line_number = Include_stack_line[i]
        indent  += "  "
        message += indent + "  (Included at line " + str(line_number) + " of " \
            + file + ")\n"
        i -= 1

    if position != None:
        message += point_to_position(position)

    if advice != "":
        message += advice + "\n"

    return message

# Return TRUE if filename was already included in the current .vcl file
def already_included(filename):
    _short_name, canonical_path = canonicalize_in_file(filename)
    return canonical_path in Included_files

def expand_variables(actions):
    result = ""
    for action in actions:
        type = action["TYPE"]
        if type == "word":
            result += action["TEXT"]
        elif type == "formalref":
            variable = action["TEXT"][1:]
            value = os.environ.get(variable)
            if not value:
                # Should be a warning not an error.
                log_error("Reference to unknown environment variable '"
                          + variable + "'", action["POSITION"])
            else:
                result += value
        else:
            implementation_error("unsupported action type in include actions")
    return result

# ---------------------------------------------------------------------------
# Parse-time error checking of references

def verify_referenced_menu(menu, parent_has_actions=False, parent_has_alternatives=False):
    commands         = menu["COMMANDS"]
    has_alternatives = parent_has_alternatives or (len(commands) != 1)

    for command in commands:
        has_actions = parent_has_actions
        if "ACTIONS" in command:
            has_actions = True
            if parent_has_actions:
                error("Nested in-line lists with associated actions may not themselves contain actions",
                      menu["POSITION"])

        terms = command["TERMS"]
        verify_menu_terms(terms, has_actions, has_alternatives, False)

def verify_menu_terms(terms, has_actions, has_alternatives, other_terms):
    if len(terms) != 1: other_terms = True
    for term in terms:
        type = term["TYPE"]
        if   type == "word" and term["OPTIONAL"]:
            #error("Alternative cannot contain an optional word",
            #      term["POSITION"])
            implementation_error("Alternative cannot contain an optional word")
        elif type == "optionalterms":
            verify_menu_terms(term["TERMS"], has_actions, has_alternatives,
                              other_terms)
        elif type == "variable" or type == "dictation":
            error("Alternative cannot contain a variable", term["POSITION"])
        elif type == "menu":
            if other_terms:
                error("An inline list cannot be combined with anything else to make up an alternative",
                      term["POSITION"])
            verify_referenced_menu(term, has_actions, has_alternatives)
        elif type == "range":
            # allow a single range with no actions if it is the only
            # alternative in the (nested) set:
            if other_terms:
                error("A range cannot be combined with anything else to make up an alternative",
                      term["POSITION"])
            if has_actions:
                error("A range alternative may not have associated actions",
                      term["POSITION"])
            if has_alternatives:
                error("A range alternative must be the only alternative in an alternative set",
                      term["POSITION"])

def add_forward_reference(variable, position):
    global Forward_references, Include_stack_file, Include_stack_line
    forward_reference = {}
    forward_reference["VARIABLE"]   = variable
    forward_reference["POSITION"]   = position
    forward_reference["STACK_FILE"] = Include_stack_file[:]
    forward_reference["STACK_LINE"] = Include_stack_line[:]
    Forward_references.append(forward_reference)

def check_forward_references():
    global Definitions, Error_count, Forward_references, Input_name
    global Include_stack_file, Include_stack_line
    for forward_reference in Forward_references:
        variable = forward_reference["VARIABLE"]
        if variable not in Definitions:
            stack_file = Include_stack_file
            stack_line = Include_stack_line

            position           = forward_reference["POSITION"]
            Include_stack_file = forward_reference["STACK_FILE"]
            Include_stack_line = forward_reference["STACK_LINE"]
            log_error("Reference to undefined variable '<" + variable + ">'",
                      position)

            Include_stack_file = stack_file
            Include_stack_line = stack_line



import vcl2py.lex as lex
lex.log_error = log_error  # temporary kludge
import vcl2py.emit as emit
emit.log_error = log_error  # temporary kludge
