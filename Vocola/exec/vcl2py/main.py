#
# Main control flow module
#

import os
import re
import sys

from vcl2py.emit      import output
from vcl2py.lex       import initialize_token_properties
from vcl2py.log       import *
from vcl2py.parse     import parse_input, check_forward_references
from vcl2py.transform import transform


VocolaVersion = "2.8.6"


# ---------------------------------------------------------------------------
# Messages to standard error

def fatal_error(message):
    print("vcl2py.py: Error: " + message, file=sys.stderr)
    sys.exit(99)


def usage(message=""):
    global VocolaVersion

    if message != "":
        print("vcl2py.py: Error: " + message, file=sys.stderr)

    print('''
Usage: python vcl2py.pl [<option>...] <inputFileOrFolder> <outputFolder>
  where <option> ::= -debug <n> | -extensions <filename> | -f
                  |-INI_file <filename> | -log_file <filename> | -log_stdout
                  | -max_commands <n> | -q | -suffix <s>

''', file=sys.stderr)
    print("Vocola 2 version: " + VocolaVersion, file=sys.stderr)
    sys.exit(99)



# ---------------------------------------------------------------------------
# Main control flow

def main_routine():
    global Debug, Default_maximum_commands, Error_encountered, Force_processing, In_folder, Default_number_words
    global Extension_functions

    # flush output after every print statement:
    #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)    # <<<>>>

    # Debug states: 0 = no info, 1 = show statements, 2 = detailed info
    Debug                    = 0
    Default_maximum_commands = 1
    Error_encountered        = False
    Force_processing         = False
    Default_number_words     = {}


    extensions_file          = ""
    ignore_INI_file          = False
    ini_file                 = ""
    log_file                 = ""
    log_to_stdout            = False
    suffix                   = "_vcl"

    argv = sys.argv[1:]
    while len(argv) > 0:
        option = argv[0]
        if not option[0:1] == "-": break
        argv.pop(0)

        if   option == "-f":          Force_processing = True; continue
        elif option == "-log_stdout": log_to_stdout    = True; continue
        elif option == "-q":          ignore_INI_file  = True; continue

        if len(argv) == 0:
            usage("missing argument for option " + option)
        argument = argv.pop(0)

        if   option == "-debug":        Debug           = safe_int(argument, 1)
        elif option == "-extensions":   extensions_file = argument
        elif option == "-INI_file":     ini_file        = argument
        elif option == "-log_file":     log_file        = argument
        elif option == "-max_commands":
            Default_maximum_commands = safe_int(argument, 1)
        elif option == "-numbers":
            Default_number_words = {}
            numbers = re.split(r'\s*,\s*', argument.strip())
            i = 0
            for number in numbers:
                if number != "":
                    Default_number_words[i] = number
                i = i + 1
        elif option == "-suffix":       suffix                   = argument
        else:
            usage("unknown option: " + option)

    if len(argv) == 2:
        inputFileOrFolder = argv[0]
        out_folder        = argv[1]
    else:
        usage()


    in_file = ""
    if os.path.isdir(inputFileOrFolder):
        # inputFileOrFolder is an entire folder
        In_folder = inputFileOrFolder
    elif os.path.exists(inputFileOrFolder):
        # inputFileOrFolder is a single file
        In_folder, filename = os.path.split(inputFileOrFolder)
        if In_folder == "": In_folder = "."
        in_file, extension  = os.path.splitext(filename)
        if not extension == ".vcl":
            fatal_error("Input file '" + inputFileOrFolder +
                        "' must end in '.vcl'")
    else:
        fatal_error("Nonexistent input filename '" + inputFileOrFolder + "'")
    if log_file == "": log_file = In_folder + os.sep + "vcl2py_log.txt"
    if ini_file == "": ini_file = In_folder + os.sep + "Vocola.INI"

    if log_to_stdout:
        set_log(sys.stdout)
    else:
        try:
            set_log(open(log_file, "w"))
        except IOError as e:
            fatal_error("Unable to open log file '" + log_file +
                        "' for writing: " + str(e))


    if not ignore_INI_file:   read_ini_file(ini_file)
    if extensions_file != "":
        Extension_functions = read_extensions_file(extensions_file)
    else:
        Extension_functions = {}
    if Debug >= 1:
        print_log("default maximum commands per utterance = " +
                  str(Default_maximum_commands))

    initialize_token_properties()
    convert_files(in_file, out_folder, suffix)

    close_log()
    if not Error_encountered:
        if not log_to_stdout: os.remove(log_file)
        sys.exit(0)
    else:
        sys.exit(1)

def safe_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default

def read_ini_file(ini_file):
    global Debug, Default_maximum_commands

    if Debug >= 1: print_log("INI file is '" + ini_file + "'")
    try:
        input = open(ini_file)
        for line in input:
            match = re.match(r'^(.*?)=(.*)$', line)
            if not match: continue
            keyword = match.group(1)
            value   = match.group(2)
            if keyword == "MaximumCommands":
                Default_maximum_commands = safe_int(value, 1)
    except IOError as e:
        return

def read_extensions_file(extensions_filename):
    global Debug
    extension_functions = {}
    if Debug >= 1: print_log("extensions file is '" + extensions_filename + "'")
    try:
        input = open(extensions_filename)
        for line in input:
            match = re.match(r'([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,\n\r]*)[\n\r]*$', line)
            if not match:
                continue

            extension_name    = match.group(1)
            minimum_arguments = safe_int(match.group(2), 1)
            maximum_arguments = safe_int(match.group(3), 1)
            needs_flushing    = safe_int(match.group(4), 1) != 0
            module_name       = match.group(5)
            function_name     = match.group(6)

            extension_functions[extension_name] = [minimum_arguments, maximum_arguments, needs_flushing, module_name, function_name]
    except IOError as e:
        pass
    return extension_functions


def expand_in_file(in_file, in_folder):
    if in_file != "":
        # just one file
        return [in_file]

    # each .vcl file in folder:
    result = []
    machine = os.environ.get("COMPUTERNAME", "").lower()
    try:
        for filename in os.listdir(in_folder):
            match = re.match(r'^(.+)\.vcl$', filename)
            if match:
                in_file = match.group(1)
                # skip machine-specific files for different machines
                match = re.search(r'@(.+)', in_file)
                if not (match and match.group(1).lower() != machine):
                    result += [in_file]
        return result
    except IOError as e:
        fatal_error("Couldn't open/list folder '" + in_folder + "': " + str(e))


def convert_files(in_file, out_folder, suffix):
    global In_folder

    files = expand_in_file(in_file, In_folder)
    for in_file in files:
        convert_file(in_file, out_folder, suffix)
    return

# Convert one Vocola command file to a .py file

  # in_file is just the base name; actual pathname is
  # <In_folder>/<in_file>.vcl where / is the correct separator
def convert_file(in_file, out_folder, suffix):
    global Debug, Error_encountered
    global Force_processing
    global In_folder
    global Input_name, Module_name
    global Default_number_words, Number_words
    global Default_maximum_commands, Maximum_commands
    global Extension_functions

    out_file = convert_filename(in_file)

    # The global Module_name is used below to implement application-specific
    # commands in the output Python
    Module_name = out_file.lower()
    # The global Input_name is used below for error logging
    Input_name = in_file + ".vcl"

    out_file = out_folder + os.sep + out_file + suffix + ".py"

    in_path = In_folder + os.sep + Input_name
    if os.path.exists(in_path):
        in_time  = os.path.getmtime(in_path)
        out_time = 0
        if os.path.exists(out_file): out_time = os.path.getmtime(out_file)
        if in_time<out_time and not Force_processing:
            return


    if Debug>=1: print_log("\n==============================")

    statements, Definitions, Function_definitions, statement_count, \
        error_count, should_emit_dictation_support, file_empty \
        = parse_input(Input_name, In_folder, Extension_functions, Debug)
    if error_count == 0:
        check_forward_references()

    # Prepend a "global" context statement if necessary
    if len(statements) == 0 or statements[0]["TYPE"] != "context":
        context            = {}
        context["TYPE"]    = "context"
        context["STRINGS"] = [""]
        statements.insert(0, context)
    #print_log(unparse_statements(statements), True)
    statements = transform(statements, Function_definitions, statement_count)
    #print_log(unparse_statements(statements), True)

    # Handle $set directives:
    Maximum_commands = Default_maximum_commands
    Number_words     = Default_number_words
    for statement in statements:
        if statement["TYPE"] == "set":
            key = statement["KEY"]
            if key == "MaximumCommands":
                Maximum_commands = safe_int(statement["TEXT"], 1)
            elif key == "numbers":
                Number_words = {}
                numbers = re.split(r'\s*,\s*', statement["TEXT"].strip())
                i = 0
                for number in numbers:
                    if number != "":
                        Number_words[i] = number
                    i = i + 1

    if error_count > 0:
        if error_count == 1:
            s = ""
        else:
            s = "s"
        print_log("  " + str(error_count) + " error" + s + " -- file not converted.")
        Error_encountered = True
        return
    if file_empty:
        # Write empty output file, for modification time comparisons
        try:
            OUT = open(out_file, "w")
            OUT.close()
        except IOError as e:
            print_log("Couldn't open output file '" + out_file + "' for writing")
        print_log("Converting " + Input_name)
        print_log("  Warning: no commands in file.")
        return

    from vcl2py.emit import output
    #emit_output(out_file, statements)
    output(out_file, statements,
           VocolaVersion,
           should_emit_dictation_support,
           Module_name,
           Number_words, Definitions, Maximum_commands,
           Extension_functions)

#
# Warning: this code is very subtle and has a matching inverse function in
# _vocola_main.py, getSourceFilename.
#
# Ensures:
#   maps [\w@]* to [\w]*, [-\w@]* to [-\w]*
#   is invertable
#   result starts with _ iff input did
#   does not change any text before the first @ or end of string, whichever
#     comes first
#
def convert_filename(in_file):
    name = in_file

    # ensure @ acts as a module name terminator for NatLink
    name = re.sub(r'(.)@', r'\1_@', name)

    marker = "e_s_c_a_p_e_d__"

    match = re.match(r'([^@]*?)((@(.*))?)$', name)
    module = match.group(1)
    suffix = match.group(2)

    if suffix == "" and name.find(marker) == -1: return name

    suffix = suffix.replace('_', '___')
    suffix = suffix.replace('@', '__a_t__')
    return module + marker + suffix
