import copy

from vcl2py.ast import *


def transform(nodes,
              function_definitions, statement_count
              ):
    global Function_definitions, Statement_count

    Function_definitions = function_definitions
    Statement_count = statement_count
    return transform_nodes(nodes)


# ---------------------------------------------------------------------------
# Transform Eval into EvalTemplate, unroll user functions, and remove
# optional term groups by duplicating commands with and without the
# optional terms.

  # takes a list of non-action nodes
def transform_nodes(nodes):   # -> nodes
    result = []
    for node in nodes:
        transform_node(node)
        if node["TYPE"] == "command":
            result += transform_command(node)
        else:
            result.append(node)
    return result

def transform_node(node):
    if "COMMANDS" in node:
        node["COMMANDS"] = transform_nodes(node["COMMANDS"])
    if "TERMS" in node:
        node["TERMS"]    = transform_nodes(node["TERMS"])
    if "MENU" in node: transform_node(node["MENU"])

    if "ACTIONS" in node:
        substitution = {}
        node["ACTIONS"] = transform_actions(substitution, node["ACTIONS"])

  # this is called after command's subnodes have been transformed:
def transform_command(command):  # -> commands !
    global Statement_count

    terms = command["TERMS"]
    i = offset_of_first_optional(terms)
    if i < 0:
        return [command]

    without         = copy.deepcopy(command)
    without["NAME"] = str(Statement_count)
    Statement_count += 1

    with_terms = command
    with_terms["TERMS"] = combine_terms(terms[0:i] + terms[i]["TERMS"] + terms[i+1:])

    without_terms    = without["TERMS"]
    without["TERMS"] = combine_terms(without_terms[0:i] + without_terms[i+1:])
    before    = len(get_variable_terms(without_terms[0:i]))
    vanishing = len(get_variable_terms(terms[i]["TERMS"]))
    after     = len(get_variable_terms(without_terms[i+1:]))
    if "ACTIONS" in without:
        without["ACTIONS"] = nop_references(without["ACTIONS"], before,
                                            vanishing, after)
    return transform_command(with_terms) + transform_command(without)

def offset_of_first_optional(terms):
    i = 0
    for term in terms:
        if term["TYPE"] == "optionalterms":
            return i
        i += 1
    return -1

def nop_references(actions, before, vanishing, after):
    nop = create_word_node("", "", -1)

    substitution = {}
    for j in range(1+before,1+before+vanishing):
        substitution[str(j)] = [nop]
    for j in range(1+before+vanishing, 1+before+vanishing+after):
        reference         = {}
        reference["TYPE"] = "reference"
        reference["TEXT"] = str(j - vanishing)
        substitution[str(j)] = [reference]

    return transform_actions(substitution, actions)

# transforms above are (partially) destructive, transforms below are
# functional except transform_eval

def transform_actions(substitution, actions):
    new_actions = []
    for action in actions:
        new_actions.extend(transform_action(substitution, action))
    return new_actions

def transform_arguments(substitution, arguments): # -> lists of actions
    new_arguments = []
    for argument in arguments:
        new_arguments.append(transform_actions(substitution, argument))
    return new_arguments

def transform_action(substitution, action):  # -> actions
    if action["TYPE"] == "formalref" or action["TYPE"] == "reference":
        name = action["TEXT"]
        if name in substitution:
            return substitution[name]
    if action["TYPE"] == "call":
        return transform_call(substitution, action)
    return [action]

def transform_call(substitution, call):  # -> actions
    global Function_definitions, argument
    new_call = {}
    new_call["TYPE"]      = call["TYPE"]
    new_call["TEXT"]      = call["TEXT"]
    new_call["CALLTYPE"]  = call["CALLTYPE"]
    if "ARGTYPES" in call:  new_call["ARGTYPES"]  = call["ARGTYPES"]
    new_call["ARGUMENTS"] = call["ARGUMENTS"]

    if new_call["CALLTYPE"] == "vocola" and new_call["TEXT"] == "Eval":
        transform_eval(new_call)
    new_call["ARGUMENTS"] = transform_arguments(substitution,
                                                new_call["ARGUMENTS"])

    if new_call["CALLTYPE"] == "user":
        arguments  = new_call["ARGUMENTS"]

        definition = Function_definitions[new_call["TEXT"]]
        formals    = definition["FORMALS"]
        body       = definition["ACTIONS"]

        bindings = {}
        i = 0
        for argument in arguments:
            bindings[formals[i]] = argument
            i += 1
        return transform_actions(bindings, body)
    return [new_call]

# Eval() is a special form that takes a single argument, which is
# composed of a series of actions.  A call to EvalTemplate is
# constructed at compile time from the actions where each word action
# supplies a piece of template text and each non-word action denotes a
# hole in the template (represented by "%a") that will be "filled" at
# runtime by the result of evaluating that non-word action.
#
# Example: the template for Eval(1 + $2-$3) is "1+%a-%a", yielding the
# call EvalTemplate("1+%a-%a", $2, $3); assuming $2 has value "3" and
# $3 has value "5", this evaluates to "8".
#
# (Values are treated as integers by %a if and only if they have the
# form of a canonical integer; e.g., 13 but not "013".)

def transform_eval(call):
    arguments = call["ARGUMENTS"]

    template = ""
    new_arguments = []
    for action in arguments[0]:
        if action["TYPE"] == "word":
            text = action["TEXT"]
            text = text.replace("%", "%%")
            template += text
        else:
            template += "%a"
            new_argument = []
            new_argument.append(action)
            new_arguments.append(new_argument)
    template_word = {}
    template_word["TYPE"] = "word"
    template_word["TEXT"] = template

    template_argument = []
    template_argument.append(template_word)
    new_arguments = [template_argument] + new_arguments

    call["TEXT"]      = "EvalTemplate"
    call["ARGUMENTS"] = new_arguments
