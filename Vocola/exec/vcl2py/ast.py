#   The parse tree is built from three kinds of nodes (statement,
# term, and action), using the following fields:
#
# statement:
#    TYPE - command/definition/function/context/include/set
#    command:
#       NAME    - unique number
#       TERMS   - list of "term" structures
#       ACTIONS - list of "action" structures
#       LINE    - last line number of command if it is a top-level command
#       FILE    - filename of file containing command
#    definition:
#       NAME    - name of variable being defined
#       MENU    - "menu" structure defining alternatives
#    function:
#       NAME    - name of function being defined
#       FORMALS - list of argument names
#       ACTIONS - list of "action" structures
#    context:
#       STRINGS - list of strings to use in context matching;
#                 the list ("") denotes the noop context restriction (:)
#       RULENAMES - list of rule names defined for this context
#    include:
#       TEXT    - filename being included before environment var. expansion
#       ACTIONS - list of "action" structures (word or formalref only)
#    set:
#       KEY     - key being set
#       TEXT    - value to set the key to
#
# term:
#    TYPE   - word/variable/range/menu/dictation/optionalterms
#    NUMBER - sequence number of this term
#    word:
#       TEXT     - text defining the word(s)
#       OPTIONAL - are these words optional?
#    variable:
#       TEXT     - name of variable being referenced
#       OPTIONAL - is this variable optional?
#    range:
#       FROM     - start number of range
#       TO       - end number of range
#    menu:
#       COMMANDS - list of "command" structures defining the menu
#    optionalterms:
#       TERMS   - list of "term" structures
#
# action:
#    TYPE - word/reference/formalref/call
#    word:
#       TEXT       - keystrokes to send
#       POSITION   - position of the start of the word
#       QUOTE_CHAR - empty if bareword else ' or "
#    reference:
#       TEXT      - reference number (a string) of reference referenced
#    formalref:
#       TEXT      - name of formal (i.e. user function argument) referenced;
#                   has a "_" in the front of user supplied name  <<<>>>
#       POSITION  - position of the start of the reference
#    call:
#       TEXT      - name of function called
#       CALLTYPE  - dragon/vocola/user/extension
#       ARGTYPES  - [dragon only] types of call arguments
#       ARGUMENTS - list of lists of actions, to be passed in call


# ---------------------------------------------------------------------------
# Miscellaneous node creation routines:

def create_word_node(text, quote_char, position):
    term = {}
    term["TYPE"]       = "word"
    term["TEXT"]       = text
    term["POSITION"]   = position
    term["QUOTE_CHAR"] = quote_char
    return term


def get_variable_terms(terms):
    variable_terms = []
    for term in terms:
        type = term["TYPE"]
        if type == "menu" or type == "range" or type == "variable" or \
           type == "dictation":
            variable_terms.append(term)
        elif type == "optionalterms":
            variable_terms += get_variable_terms(term["TERMS"])
    return variable_terms

def create_variable_node(name):
    term = {}
    term["TYPE"] = "variable"
    term["TEXT"] = name
    return term


def combine_terms(terms):   # Combine adjacent "word" terms; number resulting terms
    new_terms = []
    term_count = 0
    i = 0
    while i < len(terms):
        term = terms[i]
        i += 1

        if is_required_word(term):
            while i<len(terms) and is_required_word(terms[i]):
                term["TEXT"] += " " + terms[i]["TEXT"]
                i += 1
        term["NUMBER"] = term_count
        term_count += 1
        new_terms.append(term)

    return new_terms

def is_required_word(term):
    return term["TYPE"] == "word" and not term["OPTIONAL"]




# ---------------------------------------------------------------------------
# Unparsing of data structures (for debugging and generating error messages)

def unparse_statements(statements):
    result = ""
    for statement in statements:
        type = statement["TYPE"]
        if type == "context" or type == "include" or type == "set":
            result += unparse_directive(statement)
        elif type == "definition":
            result += unparse_definition(statement)
        elif type == "function":
            result += unparse_function_definition(statement)
        elif type == "command":
            result +=  "C" + statement["NAME"] + ":  "
            result += unparse_command(statement, True) + ";\n"
    return result + "\n"

def unparse_directive(statement):
    type = statement["TYPE"]
    if type == "set":
        return "$set '" + statement["KEY"] + "' to '" + statement["TEXT"] + "'\n"
    elif type == "context":
        return "|".join(statement["STRINGS"]) + ":\n"
    else:
        return statement["TYPE"] + ":  '" + statement["TEXT"] + "'\n"

def unparse_definition(statement):
    return "<" + statement["NAME"] + "> := " + \
        unparse_menu(statement["MENU"], True) + ";\n"

def unparse_function_definition(statement):
    result = statement["NAME"] + "(" + ",".join(statement["FORMALS"])
    result += ") := " + unparse_actions(statement["ACTIONS"])
    return result + ";\n"

def unparse_command(command, show_actions):
    result = unparse_terms(show_actions, command["TERMS"])
    if "ACTIONS" in command and show_actions:
        result += " = " + unparse_actions(command["ACTIONS"])
    return result

def unparse_terms(show_actions, terms):
    result = unparse_term(terms[0], show_actions)
    for term in terms[1:]:
        result += " " + unparse_term(term, show_actions)
    return result

def unparse_term(term, show_actions):
    if term["TYPE"] == "optionalterms":
        return "[" + unparse_terms(show_actions, term["TERMS"]) + "]"

    result = ""
    if term.get("OPTIONAL"): result +=  "["

#    if   term["TYPE"] == "word":      result += term["TEXT"]
    if   term["TYPE"] == "word":      result += "'" + term["TEXT"] + "'"
    elif term["TYPE"] == "variable":  result += "<" + term["TEXT"] + ">"
    elif term["TYPE"] == "dictation": result += "<_anything>"
    elif term["TYPE"] == "menu":
        result += unparse_menu(term, show_actions)
    elif term["TYPE"] == "range":
        result += str(term["FROM"]) + ".." + str(term["TO"])

    if term.get("OPTIONAL"): result +=  "]"
    return result

def unparse_menu(menu, show_actions):
    commands = menu["COMMANDS"]
    result = "(" + unparse_command(commands[0], show_actions)
    for command in commands[1:]:
        result += " | " + unparse_command(command, show_actions)
    return result + ")"

def unparse_actions(actions):
    if len(actions) == 0: return ""  # bug fix <<<>>>
    result  = unparse_action(actions[0])
    for action in actions[1:]:
        result += " " + unparse_action(action)
    return result

def unparse_action(action):
    if   action["TYPE"] == "word":      return unparse_word(action)
    elif action["TYPE"] == "reference": return "$" + action["TEXT"]
    elif action["TYPE"] == "formalref": return "$" + action["TEXT"]
    elif action["TYPE"] == "call":
        result = action["TEXT"] + "("
        arguments = action["ARGUMENTS"]
        if len(arguments) > 0:
            result += unparse_argument(arguments[0])
            for argument in arguments[1:]:
                result += ", " + unparse_argument(argument)
        return result + ")"
    else:
        return "<UNKNOWN ACTION>"  # should never happen...

def unparse_word(action):
    word = action["TEXT"]
    word = word.replace("'", "''")

    return "'" + word + "'"

def unparse_argument(argument):
    return unparse_actions(argument)
