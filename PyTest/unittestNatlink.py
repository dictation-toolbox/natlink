#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# testnatlink.py
#   This script performs some basic tests of the NatLink system.
#
# run from a (preferably clean) US user profile, easiest from IDLE.
# do not run from pythonwin. See also README.txt in PyTest folder
#
# May 1, 2007 - QH
# try to unify with unimacro version of natlinkmain/natlinkutils.
# putting under unittest
# tests (a bit adapted at some places) now run if natConnect is done without threading
#
#   - if threading is put on some tests fail (testDictObj,
#     failing to receive the proper callback functions)
#   - test problems/artefacts: when touching something while testing (about 10 minutes it lasts, because after
#     each test the user profile is re-opened), DragonPad cannot be got in front sometimes.
#   - after testing an instance of natspeak may be running even after you close natspeak.
#     close by hand(ctrl+alt+delete etc).
#   - a (fresh) us test user is best, especially for the WordProns and WordFuncs tests
#     (to ensure this, you can make a clean user profile and export it as 'test user us'.
#     (import it before you start doing all the tests, though most tests will continue running even
#      if you are less strict)
#   - if problems arise, change the test function name you want to isolate to tttest.... and
#     change at the bottom (about 10 lines from the bottom) the makeSuite line 'test' to 'tttest'.
#     The testing will take only the function(s) you marked this way.
#
# testWordProns and testWordFuncs are adapted to (I think) version 9, see the docstrings there...
#
# April 16, 2005 - sw
# got many, not all test working w/ v 8
# seach for '#This fails' to find broken tests


# April 1, 2000
#   - added testParser, testGramimar, testDictGram, testSelectGram
#

import sys, unittest
import os
import os.path
import time
import string
import traceback        # for printing exceptions
from struct import pack

import natlink
import gramparser
from natlinkutils import *
import natlinkutils
import win32gui

class TestError(Exception):
    pass
ExitQuietly = 'ExitQuietly'


# try some experiments more times, because gotBegin sometimes seems
# not to hit
nTries = 10
natconnectOption = 0 # or 1 for threading, 0 for not. Seems to make difference
                     # with spurious error (if set to 1), missing gotBegin and all that...
logFileName = r"C:\program files\natlink\PyTest\testresult.txt"

#---------------------------------------------------------------------------
# These tests should be run after we call natConnect
class UnittestNatlink(unittest.TestCase):
##  def mainTests():
##      lookForNatSpeak()
##      testPlayString()
##      testExecScript()
##      testDictObj()
##      testWordFuncs()
##      testNatLinkMain()
##      testWordProns()
##      testParser()
##      testGrammar()
##      testDictGram()
##  # This fails    testSelectGram()
##  # This fails    testTrayIcon()
##      testNestedMimics()
##
##      # minimize natspeak which should display the Python window
##      switchToNatSpeak()
##      natlink.playString('{Alt+space}n')
    def setUp(self):
        if not natlink.isNatSpeakRunning():
            raise TestError,'NatSpeak is not currently running'
        self.connect()
        # remember user and get DragonPad in front:
        self.user = natlink.getCurrentUser()[0]
        self.setMicState = "off"
        self.lookForDragonPad()
        if self.getWindowContents():
            raise TestError('The DragonPad window is not empty, probably open when starting the tests...')



    def tearDown(self):
        try:
            # give message:
            self.setMicState = "off"
            # kill things
            self.killCalc()
            self.lookForDragonPad()
            natlink.playString("\n\ntearDown, reopen user: '%s'"% self.user)
            self.clearTestFiles()
            # reopen user:
            natlink.openUser(self.user)
            self.killDragonPad()
        finally:
            self.disconnect()

        
    def connect(self):
        # start with 1 for thread safety when run from pythonwin:
        natlink.natConnect(natconnectOption)

    def disconnect(self):
        natlink.natDisconnect()
        
    def log(self, t, doPlaystring=None):
        # displayTest seems not to work:
        natlink.displayText(t, 0)
        if doPlaystring:
            natlink.playString(t+'\n')
        # do the global log function:
        log(t)

##    def switchToNatSpeak(self):
##        natlink.execScript('HeardWord "Start","DragonPad"')
##        time.sleep(1)
    #    natlink.execScript('HeardWord "switch","to","DragonPad"')
    def lookForDragonPad(self):
        """start/find DragonPad"""

##        try: natlink.execScript('AppBringUp "NatSpeak"')
##        except natlink.NatError:
##            raise TestError,'The NatSpeak user interface is not running'
        natlink.recognitionMimic(['start', "DragonPad"])
        
        # This will make sure that the NatSpeak window is empty.  If the NatSpeak
        # window is not empty we raise an exception to avoid possibily screwing 
        # up the users work.
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "natspeak": break
            i += 1
        else:
            self.fail("Not the correct application: %s is brought to the front, should be natspeak"% mod)
        self.DragonPadMod = mod
        self.DragonPadHndle = hndle
        return hndle
    
    def lookForCalc(self):
        """start/find Calc"""
        natlink.execScript('AppBringUp "calc"')
        
        # wait for the window:
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "calc": break
            i += 1
        else:
            raise TestError("Not the correct application: %s is brought to the front, should be calc"% mod)
        self.CalcMod = mod
        self.CalcHndle = hndle
        return hndle

    def emptyDragonPad(self):
        """assume DragonPad is in front already"""
        natlink.playString('{ctrl+a}{del}')
        self.doTestWindowContents('')
        

    def killDragonPad(self):
        print 'going to kill DragonPad'
        try:
            hndle = self.DragonPadHndle
        except AttributeError:
            return
        
        try:
            win32gui.SetForegroundWindow(hndle)
        except:
            raise TestError("cannot get DragonPad foreground, hndle: %s"% hndle)

        # wait for the right window to appear:        
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "natspeak": break
            i += 1
        else:
            raise TestError("in killDragonPad, could not get back to DragonPad window, have: %s"% mod)

        natlink.playString("{alt+f4}")
        print 'closing dragonpad'
        # wait for the window to disappear (possibly get child window y n dialog)
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            if hndle != self.DragonPadHndle: break
            i += 1
        else:
            raise TestError("in killDragonPad, could not close the DragonPad window")
        del self.DragonPadHndle

        # if gets into child window press n (not save)
##        mod, title, hndle = natlink.getCurrentModule()
##        sys.stderr.write('mod, title, hndle: %s, %s, %s'% (mod, title, hndle))
##        if mod != "natspeak":
##            return   # finished
        
        if not self.isTopWindow(hndle):
            natlink.playString("n")
            time.sleep(0.1)
        mod, title, hndle = natlink.getCurrentModule()
        if not self.isTopWindow(hndle):
            raise TestError("in killDragonPad, did not return to a top window")

    
    def killCalc(self):
        try:
            hndle = self.CalcHndle
        except AttributeError:
            # not active:
            return
        try:
            win32gui.SetForegroundWindow(hndle)
        except:
            raise TestError("cannot get calc in foreground, hndle: %s"% hndle)
        del self.CalcHndle
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "calc": break
            i += 1
        else:
            raise TestError("in killCalc, could not get back to Calc window")
        natlink.playString("{alt+f4}")

    def clearTestFiles(self):
        """remove .py and .pyc files from the natlinkmain test

        """
        import natlinkmain
        baseDirectory = natlinkmain.baseDirectory
        userDirectory = natlinkmain.userDirectory
        for dir in (baseDirectory, userDirectory):
            for trunk in ('__jMg1', '__jMg2', 'calc__jMg1'):
                for ext in ('.py', '.pyc'):
                    safeRemove(dir, trunk + ext)

    def isTopWindow(self, hndle):
        """return 1 if it is a top window, child otherwise

        (to avoid using unimacro functions in the natlink tests)
        """        
        try:
            win32gui.GetParent(hndle)
        except:
            return 1
        return 0


    def wait(self, t=1):
        time.sleep(t)


    #---------------------------------------------------------------------------
    # These test should be run before we call natConnect (now in unittestPrePost.py)

##    def preTests(self):
##    def postTests(self): # now in unittestPrePost

    #---------------------------------------------------------------------------
    # This utility subroutine executes a Python command and makes sure that
    # an exception (of the expected type) is raised.  Otherwise a TestError
    # exception is raised

    def doTestForException(self, exceptionType,command,localVars={}):
        try:
            exec(command,globals(),localVars)
        except exceptionType:
            return
        raise TestError,'Expecting an exception to be raised calling '+command

    def doTestFuncPronsReturn(self, expected,command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        actual2 = [p for p in actual if not p.startswith('frots')]        

        if actual2 != expected:
            time.sleep(1)
        self.assertEqual(expected, actual2,
                         'Function prons ("frots..." stripped!!) call "%s" returned unexpected result\nexpected: %s, got: %s (stripped: %s)'%
                         (command, expected, actual, actual2))

    def doTestActiveRules(self, gram, expected):
        """gram must be a grammar instance, sort the rules to be expected and got
        """
        expected.sort()
        got = gram.activeRules
        got.sort()
        self.assertEqual(expected, got,
                         'Active rules not as expected:\nexpected: %s, got: %s'%
                         (expected, got))


    #---------------------------------------------------------------------------
    # This utility subroutine will returns the contents of the NatSpeak window as
    # a string.  It works by using playString to select the contents of the 
    # window and copy it to the clipboard.  We have to also add the character 'x'
    # to the end of the window to handle the case that the window is empty.

    def getWindowContents(self):
        natlink.playString('{ctrl+end}x{ctrl+a}{ctrl+c}{ctrl+end}{backspace}')
        contents = natlink.getClipboard()
        if contents == '' or contents[-1:] !='x':
            raise TestError,'Failed to read the contents of the NatSpeak window'
        return contents[:-1]

    def doTestWindowContents(self, expected,testName=None):
        contents = self.getWindowContents()
        if contents != expected:
            if testName:
                raise TestError('Contents of window did not match expected text, testing %s'%testName)
            else:
                raise TestError('Contents of window did not match expected text')
                
    #---------------------------------------------------------------------------
    # Utility function which calls a routine and tests the return value

    def doTestFuncReturn(self, expected,command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if actual != expected:
            time.sleep(1)
        self.assertEquals(expected, actual, 'Function call "%s" returned unexpected result\nExpected: %s, got: %s'%
                          (command, expected, actual))

    def doTestFuncReturnWordFlag(self, expected,command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if not (actual == expected or
                actual == expected  + dgnwordflag_DNS8newwrdProp):
            time.sleep(1)
            self.fail('Function call "%s" returned unexpected result(accounting for DNS8newwrdProp)\nExpected: %s (+prop8: %s), got: %s'%
                          (command, expected, expected+dgnwordflag_DNS8newwrdProp, actual))

    def doTestFuncReturnNoneOr0(self, command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if actual not in [None, 0]:
            self.fail('Function call "%s" did not return 0 or None as expected, but: %s'
                      % (command, actual))

    #---------------------------------------------------------------------------
    # This types the keysequence {alt+esc}.  Since this is a sequence trapped
    # by the OS, we must send as system keys.

    def playAltEsc(self):
        natlink.playString('{alt+esc}',hook_f_systemkeys)

    #---------------------------------------------------------------------------

##    def lookForNatSpeak(self):
##
##        # This should find the NatSpeak window.  If the NatSpeak window is not
##        # available (because, for example, NatSpeak was not started before 
##        # running this script) then we will get the error:
##        #   NatError: Error 62167 executing script execScript (line 1)
##
##        try:
##            natlink.execScript('HeardWord "Start","DragonPad"')
##            time.sleep(1)
##        except natlink.NatError:
##            raise TestError,'The NatSpeak user interface is not running'
##
##        # This will make sure that the NatSpeak window is empty.  If the NatSpeak
##        # window is not empty we raise an exception to avoid possibily screwing
##        # up the users work.
##
##        switchToNatSpeak()
##        if getWindowContents():
##            raise TestError,'The NatSpeak window is not empty'

    #---------------------------------------------------------------------------
    # Note 1: testWindowContents will clobber the clipboard.
    # Note 2: a copy/paste of the entire window adds an extra CRLF (\r\n)

    def testPlayString(self):
        self.log("testPlayString", 0) # not to DragonPad!
        testForException =self.doTestForException
        testWindowContents = self.doTestWindowContents
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

    def testExecScript(self):
        self.log("testExecScript", 1)

        testForException = self.doTestForException
        testForException( natlink.SyntaxError, 'natlink.execScript("UnknownCommand")' )

        # TODO this needs more test

    #---------------------------------------------------------------------------

    def testDictObj(self):
        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        dictObj = DictObj()
        self.log("testDictObj", 1)

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
        
##        natlink.execScript('AppBringUp "calc.exe"')
        calcWindow = self.lookForCalc()

        moduleInfo = natlink.getCurrentModule()
        dictObj.activate(calcWindow)

        callTest = CallbackTester()
        dictObj.setBeginCallback(callTest.onBegin)
        dictObj.setChangeCallback(callTest.onTextChange)

        # remember during these tests that the dictation results are formatted
        natlink.recognitionMimic(['hello'])
##        self.wait() #!!
        testFuncReturn('Hello',"dictObj.getText(0)",locals())
        # if this fails (9) probably setChangeCallback does not work (broken??QH)
        callTest.testTextChange(moduleInfo,(0,0,'Hello',5,5))
        natlink.recognitionMimic(['there'])
##        self.wait()
        testFuncReturn('Hello there',"dictObj.getText(0)",locals())
        callTest.testTextChange(moduleInfo,(5,5,' there',11,11))

        dictObj.setTextSel(0,5)
        natlink.recognitionMimic(['and'])
##        self.wait()  #!!!!QH
        testFuncReturn('And there',"dictObj.getText(0)",locals())
        #QH why does gotBegin not hit here, sometimes????
        
    #v5/9
        callTest.testTextChange(moduleInfo,(0,6,'And ',3,3))
    #else
##        callTest.testTextChange(moduleInfo,(0,5,'And',3,3))

        dictObj.setTextSel(3,3)
        natlink.recognitionMimic([',\\comma'])
##        self.wait()
        testFuncReturn('And, there',"dictObj.getText(0)",locals())
        callTest.testTextChange(moduleInfo,(3,3,',',4,4))

        dictObj.setTextSel(5)
        natlink.recognitionMimic(['another','phrase'])
##        self.wait()
        testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
        # unimacro version stops here, no beginCallback:::
        callTest.testTextChange(moduleInfo,(4,10,' another phrase',19,19))
    #else        callTest.testTextChange(moduleInfo,(5,10,'another phrase',19,19))

        natlink.recognitionMimic(['more'])
##        self.wait()
        testFuncReturn('And, another phrase more',"dictObj.getText(0)",locals())
        callTest.testTextChange(moduleInfo,(19,19,' more',24,24))

        # the scratch that command undoes one recognition
        natlink.recognitionMimic(['scratch','that'])
##        self.wait()
        testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
        callTest.testTextChange(moduleInfo,(19,24,'',19,19))

        # NatSpeak optimizes the changed block so we only change 'ther' not
        # 'there' -- the last e did not change.
        natlink.recognitionMimic(['scratch','that'])
        self.wait()
        
        testFuncReturn('And, there',"dictObj.getText(0)",locals())
        callTest.testTextChange(moduleInfo,(5,18,'ther',5,10))

        # fill the buffer with a block of text
        # char index:    0123456789 123456789 123456789 123456789 123456789 123456789 
        dictObj.setText('This is a block of text.  Lets count one two three.  All done.',0)
        dictObj.setTextSel(0,0)
        dictObj.setVisibleText(0)

        # ok, test selection command
        natlink.recognitionMimic(['select','block','of','text'])
##        self.wait()
        
        testFuncReturn((10,23),"dictObj.getTextSel()",locals())
        callTest.testTextChange(moduleInfo,(10,10,'',10,23))
        
        natlink.recognitionMimic(['select','one','through','three'])
##        self.wait()
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
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.testTextChange(moduleInfo,(37,37,'',37,50))

        #This is a block of text.  Lets count one two three.  All done.
        natlink.recognitionMimic(['select','this','is'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.testTextChange(moduleInfo,None)

        natlink.recognitionMimic(['select','all','done'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.testTextChange(moduleInfo,None)
            
        # close the calc (now done in tearDown)
##        natlink.playString('{Alt+F4}')


    #---------------------------------------------------------------------------
        
    def testWordFuncs(self):
        """tests the different vocabulary word functions.

        These tests are a bit vulnerable and seem to have changed in more recent
        versions of NatSpeak..

        1. The word Szymanski is changed to Szymanskii, as the former one is now
        in the vocabulary are in the backup vocabulary.

        2. Properties of nonexisting words return 0 or None, they should return only None.
        If the flag == 2 (second parameter of getWordInfo) (what does
        "consider active non-dictation words" mean anyway? QH) a zero is sometimes returned.
    
        3. In order to prevent this testing error a special value (list) NoneOr0 is introduced,
        the test passes if one of the two values is returned.

        4. With version 8 a you property was introduced,
        this one is added to the previous ones where appropriate.

        5. A test that adds an existing word now succeeds, but should really fail.
        In version 8 this was not yet (apparently) the case. So version 8 now fails this test.
        see below

        QH, april 2007 (natspeak 9.1 SP1)
        """
        self.log("testWordFuncs", 1)
        # getWordInfo #
        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        testFuncReturnWordFlag = self.doTestFuncReturnWordFlag
        # two alternatives permitted (QH)
        testFuncReturnNoneOr0 = self.doTestFuncReturnNoneOr0
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

        testFuncReturnWordFlag(dgnwordflag_nodelete+dgnwordflag_no_space_before,
                       "natlink.getWordInfo(',\\comma')")
        testFuncReturnWordFlag(dgnwordflag_nodelete+dgnwordflag_title_mode,
                       "natlink.getWordInfo('and')")
        
        # this none/0 stuff is nonsense
        testFuncReturnNoneOr0("natlink.getWordInfo('FrotzBlatz',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('FrotzBlatz',7)")
        
        #
        #sw my dict _has_ Szymanski
        #
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',6)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',5)")
        
        testFuncReturnNoneOr0("natlink.getWordInfo('HeLLo',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('HeLLo',4)")
        
        # setWordInfo #

        testForException(TypeError,"natlink.setWordInfo()")
        testForException(TypeError,"natlink.setWordInfo(1)")
        testForException(TypeError,"natlink.setWordInfo('hello')")
        testForException(TypeError,"natlink.setWordInfo('hello','')")

        testFuncReturnNoneOr0("natlink.getWordInfo('hello')")
        natlink.setWordInfo('hello',dgnwordflag_nodelete)
        testFuncReturn(dgnwordflag_nodelete,"natlink.getWordInfo('hello')")
        natlink.setWordInfo('hello',0)
        testFuncReturnNoneOr0("natlink.getWordInfo('hello')")

        testForException(natlink.UnknownName,"natlink.setWordInfo('FrotzBlatz',0)")
        testForException(natlink.UnknownName,"natlink.setWordInfo('Szymanskii',0)") 
        testForException(natlink.InvalidWord,"natlink.setWordInfo('a\\b\\c\\d\\f',0)")
        
        # addWord #

        testForException(TypeError,"natlink.addWord()")
        testForException(TypeError,"natlink.addWord(1)")
        testForException(TypeError,"natlink.addWord('FrotzBlatz','hello')")
        testForException(natlink.InvalidWord,"natlink.addWord('a\\b\\c\\d\\f')")

        testFuncReturn(0,"natlink.getWordInfo('hello')")
    ## version 8:
    ##        testFuncReturn(0,"natlink.addWord('hello',dgnwordflag_nodelete)")
    ##        testFuncReturn(0,"natlink.getWordInfo('hello')")
    ## version 9 QH (this test now fails in version 8)
        testFuncReturn(1,"natlink.addWord('hello',dgnwordflag_nodelete)")
        testFuncReturn(dgnwordflag_nodelete,"natlink.getWordInfo('hello')")
        
        testFuncReturnNoneOr0("natlink.getWordInfo('FrotzBlatz')")
        testFuncReturnWordFlag(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded)")
        # The first time we run this code, the extra internal use only flag
        # 0x20000000 is added to this word.  But if ytou run the test suite
        # twice without shuttong down NatSpeak the flag will disappear.
        testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")

        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        testFuncReturnWordFlag(1,"natlink.addWord('Szymanskii',dgnwordflag_is_period)")
        testFuncReturnWordFlag(dgnwordflag_is_period,"natlink.getWordInfo('Szymanskii')")
        
        # deleteWord #
        
        testForException(TypeError,"natlink.deleteWord()")
        testForException(TypeError,"natlink.deleteWord(1)")

        testFuncReturn(dgnwordflag_is_period+dgnwordflag_DNS8newwrdProp,"natlink.getWordInfo('Szymanskii')")
        natlink.deleteWord('Szymanskii')
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        
        testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")
        natlink.deleteWord('FrotzBlatz')
        testFuncReturnNoneOr0("natlink.getWordInfo('FrotzBlatz')")

        testForException(natlink.UnknownName,"natlink.deleteWord('FrotzBlatz')")
        testForException(natlink.UnknownName,"natlink.deleteWord('Szymanskii')")
        testForException(natlink.InvalidWord,"natlink.deleteWord('a\\b\\c\\d\\f')")

    #---------------------------------------------------------------------------
    # Here we test the ability to load and unload macro files under various
    # conditions.  The way we test that a file is loaded is to test that a
    # command has been defined using recognitionMimic

    def testNatLinkMain(self):

        testRecognition = self.doTestRecognition
        baseDirectory = os.path.split(sys.modules['natlinkutils'].__dict__['__file__'])[0]
        userDirectory = natlink.getCurrentUser()[1]
        import natlinkmain
        baseDirectory = natlinkmain.baseDirectory
        userDirectory = natlinkmain.userDirectory
        toggleMicrophone = self.toggleMicrophone
        # Basic test of globals.  Make sure that our macro file is not
        # loaded.  Then load the file and make sure it is loaded.

        mes = '\n'.join(['testNatLinkMain testing\n',
               'clearing previous macro files from:',
               '\tuserDir: %s'% userDirectory,
               '\tbaseDir: %s\n\n'% baseDirectory])
        natlink.playString(mes)
        ## for extra safety:
        self.clearTestFiles()
        toggleMicrophone()

        self.log('create jMg1, 1', 1)
        
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)
        createMacroFile(baseDirectory,'__jMg1.py','1')
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)

        self.log('toggle mic, to get jMg1 in loadedGrammars', 1)
        toggleMicrophone()
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],1)
        self.lookForDragonPad()
        natlink.playString('{ctrl+a}{del}')

        # now separate two parts. Note this cannot be checked here together,
        # because changes in natlinkmain take no effect when done from this
        # program!
        if natlinkmain.checkForGrammarChanges:
            # Modify the macro file and make sure the modification takes effect
            # even if the microphone is not toggled.

            self.log('\nNow change grammar file jMg1 to 2, check for changes at each utterance', 1)

            createMacroFile(baseDirectory,'__jMg1.py','2')
            self.wait(2)
            ## with checking at each utterance next two lines should pass
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)

        else:
            self.log('\nNow change grammar file jMg1 to 2, no recognise immediate, only after mic toggle', 1)

            createMacroFile(baseDirectory,'__jMg1.py','2')
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],1)
            toggleMicrophone(1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)

        # Make sure a user specific file also works
        self.log('now new grammar file: jMg2, 3', 1)
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],0)
        createMacroFile(userDirectory,'__jMg2.py','3')
        toggleMicrophone()
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],1)

        # Make sure user specific files have precidence over global files
        self.log('now new grammar file: jMg2, 4', 1)

        createMacroFile(baseDirectory,'__jMg2.py','4')
        toggleMicrophone()
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],1)

        # Make sure that we do the right thing with application specific
        # files.  They get loaded when the application is activated.
        self.log('now new grammar file: calc_jMg1, 5', 1)

        createMacroFile(baseDirectory,'calc__jMg1.py','5')
        toggleMicrophone()
        
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],0)
        self.lookForCalc()
##        natlink.execScript('AppBringUp "calc"')
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],1)
        self.killCalc()
    ##        natlink.playString('{Alt+F4}')
#-----------------------------------------------------------
        # clean up any files created during this test
        safeRemove(baseDirectory,'__jMg1.py')
        safeRemove(baseDirectory,'__jMg2.py')
        safeRemove(userDirectory,'__jMg2.py')
        safeRemove(baseDirectory,'calc__jMg1.py')
        toggleMicrophone()

        # now that the files are gone, make sure that we no longer recognize
        # from them
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','1'],0)
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','2'],0)
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','3'],0)
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','4'],0)
        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'Python','5'],0)

## is done in tearDown:
##        # make sure no .pyc files are lying around
##        safeRemove(baseDirectory,'__jMg1.pyc')
##        safeRemove(baseDirectory,'__jMg2.pyc')
##        safeRemove(userDirectory,'__jMg2.pyc')
##        safeRemove(baseDirectory,'calc__jMg1.pyc')


    #---------------------------------------------------------------------------

    def testWordProns(self):
        """Tests word pronunciations

        This test is very vulnerable for different versions of NatSpeak etc.

        1. To avoid clashes with testWordFuncs after each test the user profile is reloaded

        2. In version 9 apparently a new word is introduced with pronunciations,
        originally it was not.  To prevent this details the pronunciations
        that start with "frots" are ignored into testing (the word being "FrotzBlatz")

        3. The last three tests are skipped, overlap partly with WordFuncs tests

        may 2007, QH, natspeak 9.1 SP1 (Dutch package)

        """        
        
        self.log("testWordProns", 1)

        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        # allow for changes dgnwordflag_DNS8newwrdProp in version 8:
        testFuncReturnWordFlag = self.doTestFuncReturnWordFlag
        # strip 'frots' in front:
        testFuncPronsReturn = self.doTestFuncPronsReturn
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
        testFuncReturnWordFlag(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
        testFuncPronsReturn(['on'],"natlink.getWordProns('FrotzBlatz')")

        # add another pron
        testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,'and')")
        testFuncReturnWordFlag(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
        testFuncPronsReturn(['on','and'],"natlink.getWordProns('FrotzBlatz')")

        # add a few prons
        testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,['~','Dat'])")
        testFuncReturnWordFlag(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
        testFuncPronsReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

        # add a duplicate pron
        testFuncReturn(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded,'on')")
        testFuncReturnWordFlag(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')")
        testFuncPronsReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

        # try to change the flags
        testFuncReturn(1,"natlink.addWord('FrotzBlatz',0,'on')")
        testFuncReturnWordFlag(0,"natlink.getWordInfo('FrotzBlatz')")
        testFuncPronsReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

        # adding the word w/o prons does nothing even if the flags change
## fails in version 9 QH:
##        testFuncReturn(0,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded)")
##        testFuncReturnWordFlag(0,"natlink.getWordInfo('FrotzBlatz')")
##        testFuncPronsReturn(['on','and','~','Dat'],"natlink.getWordProns('FrotzBlatz')")

        # delete the word
        natlink.deleteWord('FrotzBlatz')

    #---------------------------------------------------------------------------
    # Performs a recognition mimic and makes sure that the mic succeeds or fails
    # as expected.

    def doTestRecognition(self, words,shouldWork=1):
        if shouldWork:
            natlink.recognitionMimic(words)
        else:
            self.doTestForException(natlink.MimicFailed,"natlink.recognitionMimic(words)",locals())

    #---------------------------------------------------------------------------
    # Test the Grammar parser

    def testParser(self):
        self.log("testParser", 1)

        def testGrammarError(exceptionType,gramSpec):
            try:
                parser = GramParser([gramSpec])
                parser.doParse()
                parser.checkForErrors()
            except exceptionType:
                return
            raise TestError,'Expecting an exception parsing grammar '+gramSpec

        # here we try a few illegal grammars to make sure we catch the errors
        # 
        testGrammarError(SyntaxError,'badrule;')
        testGrammarError(SyntaxError,'badrule = hello;')
        testGrammarError(SyntaxError,'= hello;')
        testGrammarError(SyntaxError,'<rule> error = hello;')
        testGrammarError(SyntaxError,'<rule> exported = hello')
        testGrammarError(LexicalError,'<rule exported = hello;')
        testGrammarError(SyntaxError,'<rule> exported = ;')
        testGrammarError(SyntaxError,'<rule> exported = [] hello;')
        testGrammarError(GrammarError,'<rule> = hello;')
        testGrammarError(SyntaxError,'<rule> exported = hello ];')
        testGrammarError(SyntaxError,'<rule> exported = hello {};')
        testGrammarError(SyntaxError,'<rule> exported = hello <>;')
        testGrammarError(GrammarError,'<rule> exported = <other>;')
        testGrammarError(SymbolError,'<rule> exported = one; <rule> exported = two;')
        testGrammarError(SyntaxError,'<rule> exported = hello | | goodbye;')
        testGrammarError(SyntaxError,'<rule> exported = hello ( ) goodbye;')
        testGrammarError(SyntaxError,'<rule> exported = hello "" goodbye;')
        
    #---------------------------------------------------------------------------
    # Here we test recognition of command grammars using GrammarBase    

    def testGrammar(self):
        self.log("testGrammar", 1)

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
                if self.sawBegin > nTries:
                    self.error = 'Command grammar called gotBegin twice'
                self.sawBegin += 1
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
        testRecognition = self.doTestRecognition
        testForException = self.doTestForException
        testActiveRules = self.doTestActiveRules
        
        # load the calculator again
        calcWindow = self.lookForCalc()
        # load the calculator again
##        time.sleep(5) # let the calculator recover from last test
##        natlink.execScript('AppBringUp "calc"')
##        print natlink.getCurrentModule()
##        calcWindow = natlink.getCurrentModule()[2]
        
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
##        switchToNatSpeak()
##        natWindow = natlink.getCurrentModule()[2]
##        natlink.playString('{Alt+space}n')
##        natlink.execScript('AppBringUp "calc"')
        natWindow = self.lookForDragonPad()
        calcWindow = self.lookForCalc()
        
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

        ##
        ## now do some additional checks on activateSet:
        ## (old bug in natlinkutils, QH)
        ##
        testGram.unload()
        testGram.load("""
            <one> exported = rule one <two>;
            <two> = rule two;
            <three> exported = rule three;
            <four> exported = rule four;
            """)
        testGram.activateAll()
        testActiveRules(testGram, ['one', 'three', 'four'])

        testGram.deactivateAll()
        testActiveRules(testGram, [])
        prev = None
        for rule in 'three', 'four', 'one', 'four', 'three':
            # activate:
            testGram.activate(rule)
            if prev:
                expList = [prev, rule]
            else:
                expList = [rule]
            testActiveRules(testGram, expList)
            # activate after all active:
            testGram.activateAll()
            testForException(GrammarError, "testGram.activate('%s')"% rule, locals())
            # activate after all unactive:
            testGram.deactivateAll()
            testGram.activate(rule)
            testActiveRules(testGram, [rule])
            prev = rule

        rule = 'one'
        testGram.activate(rule)
        testForException(GrammarError, "testGram.activate('%s')"% rule, locals())
        testGram.deactivateAll()
        testActiveRules(testGram, [])

        for SET in (['one', 'three', 'four'], ['three'], ['one', 'three', 'four'], ['one', 'three']):
            testGram.activateSet(SET)
            testActiveRules(testGram, SET)
            ##with original version of natlinkutils.py you get:
            ##AssertionError: Active rules not as expected:
            ##expected: ['three'], got: ['one', 'three']
            ##fix around line 420 (copy.copy) in natlinkutils.py, QH
    
            
        

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




        # clean up
        testGram.unload()
        otherGram.unload()
##        natlink.playString('{Alt+F4}')

    #---------------------------------------------------------------------------
    # Here we test recognition of dictation grammars using DictGramBase

    def testDictGram(self):
        self.log("testDictGram")

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
        testRecognition = self.doTestRecognition
        testForException =self.doTestForException
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
##        switchToNatSpeak()
##        natWindow = natlink.getCurrentModule()[2]
##        natlink.playString('{Alt+space}n')
##        natlink.execScript('AppBringUp "calc"')
        natWindow = self.lookForDragonPad()
        calcWindow = self.lookForCalc()
        
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
##        the test must close calc!
##        natlink.playString('{Alt+F4}')
        
    #---------------------------------------------------------------------------
    # Here we test recognition of selection grammars using SelectGramBase




    def testSelectGram(self):
        self.log("testSelectGram")

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
        testRecognition = self.doTestRecognition
        testForException =self.doTestForException
        # load the calculator again
        time.sleep(5) # let the calculator recover from last test
##        natlink.execScript('AppBringUp "calc"')
##        calcWindow = natlink.getCurrentModule()[2]
        calcWindow = self.lookForCalc()

####    numbers  giving problems QH:::
####        buffer = '0 1 2 3 4 5 6 7 8 9' 
##        testGram.setSelectText(buffer)
##        testGram.activate(window=calcWindow)
##        testRecognition(['Select','2'])
##        testGram.checkExperiment(1,'self',['Select','2'],4,5)
##
##        testRecognition(['Insert Before','2'])
##        testGram.checkExperiment(1,'self',['Insert Before','2'],4,5)

        #         012345678901234567890123
        buffer = 'a simple string of text.'
        testGram.load(['Select','Correct','Insert Before'],'Through')
        testGram.setSelectText(buffer)
        testGram.activate(window=calcWindow)
        
        testRecognition(['Correct','simple','Through','of'])
        testGram.checkExperiment(1,'self',['Correct','simple','Through','of'],2,18)
        testRecognition(['Select','text'])
        testGram.checkExperiment(1,'self',['Select','text'],19,23)

        testRecognition(['Insert Before','simple'])
        testGram.checkExperiment(1,'self',['Insert Before','simple'],2,8)
        
        testRecognition(['Correct','a','Through','of'])
        testGram.checkExperiment(1,'self',['Correct','a','Through','of'],0,18)


        # test for command failures
        testForException(TypeError,"testGram.gramObj.setSelectText(1)",locals())
        testForException(TypeError,"testGram.gramObj.setSelectText('text','text')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.emptyList('list')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.appendList('list','1')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.setContext('left','right')",locals())

        # clean up
        testGram.unload()
##        natlink.playString('{Alt+F4}')

    #---------------------------------------------------------------------------
    # Testing the tray icon is hard since we can not conviently interact with
    # the UI from this test script.  But I test what I can.    

    def testTrayIcon(self):
        self.log("testTrayIcon")

        testForException =self.doTestForException
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
## special test icon, assume baseDirectory is on same level as PyTest:
##          QH, cannot get baseDirectory correct...
        import natlinkmain
        baseDirectory = natlinkmain.baseDirectory
        iconFile = baseDirectory+'/../PyTest/unittest_icon.ico'
        if not os.path.isfile(iconFile):
            raise TestError("cannot find test iconfile: %s"% iconFile)
        natlink.setTrayIcon(iconFile)
        self.wait(2)
        natlink.setTrayIcon()

    #---------------------------------------------------------------------------
    # There used to be a problem with calling recognitionMimic from within a
    # recognitionMimic call.  This test tries to test the various combinations
    # to make sure things work OK.

    def testNestedMimics(self):
        self.log("testNestedMimics", 1)
        testForException = self.doTestForException
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
        ## this test failed once (QH), I think because gotBegin was missed
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

    ##def toggleMicrophone(wait=0):
    ##    natlink.setMicState('on')
    ##    natlink.setMicState('off')
    ##    time.sleep(wait)
    def toggleMicrophone(self, w=1):
        # do it slow, the changeCallback does not hit
        # otherwise
        micState = natlink.getMicState()
        if micState == 'on':
            self.log('switching off mic')
            natlink.setMicState('off')
            time.sleep(w)
            self.log('switching on mic')
            natlink.setMicState('on')
            time.sleep(w)
            self.log('switched on mic')
        else:        
            self.log('switching on mic')
            natlink.setMicState('on')
            time.sleep(w)
            self.log('switching to "%s" mic'% micState)
            natlink.setMicState(micState)
            time.sleep(w)
            self.log('switched to "%s" mic'% micState)
            time.sleep(w)


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
        elif self.sawTextChange != (delStart,delEnd,newText,selStart,selEnd):
            raise TestError('CallbackTester  more runs gives different results')
        

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
# Forces all macro files to be reloaded by toggling the microphone
# toggleMicrophone now as method above...

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
    f = os.path.join(filePath,fileName)
    open(f,'w').write(macroFileTemplate%word)
    import natlinkmain
    fileDate = natlinkmain.getFileDate(f)
    log('time of change of %s: %s'% (f, fileDate))
    
def log(t):
    """log to print and file if present

    note print depends on the state of natlink: where is goes or disappears...
    I have no complete insight is this, but checking the logfile afterwards
    always works (QH)
    """
    print t
    if logFile:
        logFile.write(t + '\n')
    
#---------------------------------------------------------------------------
# run
#
# This is the main entry point.  It will connect to NatSpeak and perform
# a series of tests.  In the case of an error, it will cleanly disconnect
# from NatSpeak and print the exception information,
def dumpResult(testResult, logFile):
    """dump into 
    """
    if testResult.wasSuccessful():
        mes = "all succesful"
        logFile.write(mes)
        return
    for case, tb in testResult.errors:
        logFile.write('\n---------- %s --------\n'% case)
        logFile.write(tb)
        
    logFile.write('\n--------------- failures -----------------\n')
    for case, tb in testResult.failures:
        logFile.write('\n---------- %s --------\n')
        logFile.write(tb)

    


logFile = None

def run():
    global logFile, natconnectOption
    logFile = open(logFileName, "w")
    log("log messages to file: %s"% logFileName)
    log('starting unittestNatlink')
    suite = unittest.makeSuite(UnittestNatlink, 'test')
##    natconnectOption = 0 # no threading has most chances to pass...
    log('\nstarting tests with threading: %s\n'% natconnectOption)
    result = unittest.TextTestRunner().run(suite)
    dumpResult(result, logFile=logFile)
    logFile.close()

if __name__ == "__main__":
    run()
