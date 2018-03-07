#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 2000 by Joel Gould
#   Portions (c) Copyright 2000 by Dragon Systems, Inc.
#

import string
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <dgndictation> imported;
        <dgnletters> imported;
        <ruleOne> exported = demo sample eight <dgndictation> [ stop ];
        <ruleTwo> exported = demo sample eight spell <dgnletters> [ stop ];
    """

    def gotResults_dgndictation(self,words,fullResults):
        words.reverse()
        text = string.join(words)
        natlink.playString(' ' + text)

    def gotResults_dgnletters(self,words,fullResults):
        words = [x[:1] for x in words]
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
