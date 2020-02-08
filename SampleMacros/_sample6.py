#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created 2020-02-01 by Quintijn Hoogenboom
# It does the same as _sample2, but now with a list of colors
#
# _sample6.py
#
# This is a sample macro file with a two commands.  When NatSpeak has the
# focus, say "demo sample six".  It should recognize the command and type:
#   Say "demo sample six color     (the word color will be in italics)
#
# Say "demo sample six red" and it would recognize the command and type:
#   The color is red               (it types the name of the color you say)
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <firstRule> exported = demo sample six [ help ];
        <secondRule> exported = second sample six;
    """
    
    def gotResults_firstRule(self,words,fullResults):
        natlink.playString('Say "demo sample six {ctrl+i}color{ctrl+i}"{enter}')

    def gotResults_secondRule(self,words,fullResults):
        natlink.playString('The color is "%s"{enter}'%words[3])
        
    def initialize(self):
        self.load(self.gramSpec)
        self.setList('color', ['red', 'blue', 'green', 'purple', 'black', 'white', 'yellow', 'orange', 'magenta', 'cyan', 'gray'])
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
