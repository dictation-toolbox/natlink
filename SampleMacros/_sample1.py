#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# _sample1.py
#
# This is a sample macro file with a single command.  When NatSpeak has the
# focus, say "demo sample one".  It should recognize the command and type:
#   Heard macro "sample one".
#
# This file represents the simplest possible example of a NatLink macro.
#
# See also the variant _first_sample_docstring.py in the folder DisabledGrammars of Unimacro
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.
#
import sys
import os
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = d\xe9mo sample one;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

    def gotResults_start(self,words,fullResults):
        natlink.displayText('Heard macro "sample one"{enter}',0)
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
