#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 2000 by Joel Gould
#   Portions (c) Copyright 2000 by Dragon Systems, Inc.
#
# <dgletters> does not work any more (2020)
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.
#

import string
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <dgndictation> imported;
        <dgnletters> imported;
        <ruleOne> exported = d\xe9mo sample eight <dgndictation> [ stop ];
        <ruleTwo> exported = d\xe9mo sample eight spell <dgnletters> [ stop ];
    """

    def gotResults_dgndictation(self,words,fullResults):
        words.reverse()
        text = string.join(words)
        natlink.playString(' ' + text)

    def gotResults_dgnletters(self,words,fullResults):
        words = map(lambda x: x[:1], words)
        text = string.join(words, '')
        natlink.playString(' ' + text)
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
