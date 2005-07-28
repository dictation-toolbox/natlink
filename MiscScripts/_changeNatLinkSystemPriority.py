#
#(c) 2005 Scott Weinstein, Applied Recognition Inc.
#
import natlink
from natlinkutils import *
import win32process

class ThisGrammar(GrammarBase):
    priorityMap = {
                    "Real":win32process.REALTIME_PRIORITY_CLASS,
                    "High":win32process.HIGH_PRIORITY_CLASS,
                    "Low":win32process.BELOW_NORMAL_PRIORITY_CLASS,
                    "Normal":win32process.NORMAL_PRIORITY_CLASS,
                };
    gramSpec = """
        <change> exported = change NatLink priority to
            ( Real Time | High | Low  | Normal);
    """

    def gotResults_change(self,words,fullResults):
        if self.priorityMap.has_key(words[4]):
            p=self.priorityMap[words[4]]
            res=win32process.SetPriorityClass(win32process.GetCurrentProcess(),p)

    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()
thisGrammar = ThisGrammar()
thisGrammar.initialize()
def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
