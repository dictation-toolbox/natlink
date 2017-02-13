#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _samplehypothesis.py
#
# This is an example showing the gotHypothesis feature
# Quintijn Hoogenboom, q.hoogenboom@antenna.nl, november 2016
#
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):
 
    gramSpec = """
        <dummy> exported = demo gothypothesis;
    """
    def initialize(self):
        self.load(self.gramSpec, hypothesis=1, allResults=1)
        self.activateAll()
    def gotResults_dummy(self,words,fullResults):
        print 'got the dummy rule of gotHypothesis'
                           
    def gotBegin(self,moduleInfo):
        print '_samplehypothesis, starting new recognition'

    def gotHypothesis(self, words):
        """display the words when a hypothesis is called back happens
        """
        print 'hypothesis: %s'% words

    def gotResultsObject(self,recogType,resObj):
        try:
            words = resObj.getWords(0)
        except (natlink.OutOfRange, IndexError):
                words = "<???>"
        print '---result: %s'% words

thisGrammar = ThisGrammar()
thisGrammar.initialize()
def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
