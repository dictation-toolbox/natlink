#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# windict.py
#
# This is a sample Python program which demonstrates how to use the
# NatLink dictation object in a Python program.  The user interface for
# this programn is based on the PythonWin (win32) extensions.
#
# The basic idea is as follows.
#
# Dragon NaturallySpeaking handles dictation by having a dictation object
# which contains a copy oft he user document.  In this way, NatSpeak knows
# what text is on the screen so it can get the spacing write.  It also
# knows the text on the screen for the Select and Correct commands.
#
# When writing an application which supports dictation (and voice editing),
# the application must keep the contents of the NatSpeak dictation object in
# sync with the text on the screen.
#
# In this sample application, we illustrate doing this for a rich edit
# control.  There will be a rich edit contorl on the screen and we keep its
# contents synchronized with a NatSpeak dictation object.  Thus, our simple
# edit control will allow our window to behave like NatSpeak's own editor
# window (althoug hnot every feature is exposed).
#
# For correctness, you only have to intercept the "begin" callback which
# happens just before recognition starts.  At that point you have to make
# sure that the internal dictation object has a complete copy of the state
# of the edit control -- text, selection and visible range.  Then when
# recognition occurs, the dictation object will return information about
# what change happened --- text deleted, text added and selection moved.
#
# To optimize for better performance and to prevent the lose of recorded
# speech, it helps if the code doe snot wait until the tsart of recognition,
# but instead updates the dictation object after every change of the edit
# control.
#
# The best implementation only tells the dictation object aboiut the change
# (for example a character was typed), but in this code I update the
# dictation object with the entire contents of the edit control on every
# keystroke.
#

import sys
import string

# Pythonwin imports
from pywin.mfc import dialog
import win32ui
import win32api
import win32con
import win32gui

# Speech imports
import natlink
from natlinkutils import *

#---------------------------------------------------------------------------
# This code describes the dialog box.  I cheated when I created the dialog.
# I created the dialog box using Visual C++ so that I could use a graphical
# layout tool.  Then I copied the resource file information here.  The
# format of the text in the template was determined by looking at the
# pythonwin sample applications.
#

IDC_EDIT = 1000
IDC_MICBUTTON = 1001

def MakeDlgTemplate():
    style = win32con.DS_MODALFRAME|win32con.WS_POPUP|win32con.WS_VISIBLE|win32con.WS_CAPTION|win32con.WS_SYSMENU
    child = win32con.WS_CHILD|win32con.WS_VISIBLE
    templ = [
        ["Correction Test Window",(0, 0, 320, 197),style,None,(8,"MS Sans Serif")],
        ["RICHEDIT","",IDC_EDIT,(7,7,306,167),child|win32con.ES_MULTILINE|win32con.ES_AUTOVSCROLL|win32con.ES_WANTRETURN|win32con.WS_BORDER|win32con.WS_VSCROLL|win32con.WS_TABSTOP],
        [128,"Turn &Mic On",IDC_MICBUTTON,(244,176,65,14),child],
    ]
    return templ

#---------------------------------------------------------------------------
# Command grammar
#
# I have included a very simple command grammar sonsisting of one command
# "delete that" as an example.  The command grammar can be easily extended.

class CommandGrammar(GrammarBase):

    # First we list our grammar as a long string.  The grammar is in SAPI
    # format, where we define a series of rules as expressions built from
    # other rules, words and lists.  Rules which can be activated are flagged
    # with the keyword "exported".

    gramSpec = """
        <DeleteThat> exported = delete that;
    """

    # Call this function to load the grammar, activate it and install
    # install callback functions
    
    def initialize(self,dlg):
        self.dlg = dlg
        self.load(self.gramSpec)
        self.activateAll(dlg.GetSafeHwnd())
    
    # Call this function to cleanup.  We have to reset the callback
    # functions or the object will not be freed.

    def terminate(self):
        self.dlg = None
        self.unload()

    # This routine is called from GrammarBase when words are recognized from
    # the rule 'DeleteThat'.  We pass the recognition information directly
    # to the dialog box code.
        
    def gotResults_DeleteThat(self,words,fullResults):
        self.dlg.onCommand_DeleteThat(words)

#---------------------------------------------------------------------------
# VoiceDictation client
#
# This class provides a way of encapsulating the voice dictation (DictObj)
# of NatLink.  We can not derive a class from DictObj because DictObj is an
# exporeted C class, not a Python class.  But we can create a class which
# references a DictObj instance and makes it lkook like the class was
# inherited from DictObj.        

class VoiceDictation:

    def __init__(self):
        self.dictObj = None

    # Initialization.  Create a DictObj instance and activate it for the
    # dialog box window.  All callbacks from the DictObj instance will go
    # directly to the dialog box.

    def initialize(self,dlg):
        self.dlg = dlg
        self.dictObj = natlink.DictObj()
        self.dictObj.setBeginCallback(dlg.onTextBegin)
        self.dictObj.setChangeCallback(dlg.onTextChange)
        self.dictObj.activate(dlg.GetSafeHwnd())

    # Call this function to cleanup.  We have to reset the callback
    # functions or the object will not be freed.
        
    def terminate(self):
        self.dictObj.deactivate()
        self.dictObj.setBeginCallback(None)
        self.dictObj.setChangeCallback(None)
        self.dictObj = None

    # This makes it possible to access the member functions of the DictObj
    # directly as member functions of this class.
        
    def __getattr__(self,attr):
        try:
            if attr != '__dict__':
                dictObj = self.__dict__['dictObj']
                if dictObj is not None:
                    return getattr(dictObj,attr)
        except KeyError:
            pass
        raise AttributeError(attr)

#---------------------------------------------------------------------------
# Dialog box

class TestDialog(dialog.Dialog):

    # Dialog initialization.  Tell the rich text control to send us change
    # messages, install callbacks for buttons and initialize the command and
    # dictation objects.
    def OnInitDialog(self):
        rc = dialog.Dialog.OnInitDialog(self)
        self.HookCommand(self.onMicButton,IDC_MICBUTTON)
        self.HookCommand(self.onNotify,IDC_EDIT)
        self.edit = self.GetDlgItem(IDC_EDIT)
        self.edit.SetEventMask(win32con.ENM_CHANGE)
        self.grammar = CommandGrammar()
        self.grammar.initialize(self)
        self.dictObj = VoiceDictation()
        self.dictObj.initialize(self)

    # When the dialog is closed, make sure we delete the grammar and
    # dictation objects so the callbacks are reset
        
    def OnDestroy(self,msg):
        self.grammar.terminate()
        self.grammar = None
        self.dictObj.terminate()
        self.dictObj = None

    # This subroutine transfers the contents and state of the edit control
    # into the dictation object.  We currently don't bother to indicate
    # exactly what changed.  The dictation object will compare the text we
    # write with the contents of its buffer and only make the necessary
    # changes (as long as on one contigious region has changed).
        
    def updateState(self):
        text = self.edit.GetWindowText()
        selStart,selEnd = self.edit.GetSel()
        visStart,visEnd = self.getVisibleRegion()

        self.dictObj.setLock(1)
        self.dictObj.setText(text,0,0x7FFFFFFF)
        self.dictObj.setTextSel(selStart,selEnd)
        self.dictObj.setVisibleText(visStart,visEnd)
        self.dictObj.setLock(0)

    # Utility subroutine which calculates the visible region of the edit
    # control and returns the start and end of the current visible region.
        
    def getVisibleRegion(self):
        top,bottom,left,right = self.edit.GetClientRect()
        firstLine = self.edit.GetFirstVisibleLine()
        visStart = self.edit.LineIndex(firstLine)

        lineCount = self.edit.GetLineCount()
        lastLine = lineCount
        for line in range(firstLine+1,lineCount):
            charInLine = self.edit.LineIndex(line)
            left,top = self.edit.GetCharPos(charInLine)
            if top >= bottom:
                break
            lastLine = line

        visEnd = self.edit.LineIndex(lastLine+1)
        if visEnd == -1:
            visEnd = len(self.edit.GetWindowText())
        return visStart,visEnd
        
    # Special code for the microphone button.  We turn the microphone on or
    # off depending on its current state.

    def onMicButton(self,nID,code):
        micState = natlink.getMicState()
        if micState == 'on' or micState == 'sleeping':
            self.SetDlgItemText(IDC_MICBUTTON,'Turn &Mic On')
            natlink.setMicState('off')
        else:
            self.SetDlgItemText(IDC_MICBUTTON,'Turn &Mic Off')
            natlink.setMicState('on')
        self.edit.SetFocus()

    # When something changes in the edit control (usually because the user
    # is typing), update the dictation object.

    def onNotify(self,controlId,code):
        if code == win32con.EN_CHANGE:
            self.updateState()

    # This routine is invoked when we hear "delete that".  We simply play a
    # delete key.  A more sophisticated algorithm is possible, but I am
    # lazy.

    def onCommand_DeleteThat(self,words):
        natlink.playString('{Del}')

    # We get this callback just before recognition starts. This is our
    # chance to update the dictation object just in case we missed a change
    # made to the edit control.

    def onTextBegin(self,moduleInfo):
        self.updateState()

    # We get this callback when something in the dictation object changes
    # like text is added or something is selected by voice.  We then update
    # the edit control to match the dictation object.

    def onTextChange(self,delStart,delEnd,newText,selStart,selEnd):
        self.dictObj.setLock(1)
        self.edit.SetSel(delStart,delEnd)
        self.edit.ReplaceSel(newText)
        self.edit.SetSel(selStart,selEnd)
        self.dictObj.setLock(0)

#---------------------------------------------------------------------------
# This is the main routine.  Here we connect to the speech subsystem,
# create the dialog box and when the dialog is closed, disconnect from
# the speech subsystem.
#
# If an exception occurs, make sure we disconnect from NatSpeak before
# reporting the exception.

def run():
    try:
        natlink.natConnect(1)
        TestDialog(MakeDlgTemplate()).DoModal()
        natlink.natDisconnect()
    except:
        natlink.natDisconnect()
        raise

if __name__=='__main__':
    run()
