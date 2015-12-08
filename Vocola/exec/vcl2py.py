# vcl2py:  Convert Vocola voice command files to NatLink Python "grammar"
#          classes implementing those voice commands
#
# Usage: python vcl2py.py [<option>...] <inputFileOrFolder> <outputFolder>
# Where <option> can be:
#   -debug <n>             -- specify debugging level 
#                               (0 = no info, 1 = show statements, 
#                                2 = detailed info)
#   -extensions <filename> -- specify filename containing extension interface 
#                             information
#   -f                     -- force processing even if file(s) not out of date
#   -INI_file <filename>   -- specify filename of INI file to use
#   -log_file <filename>   -- specify filename to log to
#   -log_stdout            -- log to standard out instead of a file
#   -max_commands <n>      -- specify maximum number of commands per utterance
#   -numbers <s0>,<s1>,<s2>,...
#                          -- use spoken form <s0> instead of "0" in ranges,
#                             <s1> instead of "1" in ranges, etc.
#   -q                     -- ignore any INI file
#   -suffix <s>            -- use suffix <s> to distinguish Vocola generated 
#                             files (default is "_vcl")
#
#
# Copyright (c) 2000-2003, 2005, 2007, 2009-2012 by Rick Mohr.
# 
# Portions Copyright (c) 2012-15 by Hewlett-Packard Development Company, L.P.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# 11/34/2015  ml  Split up into modules
# 12/26/2013  ml  Added new built-ins, If and When
#  4/23/2013  ml  Any series of one or more terms at least one of which
#                 is not optional or <_anything> can now be optional.
#  5/01/2012  ml  Ported to Python line by line, parser replaced with 
#                 lexer/traditional parser
#  5/14/2011  ml  Selected numbers in ranges can now be spelled out
# 11/28/2010  ml  Extensions can now be called
# 05/28/2010  ml  Print_* functions -> unparse_* to avoid compiler bug
# 05/08/2010  ml  Underscores now converted to spaces by VocolaUtils
# 03/31/2010  ml  Runtime errors now caught and passed to handle_error along 
#                 with filename and line number of error location
# 01/27/2010  ml  Actions now implemented via direct translation to
#                 Python, with no delay of Dragon calls, etc.
# 01/01/2010  ml  User functions are now implemented via unrolling
# 12/30/2009  ml  Eval is now implemented via transformation to EvalTemplate
# 12/28/2009  ml  New EvalTemplate built-in function
# 09/06/2009  ml  New $set directive replaces old non-working sequence directive
#                 binary Use Command Sequences replaced by n-ary MaximumCommands
# 01/19/2009  ml  Unimacro built-in added
# 12/06/2007  ml  Arguments to Dragon functions are now checked for proper 
#                 number and datatype
# 06/02/2007  ml  Output filenames are now mangled in an invertable fashion
# 05/17/2007  ml  Eval now works correctly on any action instead of just word
#                 and reference actions.
# 05/15/2007  ml  Variable substitution regularized
#                 Empty context statements now work
# 04/18/2007  ml  (Function) Names may now start with underscores
# 04/08/2007  ml  Quotation marks can be escaped by doubling
# 01/03/2005  rm  Commands can incorporate arbitrary dictation 
#                 Enable/disable command sequences via ini file
# 04/12/2003  rm  Case insensitive window title comparisons
#                 Output e.g. "emacs_vcl.py" (don't clobber existing NatLink 
#                 files)
# 11/24/2002  rm  Option to process a single file, or only changed files
# 10/12/2002  rm  Use <any>+ instead of exporting individual NatLink commands
# 10/05/2002  rm  Generalized indenting, emit()
# 09/29/2002  rm  Built-in function: Repeat() 
# 09/15/2002  rm  User-defined functions
# 08/17/2002  rm  Use recursive grammar for command sequences
# 07/14/2002  rm  Context statements can contain '|'
#                 Support environment variable references in include statements
# 07/06/2002  rm  Function arguments allow multiple actions
#                 Built-in function: Eval()!
# 07/05/2002  rm  New code generation using VocolaUtils.py
# 07/04/2002  rm  Improve generated code: use "elif" in menus
# 06/02/2002  rm  Command sequences!
# 05/19/2002  rm  Support "include" statement
# 05/03/2002  rm  Version 1.1
# 05/03/2002  rm  Handle application names containing '_'
# 05/03/2002  rm  Convert '\' to '\\' early to avoid quotewords bug
# 02/18/2002  rm  Version 0.9
# 12/08/2001  rm  convert e.g. "{Tab_2}" to "{Tab 2}"
#                 expand in-string references (e.g. "{Up $1}")
# 03/31/2001  rm  Detect and report unbalanced quotes
# 03/06/2001  rm  Improve error checking for complex menus
# 02/24/2001  rm  Change name to Vocola
# 02/18/2001  rm  Handle terms containing an apostrophe
# 02/06/2001  rm  Machine-specific command files
# 02/04/2001  rm  Error on undefined variable or reference out of range
# 08/22/2000  rm  First usable version

# Style notes:
#   Global variables are capitalized (e.g. Definitions)
#   Local variables are lowercase    (e.g. in_folder)

from vcl2py.main import main_routine


# ---------------------------------------------------------------------------
# Okay, let's run!

main_routine();
#import profile
#profile.run('main_routine()')
