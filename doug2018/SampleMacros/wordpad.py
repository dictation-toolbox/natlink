#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# wordpad.py
#   Sample macro file which is active when Microsoft WordPad is active.
#
# April 25, 1999
#   - packaged for external release
#
# March 3, 1999
#   - initial version
#

############################################################################
#
# This is a sample grammar file.  I have implemented some basic formatting
# for Microsoft WordPad (main window).
#
# This file is loaded automatically if, and only if, a module called
# "wordpad" is active when the microphone is turned on or an utterance begins.
# The Python file must have the same name as the module (except the Python
# filename must be in lowercase).
#

# The following file gets us access to the basic NatSpeak functions like
# the ability to send keystrokes to an application.

import natlink

# The following file contains the GrammarBase infrastructure and some utility
# functions like convertResults and matchWindow.

from natlinkutils import *

############################################################################
#
# Here is the definition of our grammar.  Each user grammar should be a class
# derived from GrammarBase.  This ensures that the appropiate cleanup will be
# done when the class is garbage collected.
#

class ThisGrammar(GrammarBase):

    # First we list our grammar as a long string.  The grammar is in SAPI
    # format, where we define a series of rules as expressions built from
    # other rules, words and lists.  Rules which can be activated are flagged
    # with the keyword "exported".

    gramSpec = """
        <fontFace> = {fontFace};

        <fontSize> = 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 
            16 | 17 | 18 | 19 | 20 | 22 | 24 | 25 | 26 | 28 | 30 | 36 | 40 |
            48 | 60 | 72 | 84 | 96 | 100 | 120;

        <fontStyle> = bold | underline | italic | regular | strikeout |
            'bold italic' | plain [text];

        <objClause> = that | selection;

        <setFont> exported = 
            ( format <objClause> | make <objClause> | set font ) 
              ( <fontFace> [ <fontSize> ] [ <fontStyle> ] |
                [ [size] <fontSize> [points] ] <fontStyle> |
                [size] <fontSize> [points] ) |
            set size <fontSize> [points];

        <verb> = cut | copy | bold | italicize | underline | center | 
            'left align' | 'right align' | delete | restore;

        <verbObj> exported = <verb> <objClause>;
    """

    # Our sample grammar contains one list, {fontFace}.  Lists have to be
    # loaded after the grammar is created.  Here is a variable which
    # contains a list of the words which should be loaded into our list.

    fontFace = [ "Times", "Times New Roman", "Courier", "Courier New", "Arial" ]

    # This is the main function which creates the grammar.  self.load will
    # load the actual grammar.  It traps its own errors so it can report
    # them including the grammar source code and it return false on failure.
    #
    # Once the grammar is loaded, we load the words into our list.  This 
    # function creates the grammar but nothing is activated until later.
    
    def initialize(self):
        if not self.load(self.gramSpec): return None
        self.setList('fontFace',self.fontFace)

    # The base class calls this function (gotBegin) when speech is detected.
    # This give us a chance to activate our grammars.  We use the function
    # matchWindow to determine whether a module called 'wordpad' with a window
    # title containing '- WordPad' is active.  If so then we activate every
    # exported rule.  Otherwise we deactivate all our rules.

    def gotBegin(self, moduleInfo):
        winHandle = matchWindow( moduleInfo, 'wordpad', 'WordPad' )
        if winHandle: 
            # The window parameter is set to the handle of the currently
            # active window which we just determined to be the wordpad
            # module.  The activateAll function will activate every exported
            # rule in our grammar.  This is a convince, we could have just
            # activated a single rule by name.
            self.activateAll( window=winHandle )
        else: 
            # NatSpeak will only activate our grammar when the indicated
            # window handle is active.  Explicitly deactivating our grammars    
            # is not really necessary for this example but it is a useful
            # concept for more complex grammars.
            self.deactivateAll()
        self.sawResults = 0

    # The base class calls this function (gotResults_verb) whenever a sequence
    # of one or more words are recognized from the rule named "verb".  The
    # parameter "words" will be a list of sequential words from the recognition
    # results which were taken from the "verb" rule.  In our toy grammar,
    # there will only be one word from "verb" during each recognition.
    #
    # Our op level rules are "setFont" and "verbObj".  We can not rely on
    # the function gotResults_verbObj being called, however, because there
    # are no words in the rule "verbObj".  Fortunately, when the top-level
    # rule "verbObj" is recognized, the rule "verb" will also be recognized.
    #
    # When we get a word from "verb" we look that word up in a Python
    # dictionary and execute the code fragment which matches that word.
    # In this example, the code fragment sets a local variable to a string
    # to send to the target application.  We then send that string to the
    # currently active window using the natlink.playString utility function.

    def gotResults_verb(self,words,fullResults):
        keywords = {
            'cut':          "output = '{Ctrl+x}'",
            'copy':         "output = '{Ctrl+c}'",
            'bold':         "output = '{Ctrl+b}'",
            'italicize':    "output = '{Ctrl+i}'",
            'underline':    "output = '{Ctrl+u}'",
            'center':       "output = '{Ctrl+e}'",
            'left align':   "output = '{Ctrl+l}'",
            'right align':  "output = '{Ctrl+r}'",
            'delete':       "output = '{Del}'",
            'restore':      "output = '{Alt+o}f{Alt+y}Regular{Enter}'" }
        if words[0] in keywords: 
            exec(keywords[words[0]])
            natlink.playString(output)

    # The base class calls this function when one or more words in the
    # result come from the "setFont" rule.  The words recognized from
    # "setFont" are not interesting.  For example, if the user says
    # "set font Arial bold", then gotResults_setFont will be passed
    # the array ['set','font'] in the words parameter.
    #
    # However, each results callback also gets an array which contains
    # the full results.  For the previous example, the parameter fullResults
    # will contain the following complex array:
    #   [ ['set','setFont'], ['font','setFont'], ['Arial','fontFace'],
    #     ['bold','fontStyle'] ]
    #
    # Warning: gotResults_setFont could be called twice if there are multiple
    # disjoint sequences of words in the results from the "setFont" rule.
    # For example, if the user says "set font size 16 points", the function
    # gotResults_setFont will be called twice, once with the words parameter
    # set to ['set','font','size'] and once with the words parameter set to
    # ['points'].  To avoid doing the action twice, we set a flag at the start
    # of recognition (self.sawResults).
    #
    # To handle handle recognitions from "setFont", we use the fullResults.
    # However, the format of "fullResults" is not convient for our use.
    # Therefore, we use the function "convertResults" to convert fullResults
    # into a dictionary.  For the example above, this produces:
    #   { 'setFont':['set,'font'], 'fontFace':['Arial'], 'fontStyle':['bold'] }
    #
    # Now we can individually perform an action based on the fontFace, 
    # fontSize and fontStyle if found.

    def gotResults_setFont(self,words,fullResults):
        keywords = {
            'bold':         "output = '{Alt+y}Bold'",
            'italic':       "output = '{Alt+y}italic'",
            'regular':      "output = '{Alt+y}Regular'",
            'bold italic':  "output = '{Alt+y}Bold italic'",
            'plain':        "output = '{Alt+y}Regular'",
            'underline':    "output = '{Alt+u}'",
            'strikeout':    "output = '{Alt+k}'" }

        if self.sawResults: return None
        self.sawResults = 1

        rulesFound = convertResults(fullResults)
        # this brings up the font format dialog
        natlink.playString('{Alt+o}f')
        if 'fontFace' in rulesFound:
            # set the font face if found
            natlink.playString('{Alt+f}' + rulesFound['fontFace'][0])
        if 'fontStyle' in rulesFound:
            # handle the font style if found
            exec(keywords[ rulesFound['fontStyle'][0] ])
            natlink.playString(output)
        if 'fontSize' in rulesFound:
            # set the font size if found
            natlink.playString('{Alt+s}' + rulesFound['fontSize'][0])
        # close the font format dialog
        natlink.playString('{Enter}')

    # The GrammarBase base class offers a rich set of callbacks for results.
    # When results are recognized, it first calls "gotResultsInit" which we
    # did not use in this sample grammar.  Then it call "gotResults_XXX"
    # for each sequence of words in the results from rule "XXX".  Last,
    # it calls "gotResults".
    #
    # We do not need to do anything for "gotResults" but in our example, we
    # print the recognition results for debugging.

    def gotResults(self,words,fullResults):
        message = "Recognized '"
        first = 1
        for x in words:
            if not first: message = message + " "
            else: first = 0
            message = message + x
        message = message + "'"
        print(message)

############################################################################
#
# This is the top-level code
#
# This code gets executed when this file is (re)loaded.
#

# Every grammar file should contains two lines like this for each grammar
# class defined in the file.  These lines causes an instance of the grammar
# to be created and then initialized.

thisGrammar = ThisGrammar()
thisGrammar.initialize()

#
# Every grammar file must define a function called "unload" which will
# call the method "unload" for every grammar which the file loaded.  The
# Python wrapper code will call unload when this file is reloaded.  Calling
# unload first ensures that the classes are cleaned up.
#

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
