#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 2000 by Joel Gould
#   Portions (c) Copyright 2000 by Dragon Systems, Inc.
#
# <dgletters> does not work any more (2020)
# Put in MacroSystem folder and toggle the microphone.
# Write "d\xe9mo" to force command recognition.

#

import natlink
from natlinkcore.natlinkutils import *
from natlinkcore import nsformat

class ThisGrammar(GrammarBase):

    gramSpec = """
        <dgndictation> imported;
        <dgnletters> imported;
        <ruleOne> exported = d\xe9mo sample eight <dgndictation> ([stop]|[copy (that|line|all)]);
        <ruleTwo> exported = d\xe9mo sample eight spell <dgnletters> ([stop]|[copy (that|line|all)]);
    """
#Dgn dictation this is a test stop and I continue this is a test
    def gotResults_dgndictation(self,words,fullResults):
        """format the words with nsformat and print.
        
        With more commands in succession, the lastState is used to fix spacing and capitalization of words.
        """
        formatted_words, self.lastState = nsformat.formatWords(words, self.lastState)
        # text = ' '.join(words)
        self.lenOfWords = len(formatted_words)
        natlink.playString(formatted_words)

    def gotResults_dgnletters(self,words,fullResults):
        """the formatting is also done via nsformat
        
           but... the "commented out" trick works in practice equally well.
        """
        print(f'words for dgnletters: {words}')
        # words = map(lambda x: x[:1], words)
        # text = ''.join(words)
        letters = nsformat.formatLetters(words)
        self.lenOfWords = len(letters)
        natlink.playString(letters)


    def gotResults_ruleOne(self,words,fullResults):
        """do an action if words at end of command are caught
        """
        print(f'words for ruleOne: {words}')
        if words[0] != 'copy':
            self.copyThings(which=words[-1])

           
    def gotResults_ruleTwo(self,words,fullResults):
        """this is to catch the fixed words of ruleTwo
        """
        print(f'words for ruleTwo: {words}')
        if words[0] != 'copy':
            self.copyThings(which=words[-1])

    def copyThings(self, which):
        """copy last, line or all
        """ 
        if which == 'line':
            sendkeys('{home}{ctrl+c}')
         

    def initialize(self):
        self.lastState = None
        self.lenOfWords = 0
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
