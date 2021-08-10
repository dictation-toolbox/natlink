#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _globals.py
#   Sample macro file which is active all the time (not application specific).
#
# April 25, 1999
#   - packaged for external release
#
# March 3, 1999
#   - initial version
#

############################################################################
#
# This is a sample grammar file.  I have implemented some basic global
# commands for example purposes.
#
# This file is loaded automatically when the Python subsystem starts because
# its filename begins with an underscore (the signal for a global module).
#
# Please see the example wordpad.py for more comments.
# 

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    # We create a simple grammar to illustrate a couple of basic ideas.
    # You can say "Python microphone off" or "Python go to sleep" which
    # have exactly the same effect as "microphone off" and "go to sleep".
    #
    # You can also say "Python stop listening" which simulates sleeping
    # by putting the system into a state where the only thing which will
    # be recognized is "Python start listening"

    testGram = """
        <micOff> = Python microphone off;
        <sleep> = Python go to sleep;
        <stop> = Python stop listening;
        <notListening> exported = Python start listening;
        <normalState> exported = <micOff> | <sleep> | <stop>;
    """
    
    # Load the grammar and activate the rule "normalState".  We use 
    # activateSet instead of activate because activateSet is an efficient
    # way of saying "deactivateAll" then "activate(xxx)" for every xxx
    # in the array.  

    def initialize(self):
        self.load(self.testGram)
        self.activateSet(['normalState'])
        self.setExclusive(0)

    # When words are recognized from the rule "micOff", this function gets
    # called.  We turn the microphone off.

    def gotResults_micOff(self,words,fullResults):
        natlink.setMicState('off')
        
    # When words are recognized from the rule "sleep", this function gets
    # called.  We put the microphone in the speeling state.  This will 
    # cause the built-in NatSpeak global commands module to activate a
    # special "wake-up" state in exclusive mode.  We have no control
    # over this (although we could activate our own exclusive rule at the
    # same time).

    def gotResults_sleep(self,words,fullResults):
        natlink.setMicState('sleeping')

    # For the rule "stop", we activate the "notListening" rule which 
    # contains only one subrule.  We also force exclusive state for this
    # grammar which turns off all other non-exclusive grammar in the system.

    def gotResults_stop(self,words,fullResults):
        self.activateSet(['notListening'],exclusive=1)

    # When we get "start listening", restore the default state of this
    # grammar.

    def gotResults_notListening(self,words,fullResults):
        self.activateSet(['normalState'],exclusive=0)

#
# Here is the initialization and termination code.  See wordpad.py for more
# comments.
#

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
