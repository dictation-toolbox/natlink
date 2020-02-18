###
### scan_extensions.py - Code used to build extensions.csv file from
###                      present vocola_ext_*.py files.
###
###
### Copyright (c) 2011, 2015 by Hewlett-Packard Development Company, L.P.
###
### Permission is hereby granted, free of charge, to any person
### obtaining a copy of this software and associated documentation
### files (the "Software"), to deal in the Software without
### restriction, including without limitation the rights to use, copy,
### modify, merge, publish, distribute, sublicense, and/or sell copies
### of the Software, and to permit persons to whom the Software is
### furnished to do so, subject to the following conditions:
###
### The above copyright notice and this permission notice shall be
### included in all copies or substantial portions of the Software.
###
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
### EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
### MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
### NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
### HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
### WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
### OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
### DEALINGS IN THE SOFTWARE.
###

import os
import sys
import re


def process_extension(output, verbose, extension):
    log("    scanning %s.py..." % extension, verbose)

    functions = procedures = 0

    last_line   = ""
    line_number = 0
    f = open(extension + ".py", "r")
    try:
        for line in f:
            funcs, procs = scan(output, last_line, line, extension,
                                line_number)
            functions   += funcs
            procedures  += procs
            line_number += 1
            last_line = line
    finally:
        f.close()

    log("        found %d function(s), %d procedures(s)" %
        (functions, procedures), verbose)


def scan(output, first_line, second_line, extension, line_number):
    m = re.search(r'^\s*\#\s*Vocola\s+(function|procedure):\s*(.*)',
                  first_line, re.I)
    if m == None:
        return 0,0
    kind      = m.group(1)
    arguments = split_arguments(m.group(2))

    if len(arguments) < 1:
        error("%s.py:%d: Error: Vocola extension %s name not specified" %
              (extension, line_number, kind))
        return 0, 0
    name = arguments[0]
    if name.find(".") == -1:
        error(("%s.py:%d: Error: Vocola extension %s name does not " +
               "contain a '.'") % (extension, line_number, kind))
        return 0, 0


    m = re.search(r'^\s*def\s+([^(]+)\(([^)]*)', second_line)
    if m == None:
        error(("%s.py:%d: Error: Vocola extension specification line " +
               "not followed by a def name(... line") %
              (extension, line_number))
        return 0, 0
    function_name      = m.group(1)
    function_arguments = split_arguments(m.group(2))

    m = None
    if len(arguments) > 1:
        m = re.search(r'^(\d+)\s*(-\s*(\d+)?)?', arguments[1])
    if m:
        min = max = int(m.group(1))
        if m.group(2):
            max = -1
        if m.group(3):
            max = int(m.group(3))
    else:
        min = max = len(function_arguments)


    if kind.lower() == "function":
        is_procedure = 0
    else:
        is_procedure = 1

    definition = "%s,%d,%d,%s,%s,%s.%s\n" % (name, min, max, is_procedure,
                                             extension, extension,
                                             function_name)
    output.write(definition)

    return 1-is_procedure, is_procedure


def split_arguments(arguments):
    arguments = arguments.strip()
    # special case because of Python bug in split() resulting in [""] for "":
    if arguments == "":
        return []
    else:
        return [x.strip() for x in arguments.split(",")]


def log(message, verbose):
    if verbose:
        print(message)
        sys.stdout.flush()

def error(message):
    print(message, file=sys.stderr)
    sys.stderr.flush()



##
## Main routine:
##

def main(argv):
    program  = argv.pop(0)

    verbose = False
    if len(argv)>0 and argv[0]=="-v":
        argv.pop(0)
        verbose = True

    if len(argv) != 1:
        print("%s: usage: %s [-v] <extensions_folder>" % (program, program))
        return
    extensions_folder = argv[0]

    log("\nScanning for Vocola extensions...", verbose)

    os.chdir(extensions_folder)
    output = open(os.path.normpath(os.path.join(extensions_folder,
                                                "extensions.csv")), "w")
    try:
        for file in os.listdir(extensions_folder):
            if file.startswith("vocola_ext_") and file.endswith(".py"):
                process_extension(output, verbose, file[0:-3])
    finally:
        output.close()

if __name__ == "__main__":
    main(sys.argv)
