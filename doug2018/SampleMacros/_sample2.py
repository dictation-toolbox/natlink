#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# _sample2.py
#
# This is a sample macro file with a two commands.  When NatSpeak has the
# focus, say "demo sample two".  It should recognize the command and type:
#   Say "demo sample two color     (the word color will be in italics)
#
# Say "demo sample two red" and it would recognize the command and type:
#   The color is red               (it types the name of the color you say)
#
# This file demonstrates having two commands in one grammar.  NatLink knows
# which rule was recognized and calls the appropiate handling function
# (gotResults_xxx).  This file also demonstrates using the actual words
# recognized to control the results (we type the name of the spoken color).
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <firstRule> exported = demo sample two [ help ];
        <secondRule> exported = demo sample two
            ( red | blue | green | purple | black | white | yellow |
              orange | magenta | cyan | gray );
    """
    
    def gotResults_firstRule(self,words,fullResults):
        natlink.playString('Say "demo sample two {ctrl+i}color{ctrl+i}"{enter}')

    def gotResults_secondRule(self,words,fullResults):
        natlink.playString('The color is "%s"{enter}'%words[3])
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
