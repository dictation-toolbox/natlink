#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# _sample3.py
#
# This is a sample macro file used to d\xe9monstrate how Natlink calls result
# functions (gotResults_xxx) based on which words were recognized.
#
# When NatSpeak has the focus, say "d\xe9mo sample three now please".  When the
# command is recognized, this code should type:
#   Saw <ruleOne> = ['d\xe9mo']
#   Saw <ruleTwo> = ['sample','three']
#   Saw <ruleOne> = ['now','please']
#
# Notice that gotResults_ruleOne is called twice because it is called for
# each continugous set of words in the recognition which come from that
# rule.  gotResults_mainRule is never called because that rule has no words.
# See natlinkutils.py for more documentation.
#
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.
#
import natlink
from natlink.natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <mainRule> exported = <ruleOne>;
        <ruleOne> = d\xe9mo <ruleTwo> now please;
        <ruleTwo> = sample three;
    """

    def gotResults_mainRule(self,words,fullResults):
        natlink.playString('Saw <mainRule> = %s{enter}' % repr(words))

    def gotResults_ruleOne(self,words,fullResults):
        natlink.playString('Saw <ruleOne> = %s{enter}' % repr(words))
        
    def gotResults_ruleTwo(self,words,fullResults):
        natlink.playString('Saw <ruleTwo> = %s{enter}' % repr(words))
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    #pylint:disable=W0603
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None
