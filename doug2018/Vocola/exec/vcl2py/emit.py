import re
from vcl2py.ast import *

log_error = None   # temporary kludge

def output(out_file, statements,
           _VocolaVersion,
           _Should_emit_dictation_support,
           _Module_name,
           _Number_words,
           _Definitions,
           _Maximum_commands,
           _Extension_functions
           ):
    global NestedCallLevel
    global VocolaVersion, Should_emit_dictation_support
    global Module_name, Number_words, Definitions, Maximum_commands
    global Extension_functions

    NestedCallLevel               = 0

    VocolaVersion = _VocolaVersion
    Should_emit_dictation_support = _Should_emit_dictation_support
    Module_name = _Module_name
    Number_words = _Number_words
    Definitions = _Definitions
    Maximum_commands = _Maximum_commands
    Extension_functions = _Extension_functions

    emit_output(out_file, statements)



# ---------------------------------------------------------------------------
# Emit NatLink output

def emit_output(out_file, statements):
    global Should_emit_dictation_support, OUT
    try:
        OUT = open(out_file, "w")
    except IOError as e:
        log_error("Unable to open output file '" + out_file + \
                  "' for writing: " + str(e))
        return
    emit_file_header()
    if Should_emit_dictation_support: emit_dictation_grammar()
    for statement in statements:
        type = statement["TYPE"]
        if   type == "definition": emit_definition_grammar (statement)
        elif type == "command":    emit_command_grammar (statement)
    emit_sequence_and_context_code(statements)
    emit_number_words()
    for statement in statements:
        type = statement["TYPE"]
        if    type == "definition": emit_definition_actions (statement)
        if    type == "function":   pass
        elif type == "command":     emit_top_command_actions (statement)
    emit_file_trailer()
    OUT.close()

def emit_sequence_and_context_code(statements):
    # Build a list of context statements, and commands defined in each
    noop     = None
    context  = None
    contexts = []
    for statement in statements:
        type = statement["TYPE"]
        if type == "context":
            context = statement
            strings = context["STRINGS"]
            if strings[0] == "":   # <<<>>>
                # no-op context restriction
                if noop != None:
                    context = noop
                else:
                    noop = context
                    context["RULENAMES"] = []
                    contexts.append(context)
            else:
                context["RULENAMES"] = []
                contexts.append(context)
        elif type == "command":
            context["RULENAMES"].append(statement["NAME"])
    emit_sequence_rules(contexts)
    emit_file_middle()
    emit_context_activations(contexts)

def emit_sequence_rules(contexts):
    global Maximum_commands
    # Emit rules allowing speaking a sequence of commands
    # (and add them to the RULENAMES for the context in question)
    number = 0
    any = ""
    for context in contexts:
        names = context["RULENAMES"]
        if len(names) == 0: continue
        number += 1
        suffix = ""
        rules = '<' + '>|<'.join(names) + '>'
        strings = context["STRINGS"]
        if strings[0] == "":
            emit(2, "<any> = " + rules + ";\n")
            any = "<any>|"
        else:
            suffix = "_set" + str(number)
            emit(2, "<any" + suffix + "> = " + any + "" + rules + ";\n")
        rule_name = "sequence" + suffix
        context["RULENAMES"] = [rule_name]
        emit(2, "<" + rule_name + "> exported = " +
                repeated_upto("<any" + suffix + ">", Maximum_commands) + ";\n")

def repeated_upto(spec, count):
    # Create grammar for a spec repeated 1 upto count times
    if count>99: return spec + "+"

    result = spec
    while count > 1:
        result = spec + " [" + result + "]"
        count = count - 1
    return result

def emit_context_activations(contexts):
    app = Module_name
    module_is_global = (app.startswith("_"))

    if module_is_global:
        for context in contexts:
            names = context["RULENAMES"]
            if len(names) == 0: continue
            strings = context["STRINGS"]
            if strings[0] == "":
                emit(2, "self.activate('" + names[0] + "')\n")

    emit_file_middle2()

    emit(0, "\n    def gotBegin(self,moduleInfo):\n")
    emit(2, "self.firstWord = 0\n")
    if module_is_global:
        emit(2, "window = moduleInfo[2]\n")
    else:
        emit(2, "# Return if wrong application\n")
        executable = app
        emit(2, "window = matchWindow(moduleInfo,'" + executable + "','')\n")
        while executable.find("_") != -1:
            match = re.match(r'^(.+?)_+[^_]*$', executable)
            if not match: break
            executable = match.group(1)
            emit(2, "if not window: window = matchWindow(moduleInfo,'" + \
                    executable + "','')\n")
        emit(2, "if not window: return None\n")

    emit(2, "# Return if same window and title as before\n")
    emit(2, "if moduleInfo == self.currentModule: return None\n")
    emit(2, "self.currentModule = moduleInfo\n\n")

    # Emit code to activate the context's commands iff one of the context
    # strings matches the current window
    emit(2, "title = string.lower(moduleInfo[1])\n")
    for context in contexts:
        names = context["RULENAMES"]
        if len(names) == 0: continue
        targets = context["STRINGS"]
        if targets[0] == "":
            if not module_is_global:
                emit(2, "self.activate_rule('" + names[0] + "', moduleInfo[2], True)\n")
        else:
            targets = [make_safe_python_string(target) for target in targets]
            tests = " or ".join(["string.find(title,'" + target + "') >= 0" for target in targets])
            emit(2, "status = (" + tests + ")\n")
            emit(2, "self.activate_rule('" + names[0] + "', moduleInfo[2], status)\n")
    emit(0, "\n")


def emit_dictation_grammar():
    emit(2, "<dgndictation> imported;\n")

def emit_definition_grammar(definition):
    emit(2, "<" + definition["NAME"] + "> = ")
    emit_menu_grammar (definition["MENU"]["COMMANDS"])
    emit(0, ";\n")

def emit_command_grammar(command):
    inline_a_term_if_nothing_concrete(command)
    (first, last) = find_terms_for_main_rule(command)
    terms = command["TERMS"]
    main_terms = terms[first:last+1]
    name = command["NAME"]
    name_a = name + "a"
    name_b = name + "b"
    if first > 0: main_terms = [create_variable_node(name_a)] + main_terms
    if last < len(terms)-1: main_terms.append(create_variable_node(name_b))
    emit_rule(command["NAME"], "", main_terms)
    if first > 0: emit_rule(name_a, "", terms[0:first])
    if last < len(terms)-1: emit_rule(name_b, "", terms[last+1:])

def emit_rule(name, exported, terms):
    emit(2, "<" + name + ">" + exported + " = ")
    emit_command_terms(terms)
    emit(0, ";\n")

def emit_command_terms(terms):
    for term in terms:
        if term.get("OPTIONAL", False): emit(0, "[ ")
        if term["TYPE"] == "word":
            word = term["TEXT"].replace("\\", "\\\\")
            if word.find("'") != -1: emit(0, '"' + word + '" ')
            else:               emit(0, "'" + word + "' ")
        elif term["TYPE"] == "dictation": emit(0, "<dgndictation> ")
        elif term["TYPE"] == "variable":  emit_variable_term(term)
        elif term["TYPE"] == "range":     emit_range_grammar(term)
        elif term["TYPE"] == "menu":
            emit(0, "(")
            emit_menu_grammar(term["COMMANDS"])
            emit(0, ") ")
        if term.get("OPTIONAL", False): emit(0, "] ")

def emit_variable_term(term):
    text = term["TEXT"]
    emit(0, "<" + text + "> ")

def emit_menu_grammar(commands):
    emit_command_terms(commands[0]["TERMS"])
    for command in commands[1:]:
        emit(0, "| ")
        emit_command_terms(command["TERMS"])

def emit_range_grammar(range_term):
    i  = range_term["FROM"]
    to = range_term["TO"]
    emit(0, "(" + emit_number_word(i))
    for i in range(i+1,to+1):
        emit(0, " | " + emit_number_word(i))
    emit(0, ") ")

def emit_number_word(i):
    global Number_words
    if i in Number_words:
        return "'" + Number_words[i] + "'"
    return str(i)

def emit_number_words():
    global Number_words
    emit(1, "def convert_number_word(self, word):\n")

    if len(Number_words) == 0:
        emit(2, "return word\n\n")
        return
    elif_keyword = "if  "
    numbers = list(Number_words.keys())
    numbers.sort()
    for number in numbers:
        emit(2, elif_keyword + " word == '" + Number_words[number]+ "':\n")
        emit(3, "return '" + str(number) + "'\n")
        elif_keyword = "elif"
    emit(2, "else:\n")
    emit(3, "return word\n\n")

def emit_definition_actions(definition):
    emit(1,
         "def get_" + definition["NAME"] + "(self, list_buffer, functional, word):\n")
    emit_menu_actions("list_buffer", "functional", definition["MENU"], 2)
    emit(2, "return list_buffer\n\n")

def emit_top_command_actions(command):
    global Variable_terms, OUT
    terms = command["TERMS"]
    nterms = len(terms)
    function = "gotResults_" + command["NAME"]
    Variable_terms = get_variable_terms(terms) # used in emit_reference

    command_specification = unparse_terms(0, terms)

    emit(1, "# ")
    print(unparse_terms (0, terms), end=' ', file=OUT)
    emit(0, "\n")
    emit(1, "def " + function + "(self, words, fullResults):\n")
    emit(2, "if self.firstWord<0:\n")
    emit(3, "return\n")
    emit_optional_term_fixup(terms)
    emit(2, "try:\n")
    emit(3, "top_buffer = ''\n")
    emit_actions("top_buffer", "False", command["ACTIONS"], 3)
    emit_flush("top_buffer", "False", 3)
    emit(3, "self.firstWord += " + str(nterms) + "\n")

    # If repeating a command with no <variable> terms (e.g. "Scratch That
    # Scratch That"), our gotResults function will be called only once, with
    # all recognized words. Recurse!
    if not has_variable_term(terms):
        emit(3, "if len(words) > " + str(nterms) + ": self." + function + \
                "(words[" + str(nterms) + ":], fullResults)\n")
    emit(2, "except Exception, e:\n")
    file = command["FILE"]
    emit(3, "handle_error('" + make_safe_python_string(file) +
            "', " + str(command["LINE"]) + ", '" +
            make_safe_python_string(command_specification) +
            "', e)\n")
    emit(3, "self.firstWord = -1\n")
    emit(0, "\n")

def emit_flush(buffer, functional, indent):
    emit(indent, buffer + " = do_flush(" + functional + ", " + buffer + ");\n")

def has_variable_term(unnamed):
    for term in unnamed:
        if term["TYPE"] == "variable" or term["TYPE"] == "dictation": return 1
    return 0

# Our indexing into the "fullResults" array assumes all optional terms were
# spoken.  So we emit code to insert a dummy entry for each optional word
# that was not spoken.  (The strategy used could fail in the uncommon case
# where an optional word is followed by an identical required word.)

def emit_optional_term_fixup(unnamed):
    for term in unnamed:
        index = term["NUMBER"]
        if term.get("OPTIONAL", False):
            text = term["TEXT"]
            emit(2, "opt = " + str(index) + " + self.firstWord\n")
            emit(2, "if opt >= len(fullResults) or fullResults[opt][0] != '" + text + "':\n")
            emit(3, "fullResults.insert(opt, 'dummy')\n")
        elif term["TYPE"] == "dictation":
            emit(2, "fullResults = combineDictationWords(fullResults)\n")
            emit(2, "opt = " + str(index) + " + self.firstWord\n")
            emit(2, "if opt >= len(fullResults) or fullResults[opt][1] != 'converted dgndictation':\n")
            emit(3, "fullResults.insert(opt, ['', 'converted dgndictation'])\n")

def emit_actions(buffer, functional, actions, indent):
    for action in actions:
        type = action["TYPE"]
        if type == "reference":
            emit_reference(buffer, functional, action, indent)
        elif type == "formalref":
            implementation_error("Not all formal references transformed away")
        elif type == "word":
            safe_text = make_safe_python_string(action["TEXT"])
            emit(indent, buffer + " += '" + safe_text + "'\n")
        elif type == "call":
            emit_call(buffer, functional, action, indent)
        else:
            implementation_error("Unknown action type: '" + type + "'")

def emit_reference(buffer, functional, action, indent):
    global Variable_terms
    reference_number = int(action["TEXT"]) - 1
    variable         = Variable_terms[reference_number]
    term_number      = variable["NUMBER"]
    emit(indent, "word = fullResults[" + str(term_number) + " + self.firstWord][0]\n")
    if variable["TYPE"] == "menu":
        emit_menu_actions(buffer, functional, variable, indent)
    elif variable["TYPE"] == "range":
        emit(indent, buffer + " += self.convert_number_word(word)\n")
    elif variable["TYPE"] == "dictation":
        emit(indent, buffer + " += word\n")
    elif variable["TYPE"] == "variable":
        function = "self.get_" + variable["TEXT"]
        emit(indent, buffer + " = " + function + "(" + buffer + ", " + \
                     functional + ", word)\n")

def emit_menu_actions(buffer, functional, menu, indent):
    if not menu_has_actions(menu):
        if menu_is_range(menu):
            emit(indent, buffer + " += self.convert_number_word(word)\n")
        else:
            emit(indent, buffer + " += word\n")
    else:
        commands = flatten_menu(menu)
        if_keyword = "if"
        for command in commands:
            text = command["TERMS"][0]["TEXT"]
            text = text.replace("\\", "\\\\")
            text = text.replace("'", "\\'")
            emit(indent, if_keyword + " word == '" + text + "':\n")
            if "ACTIONS" in command:
                if len(command["ACTIONS"]) != 0:
                    emit_actions(buffer, functional,
                                 command["ACTIONS"], indent+1)
                else:
                    emit(indent+1, "pass  # no actions\n")
            else:
                emit(indent+1, buffer + " += '" + text + "'\n")
            if_keyword = "elif"

def emit_call(buffer, functional, call, indent):
    callType = call["CALLTYPE"]
    begin_nested_call()
    if   callType == "dragon":
        emit_dragon_call(buffer, functional, call, indent)
    elif callType == "extension":
        emit_extension_call(buffer, functional, call, indent)
    elif callType == "user"     :
        implementation_error("No user function call should be present here!")
    elif callType == "vocola":
        callName = call["TEXT"]
        if    callName == "Eval":
            implementation_error("Eval not transformed away")
        elif callName == "EvalTemplate":
            emit_call_eval_template(buffer, functional, call, indent)
        elif callName == "If":
            emit_call_if(buffer, functional, call, indent)
        elif callName == "Repeat":
            emit_call_repeat(buffer, functional, call, indent)
        elif callName == "Unimacro":
            emit_call_Unimacro(buffer, functional, call, indent)
        elif callName == "When":
            emit_call_when(buffer, functional, call, indent)
        else: implementation_error("Unknown Vocola function: '" + callName + "'")
    else: implementation_error("Unknown function call type: '" + callType + "'")
    end_nested_call()

def begin_nested_call():
    global NestedCallLevel
    NestedCallLevel += 1

def end_nested_call():
    global NestedCallLevel
    NestedCallLevel -= 1

def get_nested_buffer_name(root):
    global NestedCallLevel
    if NestedCallLevel == 1:
        return root
    else:
        return root + str(NestedCallLevel)

def emit_call_repeat(buffer, functional, call, indent):
    arguments = call["ARGUMENTS"]

    argument_buffer = get_nested_buffer_name("limit")
    emit(indent, argument_buffer + " = ''\n")
    emit_actions(argument_buffer, "True", arguments[0], indent)
    emit(indent, "for i in range(to_long(" + argument_buffer + ")):\n")
    emit_actions(buffer, functional, arguments[1], indent+1)

def emit_call_if(buffer, functional, call, indent):
    arguments = call["ARGUMENTS"]

    argument_buffer = get_nested_buffer_name("conditional_value")
    emit(indent, argument_buffer + " = ''\n")
    emit_actions(argument_buffer, "True", arguments[0], indent)
    emit(indent, "if " + argument_buffer + ".lower() == \"true\":\n")
    emit_actions(buffer, functional, arguments[1], indent+1)
    if len(arguments)>2:
        emit(indent, "else:\n")
        emit_actions(buffer, functional, arguments[2], indent+1)

def emit_call_when(buffer, functional, call, indent):
    arguments = call["ARGUMENTS"]

    argument_buffer = get_nested_buffer_name("when_value")
    emit(indent, argument_buffer + " = ''\n")
    emit_actions(argument_buffer, "True", arguments[0], indent)
    emit(indent, "if " + argument_buffer + " != \"\":\n")
    emit_actions(buffer, functional, arguments[1], indent+1)
    if len(arguments)>2:
        emit(indent, "else:\n")
        emit_actions(buffer, functional, arguments[2], indent+1)

def emit_arguments(call, name, indent):
    arguments = ""

    i=0
    for argument in call["ARGUMENTS"]:
        if i != 0:  arguments += ", "
        i += 1
        argument_buffer = get_nested_buffer_name(name) + "_arg" + str(i)
        emit(indent, argument_buffer + " = ''\n")
        emit_actions(argument_buffer, "True", argument, indent)
        arguments += argument_buffer
    return arguments

def emit_dragon_call(buffer, functional, call, indent):
    callName  = call["TEXT"]
    argumentTypes = call["ARGTYPES"]

    emit_flush(buffer, functional, indent)
    arguments = emit_arguments(call, "dragon", indent)
    emit(indent, "saved_firstWord = self.firstWord\n")
    emit(indent,
         "call_Dragon('" + callName + "', '" + argumentTypes + "', [" + arguments + "])\n")
    emit(indent, "self.firstWord = saved_firstWord\n")

def emit_extension_call(buffer, functional, call, indent):
    global Extension_functions
    callName      = call["TEXT"]
    callFormals   = Extension_functions[callName]
    needsFlushing = callFormals[2]
    import_name   = callFormals[3]
    function_name = callFormals[4]

    if needsFlushing:  emit_flush(buffer, functional, indent)
    arguments = emit_arguments(call, "extension", indent)
    emit(indent, "import " + import_name + "\n")
    if needsFlushing:
        emit(indent, function_name + "(" + arguments + ")\n")
    else:
        emit(indent, buffer + " += str(" + function_name + "(" + arguments + "))\n")

def emit_call_eval_template(buffer, functional, call, indent):
    arguments = emit_arguments(call, "eval_template", indent)
    emit(indent, buffer + " += eval_template(" + arguments + ")\n")

def emit_call_Unimacro(buffer, functional, call, indent):
    emit_flush(buffer, functional, indent)
    arguments = emit_arguments(call, "unimacro", indent)
    emit(indent, "call_Unimacro(" + arguments + ")\n")

# ---------------------------------------------------------------------------
# Utilities for transforming command terms into NatLink rules
#
# For each Vocola command, we define a NatLink rule and an associated
# "gotResults" function. When the command is spoken, we want the gotResults
# function to be called exactly once. But life is difficult -- NatLink calls a
# gotResults function once for each contiguous sequence of spoken words
# specifically present in the associated rule. There are two problems:
#
# 1) If a rule contains only references to other rules, it won't be called
#
# We solve this by "inlining" variables (replacing a variable term with the
# variable's definition) until the command is "concrete" (all branches contain
# a non-optional word).
#
# 2) If a rule is "split" (e.g. "Kill <n> Words") it will be called twice
#
# We solve this by generating two rules, e.g.
#    <1> exported = 'Kill' <n> <1a> ;
#    <1a> = 'Words' ;

def find_terms_for_main_rule(command):
    # Create a "variability profile" summarizing whether each term is
    # concrete (c), variable (v), or optional (o). For example, the
    # profile of "[One] Word <direction>" would be "ocv". (Menus are
    # assumed concrete, and dictation variables are treated like
    # normal variables.)

    pattern = ""
    for term in command["TERMS"]:
        if term["TYPE"] == "variable" or term["TYPE"] == "dictation":
            pattern += "v"
        elif term.get("OPTIONAL", False):
            pattern += "o"
        else:
            pattern += "c"
    # Identify terms to use for main rule.
    # We might not start with the first term. For example:
    #     [Move] <n> Left  -->  "Left" is the first term to use
    # We might not end with the last term. For example:
    #     Kill <n> Words   -->  "Kill" is the last term to use
    # And in this combined example, our terms would be "Left and Kill"
    #     [Move] <n> Left and Kill <n> Words

    match = re.match(r'v*o+v[ov]*c', pattern)
    if match:
        first = match.end(0)-1
    else:
        first = 0

    match = re.match(r'([ov]*c[co]*)v+[co]+', pattern)
    if match:
        last = match.end(1)-1
    else:
        last = len(pattern)-1

    return (first, last)

def inline_a_term_if_nothing_concrete(command):
    while not command_has_a_concrete_term(command):
        inline_a_term(command)

def command_has_a_concrete_term(command):
    for term in command["TERMS"]:
        if term_is_concrete(term): return True
    return False

def term_is_concrete(term):
    type = term["TYPE"]
    if   type == "menu":                            return True
    elif type == "variable" or type == "dictation": return False
    else: return not term["OPTIONAL"]

def inline_a_term(unnamed):
    global Definitions
    terms = unnamed["TERMS"]

    # Find the array index of the first non-optional term
    index = 0
    while (index < terms) and (terms[index]["OPTIONAL"] or terms[index]["TYPE"] == "dictation"): index += 1

    type = terms[index]["TYPE"]
    number = terms[index]["NUMBER"]
    if type == "variable":
        variable_name = terms[index]["TEXT"]
        #print "inlining variable $variable_name\n";
        definition = Definitions[variable_name]
        terms[index] = definition["MENU"]
        terms[index]["NUMBER"] = number
    elif type == "menu":
        for command in terms[index]["COMMANDS"]:
            inline_a_term(command)
    else: implementation_error("Inlining term of type '" + type + "'")

# ---------------------------------------------------------------------------
# Utilities used by "emit" methods

def emit(indent, text):
    global OUT
    OUT.write(' ' * (4 * indent) + text)

def menu_has_actions(menu):
    for command in menu["COMMANDS"]:
        if "ACTIONS" in command: return True
        for term in command["TERMS"]:
            if term["TYPE"] == "menu" and menu_has_actions(term): return True
    return False

def menu_is_range(menu):  # verified menu => can contain only 1 range as a 1st term
    commands = menu["COMMANDS"]
    for command in commands:
        terms = command["TERMS"]
        type = terms[0]["TYPE"]
        if type == "menu" and menu_is_range(terms[0]):  return True
        if type == "range":  return True
    return False

# To emit actions for a menu, build a flat list of (canonicalized) commands:
#     - recursively extract commands from nested menus
#     - distribute actions, i.e. (day|days)=d --> (day=d|days=d)
# Note that error checking happened during parsing, in verify_referenced_menu

def flatten_menu(menu, actions_to_distribute=[]):
    new_commands = []
    for command in menu["COMMANDS"]:
        if "ACTIONS" in command: new_actions = command["ACTIONS"]
        else:                          new_actions = actions_to_distribute
        terms = command["TERMS"]
        type = terms[0]["TYPE"]
        if type == "word":
            if new_actions: command["ACTIONS"] = new_actions
            new_commands.append(command)
        elif type == "menu":
            commands = flatten_menu (terms[0], new_actions)
            new_commands.extend(commands)
    return new_commands

def make_safe_python_string(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace("\n", "\\n")

    return text

# ---------------------------------------------------------------------------
# Pieces of the output Python file

def emit_file_header():
    global VocolaVersion, OUT
    from time import localtime, strftime

    now = strftime("%a %b %d %H:%M:%S %Y", localtime())
    print("# NatLink macro definitions for NaturallySpeaking", file=OUT)
    print("# coding: latin-1", file=OUT)
    print("# Generated by vcl2py " + VocolaVersion + ", " + now, file=OUT)
    print('''
import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
''', end=' ', file=OUT)

def emit_file_middle():
    print('''    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
        self.rule_state = {}
''', end=' ', file=OUT)

def emit_file_middle2():
    print('''    
    def activate_rule(self, rule, window, status):
        current = self.rule_state.get(rule)
        active = (current == window)
        if status == active: return
        if current:
            self.deactivate(rule)
            self.rule_state[rule] = None
        if status:
            try:
                self.activate(rule, window)
                self.rule_state[rule] = window
            except natlink.BadWindow:
                pass
''', end=' ', file=OUT)

def emit_file_trailer():
    print('''thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
''', end=' ', file=OUT)
