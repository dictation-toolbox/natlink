#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This grammar is plain natlink, after example excel_sample7 from Joel Gould
# adapted for word styles by Quintijn Hoogenboom (23/10/2008), for comparison with
# Dragonfly example...
#
# See also the variant winword_styles_unimacro.py in the folder DisabledGrammars of Unimacro

import natlink
from natlinkutils import *

import win32api
import win32com.client
consts = win32com.client.constants

class ThisGrammar(GrammarBase):

    gramSpec = """
        <showStyles> exported = show styles;
        <updateStyles> exported = update styles;
        <setStyle> exported = set style {style};
    """

    def initialize(self):
        self.load(self.gramSpec)
        self.application = None
        self.activated = None
        self.styles = []
        self.prevInfo = None

    def gotBegin(self,moduleInfo):
        """this method is performed at each utterance,
        whether in word or elsewhere. Therefore it has to be quick
        """
        if self.prevInfo == moduleInfo:
            # same instance, same window title, do nothing, quit quick!
            return
##        print 'gotBegin, new moduleInfo %s'% `moduleInfo`
        self.prevInfo = moduleInfo
        winHandle = matchWindow(moduleInfo,'winword','Microsoft Word')
        if winHandle:
            # if you have multiple word instances, you have to change the activated rules
            # if you go from one to another.
            if not self.application:
                self.application=win32com.client.Dispatch('Word.Application')
            if self.activated:
                if winHandle != self.activated:
                    print(('DEactivate for previous %s'% self.activated))
                    self.deactivateAll()
                    self.activated = None
            if not self.activated:
                print(('activate for %s'% winHandle))
                self.activateAll(window=winHandle)
                self.activated = winHandle
        else:
            winHandle = matchWindow(moduleInfo,'winword','')
            if not winHandle:
                print('other application, release word')
                if self.application:
                    self.application = None
            # outside an interesting window so:
            return
        
        # new modInfo, possibly a new document in front:
        print('update styles')
        self.updateStyles()
##        print 'self.styles: %s'% self.styles.keys()
            
    def updateStyles(self):
        """update the styles list, either from gotBegin or from a spoken command"""
        if self.application:
            document = self.application.ActiveDocument
            style_map = [(str(s), s) for s in  document.Styles]
            self.styles = dict(style_map)
            self.setList('style', list(self.styles.keys()))
        else:
            print(('no word application loaded... %s'% self.application))

    def gotResults_updateStyles(self, words, fullResults):
        """possibility to "manually" update the styles list"""
        self.updateStyles()

    def gotResults_showStyles(self, words, fullResults):
        """print a list of all valid styles in the messages window"""
        if self.styles:
            print(('styles in use: %s'% list(self.styles.keys())))
        else:
            print('no styles in use...')

    def gotResults_setStyle(self, words, fullResults):
        """apply a style to the cursor or selection"""
        style = words[-1]
        if style in self.styles:
            print(('setting style %s'% style))
            sel = self.application.Selection
            sel.Style = style
        else:
            print(('style not in stylelist: %s'% style))
            
# standard stuff:
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
