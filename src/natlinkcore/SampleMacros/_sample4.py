#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _sample4.py
#   Sample macro file d\xe9mostrating mouse movement.
#
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.
#
import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = d\xe9mo sample four;
    """

    def gotResults_start(self,words,fullResults):
        # execute a control-left drag down 30 pixels
        x,y = natlink.getCursorPos()
        natlink.playEvents( [ (wm_keydown,vk_control,1),
                              (wm_lbuttondown,x,y),
                              (wm_mousemove,x,y+30),
                              (wm_lbuttonup,x,y+30),
                              (wm_keyup,vk_control,1) ] )
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
