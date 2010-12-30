# vcl2py:  Convert Vocola voice command files to NatLink Python "grammar"
#          classes implementing the voice commands
#
# Usage:  perl vcl2py.pl [-extensions <f>] [-suffix <s>] 
#                        [-f] inputFileOrFolder outputFolder
# Where:
#   -extensions <f> -- specify filename containing extension interface information
#   -suffix <s>     -- use suffix <s> to distinguish Vocola generated files
#                      (default is "_vcl")
#   -f              -- force processing even if file(s) not out of date
#
#
# Copyright (c) 2002-2010 by Rick Mohr.
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
#   Global variables are capitalized (e.g. $Definitions)
#   Local variables are lowercase (e.g. $in_folder)

use Text::ParseWords;    # for quotewords
use File::Basename;      # for fileparse
use File::stat;          # for mtime

# ---------------------------------------------------------------------------
# Main control flow

sub main
{
    $VocolaVersion = "2.7.1";
    $Debug = 0;  # 0 = no info, 1 = show statements, 2 = detailed info
    $Error_encountered = 0;
    $| = 1;      # flush output after every print statement

    $extensions_info = 0;
    if ($ARGV[0] eq "-extensions") {
        shift @ARGV;
        $extensions_info = $ARGV[0];
        shift @ARGV;
    }

    $suffix = "_vcl";
    if ($ARGV[0] eq "-suffix") {
        shift @ARGV;
        $suffix = $ARGV[0];
        shift @ARGV;
    }

    $Process_all_files = 0;
    if ($ARGV[0] eq "-f") {
        $Force_processing = 1;
        shift @ARGV;
    }

    my ($input, $out_folder);
    if (@ARGV == 2) {
        $input = $ARGV[0];
        $out_folder = $ARGV[1];
    } else {
        die "Usage: perl vcl2py.pl [-extensions <f>] [-suffix <s>] [-f] inputFileOrFolder outputFolder\n";
    }

    my $in_file = "";
    if (-d $input) {
        # Input is an entire folder
        $In_folder = $ARGV[0];
    } elsif (-e $input) {
        # Input is a single file
        ($in_file, $In_folder, $extension) = fileparse($input, ".vcl");
        $extension eq ".vcl"
            or die "Input filename '$input' must end in '.vcl'\n";
    } else {
        die "Unknown input filename '$input'\n";
    }

    my $log_file = "$In_folder\\vcl2py_log.txt";
    open LOG, ">$log_file" or die "$@ $log_file\n";

    $default_maximum_commands = 1;
    read_ini_file($In_folder);
    read_extensions_file($extensions_info) if ($extensions_info);
    print LOG ("default maximum commands per utterance = $default_maximum_commands\n") if ($Debug >= 1);

    convert_files($in_file, $out_folder, $suffix);
    close LOG;

    if ($Error_encountered == 0) {
        system("del \"$log_file\"");
    }
    exit($Error_encountered);
}

sub read_ini_file
{
    my ($in_folder) = @_;
    my $ini_file = "$in_folder\\Vocola.INI";
    print LOG "INI file is '$ini_file'\n" if ($Debug >= 1);
    open INI, "<$ini_file" or return;
    while (<INI>) {
        next unless /^(.*?)=(.*)$/;
        my $keyword = $1;
        my $value = $2;
        if ($keyword eq "MaximumCommands") {
            $default_maximum_commands = $value;
        }
    }  
}

sub read_extensions_file
{
    my ($extensions_file) = @_;
    print LOG "extensions file is '$extensions_file'\n" if ($Debug >= 1);
    open EXTENSIONS, "<$extensions_file" or return;
    while (<EXTENSIONS>) {
        next unless /^([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,\n\r]*)[\n\r]*$/;
        my $extension_name    = $1;
        my $minimum_arguments = $2;
        my $maximum_arguments = $3;
        my $needs_flushing    = $4;
        my $module_name       = $5;
        my $function_name     = $6;

	$Extension_functions{$extension_name} = [$minimum_arguments, $maximum_arguments, $needs_flushing, $module_name, $function_name];
    }  
}

sub convert_files
{
    my ($in_file, $out_folder, $suffix) = @_;
    if ($in_file ne "") {
        # Convert one file
        print "Converting $in_file...\n";
        convert_file($in_file, $out_folder, $suffix);
    } else {
        # Convert each .vcl file in folder 
        opendir FOLDER, "$In_folder"
            or die "Couldn't open folder '$In_folder'\n";
        my $machine = lc($ENV{COMPUTERNAME});
        foreach (readdir FOLDER) {
            if (/^(.+)\.vcl$/) {
                my $in_file = lc($1);
                # skip machine-specific files for different machines
                next if ($in_file =~ /\@(.+)/ and $1 ne $machine);
                convert_file($in_file, $out_folder, $suffix);
            }
        }
    }
}

# Convert one Vocola command file to a .py file

sub convert_file
{
    my ($in_file, $out_folder, $suffix) = @_;
    my $out_file = convert_filename($in_file);

    # The global $Module_name is used below to implement application-specific 
    # commands in the output Python
    $Module_name = lc($out_file);
    # The global $Input_name is used below for error logging
    $Input_name = "$in_file.vcl";
    $Should_emit_dictation_support = 0;
    $out_file = "$out_folder/$out_file" . $suffix . ".py";

    $in_stats  = stat("$In_folder/$Input_name");
    $out_stats = stat("$out_file");
    $in_date  = $in_stats->mtime;
    $out_date = $out_stats ? $out_stats->mtime : 0;
    return unless $in_date > $out_date || $Force_processing;

    %Definitions = ();
    %Functions = ();
    %Function_definitions = ();
    @Forward_references = ();
    @Included_files = ();
    @Include_stack = ();
    $Error_count = 0;
    $File_empty = 1;
    $Statement_count = 1;

    if ($Debug>=1) {print LOG "\n==============================\n";}

    my @statements = parse_file($Input_name);
    &check_forward_references;

    # Prepend a "global" context statement if necessary
    if ($statements[0]->{TYPE} ne "context") {
        my $context = parse_context(": ");
        unshift(@statements, $context);
    }

    #print LOG unparse_statements (@statements);
    transform_nodes(@statements);
    #print LOG unparse_statements (@statements);

    # Handle $set directives:
    $maximum_commands = $default_maximum_commands;
    for my $statement (@statements) {
	if ($statement->{TYPE} eq "set") {
	    my $key = $statement->{KEY};
	    if ($key eq "MaximumCommands") {
		$maximum_commands = $statement->{TEXT};
	    }
	}
    }

    if ($Error_count) {
        my $s = ($Error_count == 1) ? "" : "s";
        print LOG "  $Error_count error$s -- file not converted.\n";
        $Error_encountered = 1;
        return;
    }
    if ($File_empty) {
        # Write empty output file, for modification time comparisons 
        open OUT, ">$out_file" or die "$@ $out_file\n";
        close OUT;
        print LOG "Converting $Input_name\n";
        print LOG "  Warning: no commands in file.\n";
        return;
    }
    emit_output($out_file, @statements);
}

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
sub convert_filename
{
    my ($in_file) = @_;
    my $name = $in_file;

    # ensure @ acts as a module name terminator for NatLink
    $name =~ s/(.)@/\1_@/g;

    my $marker = "e_s_c_a_p_e_d__";

    $name =~ /^([^@]*?)(@(.*))?$/;
    my ($module, $suffix) = ($1, $2);
    
    return $name if $suffix eq "" && $name !~ /$marker/;

    $suffix =~ s/_/___/g;
    $suffix =~ s/@/__a_t__/g;
    return $module . $marker . $suffix;
}


# ---------------------------------------------------------------------------
# Parsing routines
#
# The following grammar defines the Vocola language:
# (note that a "menu" is called an "alternative set" in the documentation)
#
#     statements = (context | definition | function | directive | top_command)*
#
#        context = chars* ('|' chars*)* ':'
#     definition = variable ':=' menu_body ';'
#       function = prototype ':=' action* ';'
#      directive = ('include' word | '$set' word word) ';'
#    top_command = terms '=' action* ';'
#
#        command = terms ['=' action*]
#          terms = (term | '[' simple_term ']')+
#           term = simple_term | range | menu
#    simple_term = word | variable
#         action = word | call | reference
#
#           menu = '(' menuBody ')'
#       menuBody = command ('|' command)*
#
#      prototype = functionName '(' formals ')'
#        formals = [name (',' name)*]
#           call = callName '(' arguments ')'
#      arguments = [action* (',' action*)*]
#
#
#  [lexing]
#
#           word = bare_word | quoted_word
#    quoted_word = '"' ([^"]|'""')* '"' | "'" ([^']|"''")* "'"
#      bare_word = [^\s()\[\]=|,\"\';\#]*([^\s()\[\]=|,\"\';\#:]|:(?![\s=]))
#
#       variable = '<' variableName '>'
#          range = number '..' number
#      reference = '$' (number | name)
#           name = [a-zA-Z_]\w*
#   variableName = \w+
#   functionName = [a-zA-Z_]\w*
#       callName = [a-zA-Z_][\w.]*
#
#
# The parser works as follows:
#     1) Strip comments
#     2) Find statement segments by slicing at major delimiters (: ; :=)
#     3) Parse each segment using recursive descent
#
# The parse tree is built from three kinds of nodes (statement, term, 
# and action), using the following fields:
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
#       TEXT    - filename being included
#    set:
#       KEY     - key being set
#       TEXT    - value to set the key to
# 
# term:
#    TYPE   - word/variable/range/menu/dictation
#    NUMBER - sequence number of this term
#    word:
#       TEXT     - text defining the word(s)
#       OPTIONAL - is this word optional
#    variable:
#       TEXT     - name of variable being referenced
#       OPTIONAL - is this variable optional
#    range:
#       FROM     - start number of range
#       TO       - end number of range
#    menu:
#       COMMANDS - list of "command" structures defining the menu
#       
# action:
#    TYPE - word/reference/formalref/call
#    word:
#       TEXT      - keystrokes to send
#    reference:
#       TEXT      - reference number (a string) of reference referenced
#    formalref:
#       TEXT      - name of formal (i.e. user function argument) referenced
#    call:
#       TEXT      - name of function called
#       CALLTYPE  - dragon/vocola/user/extension
#       ARGTYPES  - [dragon only] types of call arguments
#       ARGUMENTS - list of lists of actions, to be passed in call

# ---------------------------------------------------------------------------
# Built in Vocola functions with (minimum number of arguments, maximum
# number of arguments):

%Vocola_functions = (
                     Eval              => [1,1],
                     EvalTemplate      => [1,-1],
                     Repeat            => [2,2],
                     Unimacro          => [1,1],
                     );

# Vocola extensions with (extension_name, minimum_arguments, maximum_arguments,
# needs_flushing, module_name, function_name); initialized by 
# read_extensions_file():

%Extension_functions = ();

# Built in Dragon functions with (minimum number of arguments,
# template of types of all possible arguments); template has one
# letter per argument with s denoting string and i denoting integer:

%Dragon_functions = (
                     ActiveControlPick => [1,"s"],
                     ActiveMenuPick    => [1,"s"],
                     AppBringUp        => [1,"ssis"],
                     AppSwapWith       => [1,"s"],
                     Beep              => [0,""],
                     ButtonClick       => [0,"ii"],
                     ClearDesktop      => [0,""],
                     ControlPick       => [1,"s"],
                     DdeExecute        => [3,"sssi"],
                     DdePoke           => [4,"ssss"],
                     DllCall           => [3,"sss"],
                     DragToPoint       => [0,"i"],
                     GoToSleep         => [0,""],
                     HeardWord         => [1,"ssssssss"],  # max 8 words
                     HTMLHelp          => [2,"sss"],
                     MenuCancel        => [0,""],
                     MenuPick          => [1,"s"],
                     MouseGrid         => [0,"ii"],
                     MsgBoxConfirm     => [3,"sis"],
                     PlaySound         => [1,"s"],
                     RememberPoint     => [0,""],
                     RunScriptFile     => [1,"s"],
                     SendKeys          => [1,"s"],
                     SendDragonKeys    => [1,"s"],
                     SendSystemKeys    => [1,"si"],
                     SetMicrophone     => [0,"i"],
                     SetMousePosition  => [2,"iii"],
                     SetNaturalText    => [1,"i"],
                     ShellExecute      => [1,"siss"],
                     ShiftKey          => [0,"ii"],
                     TTSPlayString     => [0,"ss"],
                     Wait              => [1,"i"],
                     WaitForWindow     => [1,"ssi"],
                     WakeUp            => [0,""],
                     WinHelp           => [2,"sii"],
                     );

# parse_file returns a parse tree (list of statements), which includes in-line
# any statements from include files. Since parse_file is called recursively
# for include files, all code applying to the parse tree as a whole is
# executed in this routine.

sub parse_file    # returns a list of statements
{
    my $in_file = shift;
    push(@Included_files, $in_file);
    push(@Include_stack, $in_file);
    $in_file = "$In_folder\\$in_file";
    $Line_number = -1;
    my $text = read_file($in_file);   # strip comments, deal unbalanced quotes

    # For python output we'll need to convert '\' to '\\'.  Do it up front so
    # quotewords won't miss '\;', e.g. in 'Kill White Space = {Esc}\;'
    $text =~ s.\\.\\\\.g;

    # Find statement segments by slicing at major delimiters (: ; :=)
    my @segments = slice_into_segments($text);

    $Line_number = 1;
    my @statements = parse_statements(@segments);
    pop(@Include_stack);
    return @statements;
}

sub slice_into_segments
{
    my @segments;

    # 
    # The following code replaces:
    # 
    #    @segments = quotewords(":=|:\\s|;", "delimiters", (shift));
    #
    # which was triggering a Perl compiler bug.  It assumes there are no 
    # unbalanced quotations.
    #
    $_ = shift;
    while (/\G( :=|:\s|;
	      | ( [^:;\"\']+ | :(?![=\s]) | \"[^\"]*\" | \'[^\']*\' )+
	      )/xsgc) {
	push (@segments, $1);
    }
    return @segments;
}

# return string, stripped of comments and with unterminated quotations reported 
# then (possibly incorrectly) repaired
sub read_file     
{
    my $in_file = shift;
    my @strings;
    open IN, "<$in_file" or log_error("Unable to open '$in_file'");
    $Line_number = 1;
    while (<IN>) {
	/^(([^\'\"\#\n]+|\"[^\"]*\"|\'[^\']*\')*)(.?)(.*)$/ 
	    or die "Impossible!";
	my ($correct, $separator, $rest) = ($1, $3, $4);
	# separator is one of '', "\#", "'", or '"'
	push (@strings, $correct);
	if ($separator =~ /[\'\"]/) {
	    /^(([^\'\"\#\n]+
	       |\"([^\"]|\"\")*\"(?!\")
	       |\'([^\']|\'\')*\'(?!\')
	       )*) (.?) (.*)$/x
		or die "Impossible!";
	    log_error("Unterminated quotation: $5$6");
	    my $repair = $separator . $rest . $separator;
	    # attempt to minimize cascading errors:
	    $repair =~ s/\s*([;:|])\s*([\'\"])$/\2 \1/;
	    push (@strings, $repair);
	}
	push (@strings, "\n");
	$Line_number++;
    }
    close IN;
    join ('', @strings);
}

# This is the main parsing loop.
# Statement segments are in the global argument array @_
# Segments will be removed as they are parsed by parse_ routines

sub parse_statements    # statements = (context | top_command | definition)*
{
    my (@statements, $statement);

    while (@_ > 1)  # while segment array is not empty...
    {
        @Variable_terms = ();  # used in error-checking
        @Formals = ();
        eval { $statement = (&parse_context or
                             &parse_definition or
                             &parse_top_command or
                             &parse_directive)
               };
        if    ($@)             {log_error($@)}  # Catch calls to "die"
        elsif (not $statement) {log_error("Illegal statement: '@_[0]'"); shift}
        else {
            # Got a valid statement
            if ($statement->{TYPE} eq "definition") {
                my $name = $statement->{NAME};
                if ($Definitions{$name}) {log_error("Redefinition of <$name>")}
                $Definitions{$name} = $statement;
            } elsif ($statement->{TYPE} eq "command") {
                $statement->{NAME} = $Statement_count++;
            }

	    if ($statement->{TYPE} ne "include") {
                push (@statements, $statement);
            } else {
                # Handle include file
                my $include_file = expand_variables($statement->{TEXT});
                unless (already_included($include_file)) {
                    # Save context, get statements from include file, restore 
                    push (@Include_stack, $Line_number, \@_);
                    push (@statements, parse_file($include_file));
                    @_ = @{ pop(@Include_stack) };
                    $Line_number = pop(@Include_stack);
                }
            }
        }
    }
    if (@_[0] =~ /\S/) {
        &shift_delimiter;
        log_error("Missing final delimiter");
    }
    
    return @statements;
}

sub parse_context    # context = chars* ('|' chars*)* ':'
{
    if ($_[0] =~ /^:\s$/ or $_[1] =~ /^:\s$/) {
        my $statement = {};
        $statement->{TYPE} = "context";
        my @strings;
        if ($_[1] =~ /:\s/) {
            &shift_clause;
            if (/=/) {die "Context statement contains '=' (missing ';'?)\n"}
            while (1) {
                /\G\s*([^|]*)/gc;
                $string = $1;
                $string =~ s/\s+$//; # remove trailing whitespace
                push (@strings, lc($string));
                last unless /\G\|/gc;
            }
        } else {
            &shift_delimiter;
            push (@strings, "");
        }
        $statement->{STRINGS} = \@strings;
        if ($Debug>=1) {print LOG unparse_directive ($statement)}
        return $statement;
    }
}

sub parse_definition
{
    if ($_[1] eq ":=" and $_[3] eq ";") {
        &shift_clause;
        my $statement = (&parse_variable_definition or
                         &parse_function_definition or
                         die "Illegal definition: '$_'\n");
        return $statement;
    }
}

sub parse_variable_definition    # definition = variable ':=' menu_body ';'
{
    if (/^\s*<(.*)>\s*$/) {
	my $name = $1;
        &shift_clause;
	&check_variable_name($name);
	$name ne "_anything"
	    or die "Built-in list <_anything> is not redefinable\n";
        my $statement = {};
        $statement->{TYPE} = "definition";
        $statement->{NAME} = $name;
        my $menu = &parse_menu_body;
        &ensure_empty;
        if ($menu->{TYPE} eq "menu") {verify_referenced_menu($menu)};
        $statement->{MENU} = $menu;
        if ($Debug>=1) {print LOG unparse_definition ($statement)}
        return $statement;
    }
}

sub check_variable_name
{
    my $name = shift;
    $name =~ /^\w+$/
	or die "Illegal variable name: <$name>\n";
}

sub parse_function_definition   # function = prototype ':=' action* ';'
                                # prototype = functionName '(' formals ')'
{
    if (/\G\s*([a-zA-Z_.][\w.]*?)\s*\(\s*(.*?)\s*\)/gc) {
        my $functionName = $1;
        my $formalsString = $2;
        if ($Debug>=2) {print LOG "Found user function:  $functionName()\n"}
        my $statement = {};
        $statement->{TYPE} = "function";
        $statement->{NAME} = $functionName;
        my @formals = parse_formals($formalsString);
        $statement->{FORMALS} = \@formals;
        @Formals = @formals; # Used below in &parse_formal_reference
        &shift_clause;
        $statement->{ACTIONS} = &parse_actions;
	if ($functionName =~ /\./)
	    {die "illegal user function name: $functionName\n"}
        defined ($Functions{$functionName})
            and die "Redefinition of $functionName()\n";
        $Functions{$functionName} = @formals;  # remember number of formals
        $Function_definitions{$functionName} = $statement;
        if ($Debug>=1) {print LOG unparse_function_definition ($statement)}
        return $statement;
    }
}

sub parse_formals    # formals = [name (',' name)*]
{
    my $formalsString = shift;
    my @formals = split /\s*,\s*/, $formalsString;
    my @safe_formals = ();
    for my $formal (@formals) {
        $formal =~ /^[a-zA-Z_]\w*$/
            or die "Illegal formal name: '$formal'\n";
        if ($Debug>=2) {print LOG "Found formal:  $formal\n"}
        push (@safe_formals, "_$formal");
    }
    return @safe_formals;
}

sub parse_top_command    # top_command = terms '=' action* ';'
{
    if ($_[1] eq ";" and $_[0] =~ /=/) {
        &shift_clause;
        my $statement = &parse_command;
        &ensure_empty;
        $File_empty = 0;
        if ($Debug>=1) {print LOG unparse_command ($statement, 1) . "\n"}
        return $statement;
    }
}

sub parse_directive    # directive = ('include' word | '$set' word word) ';'
{
    if ($_[1] eq ";") {
        &shift_clause;
        my $statement = {};
        if (/^\s*include\s+/gc) {
	    $statement->{TYPE} = "include";
            my $word = &parse_word or die "Can't tell what to include\n";
            $statement->{TEXT} = $word->{TEXT};
            &ensure_empty;
	} elsif (/^\s*\$set\s+/gc) {
	    $statement->{TYPE} = "set";
            my $word = &parse_word or die "What to set is missing\n";
            $statement->{KEY} = $word->{TEXT};
            $word = &parse_word or die "What to set as value is missing\n";
            $statement->{TEXT} = $word->{TEXT};
            &ensure_empty;
        } else {die "Unrecognized statement\n"}
        if ($Debug>=1) {print LOG unparse_directive ($statement)}
        return $statement;
    }
}

sub parse_command    # command = terms ['=' action*]
{
    my $terms = &parse_terms;
    return 0 unless $terms;

    my $command = {};
    $command->{TYPE} = "command";
    $command->{LINE} = $Line_number;
    my $last = $#Include_stack;
    my $file = $Include_stack[$last];
    $command->{FILE} = $file;
    $command->{TERMS} = $terms;

    # Count variable terms for range checking in &parse_reference
    @Variable_terms = get_variable_terms($command);

    if (/\G\s*=/gc) {
        $command->{ACTIONS} = &parse_actions;
    }
    return $command;
}

sub parse_terms    # terms = (term | '[' simple_term ']')+
{
    my (@terms, $term);
    my $error = 1;
    while (1) {
        my $optional = /\G\s*\[/gc;
        if ($optional) {
            $term = &parse_simple_term;
            if    (not $term)       {die "Expected term after '['\n"}
            elsif (not /\G\s*\]/gc) {die "Missing ']'\n"}
        } else {
            $term = &parse_term;
        }
        if ($term) {
            $term->{OPTIONAL} = $optional;
            $error = 0 if (not $optional and $term->{TYPE} ne "dictation");
            push (@terms, $term);
        } elsif (not @terms) {
            return 0;
        } elsif ($error) {
            die "At least one term must not be optional or <_anything>\n";
        } else {
            return combine_terms(@terms);
        }
    }
}

sub combine_terms    # Combine adjacent "word" terms; number resulting terms
{
    my @terms;
    my $term_count = 0;
    while (@_) {
        my $term = shift;
        if (&is_required_word($term)) {
            while (@_ and &is_required_word) {
                $term->{TEXT} .= " " . shift->{TEXT};
            }
        }
        $term->{NUMBER} = $term_count++;
        push (@terms, $term);
    }
    return \@terms;
}

sub is_required_word {@_[0]->{TYPE} eq "word" and not @_[0]->{OPTIONAL}}

sub parse_term    #  term = simple_term | range | menu
                  # range = number '..' number
                  #  menu = '(' menuBody ')'
{
    my $term;
    if (/\G\s*\(/gc) {
        $term = &parse_menu_body;
        if (not /\G\s*\)/gc) {die "End of alternative set before ')'\n"}
        if ($Debug>=2) {print LOG "Found menu:  "; 
                        print LOG unparse_menu ($term, 1) . "\n"}
    } elsif (/\G\s*(\d*)\.\.(\d*)/gc) {
        $term = {};
        $term->{TYPE} = "range";
        $term->{FROM} = $1;
        $term->{TO}   = $2;
        if ($Debug>=2) {print LOG "Found range:  $1..$2\n"}
    } else {
        $term = &parse_simple_term;
    }
    return $term;
}

sub parse_simple_term    # simple_term = word | variable
                         #    variable = '<' name '>'
{
    if (/\G\s*<(.*?)>/gc) {
	my $name = $1;
	&check_variable_name($name);
        if ($name eq "_anything") {
            if ($Debug>=2) {print LOG "Found <_anything>\n"}
            return create_dictation_node();
        } else {
            if ($Debug>=2) {print LOG "Found variable:  <$name>\n"}
            add_forward_reference($name) unless $Definitions{$name};
            return create_variable_node($name);
        }
    } else {
        return &parse_word;
    }
}

sub create_dictation_node
{
    $Should_emit_dictation_support = 1;
    my $term = {};
    $term->{TYPE} = "dictation";
    return $term
}

sub create_variable_node
{
    my $term = {};
    $term->{TYPE} = "variable";
    $term->{TEXT} = shift;
    return $term
}

sub parse_menu_body    # menuBody = command ('|' command)*
{
    my $menu = {};
    my @commands;
    while (1) {
        my $command = &parse_command;
        if (not $command) {die "Empty alternative set\n"}
        push (@commands, $command);
        last unless /\G\s*\|/gc;
    }
    $menu->{TYPE} = "menu";
    $menu->{COMMANDS} = \@commands;
    return $menu;
}

sub parse_actions    # action = word | call | reference
{
    my @actions;
    while (my $action = (&parse_reference or &parse_call or &parse_word)) {
        if ($action->{TYPE} ne "word" || $action->{TEXT} eq "") {
            push (@actions, $action);
        } else {
            # expand in-string references (e.g. "{Up $1}") and unquote 
            # $'s (e.g., \$ -> $)
            while ($action->{TEXT} =~ /\G(.*?)(?<!\\)\$(\d+|[a-zA-Z_]\w*)/gc) {
                my ($word, $ref) = ($1, $2);
		push (@actions, create_word_node($word, 1)) if $word;
		if ($ref =~ /^\d+/) {
		    push (@actions, create_reference_node($ref));
		} else {
		    push (@actions, create_formal_reference_node($ref));
		}
            }
            if ($action->{TEXT} =~ /\G(.+)/gc) {
                push (@actions, create_word_node($1, 1));
            }
        }
    }
    return \@actions;
}

sub parse_reference    # reference = '$' (number | name)
{
    if      (/\G\s*\$(\d+)/gc) {
        return create_reference_node($1);
    } elsif (/\G\s*\$([a-zA-Z_]\w*)/gc) {
        return create_formal_reference_node($1);
    }
}

sub create_reference_node
{
    my $n = shift;
    if ($n > @Variable_terms) {die "Reference '\$$n' out of range\n"}
    my $term = $Variable_terms[$n - 1];
    if ($term->{TYPE} eq "menu") {verify_referenced_menu($term)};
    if ($Debug>=2) {print LOG "Found reference:  \$$n\n"}
    my $action = {};
    $action->{TYPE} = "reference";
    $action->{TEXT} = $n;
    return $action;
}

sub create_formal_reference_node
{
    my $name = shift;
    my $formal = "_" . $name;
    grep {$_ eq $formal} @Formals
        or die "Reference to unknown formal '\$$name'\n";
    if ($Debug>=2) {print LOG "Found formal reference:  \$$name\n"}
    my $action = {};
    $action->{TYPE} = "formalref";
    $action->{TEXT} = "$formal";
    return $action;
}

sub parse_call    # call = callName '(' arguments ')'
{
    if (/\G\s*([\w.]+?)\s*\(/gc) {
        my $callName = $1;
        if ($Debug>=2) {print LOG "Found call:  $callName()\n"}
        my $action = {};
        $action->{TYPE} = "call";
        $action->{TEXT} = $callName;
        $action->{ARGUMENTS} = &parse_arguments;
        if (not /\G\s*\)/gc) {die "Missing ')'\n"}
        my $nActuals = @{ $action->{ARGUMENTS} };
	my $lFormals, $uFormals, @callFormals;
	if ($callName =~ /\./) {
	    if (defined($Extension_functions{$callName})) {
		@callFormals = $Extension_functions{$callName};
		$lFormals = $callFormals[0][0];
		$uFormals = $callFormals[0][1];
		$action->{CALLTYPE} = "extension";
	    } else {
		die "Call to unknown extension '$callName'\n";
	    }
	} elsif (defined($Dragon_functions{$callName})) {
	    @callFormals = $Dragon_functions{$callName};
	    $lFormals =        $callFormals[0][0];
	    $uFormals = length($callFormals[0][1]);
            $action->{CALLTYPE} = "dragon";
            $action->{ARGTYPES} = $callFormals[0][1];
        } elsif (defined($Vocola_functions{$callName})) {
	    @callFormals = $Vocola_functions{$callName};
	    $lFormals = $callFormals[0][0];
	    $uFormals = $callFormals[0][1];
            $action->{CALLTYPE} = "vocola";
        } elsif (defined($Functions{$callName})) {
	    $lFormals = $uFormals = $Functions{$callName};
            $action->{CALLTYPE} = "user";
        } else {
            die "Call to unknown function '$callName'\n";
        }

        if ($lFormals != -1 and $nActuals < $lFormals) {
            die "Too few arguments passed to '$callName' (minimum of $lFormals required)\n";
        } 
        if ($uFormals != -1 and $nActuals > $uFormals) {
            die "Too many arguments passed to '$callName' (maximum of $uFormals allowed)\n";
        } 
        return $action;
    }
}

sub parse_arguments    # arguments = [action* (',' action*)*]
{
    my @arguments;
    my $argument = &parse_actions;
    return unless @{$argument};
    while (1) {
        push (@arguments, $argument);
        last unless /\G\s*,/gc;
        $argument = &parse_actions;
        if (not @{$argument}) {die "Missing or invalid argument\n"}
    }
    return \@arguments;
}

# word      = bare_word | '"' ([^"]|'""')* '"' | "'" ([^']|"''")* "'"
# bare_word = [^\s()\[\]=|,\"\';\#]*([^\s()\[\]=|,\"\';\#:]|:(?![\s=]))
sub parse_word    
{
    if (   /\G\s*(\")(([^\"]|\"\")*)\"\s*/gc      # double quoted word
        or /\G\s*(\')(([^\']|\'\')*)\'\s*/gc      # single quoted word
        or /\G\s*()([^\s()\[\]=|,\"\';\#]+)/gc)   # bare word
    {
	my ($quote, $word) = ($1, $2);
	$word =~ s/$quote$quote/$quote/g if $quote;
        if ($Debug>=2) {print LOG "Found word:  '$word'\n"}
        return create_word_node($word, 0);
    }
}

sub create_word_node
{
    my $text = shift;
    my $substitute = shift;
    $text =~ s/\\\\\$/\$/g if $substitute;  # convert \\$ to $ (\'s doubled)
    my $term = {};
    $term->{TYPE} = "word";
    $term->{TEXT} = $text;
    return $term;
}

sub ensure_empty
{
    if (/\G\s*(\S+)/gc) {
        die "Unexpected text: '$1'\n";
    }
}

# The argument list contains a string we want to parse, followed by a 
# delimiter.  Splice them both out of the list, making the string the
# current argument ($_).  Also count newlines for error reporting.

sub shift_clause
{
    $_ = $_[0] . $_[1];
    $Line_number++ while (/\G.*?\n/gc);
    $_ = shift;
    shift;
}

sub shift_delimiter 
{
    $_ = shift;
    $Line_number++ while (/\G.*?\n/gc);
}

sub log_error
{
    # a variant of this code may be found in check_forward_references
    print LOG "Converting $Input_name\n" unless $Error_count;
    print LOG &format_error_message;
    $Error_count++;
}

# Here is what the include stack looks like (growing downwards): 
#   name of top-level file 
#   line number of first include
#   segments pending after first include
#   name of first include file
#   line number of second include
#   segments pending after second include
#   name of second include file

sub format_error_message
{
    my $message = shift;
    chomp($message);
    my $last = $#Include_stack;
    my $line = $Line_number;
    if ($Line_number == -1) {
        # "Unable to open file" -- ignore top frame of include stack
        $line = $Include_stack[$last - 2];
        $last -= 3;
    }
    my $file_msg = ($last <= 0) ? "" : " of $Include_stack[$last]";
    $message = "  Error at line $line$file_msg:  $message\n";
    my $indent = "";
    for (my $i = $last; $i >= 3; $i -= 3) {
        my $line = $Include_stack[$i - 2];
        my $file = $Include_stack[$i - 3];
        $indent .= "  ";
        $message .= "$indent  (Included at line $line of $file)\n";
    }
    return $message;   
}

sub already_included
{
    # Return TRUE if $filename was already included in the current file
    my $filename = shift;
    for my $included (@Included_files) {
        return 1 if ($included eq $filename);
    }
    return 0;
}

sub expand_variables
{
    my $text = shift;
    $text =~ s/\\\\/\\/g;    # undo doubling of backslashes
    my $result = "";
    while ($text =~ /\G(.*?)(?<!\\)\$(\d+|[a-zA-Z_]\w*)/gc) {
	my ($word, $variable) = ($1, $2);
	$word =~ s/\\\$/\$/g;
        my $value = $ENV{$variable};
        log_error("Reference to unknown environment variable $variable") unless $value;
	$result .= $word . $value;
    }
    $text =~ /\G(.*)/gc;
    $word = $1;
    $word =~ s/\\\$/\$/g;
    return $result . $word;
    # Should be a warning not an error.
}

# ---------------------------------------------------------------------------
# Parse-time error checking of references

sub verify_referenced_menu
{
    my ($menu, $parent_has_actions) = @_;
    my @commands = @{ $menu->{COMMANDS} };
    for my $command (@commands) {
        my $has_actions = $parent_has_actions;
        my @actions = @{ $command->{ACTIONS} };
        if (@actions) {
            if ($parent_has_actions) {die "Actions may not be nested\n"}
            $has_actions = 1;
            # make sure no actions are references
            for my $action (@actions) {
                if ($action->{TYPE} eq "reference") {
                    die "Substitution may not contain a reference\n";
                }
            }
        }
        my @terms = @{ $command->{TERMS} };
        if (@terms > 1) {die "Alternative is too complex\n"}
        my $type = $terms[0]->{TYPE};
        if    ($type eq "menu"){verify_referenced_menu($terms[0],$has_actions)}
        elsif ($type eq "variable" or $type eq "definition") {
            die "Alternative cannot be a variable\n";
        }
        elsif ($type eq "range") {
            # allow a single range with no actions
            return if (not $has_actions and @commands == 1);
            die "Alternative cannot be a range\n";
        }
    }
}

sub add_forward_reference
{
    my $variable = shift;
    my $forward_reference = {};
    $forward_reference->{VARIABLE} = $variable;
    $forward_reference->{MESSAGE} =
       format_error_message("Reference to undefined variable '<$variable>'\n");
    push (@Forward_references, $forward_reference);
}

sub check_forward_references
{
    for my $forward_reference (@Forward_references) {
        my $variable = $forward_reference->{VARIABLE};
        if (not $Definitions{$variable}) {
	    print LOG "Converting $Input_name\n" unless $Error_count;
            print LOG $forward_reference->{MESSAGE};
            $Error_count++;
        }
    }
}

# ---------------------------------------------------------------------------
# Unparsing of data structures (for debugging and generating error messages)

sub unparse_statements
{
    my $result = "";
    for my $statement (@_) {
        my $type = $statement->{TYPE};
        if ($type eq "context" || $type eq "include" || $type eq "set") {
            $result .= unparse_directive ($statement);
        } elsif ($type eq "definition") {
            $result .= unparse_definition ($statement);
        } elsif ($type eq "function") {
            $result .= unparse_function_definition ($statement);
        } elsif ($type eq "command") {
            $result .=  "C$statement->{NAME}:  ";
            $result .= unparse_command ($statement, 1) . ";\n";
        }
    }
    return $result . "\n";
}

sub unparse_directive
{
    my $statement = shift;
    my $type = $statement->{TYPE};
    if ($type eq "set") {
	return "\$set '$statement->{KEY}' to '$statement->{TEXT}'\n";
    } else {
	return "$statement->{TYPE}:  '$statement->{TEXT}'\n";
    }
}

sub unparse_definition
{
    my $statement = shift;
    return "<$statement->{NAME}> := " . unparse_menu ($statement->{MENU}, 1)
	. ";\n";
}

sub unparse_function_definition
{
    my $statement = shift;
    my $result = "$statement->{NAME}(" . join(',', @{ $statement->{FORMALS} });
    $result .= ") := " . unparse_actions (@{ $statement->{ACTIONS} });
    return $result . ";\n";
}

sub unparse_command
{
    my ($command, $show_actions) = @_;
    my $result = unparse_terms ($show_actions, @{ $command->{TERMS} });
    if ($command->{ACTIONS} && $show_actions) {
        my $result .= " = " . unparse_actions (@{ $command->{ACTIONS} });
    }
    return $result;
}

sub unparse_terms
{
    my $show_actions = shift;
    my $result = unparse_term(shift, $show_actions);
    for my $term (@_) {
        $result .= " " . unparse_term($term, $show_actions);
    }
    return $result;
}

sub unparse_term
{
    my ($term, $show_actions) = @_;
    my $result = "";
    if ($term->{OPTIONAL}) {$result .=  "["}
    if    ($term->{TYPE} eq "word")      {$result .= "$term->{TEXT}"}
    elsif ($term->{TYPE} eq "variable")  {$result .= "<$term->{TEXT}>"}
    elsif ($term->{TYPE} eq "dictation") {$result .= "<_anything>"}
    elsif ($term->{TYPE} eq "menu")      {$result .= unparse_menu ($term, 
								   $show_actions)}
    elsif ($term->{TYPE} eq "range") {
        $result .= "$term->{FROM}..$term->{TO}";
    }
    if ($term->{OPTIONAL}) {$result .=  "]"}
    return $result;
}

sub unparse_menu
{
    my @commands = @{ shift->{COMMANDS} };
    my $show_actions = shift;
    my $result = "(" . unparse_command(shift @commands, $show_actions);
    for my $command (@commands) {
        $result .= " | " . unparse_command($command, $show_actions);
    }
    return $result . ")";
}

sub unparse_actions
{
    my $result = unparse_action(shift);
    for my $action (@_) {
        $result .= " " . unparse_action($action);
    }
    return $result;
}

sub unparse_action
{
    my $action = shift;
    if    ($action->{TYPE} eq "word")     {return unparse_word($action)}
    elsif ($action->{TYPE} eq "reference"){return "\$$action->{TEXT}"}
    elsif ($action->{TYPE} eq "formalref"){return "\$$action->{TEXT}"}
    elsif ($action->{TYPE} eq "call") {
        my $result = "$action->{TEXT}(";
        if (my @arguments = @{ $action->{ARGUMENTS} }) {
            $result .= unparse_argument(shift @arguments);
            for my $argument (@arguments) {
                $result .= ", " . unparse_argument($argument);
            }
        }
        return $result . ")";
    }
}

sub unparse_word
{
    my $action = shift;
    my $word = $action->{TEXT}; 
    $word =~ s/\'/\'\'/g;
    return "'$word'" ;
}

sub unparse_argument
{
    my $argument = shift;
    return unparse_actions(@{$argument});
}

# ---------------------------------------------------------------------------
# Transform Eval into EvalTemplate, unroll user functions

  # takes a list of non-action nodes
sub transform_nodes
{
    foreach my $node (@_) {
	transform_node($node);
    }
}

sub transform_node
{
    my $node = shift;

    if ($node->{COMMANDS})  { transform_nodes(@{ $node->{COMMANDS} }); }
    if ($node->{TERMS})     { transform_nodes(@{ $node->{TERMS} }); }
    if ($node->{MENU})      { transform_node(    $node->{MENU}); }

    if ($node->{ACTIONS})   { 
	$node->{ACTIONS} = transform_actions({}, @{ $node->{ACTIONS} }); 
    }
}

# transforms above are destructive, transforms below are functional
# except transform_eval

sub transform_actions
{
    my $substitution = shift;
    my @new_actions = ();

    foreach my $action (@_) {
	push(@new_actions, transform_action($substitution, $action));
    }

    return \@new_actions;
}

sub transform_arguments          # lists of actions
{
    my $substitution = shift;
    my @new_arguments = ();

    foreach my $argument (@_) {
	push(@new_arguments, transform_actions($substitution, @{$argument}));
    }

    return \@new_arguments;
}

sub transform_action
{
    my ($substitution, $action) = @_;

    if ($action->{TYPE} eq "formalref") { 
	my $name = $action->{TEXT};
	if ($substitution->{$name}) {
	    return @{ $substitution->{$name} };
	}
    }

    if ($action->{TYPE} eq "call") { 
	return transform_call($substitution, $action); 
    }

    return $action;
}

sub transform_call
{
    my ($substitution, $call) = @_;

    my $new_call = {};
    $new_call->{TYPE}      = $call->{TYPE};
    $new_call->{TEXT}      = $call->{TEXT};
    $new_call->{CALLTYPE}  = $call->{CALLTYPE};
    if ($call->{ARGTYPES}) { $new_call->{ARGTYPES}  = $call->{ARGTYPES}; }
    $new_call->{ARGUMENTS} = $call->{ARGUMENTS};

    if ($new_call->{CALLTYPE} eq "vocola" and $new_call->{TEXT} eq "Eval") {
	transform_eval($new_call);
    }

    $new_call->{ARGUMENTS} = transform_arguments($substitution, 
						 @{$new_call->{ARGUMENTS}});

    if ($new_call->{CALLTYPE} eq "user") {
        my @arguments  = @{ $new_call->{ARGUMENTS} };

        my $definition = $Function_definitions{$new_call->{TEXT}};
        my @formals    = @{ $definition->{FORMALS} };
        my $body       = $definition->{ACTIONS};

	my $bindings = {};
	my $i = 0;
	foreach $argument (@arguments) {
	    $bindings->{$formals[$i]} = $argument;
	    $i += 1;
	}

	return @{ transform_actions($bindings, @{ $body }) };
    }

    return $new_call;
}

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

sub transform_eval
{
    my $call = shift;
    my @arguments = @{ $call->{ARGUMENTS} };

    my $template = "";
    my @new_arguments = ();
    foreach my $action (@{ $arguments[0] }) {
	if ($action->{TYPE} eq "word") {
	    my $text = $action->{TEXT};
	    $text =~ s/%/%%/g;
	    $template .= $text;
	} else {
	    $template .= "%a";
	    my @new_argument = ();
	    push(@new_argument, $action);
	    push(@new_arguments, \@new_argument);
	}
    }

    my $template_word = {};
    $template_word->{TYPE} = "word";
    $template_word->{TEXT} = $template;

    my @template_argument = ();
    push(@template_argument, $template_word);
    unshift(@new_arguments, \@template_argument);

    $call->{TEXT}      = "EvalTemplate"; 
    $call->{ARGUMENTS} = \@new_arguments;
}


# ---------------------------------------------------------------------------
# Emit NatLink output

sub emit_output
{
    my ($out_file, @statements) = @_;
    open OUT, ">$out_file" or die "$@ $out_file\n";
    &emit_file_header;
    &emit_dictation_grammar if $Should_emit_dictation_support;
    for my $statement (@statements) {
        my $type = $statement->{TYPE};
        if    ($type eq "definition") {emit_definition_grammar ($statement)}
        elsif ($type eq "command")    {emit_command_grammar ($statement)}
    }
    &emit_sequence_and_context_code;
    for my $statement (@statements) {
        my $type = $statement->{TYPE};
        if    ($type eq "definition") {emit_definition_actions ($statement)}
        if    ($type eq "function")   {}
        elsif ($type eq "command")    {emit_top_command_actions ($statement)}
    }
    &emit_file_trailer;
    close OUT;
}

sub emit_sequence_and_context_code
{
    # Build a list of context statements, and commands defined in each
    my (@contexts, $context, $noop);
    for my $statement (@_) {
        my $type = $statement->{TYPE};
        if ($type eq "context") {
	    $context = $statement;
	    my @strings = @{ $context->{STRINGS} };
	    if ($strings[0] eq "") {
		# no-op context restriction
		if ($noop) {
		    $context = $noop;
		} else {
		    $noop = $context;
		    push (@contexts, $context);
		}
	    } else {
		push (@contexts, $context);
	    }
        } elsif ($type eq "command") {
            push (@{ $context->{RULENAMES} }, $statement->{NAME});
        }
    }
    emit_sequence_rules(@contexts);
    &emit_file_middle;
    emit_context_definitions(@contexts);
    emit_context_activations(@contexts);
}

sub emit_sequence_rules
{
    # Emit rules allowing speaking a sequence of commands
    # (and add them to the RULENAMES for the context in question)
    my $number = 0;
    my $any = "";
    for my $context (@_) {
        my @names = @{ $context->{RULENAMES} };
        next if @names == 0;
        $number++;
        my $suffix = "";
        my $rules = '<' . join('>|<', @names) . '>';
        my @strings = @{ $context->{STRINGS} };
        if ($strings[0] eq "") {
            emit(2, "<any> = $rules;\n");
            $any = "<any>|";
        } else {
            $suffix = "_set$number";
            emit(2, "<any$suffix> = $any$rules;\n");
        }
        my $rule_name = "sequence$suffix";
        $context->{RULENAMES} = [$rule_name];
	emit(2, "<$rule_name> exported = " 
	        . repeated_upto("<any$suffix>", $maximum_commands) . ";\n");
    }
}

sub repeated_upto
{
    # Create grammar for a $spec repeated 1 upto $count times
    my $spec = shift;
    my $count = shift;

    return "$spec+" if $count>99;

    my $result = $spec;
    while ($count > 1) {
	$result = "$spec [$result]";
	$count = $count - 1
    }

    return $result
}

sub emit_context_definitions
{
    # Emit a "rule set" definition containing all command names in this context
    my $number = 0;
    for my $context (@_) {
        my @names = @{ $context->{RULENAMES} };
        next if @names == 0;
        $number++;
        my $first_name = shift @names;
        emit(2, "self.ruleSet$number = ['$first_name'");
        for my $name (@names) {print OUT ",'$name'"}
        emit(0, "]\n");
    }
}

sub emit_context_activations
{
    my $app = $Module_name;
    my $module_is_global = ($app =~ /^\_/);
    my $module_has_prefix = 0;
    if ($app =~ /^(.+?)_.*/) {
        $prefix = $1;
        $module_has_prefix = 1;
    }
    #emit(2, "self.activateAll()\n") if $module_is_global;
    emit(0, "\n    def gotBegin(self,moduleInfo):\n");
    if ($module_is_global) {
        emit(2, "window = moduleInfo[2]\n");
    } else {
        emit(2, "\# Return if wrong application\n");
        emit(2, "window = matchWindow(moduleInfo,'$app','')\n");
        if ($module_has_prefix) {
            emit(2, "if not window: window = matchWindow(moduleInfo,'$prefix','')\n");
        }
        emit(2, "if not window: return None\n");
    }
    emit(2, "self.firstWord = 0\n");
    emit(2, "\# Return if same window and title as before\n");
    emit(2, "if moduleInfo == self.currentModule: return None\n");
    emit(2, "self.currentModule = moduleInfo\n\n");
    emit(2, "self.deactivateAll()\n");
    emit(2, "title = string.lower(moduleInfo[1])\n");

    # Emit code to activate the context's commands if one of the context
    # strings matches the current window
    my $number = 0;
    for my $context (@_) {
        next if not $context->{RULENAMES};
        $number++;
	my @targets = @{ $context->{STRINGS} };
	@targets = map {make_safe_python_string($_)} @targets;
        my $tests = join " or ", map {"string.find(title,'$_') >= 0"}
                                     @targets;
        emit(2, "if $tests:\n");
        emit(3, "for rule in self.ruleSet$number:\n");
        if ($module_is_global) {emit(4, "self.activate(rule)\n");}
        else {
	    emit(4, "try:\n");
	    emit(5, "self.activate(rule,window)\n");
	    emit(4, "except BadWindow:\n");
	    emit(5, "pass\n");
	}
    }
    emit(0, "\n");
}

#        if (not $module_is_global) {
#            emit(3, "    self.activate(rule,window)\n");
#        } else {
#            emit(3, "    if rule not in self.activeRules:\n");
#            emit(3, "        self.activate(rule,window)\n");
#            emit(2, "else:\n");
#            emit(3, "for rule in self.ruleSet$number:\n");
#            emit(3, "    if rule in self.activeRules:\n");
#            emit(3, "        self.deactivate(rule,window)\n");
#        }

sub emit_dictation_grammar
{
    emit(2, "<dgndictation> imported;\n");
}

sub emit_definition_grammar
{
    my $definition = shift;
    emit(2, "<$definition->{NAME}> = ");
    emit_menu_grammar (@{ $definition->{MENU}->{COMMANDS} });
    emit(0, ";\n");
}

sub emit_command_grammar
{
    my $command = shift;
    inline_a_term_if_nothing_concrete($command);
    my ($first, $last) = find_terms_for_main_rule($command);
    my @terms = @{ $command->{TERMS} };
    my @main_terms = @terms[$first .. $last];
    my $name = $command->{NAME};
    my $name_a = $name . "a";
    my $name_b = $name . "b";
    @main_terms = (create_variable_node($name_a), @main_terms) if $first > 0;
    push (@main_terms, create_variable_node($name_b)) if $last < $#terms;
    emit_rule($command->{NAME}, "", @main_terms);
    emit_rule($name_a, "", @terms[0 .. $first-1]) if $first > 0;
    emit_rule($name_b, "", @terms[$last+1 .. $#terms]) if $last < $#terms;
}

sub emit_rule
{
    my $name = shift;
    my $exported = shift;
    emit(2, "<$name>$exported = ");
    emit_command_terms(@_);
    emit(0, ";\n");
}

sub emit_command_terms
{
    for my $term (@_) {
        if ($term->{OPTIONAL}) {emit(0, "[ ")}
        if ($term->{TYPE} eq "word") {
            my $word = $term->{TEXT};
            if ($word =~ /\'/) {emit(0, '"' . "$word" . '" ')}
            else               {emit(0, "'$word' ")}
        } elsif ($term->{TYPE} eq "dictation") {emit(0, "<dgndictation> ")}
        elsif   ($term->{TYPE} eq "variable")  {emit_variable_term($term)}
        elsif   ($term->{TYPE} eq "range")     {emit_range_grammar($term)}
        elsif   ($term->{TYPE} eq "menu") {
            emit(0, "(");
            emit_menu_grammar(@{ $term->{COMMANDS}} );
            emit(0, ") ");
        }
        if ($term->{OPTIONAL}) {emit(0, "] ")}
    }
}

sub emit_variable_term
{
    my $term = shift;
    my $text = $term->{TEXT};
    emit(0, "<$text> ");
}

sub emit_menu_grammar
{
    emit_command_terms(@{ shift->{TERMS} });
    for my $command (@_) {
        emit(0, "| ");
        emit_command_terms(@{ $command->{TERMS} });
    }
}

sub emit_range_grammar
{
    my $i  = @_[0]->{FROM};
    my $to = @_[0]->{TO};
    emit(0, "($i");
    while (++$i <= $to) {emit(0, " | $i")}
    emit(0, ") ");
}

sub emit_definition_actions
{
    my $definition = shift;
    emit(1, 
	 "def get_$definition->{NAME}(self, list_buffer, functional, word):\n");
    emit_menu_actions("list_buffer", "functional", $definition->{MENU}, 2);
    emit(2, "return list_buffer\n\n");
}

sub emit_top_command_actions
{
    my $command = shift;
    my @terms = @{ $command->{TERMS} };
    my $nterms = @terms;
    my $function = "gotResults_$command->{NAME}";
    @Variable_terms = get_variable_terms($command); # used in emit_reference

    my $command_specification = unparse_terms(0, @terms);

    emit(1, "\# ");
    print OUT unparse_terms (0, @terms);
    emit(0, "\n");
    emit(1, "def $function(self, words, fullResults):\n");
    emit(2, "if self.firstWord<0:\n");
    emit(3, "return\n");
    emit_optional_term_fixup(@terms);
    emit(2, "try:\n");
    emit(3, "top_buffer = ''\n");
    emit_actions("top_buffer", "False", $command->{ACTIONS}, 3);
    emit_flush("top_buffer", "False", 3);
    emit(3, "self.firstWord += $nterms\n");

    # If repeating a command with no <variable> terms (e.g. "Scratch That
    # Scratch That"), our gotResults function will be called only once, with
    # all recognized words. Recurse!
    unless (has_variable_term(@terms)) {
        emit(3, "if len(words) > $nterms: self.$function(words[$nterms:], fullResults)\n");
    }

    emit(2, "except Exception, e:\n");
    my $file = $command->{FILE};
    $file =~ s/\\/\\\\/g;
    emit(3, "handle_error('" . make_safe_python_string($file)
            . "', " . $command->{LINE} . ", '" 
	    . make_safe_python_string($command_specification) 
            . "', e)\n");
    emit(3, "self.firstWord = -1\n");
    emit(0, "\n");
}

sub emit_flush
{
    my ($buffer, $functional, $indent) = @_;

    emit($indent, "$buffer = do_flush($functional, $buffer);\n");
}

sub has_variable_term
{
    for my $term (@_) {
        return 1 if $term->{TYPE} eq "variable" or $term->{TYPE} eq "dictation";
    }
    return 0;
}

# Our indexing into the "fullResults" array assumes all optional terms were 
# spoken.  So we emit code to insert a dummy entry for each optional word 
# that was not spoken.  (The strategy used could fail in the uncommon case 
# where an optional word is followed by an identical required word.)

sub emit_optional_term_fixup
{
    for my $term (@_) {
	my $index = $term->{NUMBER};
        if ($term->{OPTIONAL}) {
            my $text = $term->{TEXT};
            emit(2, "opt = $index + self.firstWord\n");
            emit(2, "if opt >= len(fullResults) or fullResults[opt][0] != '$text':\n");
            emit(3, "fullResults.insert(opt, 'dummy')\n");
        }
	elsif ($term->{TYPE} eq "dictation") {
	    emit(2, "fullResults = combineDictationWords(fullResults)\n");
            emit(2, "opt = $index + self.firstWord\n");
            emit(2, "if opt >= len(fullResults) or fullResults[opt][1] != 'dgndictation':\n");
            emit(3, "fullResults.insert(opt, ['', 'dgndictation'])\n");
	}
    }   
}

sub emit_actions
{
    my ($buffer, $functional, $actions, $indent) = @_;
    for my $action (@{$actions}) {
        my $type = $action->{TYPE};
        if ($type eq "reference") {
            emit_reference($buffer, $functional, $action, $indent);
        } elsif ($type eq "formalref") {
	    die "Compiler Error: not all formal references transformed away.\n";
        } elsif ($type eq "word") {
            my $safe_text = make_safe_python_string($action->{TEXT});
            emit($indent, "$buffer += '$safe_text'\n");
        } elsif ($type eq "call") {
            emit_call($buffer, $functional, $action, $indent);
        } else {
            die "Unknown action type: '$type'\n";
        }
    }
}

sub get_variable_terms
{
    my $command = shift;
    my @variable_terms;
    for my $term (@{ $command->{TERMS} }) {
        my $type = $term->{TYPE};
        if ($type eq "menu" or $type eq "range" or $type eq "variable" or
            $type eq "dictation") {
            push (@variable_terms, $term);
        }
    }
    return @variable_terms;
}

sub emit_reference
{
    my ($buffer, $functional, $action, $indent) = @_;
    my $reference_number = $action->{TEXT} - 1;
    my $variable = $Variable_terms[$reference_number];
    my $term_number = $variable->{NUMBER};
    emit($indent, "word = fullResults[$term_number + self.firstWord][0]\n");
    if ($variable->{TYPE} eq "menu") {
        emit_menu_actions($buffer, $functional, $variable, $indent);
    } elsif ($variable->{TYPE} eq "range" or $variable->{TYPE} eq "dictation") {
        emit($indent, "$buffer += word\n");
    } elsif ($variable->{TYPE} eq "variable") {
        my $function = "self.get_$variable->{TEXT}";
        emit($indent, "$buffer = $function($buffer, $functional, word)\n");
    }
}

sub emit_menu_actions
{
    my ($buffer, $functional, $menu, $indent) = @_;
    if (not menu_has_actions($menu)) {
        emit($indent, "$buffer += word\n");
    } else {
        my @commands = flatten_menu($menu);
        my $if = "if";
        for my $command (@commands) {
            my $text = $command->{TERMS}[0]->{TEXT};
            $text =~ s/'/\\'/g;
            emit($indent, "$if word == '$text':\n");
            if ($command->{ACTIONS}) {
		if (@{$command->{ACTIONS}}) {
		    emit_actions($buffer, $functional, 
				 $command->{ACTIONS}, $indent+1);
		} else {
		    emit($indent+1, "pass  # no actions\n");
		}
            } else {
                emit($indent+1, "$buffer += '$text'\n");
            }
            $if = "elif";
        }
    }
}

sub emit_call
{
    my ($buffer, $functional, $call, $indent) = @_;
    my $callType = $call->{CALLTYPE};
    begin_nested_call();
    if    ($callType eq "dragon"   ) {&emit_dragon_call}
    elsif ($callType eq "extension") {&emit_extension_call}
    elsif ($callType eq "user"     ) {
	die "No user function call should be present here!";
    } elsif ($callType eq "vocola") {
        my $callName = $call->{TEXT};
        if    ($callName eq "Eval")         {
	    die "Compiler error: Eval not transformed away\n";
	} elsif ($callName eq "EvalTemplate") {&emit_call_eval_template}
        elsif ($callName eq   "Repeat")       {&emit_call_repeat}
        elsif ($callName eq   "Unimacro")     {&emit_call_Unimacro}
        else {die "Unknown Vocola function: '$callName'\n"}
    } else {die "Unknown function call type: '$callType'\n"}
    end_nested_call();
}
sub begin_nested_call{ $NestedCallLevel += 1}
sub   end_nested_call{ $NestedCallLevel -= 1}

sub get_nested_buffer_name
{
    my $root = shift;
    return ($NestedCallLevel == 1) ? $root : "$root$NestedCallLevel";
}

sub emit_call_repeat
{
    my ($buffer, $functional, $call, $indent) = @_;
    my @arguments = @{ $call->{ARGUMENTS} };

    my $argument_buffer = get_nested_buffer_name("limit");
    emit($indent, "$argument_buffer = ''\n");
    emit_actions("$argument_buffer", "True", $arguments[0], $indent);
    emit($indent, "for i in range(to_long($argument_buffer)):\n");
    emit_actions($buffer, $functional, $arguments[1], $indent+1);
}

sub emit_arguments
{
    my ($call, $name, $indent) = @_;
    my $arguments = "";

    my $i=0;
    for my $argument (@{ $call->{ARGUMENTS} }) {
	if ($i ne 0) { $arguments .= ", "; }
	$i += 1;
	my $argument_buffer = get_nested_buffer_name($name) . "_arg$i";
	emit($indent, "$argument_buffer = ''\n");
	emit_actions($argument_buffer, "True", $argument, $indent);
	$arguments .= $argument_buffer;
    }

    return $arguments;
}

sub emit_dragon_call
{
    my ($buffer, $functional, $call, $indent) = @_;
    my $callName  = $call->{TEXT};
    my $argumentTypes = $call->{ARGTYPES};

    emit_flush($buffer, $functional, $indent);
    my $arguments = emit_arguments($call, "dragon", $indent);
    emit($indent, 
	 "call_Dragon('$callName', '$argumentTypes', [$arguments])\n");
}

sub emit_extension_call
{
    my ($buffer, $functional, $call, $indent) = @_;
    my $callName      = $call->{TEXT};
    my @callFormals   = $Extension_functions{$callName};
    my $needsFlushing = $callFormals[0][2];
    my $import_name   = $callFormals[0][3];
    my $function_name = $callFormals[0][4];

    if ($needsFlushing) { emit_flush($buffer, $functional, $indent); }
    my $arguments = emit_arguments($call, "extension", $indent);
    emit($indent, "import $import_name\n");
    if ($needsFlushing) {
	emit($indent, "$function_name($arguments)\n");
    } else {
	emit($indent, "$buffer += str($function_name($arguments))\n");
    }
}

sub emit_call_eval_template
{
    my ($buffer, $functional, $call, $indent) = @_;

    my $arguments = emit_arguments($call, "eval_template", $indent);
    emit($indent, "$buffer += eval_template($arguments)\n");
}

sub emit_call_Unimacro
{
    my ($buffer, $functional, $call, $indent) = @_;

    emit_flush($buffer, $functional, $indent);
    my $arguments = emit_arguments($call, "unimacro", $indent);
    emit($indent, "call_Unimacro($arguments)\n");
}


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

sub find_terms_for_main_rule
{
    # Create a "variability profile" summarizing whether each term is
    # concrete (c), variable (v), or optional (o). For example, the
    # profile of "[One] Word <direction>" would be "ocv". (Menus are
    # assumed concrete, and dictation variables are treated like
    # normal variables.)

    $_ = "";
    for my $term (@{ shift->{TERMS} }) {
        $_ .= (($term->{TYPE} eq "variable") or $term->{TYPE} eq "dictation") 
                 ? "v" : ($term->{OPTIONAL}) ? "o" : "c";
    }

    # Identify terms to use for main rule.
    # We might not start with the first term. For example:
    #     [Move] <n> Left  -->  "Left" is the first term to use
    # We might not end with the last term. For example:
    #     Kill <n> Words   -->  "Kill" is the last term to use
    # And in this combined example, our terms would be "Left and Kill"
    #     [Move] <n> Left and Kill <n> Words

    my $first = /^(v*o+v[ov]*c)/        ? length($1)-1 : 0;
    my $last  = /^([ov]*c[co]*)v+[co]+/ ? length($1)-1 : length($_)-1;
    return ($first, $last);
}

sub inline_a_term_if_nothing_concrete
{
    my $command = shift;
    while (!command_has_a_concrete_term($command)) {
        inline_a_term($command);
    }
}

sub command_has_a_concrete_term
{
    my $command = shift;
    for my $term (@{ $command->{TERMS} }) {
        return 1 if term_is_concrete($term);
    }
    return 0;
}

sub term_is_concrete
{
    my $term = shift;
    my $type = $term->{TYPE};
    if    ($type eq "menu")                             {return 1}
    elsif ($type eq "variable" or $type eq "dictation") {return 0}
    else {return not $term->{OPTIONAL}}
}

sub inline_a_term
{
    my $terms = shift->{TERMS};

    # Find the array index of the first non-optional term
    my $index = 0;
    $index++
        while ($index < @{$terms}) and
            ($terms->[$index]->{OPTIONAL} or
             $terms->[$index]->{TYPE} eq "dictation");

    my $type = $terms->[$index]->{TYPE};
    my $number = $terms->[$index]->{NUMBER};
    if ($type eq "variable") {
        my $variable_name = $terms->[$index]->{TEXT};
        #print "inlining variable $variable_name\n";
        my $definition = $Definitions{$variable_name};
        $terms->[$index] = $definition->{MENU};
        $terms->[$index]->{NUMBER} = $number;
    } elsif ($type eq "menu") {
        for my $command (@{ $terms->[$index]->{COMMANDS} }) {
            inline_a_term($command);
        }
    } else {die "Internal error inlining term of type '$type'\n"}
}

# ---------------------------------------------------------------------------
# Utilities used by "emit" methods

sub emit
{
    my ($indent, $string) = @_;
    print OUT ' ' x (4 * $indent), $string;
}

sub menu_has_actions
{
    for my $command (@{ shift->{COMMANDS} }) {
        return 1 if $command->{ACTIONS};
        for $term (@{ $command->{TERMS} }) {
            return 1 if $term->{TYPE} eq "menu" and menu_has_actions($term);
        }
    }
    return;
}

# To emit actions for a menu, build a flat list of (canonicalized) commands:
#     - recursively extract commands from nested menus
#     - distribute actions, i.e. (day|days)=d --> (day=d|days=d)
# Note that error checking happened during parsing, in verify_referenced_menu

sub flatten_menu
{
    my ($menu, $actions_to_distribute) = @_;
    my (@new_commands, $new_actions);
    for my $command (@{ $menu->{COMMANDS} }) {
        if ($command->{ACTIONS}) {$new_actions = $command->{ACTIONS}}
        else                     {$new_actions = $actions_to_distribute}
        my @terms = @{ $command->{TERMS} };
        my $type = $terms[0]->{TYPE};
        if ($type eq "word") {
            $command->{ACTIONS} = $new_actions if $new_actions;
            push (@new_commands, $command);
        } elsif ($type eq "menu") {
            my @commands = flatten_menu ($terms[0], $new_actions);
            push (@new_commands, @commands);
        } 
    }
    return @new_commands;
}

sub make_safe_python_string
{
    # we have already doubled backslashes by this time
    my $text = $_[0] . "";
    $text =~ s/'/\\'/g;
    $text =~ s/\n/\\n/g;
    return $text;
}

# ---------------------------------------------------------------------------
# Pieces of the output Python file

sub emit_file_header
{
    $now = localtime;
    print OUT "\# NatLink macro definitions for NaturallySpeaking\n"; 
    print OUT "\# coding: latin-1\n";
    print OUT "\# Generated by vcl2py $VocolaVersion, $now\n";
    print OUT <<MARK;

import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
MARK
}

sub emit_file_middle
{
    print OUT <<MARK;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
MARK
}

sub emit_file_trailer
{
    print OUT <<MARK;
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
MARK
}

# ---------------------------------------------------------------------------
# Okay, let's run!

main();
