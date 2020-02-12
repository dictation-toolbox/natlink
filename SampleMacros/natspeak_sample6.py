#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# natspeak_sample6.py
#
# This macro file d\xe9monstrates how to write application specific code.  We
# define two commands.  "d\xe9mo sample six" can only be spoken to the NatSpeak
# main window.  "d\xe9mo sample six font" can only be spoken to the NatSpeak
# font dialog.  We make the second command exclusive so that all other
# commands are disabled when thefont dialog is active.
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <mainRule> exported = d\xe9mo sample six [ main ];
        <fontRule> exported = d\xe9mo sample six font;
    """

    def gotBegin(self,moduleInfo):
        windowId = matchWindow(moduleInfo,'natspeak','Dragon')
        if windowId:
            self.activate('mainRule',window=windowId,noError=1)
        windowId = matchWindow(moduleInfo,'natspeak','Font')
        if windowId:
            self.activate('fontRule',exclusive=1,noError=1)
        else:
            self.deactivate('fontRule',noError=1)
            self.setExclusive(0)
        
    def initialize(self):
        self.load(self.gramSpec)

    def gotResults_mainRule(self,words,fullResults):
        natlink.playString('Saw <mainRule>')

    def gotResults_fontRule(self,words,fullResults):
        natlink.playString('Saw <fontRule>')

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
