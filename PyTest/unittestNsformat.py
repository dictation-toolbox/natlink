#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# unittestNsformat.py
#   This script performs tests of the nsformat module, which was provided by Joel Gould and put into the
#   natlink Core folder by Quintijn, 2009
#
# run from a (preferably clean) US user profile, easiest from IDLE.
# do not run from pythonwin. See also README.txt in PyTest folder
#
# October, 2009, QH, added tests for nsformat

import sys, unittest, types
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
from nsformat import *

class TestError(Exception):
    pass
ExitQuietly = 'ExitQuietly'


# try some experiments more times, because gotBegin sometimes seems
# not to hit
nTries = 10
natconnectOption = 0 # or 1 for threading, 0 for not. Seems to make difference
                     # with spurious error (if set to 1), missing gotBegin and all that...
logFileName = r"D:\natlink\natlink\PyTest\testresult.txt"

#---------------------------------------------------------------------------
# These tests should be run after we call natConnect
class UnittestNsformat(unittest.TestCase):
    def setUp(self):
        if not natlink.isNatSpeakRunning():
            raise TestError,'NatSpeak is not currently running'
        self.connect()
        # remember user and get DragonPad in front:
        self.setMicState = "off"
        #self.lookForDragonPad()



    def tearDown(self):
        try:
            # give message:
            self.setMicState = "off"
            # kill things
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
        while i < 50:
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
        time.sleep(0.5)


    def isTopWindow(self, hndle):
        """return 1 if it is a top window, child otherwise

        (to avoid using unimacro functions in the natlink tests)
        """        
        try:
            parent = win32gui.GetParent(hndle)
        except:
            return 1
        else:
            return parent == 0 


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
    def doTestFuncReturnAlternatives(self, expected,command,localVars=None):
        
        # account for different values in case of [None, 0] (wordFuncs)
        # expected is a tuple of alternatives, which one of them should be equal to expected
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if type(expected) != types.TupleType:
            raise TestError("doTestFuncReturnAlternatives, invalid input %s, tuple expected"% `expected`)
        for exp in expected:
            if actual == exp:
                break
        else:
            self.fail('Function call "%s" returned unexpected result\nnot one of expected values: %s\ngot: %s'%
                          (command, `expected`, actual))

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

    def tttestPlayString(self):
        self.log("testPlayString", 0) # not to DragonPad!
        testForException =self.doTestForException
        testWindowContents = self.doTestWindowContents
        # test some obvious error cases
        testForException(TypeError,"natlink.playString()")
        testForException(TypeError,"natlink.playString(1)")
        testForException(TypeError,"natlink.playString('','')")
        self.wait()
        natlink.playString('This is a test')
##        try:
        self.wait()
        testWindowContents('This is a test','playString')
##        except KeyboardInterrupt:
##            # This failure sometimes happens on Windows 2000
##            print
##            print '*******'
##            print 'One of the NatLink tests has failed.'
##            print
##            print 'This particular failure has been seen on Windows 2000 when'
##            print 'there is a problem switching to Dragon NaturallySpeaking.'
##            print
##            print 'To fix this:'
##            print '(1) Switch to the Dragon NaturallySpeaking window'
##            print '(2) Switch back to Python'
##            print '(3) Try this selftest again - testnatlink.run()'
##            raise ExitQuietly

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

    def tttestExecScript(self):
        self.log("testExecScript", 1)

        testForException = self.doTestForException
        testForException( natlink.SyntaxError, 'natlink.execScript("UnknownCommand")' )

        # TODO this needs more test

# here we test the nsformat functions, (provided by Joel Gould, now in Core directory)
# in order to format a recognition (of DictGram) into a string, preserving the state
# of the formatting flags
    def testNsformat(self):
        self.log("testNsformat")
        pass
        testFuncReturn = self.doTestFuncReturn

        expected1 = ('Hello', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        testFuncReturn(expected1, 'formatWords(["hello"], %s)'% None, locals())

        expected2 = (' again.', [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        testFuncReturn(expected2, 'formatWords(["again", r".\period"], expected1[1])', locals())

        expected3 = ('  New sentence', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        testFuncReturn(expected3, 'formatWords(["new", "sentence"], expected2[1])', locals())

    def tttestFormatconvenstions(self):
        pass

   
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
    logFile.write('\n--------------- errors -----------------\n')
    for case, tb in testResult.errors:
        logFile.write('\n---------- %s --------\n'% case)
        logFile.write(tb)
        
    logFile.write('\n--------------- failures -----------------\n')
    for case, tb in testResult.failures:
        logFile.write('\n---------- %s --------\n'% case)
        logFile.write(tb)

    


logFile = None

def run():
    global logFile, natconnectOption
    logFile = open(logFileName, "w")
    log("log messages to file: %s"% logFileName)
    log('starting unittestNsformat')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def tttest....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    suite = unittest.makeSuite(UnittestNsformat, 'test')
##    natconnectOption = 0 # no threading has most chances to pass...
    log('\nstarting tests with threading: %s\n'% natconnectOption)
    result = unittest.TextTestRunner().run(suite)
    dumpResult(result, logFile=logFile)
    
    logFile.close()

if __name__ == "__main__":
    run()
