#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# _sample5.py
#
# This sample file demonstrates how to use the clipboard to communicate
# between your application and Python code.  To use this macro, make sure
# that NatSpeak is active and that there is text in the window.  Position
# the caret inside a word on the screen and say "demo sample five".  This
# code will then reverse the letters in the word containing the caret.
#
# You can say "demo sample five 3 words" and this code will reverse three
# words ending with the word which contains the caret.
#
# Notice that we send keystrokes to select the words in NatSpeak.  Then we
# send the keystroke ctrl+c to copy the selected word to the clipboard.  The
# function natlink.getClipboard() give this code access to the clipboard. We
# reverse the text and send it back to the application (by typing it).
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = demo sample five
            [ (1 | 2 | 3 | 4) words ];
    """

    def gotResults_start(self,words,fullResults):
        # figure out how many words
        if len(words) > 3:
            count = int(words[3])
        else:
            count = 1
        # select that many words
        natlink.playString('{ctrl+right}{left}')
        natlink.playString('{ctrl+shift+left %d}'%count)
        natlink.playString('{ctrl+c}')
        text = natlink.getClipboard()
        # reverse the text
        newText = reverse(text)
        natlink.playString(newText)
        
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

def reverse(text):
    newText = ''
    for char in text:
        newText = char + newText
    return newText

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
