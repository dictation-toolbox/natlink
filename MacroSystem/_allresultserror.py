__version__ = "$Revision: 337 $, $Date: 2010-12-23 17:32:41 +0100 (do, 23 dec 2010) $, $Author: quintijn $"
# Quintijn Hoogenboom, December 2010
"""Grammar that shows error of load with allResults flag and os.startsfile

"""

import string, os, sys, re, time
import natlink
#natbj = __import__('natlinkutilsbj')
natut = __import__('natlinkutils')
#natqh = __import__('natlinkutilsqh')
#import actions


### change here:
testfile = r'C:\temp\test.txt'
allresultsflag = 1

###


ancestor = natut.GrammarBase
class UtilGrammar(ancestor):
    name = 'all results error'
    gramSpec = """
<testing> exported = testing all results error;
<startfile> exported = testing startfile;
    """

    def initialize(self):
        # with allResults gives error after you call "open file with startfile"
        if allresultsflag:
            print 'loading/activating allresultserror grammar WITH flag: %s (test should crash NatSpeak)'% allresultsflag
            print 'the command that crashed is "edit commands" of Vocola'
            self.load(self.gramSpec, allResults=allresultsflag)
        else:
            print 'loading/activating allresultserror grammar WITHOUT flag, test should run without crash'
            print 'Try the command "edit commands" of Vocola'
            self.load(self.gramSpec)
        #print 'activate rules of test grammar "all results error"'
        self.activateAll()
        
    def gotBegin(self, moduleInfo):
        pass

    def gotResults_testing(self, words, fullResults):
        print 'got test rule "all results error"!!'

    def gotResults_startfile(self, words, fullResults):
        print 'got test rule "startfile", open after 1 second!!'
        time.sleep(1)
        os.startfile(testfile)


# standard stuff Joel (adapted for possible empty gramSpec, QH, unimacro)
utilGrammar = UtilGrammar()
if utilGrammar.gramSpec:
    print 'loading all results bug grammar'
    utilGrammar.initialize()

def unload():
    global utilGrammar #, messageDictGrammar
    if utilGrammar: utilGrammar.unload()
    utilGrammar = None
