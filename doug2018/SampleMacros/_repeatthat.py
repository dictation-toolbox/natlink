#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 2000 by Joel Gould
#
# This is the implementation of "repeat that".  In this implementation, you
# can say "repeat that" or "repeat that N times" to repeat the last
# recognition.
# 

import natlink
from natlinkutils import *

lastResult = None

class CatchAllGrammar(GrammarBase):

    gramSpec = """
        <start> exported = {emptyList};
    """

    def initialize(self):
        self.load(self.gramSpec,allResults=1)
        self.activateAll()

    def gotResultsObject(self,recogType,resObj):
        global lastResult
        if recogType == 'reject':
            lastResult = None
        elif resObj.getWords(0)[:2] != ['repeat','that']:
            lastResult = resObj.getWords(0)
            
class RepeatGrammar(GrammarBase):

    gramSpec = """
        <start> exported = repeat that
          [ ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
              10 | 20 | 30 | 40 | 50 | 100 ) times ];
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

    def gotResults_start(self,words,fullResults):
        global lastResult
        if len(words) > 2:
            count = int(words[2])
        else:
            count = 1
        if lastResult:
            for i in range(count):
                natlink.recognitionMimic(lastResult)

catchAllGrammar = CatchAllGrammar()
catchAllGrammar.initialize()
repeatGrammar = RepeatGrammar()
repeatGrammar.initialize()

def unload():
    global catchAllGrammar
    global repeatGrammar
    if catchAllGrammar:
        catchAllGrammar.unload()
    catchAllGrammar = None
    if repeatGrammar:
        repeatGrammar.unload()
    repeatGrammar = None
