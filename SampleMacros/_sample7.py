#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created 2020-02-01 by Quintijn Hoogenboom
# It does the same as _sample2, but now with a list of colors
#
# _sample7.py
#
# This is more a manual test, to see if various list and optional rules work.
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <runone> exported = mimic runone;
        <runtwo> exported = mimic two {colors};
        <runfour> exported = mimic four <extraword> [{colors}]+;
        <runsix> exported = mimic six {colors}+;
        <runseven> exported = mimic seven <wordsalternatives>;
        <runeight> exported = mimic eight <wordsalternatives>+;
        <extraword> = painting ;
        <wordsalternatives> = house | tent | church | tower;
    """       
    def initialize(self):
        self.load(self.gramSpec)
        self.setList('colors', ['red', 'blue', 'green', 'purple', 'white', 'yellow', 'orange', 'magenta', 'cyan', 'gray'])
        self.activateAll()

    def gotResultsObject(self, recogType, resObj):
        print('sample 7, got: %s'% resObj.getWords(0))

thisGrammar = ThisGrammar()
thisGrammar.initialize()



def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
