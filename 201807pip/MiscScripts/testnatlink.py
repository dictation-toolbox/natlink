#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# testnatlink.py
#   This script performs some basic tests of the NatLink system.
#    Restart NatSpeak before rerunning this script. This is because the test
#    script will leave some state around which will make it fail if run again
#
#    Do *not* save your speech files after a test
# 
#
# April 16, 2005 - sw
# got many, not all test working w/ v 8
# seach for '#This fails' to find broken tests


# April 1, 2000
#   - added testParser, testGrammar, testDictGram, testSelectGram
#

import sys
import os
import os.path
import time
import string
import traceback        # for printing exceptions
from struct import pack

import natlink
import gramparser
from natlinkutils import *

TestError = 'TestError'
ExitQuietly = 'ExitQuietly'

#---------------------------------------------------------------------------
# These tests should be run after we call natConnect

def	mainTests():
	lookForNatSpeak()
	testPlayString()
	testExecScript()
	testDictObj()
	testWordFuncs()
	testNatLinkMain()
	testWordProns()
	testParser()
	testGrammar()
	testDictGram()
# This fails	testSelectGram()
# This fails	testTrayIcon()
	testNestedMimics()

	# minimize natspeak	which should display the Python	window
	switchToNatSpeak()
	natlink.playString('{Alt+space}n')

def switchToNatSpeak():
    natlink.execScript('HeardWord "Start","DragonPad"')
    time.sleep(1)
#    natlink.execScript('HeardWord "switch","to","DragonPad"')

#---------------------------------------------------------------------------
# These test should be run before we call natConnect

def preTests():
    # make sure that NatSpeak is loaded into memory
    if not natlink.isNatSpeakRunning():
        raise TestError,'NatSpeak is not currently running'

    # these function should all fail before natConnect is called
    testForException( natlink.NatError, "natlink.playString('')" )
    testForException( natlink.NatError, "natlink.getCurrentModule()" )
    testForException( natlink.NatError, "natlink.getCurrentUser()" )
    testForException( natlink.NatError, "natlink.getMicState()" )
    testForException( natlink.NatError, "natlink.setMicState('off')" )
    testForException( natlink.NatError, "natlink.execScript('')" )
    testForException( natlink.NatError, "natlink.recognitionMimic('')" )
    testForException( natlink.NatError, "natlink.playEvents([])" )
    testForException( natlink.NatError, "natlink.inputFromFile('test.wav')" )
    testForException( natlink.NatError, "natlink.setTimerCallback(None)" )
    testForException( natlink.NatError, "natlink.getTrainingMode()" )
    testForException( natlink.NatError, "natlink.startTraining('calibrate')" )
    testForException( natlink.NatError, "natlink.finishTraining()" )
    testForException( natlink.NatError, "natlink.getAllUsers()" )
    testForException( natlink.NatError, "natlink.openUser('testUser')" )
    testForException( natlink.NatError, "natlink.saveUser()" )
    testForException( natlink.NatError, "natlink.getUserTraining()" )
    testForException( natlink.NatError, "natlink.waitForSpeech(0)" )
    testForException( natlink.NatError, "natlink.GramObj().load('')" )
    testForException( natlink.NatError, "natlink.DictObj()" )

    # these functions should all work before natConnect is called
    natlink.displayText('',0)
    natlink.getClipboard()
    natlink.getCallbackDepth()
    natlink.getCursorPos()
    natlink.getScreenSize()
    natlink.setBeginCallback(None)
    natlink.setChangeCallback(None)
    natlink.isNatSpeakRunning()

#---------------------------------------------------------------------------
# These tests should be run after we call natDisconnect

def postTests():
    # make sure that NatSpeak is still loaded into memory
    if not natlink.isNatSpeakRunning():
        raise TestError,'NatSpeak is not currently running'

    # make sure we get exceptions again assessing our functions
    testForException( natlink.NatError, "natlink.playString('')" )
    testForException( natlink.NatError, "natlink.getCurrentModule()" )

#---------------------------------------------------------------------------
# This utility subroutine executes a Python command and makes sure that
# an exception (of the expected type) is raised.  Otherwise a TestError
# exception is raised

def testForException(exceptionType,command,localVars={}):
    try:
        exec(command,globals(),localVars)
    except exceptionType:
        return
    raise TestError,'Expecting an exception to be raised calling '+command

#---------------------------------------------------------------------------
# This utility subroutine will returns the contents of the NatSpeak window as
# a string.  It works by using playString to select the contents of the 
# window and copy it to the clipboard.  We have to also add the character 'x'
# to the end of the window to handle the case that the window is empty.

def getWindowContents():
    natlink.playString('{ctrl+end}x{ctrl+a}{ctrl+c}{ctrl+end}{backspace}')
    contents = natlink.getClipboard()
    if contents == '' or contents[-1:] !='x':
        raise TestError,'Failed to read the contents of the NatSpeak window'
    return contents[:-1]

def testWindowContents(expected,testName):
    contents = getWindowContents()
    if contents != expected:
        raise TestError,'Contents of window did not match expected text, testing '+testName

#---------------------------------------------------------------------------
# Utility function which calls a routine and tests the return value

def testFuncReturn(expected,command,localVars={}):
    actual = eval(command,globals(),localVars)
    if actual != expected:
        raise TestError,"Function call: %s\n  returned: %s\n  expected %s"%(command,repr(actual),repr(expected))

#---------------------------------------------------------------------------
# This types the keysequence {alt+esc}.  Since this is a sequence trapped
# by the OS, we must send as system keys.

def playAltEsc():
    natlink.playString('{alt+esc}',hook_f_systemkeys)

#---------------------------------------------------------------------------

def lookForNatSpeak():

    # This should find the NatSpeak window.  If the NatSpeak window is not
    # available (because, for example, NatSpeak was not started before 
    # running this script) then we will get the error:
    #   NatError: Error 62167 executing script execScript (line 1)

    try:
        natlink.execScript('HeardWord "Start","DragonPad"')
        time.sleep(1)
    except natlink.NatError:
        raise TestError,'The NatSpeak user interface is not running'

    # This will make sure that the NatSpeak window is empty.  If the NatSpeak
    # window is not empty we raise an exception to avoid possibily screwing
    # up the users work.

    switchToNatSpeak()
    if getWindowContents():
        raise TestError,'The NatSpeak window is not empty'

#---------------------------------------------------------------------------
# Note 1: testWindowContents will clobber the clipboard.
# Note 2: a copy/paste of the entire window adds an extra CRLF (\r\n)

def testPlayString():

    # test some obvious error cases
    testForException(TypeError,"natlink.playString()")
    testForException(TypeError,"natlink.playString(1)")
    testForException(TypeError,"natlink.playString('','')")

    natlink.playString('This is a test')
    try:
        testWindowContents('This is a test','playString')
    except KeyboardInterrupt:
        # This failure sometimes happens on Windows 2000
        print
        print '*******'
        print 'One of the NatLink tests has failed.'
        print
        print 'This particular failure has been seen on Windows 2000 when'
        print 'there is a problem switching to Dragon NaturallySpeaking.'
        print
        print 'To fix this:'
        print '(1) Switch to the Dragon NaturallySpeaking window'
        print '(2) Switch back to Python'
        print '(3) Try this selftest again - testnatlink.run()'
        raise ExitQuietly

    natlink.playString('{ctrl+a}{ctrl+c}{end}{ctrl+v}{backspace 9}')
    testWindowContents('This is a testThis i','playString')

    natlink.playString('{ctrl+a}{del}')
    natlink.playString('testing',hook_f_shift)
    testWindowContents('Testing','playString')

    natlink.playString(' again')
    natlink.playString('a{ctrl+c}{del}',hook_f_ctrl)
    natlink.playString('ep',hook_f_alt)
    testWindowContents('Testing again\r\n','playString')

    natlink.playString('a{ctrl+c}{del}',hook_f_rightctrl)
    natlink.playString('ep',hook_f_rightalt)
    natlink.playString('now',hook_f_rightshift)
    testWindowContents('Testing again\r\n\r\nNow','playString')

    natlink.playString('{ctrl+a}{del}')
    natlink.playString('oneWORD ',genkeys_f_uppercase)
    natlink.playString('twoWORDs ',genkeys_f_lowercase)
    natlink.playString('threeWORDs',genkeys_f_capitalize)
    testWindowContents('ONEWORD twowords ThreeWORDs','playString')

    natlink.playString('{ctrl+a}{del}')
    testWindowContents('','playString')

#---------------------------------------------------------------------------

def testExecScript():

    testForException( natlink.SyntaxError, 'natlink.execScript("UnknownCommand")' )

    # TODO this needs more test

#---------------------------------------------------------------------------

def testDictObj():
    dictObj = DictObj()

    #-----
    # test some obvious error cases
    
    testForException(TypeError,"dictObj.activate()",locals())
    testForException(TypeError,"dictObj.activate('')",locals())
    testForException(TypeError,"dictObj.activate(1,2)",locals())
    testForException(TypeError,"dictObj.deactivate(1)",locals())
    testForException(TypeError,"dictObj.setBeginCallback('')",locals())
    testForException(TypeError,"dictObj.setChangeCallback('')",locals())
    testForException(TypeError,"dictObj.setLock()",locals())
    testForException(TypeError,"dictObj.setLock(0,1)",locals())
    testForException(TypeError,"dictObj.setLock('')",locals())
    testForException(TypeError,"dictObj.getLength(1)",locals())
    testForException(TypeError,"dictObj.setText('')",locals())
    testForException(TypeError,"dictObj.setText('','')",locals())
    testForException(TypeError,"dictObj.setText('',0,1,2)",locals())
    testForException(TypeError,"dictObj.getText()",locals())
    testForException(TypeError,"dictObj.getText('')",locals())
    testForException(TypeError,"dictObj.getText(0,1,2)",locals())
    testForException(TypeError,"dictObj.setTextSel()",locals())
    testForException(TypeError,"dictObj.setTextSel('')",locals())
    testForException(TypeError,"dictObj.setTextSel(0,1,2)",locals())
    testForException(TypeError,"dictObj.getTextSel(0)",locals())
    testForException(TypeError,"dictObj.setVisibleText()",locals())
    testForException(TypeError,"dictObj.setVisibleText('')",locals())
    testForException(TypeError,"dictObj.setVisibleText(0,1,2)",locals())
    testForException(TypeError,"dictObj.getVisibleText(0)",locals())

    testForException(natlink.BadWindow,"dictObj.activate(1)",locals())
    testForException(natlink.WrongState,"dictObj.setLock(0)",locals())

    #-----
    # without using dictation, we test the basic operations of the internal
    # buffer
    
    dictObj.setLock(1)
    dictObj.setLock(1)        # locks should nest
    dictObj.setLock(0)
    dictObj.setLock(0)
    testForException(natlink.WrongState,"dictObj.setLock(0)",locals())

    dictObj.deactivate()    # always safe
    
    dictObj.setChangeCallback(None)        # always safe
    dictObj.setBeginCallback(None)        # always safe

    dictObj.setLock(1)

    testFuncReturn(0,"dictObj.getLength()",locals())
    testFuncReturn('',"dictObj.getText(0)",locals())
    testFuncReturn((0,0),"dictObj.getTextSel()",locals())

# This fails
#testFuncReturn((0,0x7FFFFFFF),"dictObj.getVisibleText()",locals())

    dictObj.setText('Testing',0)
    testFuncReturn('Testing',"dictObj.getText(0)",locals())
    testFuncReturn('T',"dictObj.getText(0,1)",locals())
    testFuncReturn('',"dictObj.getText(1,1)",locals())
    testFuncReturn('Testing',"dictObj.getText(0,99)",locals())
    testFuncReturn('Testing',"dictObj.getText(0,7)",locals())
    testFuncReturn('Testin',"dictObj.getText(0,-1)",locals())
    testFuncReturn('g',"dictObj.getText(-1)",locals())
    testFuncReturn('n',"dictObj.getText(-2,-1)",locals())
    testFuncReturn('',"dictObj.getText(-1,-1)",locals())
    testFuncReturn('est',"dictObj.getText(1,4)",locals())
    testFuncReturn('',"dictObj.getText(4,1)",locals())
    testFuncReturn('',"dictObj.getText(-1,-2)",locals())
    testFuncReturn('',"dictObj.getText(100)",locals())
    testFuncReturn(7,"dictObj.getLength()",locals())
    testFuncReturn((7,7),"dictObj.getTextSel()",locals())
# This fails
#    testFuncReturn((0,0x7FFFFFFF),"dictObj.getVisibleText()",locals())

    dictObj.setText('AB',0,0)
    testFuncReturn('ABTesting',"dictObj.getText(0)",locals())
    dictObj.setText('CD',3,4)
    testFuncReturn('ABTCDsting',"dictObj.getText(0)",locals())
    dictObj.setText('EF',100)
    testFuncReturn('ABTCDstingEF',"dictObj.getText(0)",locals())
    dictObj.setText('GH',-1)
    testFuncReturn('ABTCDstingEGH',"dictObj.getText(0)",locals())
    dictObj.setText('IK',6,0)
    testFuncReturn('ABTCDsIKtingEGH',"dictObj.getText(0)",locals())
    dictObj.setText('HelloThere',0)
    testFuncReturn('HelloThere',"dictObj.getText(0)",locals())

    testFuncReturn(10,"dictObj.getLength()",locals())
    testFuncReturn((10,10),"dictObj.getTextSel()",locals())
# This fails testFuncReturn((0,0x7FFFFFFF),"dictObj.getVisibleText()",locals())

    dictObj.setTextSel(0)
    testFuncReturn((0,10),"dictObj.getTextSel()",locals())
    dictObj.setTextSel(-1)
    testFuncReturn((9,10),"dictObj.getTextSel()",locals())
    dictObj.setTextSel(1,4)
    testFuncReturn((1,4),"dictObj.getTextSel()",locals())
    dictObj.setTextSel(4,1)
    testFuncReturn((4,4),"dictObj.getTextSel()",locals())
    dictObj.setTextSel(-4,-1)
    testFuncReturn((6,9),"dictObj.getTextSel()",locals())

    dictObj.setVisibleText(-1)
    testFuncReturn((9,10),"dictObj.getVisibleText()",locals())
    dictObj.setVisibleText(1,4)
    testFuncReturn((1,4),"dictObj.getVisibleText()",locals())
    dictObj.setVisibleText(4,1)
    testFuncReturn((4,4),"dictObj.getVisibleText()",locals())
    dictObj.setVisibleText(-4,-1)
    testFuncReturn((6,9),"dictObj.getVisibleText()",locals())
    dictObj.setVisibleText(0)
    testFuncReturn((0,10),"dictObj.getVisibleText()",locals())

    dictObj.setText('',0)
    testFuncReturn(0,"dictObj.getLength()",locals())
    testFuncReturn((0,0),"dictObj.getTextSel()",locals())
    # This fails testFuncReturn((0,10),"dictObj.getVisibleText()",locals())

    dictObj.setLock(0)
    
    #----------
    # To force this dictation object to receive recognitions, we launch
    # the calc application and attach a dictation grammar to the calc.
    #
    # We use the calc because we are (almost) certain that it exists
    # in all Windows installations and because it does not have any edit
    # or rich edit fields which may be dictation enabled.
    
    natlink.execScript('AppBringUp "calc.exe"')
    moduleInfo = natlink.getCurrentModule()
    dictObj.activate(moduleInfo[2])

    callTest = CallbackTester()
    dictObj.setBeginCallback(callTest.onBegin)
    dictObj.setChangeCallback(callTest.onTextChange)

    # remember during these tests that the dictation results are formatted
    natlink.recognitionMimic(['hello'])
    testFuncReturn('Hello',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(0,0,'Hello',5,5))
    natlink.recognitionMimic(['there'])
    testFuncReturn('Hello there',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(5,5,' there',11,11))

    dictObj.setTextSel(0,5)
    natlink.recognitionMimic(['and'])
    testFuncReturn('And there',"dictObj.getText(0)",locals())

#v5
    callTest.testTextChange(moduleInfo,(0,6,'And ',3,3))
#else
#    callTest.testTextChange(moduleInfo,(0,5,'And',3,3))

    dictObj.setTextSel(3,3)
    natlink.recognitionMimic([',\\comma'])
    testFuncReturn('And, there',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(3,3,',',4,4))

    dictObj.setTextSel(5)
    natlink.recognitionMimic(['another','phrase'])
    testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(4,10,' another phrase',19,19))
#else        callTest.testTextChange(moduleInfo,(5,10,'another phrase',19,19))

    natlink.recognitionMimic(['more'])
    testFuncReturn('And, another phrase more',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(19,19,' more',24,24))

    # the scratch that command undoes one recognition
    natlink.recognitionMimic(['scratch','that'])
    testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(19,24,'',19,19))

    # NatSpeak optimizes the changed block so we only change 'ther' not
    # 'there' -- the last e did not change.
    natlink.recognitionMimic(['scratch','that'])
    testFuncReturn('And, there',"dictObj.getText(0)",locals())
    callTest.testTextChange(moduleInfo,(5,18,'ther',5,10))

    # fill the buffer with a block of text
    # char index:    0123456789 123456789 123456789 123456789 123456789 123456789 
    dictObj.setText('This is a block of text.  Lets count one two three.  All done.',0)
    dictObj.setTextSel(0,0)
    dictObj.setVisibleText(0)

    # ok, test selection command
    natlink.recognitionMimic(['select','block','of','text'])
    testFuncReturn((10,23),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,(10,10,'',10,23))
    
    natlink.recognitionMimic(['select','one','through','three'])
    testFuncReturn((37,50),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,(37,37,'',37,50))

    # text selection of non-existant text
    testForException(natlink.MimicFailed,"natlink.recognitionMimic(['select','helloxxx'])")
    testFuncReturn((37,50),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,None)

    # now we clamp down on the visible range and prove that we can select
    # within the range but not outside the range
    dictObj.setVisibleText(10,50)
    dictObj.setTextSel(0,0)
    
    natlink.recognitionMimic(['select','one','through','three'])
    testFuncReturn((37,50),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,(37,37,'',37,50))

    #This is a block of text.  Lets count one two three.  All done.
    natlink.recognitionMimic(['select','this','is'])
    testFuncReturn((37,50),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,None)

    natlink.recognitionMimic(['select','all','done'])
    testFuncReturn((37,50),"dictObj.getTextSel()",locals())
    callTest.testTextChange(moduleInfo,None)
        
    # close the calc
    natlink.playString('{Alt+F4}')

#---------------------------------------------------------------------------
# This class is used when we test callbacks.  We will create an instance
# of this class and use the member functions of this class as the callbacks.
# Using a class allows us to both detect the callbacks and query the values
# seen by the callbacks.

class CallbackTester:

    def __init__(self):
        self.reset()

    # change callback of DictObj
    def onTextChange(self,delStart,delEnd,newText,selStart,selEnd):
        # because of the bug in NatSpeak where we can get two change
        # callbacks in a row, especially when dealing with scratch that, we
        # ignore all but the first callback
        if self.sawTextChange == None:
            self.sawTextChange = (delStart,delEnd,newText,selStart,selEnd)

    # begin callback of natlink,GramObj and DictObj
    def onBegin(self,moduleInfo):
        self.sawBegin = moduleInfo

    # timer callback of natlink
    def onTimer(self):
        self.sawTimer = 1

    # change callback of natlink
    def onChange(self,what,value):
        self.sawChange = (what,value)

    # results callback of GramObj:
    def onResults(self,results,resObj):
        self.sawResults = (results,resObj)

    # resets the local variables in preparation of a new test
    def reset(self):
        self.sawTextChange = None
        self.sawBegin = None
        self.sawTimer = None
        self.sawChange = None
        self.sawResults = None

    # Tests the contents of the object.  For this test we assume that we saw
    # both a begin callback and a test change callback with the indicated
    # values
    def testTextChange(self,moduleInfo,textChange):
        if self.sawBegin != moduleInfo:
            raise TestError,"Wrong results from begin callback\n  saw: %s\n  expecting: %s"%(repr(self.sawBegin),repr(moduleInfo))
        if self.sawTextChange != textChange:
            raise TestError,"Wrong results from change callback\n  saw: %s\n  expecting: %s"%(repr(self.sawTextChange),repr(textChange))
        self.reset()
    
    # Tests the contents of the object.  For this test we assume that we saw
    # both a begin callback and a results callback with the indicated values
    def testResults(self,moduleInfo,results):
        if self.sawBegin != moduleInfo:
            raise TestError,"Wrong results from begin callback\n  saw: %s\n  expecting: %s"%(repr(self.sawBegin),repr(moduleInfo))
        if self.sawResults == None and results != None:
            raise TestError,"Did not see results callback"
        if self.sawResults != None and self.sawResults[0] != results:
            raise TestError,"Wrong results from results callback\n  saw: %s\n  expecting: %s "%(repr(self.sawResults[0]),repr(results))
        self.reset()

#---------------------------------------------------------------------------
    
def testWordFuncs():

    # getWordInfo #
    
    testForException(TypeError,"natlink.getWordInfo()")
    testForException(TypeError,"natlink.getWordInfo(1)")
    testForException(TypeError,"natlink.getWordInfo('hello','flags')")
    testForException(natlink.ValueError,"natlink.getWordInfo('hello',-1)")
    testForException(natlink.ValueError,"natlink.getWordInfo('hello',8)")
    testForException(natlink.InvalidWord,"natlink.getWordInfo('a\\b\\c\\d\\f')")
    testForException(natlink.InvalidWord,"natlink.getWordInfo('a'*200)")

    # Assumptions:
    #
    # (1) User has not modified wordInfo flags of common words
    # (2) FrotzBlatz is not in the vocabulary
    # (3) Szymanski has not been moved to the dictation state
    # (4) HeLLo (with that capitalization) is not in the vocabulary

    testFuncReturn(0,"natlink.getWordInfo('hello')")
    testFuncReturn(0,"natlink.getWordInfo('hello',0)")
    testFuncReturn(0,"natlink.getWordInfo('hello',1)")
    testFuncReturn(0,"natlink.getWordInfo('hello',2)")
    testFuncReturn(0,"natlink.getWordInfo('hello',3)")
    testFuncReturn(0,"natlink.getWordInfo('hello',4)")
    testFuncReturn(0,"natlink.getWordInfo('hello',5)")
    testFuncReturn(0,"natlink.getWordInfo('hello',6)")
    testFuncReturn(0,"natlink.getWordInfo('hello',7)")

    testFuncReturn(dgnwordflag_nodelete+dgnwordflag_no_space_before,"natlink.getWordInfo(',\\comma')")
    testFuncReturn(dgnwordflag_nodelete+dgnwordflag_title_mode+dgnwordflag_DNS8newwrdProp,"natlink.getWordInfo('and')")
    
    # this none/0 stuff is nonsense
    testFuncReturn(None,"natlink.getWordInfo('FrotzBlatz',0)")
    testFuncReturn(None,"natlink.getWordInfo('FrotzBlatz',7)")
    
    #
    #sw my dict _has_ Szymanski
    #
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',0)")
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',6)")
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',1)")
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',1)")
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',5)")
    
    testFuncReturn(None,"natlink.getWordInfo('HeLLo',0)")
    testFuncReturn(0,"natlink.getWordInfo('HeLLo',4)")
    
    # setWordInfo #

    testForException(TypeError,"natlink.setWordInfo()")
    testForException(TypeError,"natlink.setWordInfo(1)")
    testForException(TypeError,"natlink.setWordInfo('hello')")
    testForException(TypeError,"natlink.setWordInfo('hello','')")

    testFuncReturn(0,"natlink.getWordInfo('hello')")
    natlink.setWordInfo('hello',dgnwordflag_nodelete)
    testFuncReturn(dgnwordflag_nodelete,"natlink.getWordInfo('hello')")
    natlink.setWordInfo('hello',0)
    testFuncReturn(0,"natlink.getWordInfo('hello')")

    testForException(natlink.UnknownName,"natlink.setWordInfo('FrotzBlatz',0)")
    testForException(natlink.UnknownName,"natlink.setWordInfo('Szymanskii',0)") 
    testForException(natlink.InvalidWord,"natlink.setWordInfo('a\\b\\c\\d\\f',0)")
    
    # addWord #

    testForException(TypeError,"natlink.addWord()")
    testForException(TypeError,"natlink.addWord(1)")
    testForException(TypeError,"natlink.addWord('FrotzBlatz','hello')")
    testForException(natlink.InvalidWord,"natlink.addWord('a\\b\\c\\d\\f')")

    testFuncReturn(0,"natlink.getWordInfo('hello')")
    testFuncReturn(0,"natlink.addWord('hello',dgnwordflag_nodelete)")
    testFuncReturn(0,"natlink.getWordInfo('hello')")
    
    testFuncReturn(None,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded)")
    # The first time we run this code, the extra internal use only flag
    # 0x20000000 is added to this word.  But if ytou run the test suite
    # twice without shuttong down NatSpeak the flag will disappear.
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")

    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',0)")
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',1)")
    testFuncReturn(1,"natlink.addWord('Szymanskii',dgnwordflag_is_period)")
    testFuncReturn(dgnwordflag_is_period+dgnwordflag_DNS8newwrdProp,"natlink.getWordInfo('Szymanskii')")
    
    # deleteWord #
    
    testForException(TypeError,"natlink.deleteWord()")
    testForException(TypeError,"natlink.deleteWord(1)")

    testFuncReturn(dgnwordflag_is_period+dgnwordflag_DNS8newwrdProp,"natlink.getWordInfo('Szymanskii')")
    natlink.deleteWord('Szymanskii')
    testFuncReturn(None,"natlink.getWordInfo('Szymanskii',0)")
    testFuncReturn(None ,"natlink.getWordInfo('Szymanskii',1)")
    
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")
    natlink.deleteWord('FrotzBlatz')
    testFuncReturn(None,"natlink.getWordInfo('FrotzBlatz')")

    testForException(natlink.UnknownName,"natlink.deleteWord('FrotzBlatz')")
    testForException(natlink.UnknownName,"natlink.deleteWord('Szymanskii')")
    testForException(natlink.InvalidWord,"natlink.deleteWord('a\\b\\c\\d\\f')")

#---------------------------------------------------------------------------
# Here we test the ability to load and unload macro files under various
# conditions.  The way we test that a file is loaded is to test that a
# command has been defined using recognitionMimic

def testNatLinkMain():

    baseDirectory = os.path.split(sys.modules['natlinkutils'].__dict__['__file__'])[0]
    userDirectory = natlink.getCurrentUser()[1]
    
    # Basic test of globals.  Make sure that our macro file is not
    # loaded.  Then load the file and make sure it is loaded.

    w=3

    safeRemove(baseDirectory,'__jMg1.py')
    safeRemove(baseDirectory,'__jMg1.pyc')
    safeRemove(baseDirectory,'__jMg1.py')
    safeRemove(baseDirectory,'__jMg1.pyc')
    safeRemove(baseDirectory,'__jMg2.py')
    safeRemove(baseDirectory,'__jMg2.pyc')
    safeRemove(userDirectory,'__jMg2.py')
    safeRemove(userDirectory,'__jMg2.pyc')
    safeRemove(baseDirectory,'calc__jMg1.py')
    safeRemove(baseDirectory,'calc__jMg1.pyc')
    
    toggleMicrophone(5)
    
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)
    createMacroFile(baseDirectory,'__jMg1.py','1')
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)

    toggleMicrophone(w)

    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],1)
    # Modify the macro file and make sure the modification takes effect
    # even if the microphone is not toggled.

    switchToNatSpeak()
    natlink.playString('Waiting for 1 minute to pass...')
    time.sleep(60)
    natlink.playString('{ctrl+a}{del}')
    
    createMacroFile(baseDirectory,'__jMg1.py','2')
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],1)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)

    # Make sure a user specific file also works

    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],0)
    createMacroFile(userDirectory,'__jMg2.py','3')
    toggleMicrophone(w)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],1)

    # Make sure user specific files have precidence over global files

    createMacroFile(baseDirectory,'__jMg2.py','4')
    toggleMicrophone(w)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],1)

    # Make sure that we do the right thing with application specific
    # files.  They get loaded when the application is activated.

    createMacroFile(baseDirectory,'calc__jMg1.py','5')
    toggleMicrophone(w)
    
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],0)
    natlink.execScript('AppBringUp "calc"')
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],1)
    natlink.playString('{Alt+F4}')

    # clean up any files created during this test
    safeRemove(baseDirectory,'__jMg1.py')
    safeRemove(baseDirectory,'__jMg2.py')
    safeRemove(userDirectory,'__jMg2.py')
    safeRemove(baseDirectory,'calc__jMg1.py')
    toggleMicrophone(w)

    # now that the files are gone, make sure that we no longer recognize
    # from them
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],0)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],0)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','4'],0)
    testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],0)

    # make sure no .pyc files are lying around
    safeRemove(baseDirectory,'__jMg1.pyc')
    safeRemove(baseDirectory,'__jMg2.pyc')
    safeRemove(userDirectory,'__jMg2.pyc')
    safeRemove(baseDirectory,'calc__jMg1.pyc')

#---------------------------------------------------------------------------

def testWordProns():

    testForException(TypeError,"natlink.getWordProns()")
    testForException(TypeError,"natlink.getWordProns(1)")
    testForException(TypeError,"natlink.getWordProns('hello','and')")
    testForException(natlink.InvalidWord,"natlink.getWordProns('a\\b\\c\\d\\f')")

    # we assume these words are not active
    testFuncReturn(None,"natlink.getWordProns('FrotzBlatz')")
    testFuncReturn(None,"natlink.getWordProns('Szymanskii')")

    # I have looked up the expected pronunciations for these words
    testFuncReturn(['an','and','~'],"natlink.getWordProns('and')")
    testFuncReturn(['Dat'],"natlink.getWordProns('that')")
    testFuncReturn(['on'],"natlink.getWordProns('on')")

    # make sure that the pronunciation of 'four' in included in the list
    # of prons of 'for'
    pronFour = natlink.getWordProns('four')
    pronFor = natlink.getWordProns('for')
    for pron in pronFour:
        if pron not in pronFor:
            raise TestError,'getWordProns returned unexpected pronunciation list for For/Four'
        
    # same thing for 'two' and 'to'                                
    pronTwo = natlink.getWordProns('two')
    pronTo = natlink.getWordProns('to')
    for pron in pronTwo:
        if pron not in pronTo:
            raise TestError,'getWordProns returned unexpected pronunciation list for To/Two'

    # check errors
    testForException(TypeError,"natlink.addWord('FrotzBlatz',0,0)")
    testForException(TypeError,"natlink.addWord('FrotzBlatz',0,[0])")
    testForException(TypeError,"natlink.addWord('FrotzBlatz',0,'one','two')")
    
    # now add in FrotzBlatz with a known pron
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,'on')")
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on'],"natlink.getWordProns('FrotzBlatz')")

    # add another pron
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,'and')")
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on','and'],"natlink.getWordProns('FrotzBlatz')")

    # add a few prons
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,['~','Dat'])")
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

    # add a duplicate pron
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,'on')")
    testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

    # try to change the flags
    testFuncReturn(1,"natlink.addWord('FrotzBlatz',0,'on')")
    testFuncReturn(0,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

    # adding the word w/o prons does nothing even if the flags change
    testFuncReturn(0,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded)")
    testFuncReturn(0,"natlink.getWordInfo('FrotzBlatz')")
    testFuncReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

    # delete the word
    natlink.deleteWord('FrotzBlatz')

#---------------------------------------------------------------------------
# Performs a recognition mimic and makes sure that the mic succeeds or fails
# as expected.

def testRecognition(words,shouldWork=1):
    if shouldWork:
        natlink.recognitionMimic(words)
    else:
        testForException(natlink.MimicFailed,"natlink.recognitionMimic(words)",locals())

#---------------------------------------------------------------------------
# Forces all macro files to be reloaded by toggling the microphone

def toggleMicrophone(wait=0):
    natlink.setMicState('on')
    natlink.setMicState('off')
    time.sleep(wait)
#---------------------------------------------------------------------------
# Removes a file if it exists

def safeRemove(filePath,fileName):
    fullName = os.path.join(filePath,fileName)
    if os.access(fullName,0):
        os.remove(fullName)
    
#---------------------------------------------------------------------------
#
# Creates a macro file in a given directory which will recognize the grammar
# consisting of two words, 'jMg' and the passed word.
#
#sw
#jMG gives me problems,
#so,,,
macroFileTemplate = """
import natlink
from natlinkutils import *
class ThisGrammar(GrammarBase):
    gramSpec = '<Start> exported = this is automated testing from Python %s;'
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()
thisGrammar = ThisGrammar()
thisGrammar.initialize()
def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
"""

def createMacroFile(filePath,fileName,word):
    open(os.path.join(filePath,fileName),'w').write(macroFileTemplate%word)

#---------------------------------------------------------------------------
# Test the Grammar parser

def testParser():

    def testGrammerError(exceptionType,gramSpec):
        try:
            parser = GramParser([gramSpec])
            parser.doParse()
            parser.checkForErrors()
        except exceptionType:
            return
        raise TestError,'Expecting an exception parsing grammar '+gramSpec

    # here we try a few illegal grammars to make sure we catch the errors
    # 
    testGrammerError(SyntaxError,'badrule;')
    testGrammerError(SyntaxError,'badrule = hello;')
    testGrammerError(SyntaxError,'= hello;')
    testGrammerError(SyntaxError,'<rule> error = hello;')
    testGrammerError(SyntaxError,'<rule> exported = hello')
    testGrammerError(LexicalError,'<rule exported = hello;')
    testGrammerError(SyntaxError,'<rule> exported = ;')
    testGrammerError(SyntaxError,'<rule> exported = [] hello;')
    testGrammerError(GrammarError,'<rule> = hello;')
    testGrammerError(SyntaxError,'<rule> exported = hello ];')
    testGrammerError(SyntaxError,'<rule> exported = hello {};')
    testGrammerError(SyntaxError,'<rule> exported = hello <>;')
    testGrammerError(GrammarError,'<rule> exported = <other>;')
    testGrammerError(SymbolError,'<rule> exported = one; <rule> exported = two;')
    testGrammerError(SyntaxError,'<rule> exported = hello | | goodbye;')
    testGrammerError(SyntaxError,'<rule> exported = hello ( ) goodbye;')
    testGrammerError(SyntaxError,'<rule> exported = hello "" goodbye;')
    
#---------------------------------------------------------------------------
# Here we test recognition of command grammars using GrammarBase    

def testGrammar():

    # Create a simple command grammar.  This grammar simply gets the results
    # of the recognition and saves it in member variables.  It also contains
    # code to check for the results of the recognition.
    class TestGrammar(GrammarBase):

        def __init__(self):
            GrammarBase.__init__(self)
            self.resetExperiment()

        def resetExperiment(self):
            self.sawBegin = 0
            self.recogType = None
            self.words = []
            self.fullResults = []
            self.error = None

        def gotBegin(self,moduleInfo):
            if self.sawBegin:
                self.error = 'Command grammar called gotBegin twice'
            self.sawBegin = 1
            if moduleInfo != natlink.getCurrentModule():
                self.error = 'Invalid value for moduleInfo in GrammarBase.gotBegin'

        def gotResultsObject(self,recogType,resObj):
            if self.recogType:
                self.error = 'Command grammar called gotResultsObject twice'
            self.recogType = recogType

        def gotResults(self,words,fullResults):
            if self.words:
                self.error = 'Command grammar called gotResults twice'
            self.words = words
            self.fullResults = fullResults

        def checkExperiment(self,sawBegin,recogType,words,fullResults):
            if self.error:
                raise TestError,self.error
            if self.sawBegin != sawBegin:
                raise TestError,'Unexpected result for GrammarBase.sawBegin\n  Expected %d\n  Saw %d'%(sawBegin,self.sawBegin)
            if self.recogType != recogType:
                raise TestError,'Unexpected result for GrammarBase.recogType\n  Expected %s\n  Saw %s'%(recogType,self.recogType)
            if self.words != words:
                raise TestError,'Unexpected result for GrammarBase.words\n  Expected %s\n  Saw %s'%(repr(words),repr(self.words))
            if self.fullResults != fullResults:
                raise TestError,'Unexpected result for GrammarBase.fullResults\n  Expected %s\n  Saw %s'%(repr(fullResults),repr(self.fullResults))
            self.resetExperiment()

    testGram = TestGrammar()

    # load the calculator again
    time.sleep(5) # let the calculator recover from last test
    natlink.execScript('AppBringUp "calc"')
    print natlink.getCurrentModule()
    calcWindow = natlink.getCurrentModule()[2]
    
    # Activate the grammar and try a test recognition
    testGram.load('<Start> exported = hello there;')
    testGram.activateAll(window=calcWindow)
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,'self',['hello','there'],[('hello','Start'),('there','Start')])

    # With the grammar deactivated, we should see nothing.  But to make this
    # work we need another grammar active to catch the recognition.
    otherGram = TestGrammar()
    otherGram.load('<Start> exported = hello there;')
    otherGram.activateAll(window=0)

    testGram.deactivateAll()
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,None,[],[])

    # on a different window, we should see nothing (we need a real window
    # handle so we switch to the NatSpeak window to get its handle)
    switchToNatSpeak()
    natWindow = natlink.getCurrentModule()[2]
    natlink.playString('{Alt+space}n')
    natlink.execScript('AppBringUp "calc"')
    
    testGram.activateAll(window=natWindow)
    testRecognition(['hello','there'])
# This fails    testGram.checkExperiment(1,None,[],[])

    # activate us for a different window and make sure we see the
    # recognition when we ask for all results
    otherGram.deactivateAll()
    otherGram.activateAll(window=calcWindow)
    
    testGram.unload()
    testGram.load('<Start> exported = hello there;',allResults=1)
    testGram.activateAll(window=0)
    testRecognition(['hello','there'])
   
   #This fails testGram.checkExperiment(1,'other',[],[])
   
    testGram.resetExperiment()

    # now we create a more complex grammar and test the result
    testGram.unload()
    testGram.load("""
        <other> exported = one [two];
        <inner> = see <other>;
        <start> exported = I <inner> now; """)
    testGram.activateAll(window=calcWindow)
    testRecognition(['I','see','one','now'])
    testGram.checkExperiment(1,'self',['I','see','one','now'],
        [('I','start'),('see','inner'),('one','other'),('now','start')])

    # try a few illegal grammars to make sure they are reported properly (we
    # already tested the grammar parser so this does not have to be
    # exhaustive)
    testGram.unload()
    testForException(SyntaxError,"testGram.load('badrule;')",locals())
    testForException(GrammarError,"testGram.load('<rule> = hello;')",locals())

    # most calls are not legal before load is called (successfully)
    testForException(natlink.NatError,"testGram.gramObj.activate('start',0)",locals())
    testForException(natlink.NatError,"testGram.gramObj.deactivate('start')",locals())
    testForException(natlink.NatError,"testGram.gramObj.setExclusive(1)",locals())
    testForException(natlink.NatError,"testGram.gramObj.emptyList('list')",locals())
    testForException(natlink.NatError,"testGram.gramObj.appendList('list','word')",locals())

    # make sure we get errors from illegal calls
    testGram.load('<rule> exported = {list};')
    testForException(natlink.UnknownName,"testGram.gramObj.activate('start',0)",locals())
    testForException(natlink.BadWindow,"testGram.gramObj.activate('rule',1)",locals())
    testGram.gramObj.activate('rule',0)
    testForException(natlink.WrongState,"testGram.gramObj.deactivate('start')",locals())
    testGram.gramObj.deactivate('rule')
    testForException(natlink.WrongState,"testGram.gramObj.deactivate('rule')",locals())
    testForException(natlink.UnknownName,"testGram.gramObj.emptyList('rule')",locals())
    testForException(natlink.UnknownName,"testGram.gramObj.appendList('rule','word')",locals())
    
    testForException(TypeError,"testGram.gramObj.activate()",locals())
    testForException(TypeError,"testGram.gramObj.activate(1)",locals())
    testForException(TypeError,"testGram.gramObj.activate('rule','')",locals())
    testForException(TypeError,"testGram.gramObj.deactivate()",locals())
    testForException(TypeError,"testGram.gramObj.deactivate(1)",locals())
    testForException(TypeError,"testGram.gramObj.setExclusive('')",locals())
    testForException(TypeError,"testGram.gramObj.emptyList()",locals())
    testForException(TypeError,"testGram.gramObj.emptyList(1)",locals())
    testForException(TypeError,"testGram.gramObj.appendList()",locals())
    testForException(TypeError,"testGram.gramObj.appendList(1)",locals())
    testForException(TypeError,"testGram.gramObj.appendList('list',1)",locals())
    
    testForException(natlink.WrongType,"testGram.gramObj.setContext('before','after')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.setSelectText('text')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.getSelectText()",locals())

    # clean up
    testGram.unload()
    otherGram.unload()
    natlink.playString('{Alt+F4}')

#---------------------------------------------------------------------------
# Here we test recognition of dictation grammars using DictGramBase

def testDictGram():

    # Create a dictation grammar.  This grammar simply gets the results of
    # the recognition and saves it in member variables.  It also contains
    # code to check for the results of the recognition.
    class TestDictGram(DictGramBase):

        def __init__(self):
            DictGramBase.__init__(self)
            self.resetExperiment()

        def resetExperiment(self):
            self.sawBegin = 0
            self.recogType = None
            self.words = []
            self.error = None

        def gotBegin(self,moduleInfo):
            if self.sawBegin:
                self.error = 'Dictation grammar called gotBegin twice'
            self.sawBegin = 1
            if moduleInfo != natlink.getCurrentModule():
                self.error = 'Invalid value for moduleInfo in DictGramBase.gotBegin'

        def gotResultsObject(self,recogType,resObj):
            if self.recogType:
                self.error = 'Dictation grammar called gotResultsObject twice'
            self.recogType = recogType

        def gotResults(self,words):
            if self.words:
                self.error = 'Dictation grammar called gotResults twice'
            self.words = words

        def checkExperiment(self,sawBegin,recogType,words):
            if self.error:
                raise TestError,self.error
            if self.sawBegin != sawBegin:
                raise TestError,'Unexpected result for DictGramBase.sawBegin\n  Expected %d\n  Saw %d'%(sawBegin,self.sawBegin)
            if self.recogType != recogType:
                raise TestError,'Unexpected result for DictGramBase.recogType\n  Expected %s\n  Saw %s'%(recogType,self.recogType)
            if self.words != words:
                raise TestError,'Unexpected result for DictGramBase.words\n  Expected %s\n  Saw %s'%(repr(words),repr(self.words))
            self.resetExperiment()

    testGram = TestDictGram()

    # load the calculator again
    time.sleep(5) # let the calculator recover from last test
    natlink.execScript('AppBringUp "calc"')
    calcWindow = natlink.getCurrentModule()[2]
    print natlink.getCurrentModule()
    
    # Activate the grammar and try a test recognition
    testGram.load()
    testGram.activate(window=calcWindow)
    time.sleep(0.2)
    testRecognition(['this','is','a','test','.\\period'])
    testGram.checkExperiment(1,'self',['this','is','a','test','.\\period'])

    # try unloading and reloading
    testGram.unload()
    testGram.load()
    testGram.activate(window=calcWindow)
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,'self',['hello','there'])
    
    # With the grammar deactivated, we should see nothing.  But to make this
    # work we need another grammar active to catch the recognition.
    otherGram = GrammarBase()
    otherGram.load('<Start> exported = hello there;')
    otherGram.activateAll(window=0)

    testGram.deactivate()
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,None,[])

    # on a different window, we should see nothing (we need a real window
    # handle so we switch to the NatSpeak window to get its handle)
    switchToNatSpeak()
    natWindow = natlink.getCurrentModule()[2]
    natlink.playString('{Alt+space}n')
    natlink.execScript('AppBringUp "calc"')
    
    testGram.activate(window=natWindow)
    testRecognition(['hello','there'])
    #This fails testGram.checkExperiment(1,None,[])

    # activate us globally and make sure we see the recognition when we ask
    # for all results
    otherGram.deactivateAll()
    otherGram.activateAll(window=calcWindow)
    
    testGram.unload()
    testGram.load(allResults=1)
    testGram.activate(window=0)
    testRecognition(['hello','there'])

    try:
        testGram.checkExperiment(1,'other',[])
    except TestError:
        # This failure sometimes happens when NatText is enabled
        print
        print 'Warning'
        print
        print 'One of the minor tests failed.  This test failure occurs if'
        print 'NaturalText is enabled.  If NaturalText is disabled, this test'
        print 'should work.  If you know that NaturalText is disabled and you'
        print 'get this message then you will need to track down or report the'
        print 'selftest failure.'
        print ''
        print 'If you have no idea what NaturalText is, or you do not know how'
        print 'to determine whether it is enabled or disables then you can safely'
        print 'ignore this message.'
        print
    
    testGram.resetExperiment()

    # Here we test the grammar calls.  Only the context call is legal for
    # dictation grammars.  And we can not test if it has any effect without
    # a real recognition.
    testGram.gramObj.setContext()
    testGram.gramObj.setContext('hello')
    testGram.gramObj.setContext('left','right')
    testForException(TypeError,"testGram.gramObj.setContext(1)",locals())
    testForException(TypeError,"testGram.gramObj.setContext('left',2)",locals())
    testForException(TypeError,"testGram.gramObj.setContext('left','right','error')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.emptyList('list')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.appendList('list','1')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.setSelectText('')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.getSelectText()",locals())
    
    # clean up
    testGram.unload()
    otherGram.unload()
    natlink.playString('{Alt+F4}')
    
#---------------------------------------------------------------------------
# Here we test recognition of selection grammars using SelectGramBase

def testSelectGram():

    # Create a selection grammar.  This grammar simply gets the results of
    # the recognition and saves it in member variables.  It also contains
    # code to check for the results of the recognition.
    class TestSelectGram(SelectGramBase):

        def __init__(self):
            SelectGramBase.__init__(self)
            self.resetExperiment()

        def resetExperiment(self):
            self.sawBegin = 0
            self.recogType = None
            self.words = []
            self.start = 0
            self.end = 0
            self.error = None

        def gotBegin(self,moduleInfo):
            if self.sawBegin:
                self.error = 'Selection grammar called gotBegin twice'
            self.sawBegin = 1
            if moduleInfo != natlink.getCurrentModule():
                self.error = 'Invalid value for moduleInfo in SelectGramBase.gotBegin'

        def gotResultsObject(self,recogType,resObj):
            if self.recogType:
                self.error = 'Selection grammar called gotResultsObject twice'
            self.recogType = recogType

        def gotResults(self,words,start,end):
            if self.words:
                self.error = 'Selection grammar called gotResults twice'
            self.words = words
            self.start = start
            self.end = end

        def checkExperiment(self,sawBegin,recogType,words,start,end):
            if self.error:
                raise TestError,self.error
            if self.sawBegin != sawBegin:
                raise TestError,'Unexpected result for SelectGramBase.sawBegin\n  Expected %d\n  Saw %d'%(sawBegin,self.sawBegin)
            if self.recogType != recogType:
                raise TestError,'Unexpected result for SelectGramBase.recogType\n  Expected %s\n  Saw %s'%(recogType,self.recogType)
            if self.words != words:
                raise TestError,'Unexpected result for SelectGramBase.words\n  Expected %s\n  Saw %s'%(repr(words),repr(self.words))
            if self.start != start:
                raise TestError,'Unexpected range start for SelectGramBase.words\n  Expected %d\n  Saw %d'%(start, self.start)
            if self.end != end:
                raise TestError,'Unexpected range end for SelectGramBase.words\n  Expected %d\n  Saw %d'%(end, self.end)
            self.resetExperiment()            

    testGram = TestSelectGram()

    # load the calculator again
    time.sleep(5) # let the calculator recover from last test
    natlink.execScript('AppBringUp "calc"')
    calcWindow = natlink.getCurrentModule()[2]

    # create a sample test buffer and load a simple grammar
    buffer = '0 1 2 3 4 5 6 7 8 9'
    testGram.load(['select'],'')
    testGram.setSelectText(buffer)
    testGram.activate(window=calcWindow)
    testRecognition(['select','2'])
    testGram.checkExperiment(1,'self',['select','2'],4,5)
    
    testRecognition(['select','2','3'])
    testGram.checkExperiment(1,'self',['select','2','3'],4,7)

    # make sure these do not get recognized
    testForException(natlink.MimicFailed,"testRecognition(['select','hello'])")
    testGram.checkExperiment(1,None,[],0,0)
    testForException(natlink.MimicFailed,"testRecognition(['select','2','2'])")
    testGram.checkExperiment(1,None,[],0,0)

    # try a more complex grammar
    testGram.unload()
    testGram.load(['select','Correct','Insert Before'],'Through')
    testGram.setSelectText(buffer)
    testGram.activate(window=calcWindow)
    testRecognition(['select','2'])
    testGram.checkExperiment(1,'self',['select','2'],4,5)

    testRecognition(['Insert Before','2'])
    testGram.checkExperiment(1,'self',['Insert Before','2'],4,5)
    
    testRecognition(['Correct','1','Through','7'])
    testGram.checkExperiment(1,'self',['Correct','1','Through','7'],2,15)

    # test for command failures
    testForException(TypeError,"testGram.gramObj.setSelectText(1)",locals())
    testForException(TypeError,"testGram.gramObj.setSelectText('text','text')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.emptyList('list')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.appendList('list','1')",locals())
    testForException(natlink.WrongType,"testGram.gramObj.setContext('left','right')",locals())

    # clean up
    testGram.unload()
    natlink.playString('{Alt+F4}')

#---------------------------------------------------------------------------
# Testing the tray icon is hard since we can not conviently interact with
# the UI from this test script.  But I test what I can.    

def testTrayIcon():
    testForException(TypeError,"natlink.setTrayIcon(1)")
    testForException(TypeError,"natlink.setTrayIcon('up',1)")
    testForException(TypeError,"natlink.setTrayIcon('up','up',1)")

    # make sure all the built-in names work
    validIcons = [ 'right', 'right2', 'down', 'down2', 'left',
        'left2', 'up', 'up2', 'nodir' ]
    for icon in validIcons:
        natlink.setTrayIcon(icon)
    natlink.setTrayIcon('')

    # make sure we detect a missing file or bad name
    testForException(natlink.ValueError,"natlink.setTrayIcon('invalid')")

    # try to open an explicit file
    baseDirectory = os.path.split(sys.modules['natlinkutils'].__dict__['__file__'])[0]
    iconFile = baseDirectory+'/../NatlinkSource/idi_nodir.ico'
    natlink.setTrayIcon(iconFile)
    natlink.setTrayIcon()

#---------------------------------------------------------------------------
# There used to be a problem with calling recognitionMimic from within a
# recognitionMimic call.  This test tries to test the various combinations
# to make sure things work OK.

def testNestedMimics():

    class TestGrammar(GrammarBase):

        gramSpec = """
            <run> exported = test test run ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 ) ;
            <test1> exported = test test 1 ;
            <test2> exported = test test 2 ;
            <test3> exported = test test 3 ;
            <test4> exported = test test 4 ;
            <test5> exported = test test 5 ;
            <test6> exported = test test 6 ;
            <test7> exported = test test 7 ;
            <test8> exported = test test 8 ;
            <test9> exported = test test 9 ;
        """

        def resetExperiment(self):
            self.results = []

        def checkExperiment(self,expected):
            if self.results != expected:
                raise TestError, "Grammar failed to get recognized\n   Expected = %s\n   Results = %s"%( str(expected), str(self.results) )
            self.resetExperiment()
    
        def initialize(self):
            self.load(self.gramSpec)
            self.activateAll()
            self.resetExperiment()

        def gotResults_run(self,words,fullResults):
            self.results.append('run')
            natlink.recognitionMimic(['test','test',words[3]])

        def gotResults_test1(self,words,fullResults):
            self.results.append('1')

        def gotResults_test2(self,words,fullResults):
            self.results.append('2')
            natlink.recognitionMimic(['test','test','1'])

        def gotResults_test3(self,words,fullResults):
            self.results.append('3')
            natlink.execScript('HeardWord "test","test","1"')

        def gotResults_test4(self,words,fullResults):
            self.results.append('4')
            natlink.execScript('HeardWord "test","test","3"')

        def gotResults_test5(self,words,fullResults):
            self.results.append('5')
            testForException(natlink.MimicFailed,"natlink.recognitionMimic(['*unknown-word*'])")

    testGram = TestGrammar()
    testGram.initialize()
    
    natlink.recognitionMimic(['test','test','run','1'])
    testGram.checkExperiment(['run','1'])
    
    natlink.recognitionMimic(['test','test','run','2'])
    testGram.checkExperiment(['run','2','1'])

    natlink.recognitionMimic(['test','test','run','3'])
    testGram.checkExperiment(['run','3','1'])
    
    natlink.recognitionMimic(['test','test','run','4'])
    testGram.checkExperiment(['run','4','3','1'])

    natlink.recognitionMimic(['test','test','run','5'])
    testGram.checkExperiment(['run','5'])

    testGram.unload()
    
#---------------------------------------------------------------------------
# run
#
# This is the main entry point.  It will connect to NatSpeak and perform
# a series of tests.  In the case of an error, it will cleanly disconnect
# from NatSpeak and print the exception information,

def run():
    try:
        preTests()
        natlink.natConnect()
        mainTests()
        natlink.natDisconnect()
        postTests()
        print
        print 'All tests passed!'
        print
        print 'Please shutdown NatSpeak before rerunning this script'
        print 'or saving your user files.  This is because the test'
        print 'script will leave some state around which will make it'
        print 'fail if run again.'
        print
        print 'Do *not* save your speech files right now.'
    except ExitQuietly:
        natlink.natDisconnect()
        print ''
    except:
        natlink.natDisconnect()
        print ''
        traceback.print_exc()

if __name__=='__main__':
    if len(sys.argv) >1 and sys.argv[1] == "doTest":
        run()
        natlink.displayText("test",0)
        time.sleep(2)    
