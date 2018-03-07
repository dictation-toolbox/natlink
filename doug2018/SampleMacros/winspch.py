#
# This is a sample of adding grammar based speech recognition to a simple
# Python application written using the Python win32 libraries.
#

import sys
import string

# Pythonwin imports
from pywin.mfc import dialog
import win32ui
import win32api
import win32con

# Speech imports
import natlink
from natlinkutils import *

#---------------------------------------------------------------------------
#
# This code describes the dialog box.  I cheated when I created the dialog.
# I created the dialog box using Visual C++ so that I could use a graphical
# layout tool.  Then I copied the resource file information here.  The format
# of the text in the template was determined by looking at the pythonwin
# sample applications.
#

IDC_EDIT=1000
IDC_PRESS=1001
IDC_CLICK=1002
IDC_MIC=1003
IDC_NOTHING=1004
IDC_SPEECH=1005

def MakeDlgTemplate():
    style = win32con.DS_MODALFRAME | win32con.WS_POPUP | win32con.WS_VISIBLE | win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.DS_SETFONT
    child = win32con.WS_CHILD | win32con.WS_VISIBLE
    templ = [
        ["Sample Dialog",(0, 0, 264, 165),style,None,(8, "MS Sans Serif")],
        [130,"You can speak the names of any of the buttons, or a number less than 1 billion.",
                    -1,(7,7,249,8),child|win32con.SS_LEFT],
        [128,"&Press Me",IDC_PRESS,(7,21,60,14),child|win32con.BS_PUSHBUTTON|win32con.WS_TABSTOP],
        [128,"&Click This Button",IDC_CLICK,(74,41,66,10),child|win32con.BS_AUTOCHECKBOX|win32con.WS_TABSTOP],
        [128,"&Turn Mic On",IDC_MIC,(193,21,64,14),child|win32con.BS_PUSHBUTTON|win32con.WS_TABSTOP],
        [128,"&Do Nothing",IDC_NOTHING,(74,21,60,14),child|win32con.BS_PUSHBUTTON|win32con.WS_TABSTOP],
        [128,"&Speech Works",IDC_SPEECH,(7,38,60,14),child|win32con.BS_PUSHBUTTON|win32con.WS_TABSTOP],
        [128,"Close &Window",win32con.IDCANCEL,(193,39,64,14),child|win32con.BS_PUSHBUTTON|win32con.WS_TABSTOP],
        [130,"Messages show up here:",-1,(7,60,80,8),child|win32con.SS_LEFT],
        [129,"",IDC_EDIT,(7,72,250,85),child|win32con.ES_MULTILINE|win32con.WS_BORDER|
                    win32con.ES_AUTOVSCROLL|win32con.WS_VSCROLL],
      ]
    return templ

#---------------------------------------------------------------------------
#
# This is the grammar.  It handles all recognition and prints messages when
# anything is recognized.
#

class TestGrammar(GrammarBase):

    # First we list our grammar as a long string.  The grammar is in SAPI
    # format, where we define a series of rules as expressions built from
    # other rules, words and lists.  Rules which can be activated are flagged
    # with the keyword "exported".
    #
    # Our grammar lets us say the name of any button or any number less then
    # 1 billion.  The number grammar was included as an example of a complex
    # grammar while the button grammar is very simple.

    gramSpec = """
        <1to99> = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
                 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 |
            10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
            20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
            30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 |
            40 | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 |
            50 | 51 | 52 | 53 | 54 | 55 | 56 | 57 | 58 | 59 |
            60 | 61 | 62 | 63 | 64 | 65 | 66 | 67 | 68 | 69 |
            70 | 71 | 72 | 73 | 74 | 75 | 76 | 77 | 78 | 79 |
            80 | 81 | 82 | 83 | 84 | 85 | 86 | 87 | 88 | 89 |
            90 | 91 | 92 | 93 | 94 | 95 | 96 | 97 | 98 | 99;
                        
        <1to999> =  <1to99> |
            ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 ) hundred [ [and] <1to99> ];

        <number> = 0 | <1to999> [ 
            thousand [ [and] <1to999> ] |
            million [ [and] <1to999> [ thousand [ [and] <1to999> ] ] ] 
          ];

        <button> = press me | speech works | do nothing | click this button |
            turn mic off | close window;

        <start> exported = <number> | <button>;
    """

    # Call this function to load the grammar, activate it and install 
    # install callback functions

    def initialize(self,dlg):
        self.dlg = dlg
        self.load(self.gramSpec)
        self.activateAll(window=dlg.GetSafeHwnd())
    
    # Call this function to cleanup.  We have to reset the callback
    # functions or the object will not be freed.

    def terminate(self):
        self.dlg = None
        self.unload()

    # This routine is called from GrammarBase for any recognition.  We use
    # it to type a message

    def gotResultsInit(self,words,fullResults):
        print(('Got recognition:', string.join(words)))
        self.digits = 0
        self.hundreds = 0
        self.number = 0
        self.sawNumber = 0

    # This routine is called from GrammarBase when words are recognized
    # from the rule 'button'.  We lookup what was recognized in a dictionary
    # and type the indicated keystrokes.

    def gotResults_button(self,words,fullResults):
        action = {
            'press me':'{alt+p}',
            'speech works':'{alt+s}',
            'do nothing':'{alt+d}',
            'click this button':'{alt+c}',
            'turn mic off':'{alt+t}',
            'close window':'{alt+w}' }
        natlink.playString(action[string.join(words)])

    # These callbacks are made when the recognition results contain contiguous
    # sequenes of words from the corresponding state.  We use this information
    # to parse the results into some member veriables

    def gotResults_1to99(self,words,fullResults):
        self.sawNumber = 1
        self.digits = string.atoi(words[0])

    def gotResults_1to999(self,words,fullResults):
        self.sawNumber = 1
        self.hundreds = string.atoi(words[0])

    def gotResults_number(self,words,fullResults):
        self.sawNumber = 1
        temp = self.digits + self.hundreds * 100
        self.digits = 0
        self.hundreds = 0
        if words[0] == 'thousand':
            self.number = self.number + 1000 * temp
        elif words[0] == 'million':
            self.number = self.number + 1000000 * temp
        elif words[0] != '0':
            raise ValueError("Unexpected recognition results")

    # This callback is made at the end of results processing.  Here we 
    # finish the number formatting and print the results

    def gotResults(self,words,fullResults):
        if not self.sawNumber: return None
        self.number = self.number + self.digits + self.hundreds * 100
        print(('Resulting number is %d' % self.number))

#---------------------------------------------------------------------------
#
# This is the dialog box itself.  It does the following:
#   (1) remaps sysout so all 'print' statements appear in the window
#   (2) prints a message when any button is pressed
#   (3) creates a grammar to handle the recognition
#   (4) installs callback which detect when the microphone changes state
#

class TestDialog(dialog.Dialog):

    def OnInitDialog(self):
        rc = dialog.Dialog.OnInitDialog(self)
        self.HookCommand(self.onButton,IDC_PRESS)
        self.HookCommand(self.onButton,IDC_CLICK)
        self.HookCommand(self.onButton,IDC_SPEECH)
        self.HookCommand(self.onButton,IDC_NOTHING)
        self.HookCommand(self.onMic,IDC_MIC)
        self.oldStdout = sys.stdout
        sys.stdout = self
        self.message = ''
        self.grammar = TestGrammar()
        self.grammar.initialize(self)
        natlink.setChangeCallback(self.changeCallback)

    # When the dialog is closed, make sure we delete the grammar and reset the
    # callbacks

    def OnDestroy(self,msg):
        natlink.setChangeCallback(None)
        self.grammar.terminate()
        self.grammar = None
        sys.stdout = self.oldStdout

    # This function is called when a change occurs in NatSpeak.  We log the
    # change and if the microphone changes state then we update the interface.

    def changeCallback(self,what,param):
        if what == 'user':
            print(('User changed.  New user is', param[0]))
        elif what == 'mic':
            print(('Microphone state changed.  New state is', param))
            if param == 'on' or param == 'sleeping':
                self.SetDlgItemText(IDC_MIC,'&Turn Mic Off')
            else:
                self.SetDlgItemText(IDC_MIC,'&Turn Mic On')

    # Called when any button except IDC_MIC is pressed

    def onButton(self,nID,code):
        text = { IDC_PRESS:'Press Me',
                 IDC_CLICK:'Click This Button',
                 IDC_SPEECH:'Speech Works',
                 IDC_NOTHING:'Do Nothing' }
        print(('Button click:', text[nID]))

    # Special code for the microphone button.  We turn the microphone on or
    # off depending on its current state.  We do not update the button text
    # here.  That is done when we get the callback that the microphone has
    # changed state.

    def onMic(self,nID,code):
        micState = natlink.getMicState()
        if micState == 'on' or micState == 'sleeping':
            print('Button click: Turn Mic Off')
            natlink.setMicState('off')
        else:
            print('Button click: Turn Mic On')
            natlink.setMicState('on')

    # This function is called when we print. It puts the string in the
    # edit control instead of the standard sysout and scrolls the edit
    # control to the bottom

    def write(self,text):
        self.message = self.message + string.replace(text,'\n','\r\n')
        self.SetDlgItemText(IDC_EDIT,self.message)
        self.GetDlgItem(IDC_EDIT).SendMessage(win32con.EM_SETSEL,0x7FFF,0x7FFF)
        self.GetDlgItem(IDC_EDIT).SendMessage(win32con.EM_SCROLLCARET,0,0)
          
#---------------------------------------------------------------------------
#
# This is the main routine.  Here we connect to the speech subsystem,
# create the dialog box and when the dialog is closed, disconnect from
# the speech subsystem.
#

def run():
    natlink.natConnect(1)
    TestDialog(MakeDlgTemplate()).DoModal()
    natlink.natDisconnect()

if __name__=='__main__':
    run()
