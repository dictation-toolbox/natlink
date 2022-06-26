#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
#pylint:disable=C0115, C0116, R0201, W0613
"""_sample_runmimic.py

This script tests the commands with alternatives in interactive mode

With recognitionMimic this grammar (from unittestNatlink.py) fails, October 2021.

when calling "mimic runzero" or "mimic north", the following lines should be printed in the Messages from Natlink window:

Heard macro "mimic runsimplezero", "['mimic', 'runzero']"
Heard macro "mimic runsimpleone", "['mimic', 'north']"

"""
from natlinkcore.natlinkutils import GrammarBase

class ThisGrammar(GrammarBase):

    gramSpec = """
        <runsimplezero> exported = mimic runzero;
        <runsimpleone> exported = mimic (north | east | south | west) ;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

    def gotResults_runsimplezero(self,words,fullResults):
        print(f'Heard macro "mimic runsimplezero", "{words}"')
    def gotResults_runsimpleone(self,words,fullResults):
        print(f'Heard macro "mimic runsimpleone", "{words}"')
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None
