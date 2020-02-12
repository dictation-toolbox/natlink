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
# focus, say "d\xe9mo sample six".  It should recognize the command and type:
#   Say "d\xe9mo sample six color     (the word color will be in italics)
#
# Say "d\xe9mo sample six red" and it would recognize the command and type:
#   The color is red               (it types the name of the color you say)
#
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.
#


import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <firstRule> exported = d\xe9mo sample six [ help ];
        <secondRule> exported = d\xe9mo sample six {color};
    """
    
    def gotResults_firstRule(self,words,fullResults):
        natlink.playString('Say "d\xe9mo sample six {ctrl+i}color{ctrl+i}"{enter}')

    def gotResults_secondRule(self,words,fullResults):
        natlink.playString('The color is "%s"{enter}'% words[-1])
        
    def initialize(self):
        print('.... _sample6 loading')
        self.load(self.gramSpec)
        print('validLists: ', self.validLists)
        print('validRules: ', self.validRules)
        self.setList('color', ['red', 'blue', 'green', 'purple', 'white', 'yellow', 'orange', 'magenta', 'cyan', 'gray'])
        print("list color set, loading ready....")
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
