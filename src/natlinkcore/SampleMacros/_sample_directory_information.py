# Python Macro Language for Dragon NaturallySpeaking
#     (c) Copyright 1999 by Joel Gould
#     Portions (c) Copyright 1999 by Dragon Systems, Inc.
"""
    _sample_directory_information.py

    This is a sample macro file with a single command.  When NatSpeak has the
    focus, say "demo directory information".
    It should give inside information about the NatlinkDirectory etc.
"""
#pylint:disable=C0116, C0115, W0613
import natlink
import natlinkcore
from natlinkcore import natlinkstatus
from natlinkcore.natlinkutils import GrammarBase
status = natlinkstatus.NatlinkStatus()

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = sample directory (info|information);
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

    def gotResults_start(self, words, fullResults):
        #pylint:disable=R0201
        natlink.displayText('\nHeard macro "sample directory (info|information)"\n\n',0)
        language = status.get_language()
        print(f'Language is: {language}')
        print(f'NatlinkDirectory from status (natlinkstatus): {status.getNatlinkDirectory()}')
        # obsolete:
        # print(f'NatlinkUserDirectory from natlinkcore: {natlinkcore.getNatlinkUserDirectory()}')
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603, C0321
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
