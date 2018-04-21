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
# February 2018, QH:
# with DPI15 a thorough testing again.
# the basic natlinkmain test
# September 2015, QH:
# start with importing natlinkmain and do natlinkmain.start_natlink(). Then baseDirectory etc. are filled.
#
# july 2012
# parser tests in unittest of QH (will be put in natlink at some time)
# test actual recognitions from different grammar constructs.
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
#     The testing will take only the function(s) you marked this way. Please do not forget to
#     change back when finished!!
#
# testWordProns and testWordFuncs are adapted to (I think) version 9, see the docstrings there...
#
# April 16, 2005 - sw
# got many, not all test working w/ v 8
# seach for '#This fails' to find broken tests


# April 1, 2000
#   - added testParser, testGramimar, testDictGram, testSelectGram
#
import six
import sys, unittest, types
import os
import os.path
import time
import string
import traceback        # for printing exceptions
from struct import pack


#--------- two utility functions:
def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder or baseFolder == '.':
        baseFolder = os.getcwd()
    return baseFolder

def getCoreDir(thisDir):
    """get the NatLink core folder, relative from the current folder

    This folder should be relative to this with ../MacroSystem/core and should
    contain natlinkmain.p, natlink.dll, and natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'MacroSystem', 'core') )
    if not os.path.isdir(coreFolder):
        print 'not a directory: %s'% coreFolder
        return thisDir
##    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
##    if not os.path.isfile(dllPath):
##        print 'natlink.dll not found in core directory: %s'% coreFolder
##        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder

thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('unittestNatlink cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'inserting %s to pythonpath...'% coreDir
    sys.path.insert(0, coreDir)

natconnectOption = 0 # or 1 for threading, 0 for not. Seems to make difference
                     # at least some errors in testNatlinkMain seem to be raised when set to 0
doSleep = 0.1
# set to a small (time) number if some tests should be slowed down
                     # eg doTestWindowContents
                     # especially after a paste action, some pause should be set..
                     # 0.1 seems to fit, 0.05 seems to be too short...
                     # see testNatlinkutilsPlayString and testPlayString

import natlink
import natlinkmain  # for Dragon 12, need recognitionMimic from natlinkmain
natlinkmain.start_natlink(natconnectOption) #?? otherwise baseDirectory etc have no values...
import gramparser
from natlinkutils import *
import natlinkutils
import win32gui

# make different versions testing possible:
import natlinkstatus
nlstatus = natlinkstatus.NatlinkStatus()
DNSVersion = nlstatus.getDNSVersion()
import natlink
class TestError(Exception):
    pass
class ShouldBeCommandError(Exception):
    pass # for testing commands to be commands, not dictate...
ExitQuietly = 'ExitQuietly'

def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder or baseFolder == '.':
        baseFolder = os.getcwd()
        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

thisDir = getBaseFolder(globals())


# try some experiments more times, because gotBegin sometimes seems
# not to hit
nTries = 10
logFileName = os.path.join(thisDir, "testresult.txt")

## try more special file names, test in testNatlinkMain:
spacesFilenameGlobal = '_with spaces'
spacesFilenameCalcInvalid = 'calc with spaces' # must be only "calc" or "calc_ ajajajaja"
spacesFilenameCalcValid = 'calc_with underscore'   
specialFilenameCalc = 'calc_JMg+++&_'
specialFilenameGlobal = '__jMg_$&^_abc'
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
        self.clearTestFiles()
        if not natlink.isNatSpeakRunning():
            raise TestError('NatSpeak is not currently running')
        self.connect()
        # remember user and get DragonPad in front:
        self.user = natlink.getCurrentUser()[0]
        self.setMicState = "off"
        self.komodoHndle = natlink.getCurrentModule()[2]
        self.lookForDragonPad()
        # self.lookForWord()
        
    def tearDown(self):
        try:
            # give message:
            self.setMicState = "off"
            # kill things
            self.killCalc()
            self.lookForDragonPad()
            natlink.playString("\n\ntearDown, reopen user: '%s'"% self.user)
            self.clearTestFiles()
            self.clearDragonPad()
            # reopen user:
            #natlink.openUser(self.user)
            #self.killDragonPad()
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
    def lookForWord(self):
        """try some tests with word,
        """
        natlink.execScript('AppBringup "winword"')
        i = 0
        while i < 50:
            time.sleep(0.2)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            print 'mod: %s'% mod
            if mod == 'winword':
                print 'got word after %s steps'% i
                break
            i += 1
        natlink.playString("{ctrl+a}{ctrl+c}")
        self.wait(1)
        t = natlink.getClipboard()
        if t:
            natlink.playString("{ctrl+n}")
            self.wait(0.5)
        

    def lookForDragonPad(self):
        """start/find DragonPad"""

##        try: natlink.execScript('AppBringUp "NatSpeak"')
##        except natlink.NatError:
##            raise TestError,'The NatSpeak user interface is not running'
##         ??? Start instead of start ???
        natlink.recognitionMimic(['Start', "DragonPad"])
        
        # This will make sure that the NatSpeak window is empty.  If the NatSpeak
        # window is not empty we raise an exception to avoid possibily screwing 
        # up the users work.
        i = 0
        while i < 50:
            time.sleep(0.2)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            # print 'mod: %s'% mod
            if mod == "natspeak": break
            i += 1
            print 'waiting for DragonPad: %s'% i
        else:
            self.fail("Not the correct application: %s is brought to the front, should be natspeak"% mod)
        self.DragonPadMod = mod
        self.DragonPadHndle = hndle
        return hndle

    def clearDragonPad(self):
        """check DragonPad in foreground and send """

##        try: natlink.execScript('AppBringUp "NatSpeak"')
##        except natlink.NatError:
##            raise TestError,'The NatSpeak user interface is not running'
##         ??? Start instead of start ???
        mod, title, hndle = natlink.getCurrentModule()
        mod = getBaseName(mod)
        print 'mod: %s'% mod
        if mod != "natspeak":
            raise TestError("clearDragonPad: DragonPad should be in the foreground, not: %s"% mod)
        natlink.playString("{ctrl+a}{del}")
        time.sleep(0.2)
    
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

        natlink.execScript('SendSystemKeys "{numkey*}"')
        time.sleep(0.5)
        natlink.execScript('SendSystemKeys "{esc}"')
        time.sleep(0.5)
        
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
            wantHndle = self.CalcHndle
        except AttributeError:
            # not active:
            return
        i = 0
        while i < 10:
            try:
                win32gui.SetForegroundWindow(wantHndle)
            except:
                pass
            time.sleep(0.1)
            mod, title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "calc" and hndle == wantHndle : break
            natlink.playString("{alt+tab}", 0x200)
            i += 1
        else:
            raise TestError("in killCalc, could not get back to Calc window")
        if i:
            print 'got calc after %s steps'
        natlink.playString("{alt+f4}")
        time.sleep(0.5)

    def clearTestFiles(self):
        """remove .py and .pyc files from the natlinkmain test

        """
        baseDirectory = natlinkmain.baseDirectory
        userDirectory = natlinkmain.userDirectory
        unimacroDirectory = natlinkmain.unimacroDirectory
        for dir in (baseDirectory, unimacroDirectory, userDirectory):
            for trunk in ('__jMg1', '__jMg2', 'calc__jMg1',
                          specialFilenameGlobal, specialFilenameCalc,
                          spacesFilenameGlobal, spacesFilenameCalcValid, spacesFilenameCalcInvalid,
                          "_", "calc_", "calculator"):
                for ext in ('.py', '.pyc'):
                    safeRemove(dir, trunk + ext)

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


    def wait(self, t=None):
        """wait some time, doSleep (if set) or 0.1 or whatever is passed
        """
        if t is None:
            t = doSleep or 0.1
        time.sleep(t)


    #---------------------------------------------------------------------------
    # These test should be run before we call natConnect (now in unittestPrePost.py)

##    def preTests(self):
##    def postTests(self): # now in unittestPrePost

    #---------------------------------------------------------------------------
    # This utility subroutine executes a Python command and makes sure that
    # an exception (of the expected type) is raised.  Otherwise a TestError
    # exception is raisedhello world

    def doTestForException(self, exceptionType,command,localVars={}):
        try:
            exec(command,globals(),localVars)
        except exceptionType:
            return
        raise TestError('Expecting an exception to be raised calling %s'% repr(command))

    def doTestFuncPronsReturn(self, expected,command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        if localVars == None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        # actual2 = [p for p in actual if not p.startswith('frots')]        

        if actual is None:
            self.fail('doTestFuncPronsReturn: word does not exist: command; "%s"'% command)
        if type(expected) == types.TupleType:
            for e in expected:
                if actual == e:
                    return
            else:
                self.fail('doTestFuncPronsReturn: actual (%s) does not match one of the expected results (%s), command: "%s"'%
                          (actual, repr(expected), command))
        else:
            self.assertEqual(expected, actual,
                         'doTestFuncPronsReturn, actual (%s) does not match expected (%s), command: "%s"'%
                         (actual, expected, command))

    def doTestActiveRules(self, gram, expected):
        """gram must be a grammar instance, sort the rules to be expected and got
        """
        got = gram.activeRules
        if type(got) != types.DictType:
            raise TestError('doTestActiveRules, activeRules should be a dict, not: %s (%s)'% (repr(got), type(got)))
        if type(expected) != types.DictType:
            raise TestError('doTestActiveRules, expected should be a dict, not: %s (%s)'% (repr(expected), type(expected)))
        
        self.assertEqual(expected, got,
                         'Active rules not as expected:\nexpected: %s, got: %s'%
                         (expected, got))

    def doTestValidRules(self, gram, expected):
        """gram must be a grammar instance, sort the rules to be expected and got
        """
        got = gram.validRules
        if type(got) != types.ListType:
            raise TestError('doTestValidRules, activeRules should be a list: %s (%s)'% (repr(got), type(got)))
        if type(expected) != types.ListType:
            raise TestError('doTestValidRules, expected should be a list, not: %s (%s)'% (repr(expected), type(expected)))
        got.sort()
        expected.sort()
        
        self.assertEqual(expected, got,
                         'Valid rules not as expected:\nexpected: %s, got: %s'%
                         (expected, got))


    #---------------------------------------------------------------------------
    # This utility subroutine will returns the contents of the NatSpeak window as
    # a string.  It works by using playString to select the contents of the 
    # window and copy it to the clipboard.  We have to also add the character 'x'
    # to the end of the window to handle the case that the window is empty.

    def getWindowContents(self):
        """get the foreground window contents, used mainly in DragonPad
        use natlink.playString, and insert pauses 
        """
        clearClipboard()
        self.wait()
        natlink.playString('{ctrl+end}x{ctrl+a}')
        self.wait()
        natlink.playString('{ctrl+c}')
        self.wait()
        contents = natlink.getClipboard()
        self.wait()
        natlink.playString('{ctrl+end}{backspace}')
        if contents == '':
            return ''
        if contents[-1:] !='x':
            raise TestError,'Failed to read the contents of the NatSpeak window: |%s|'% repr(contents)
        return contents[:-1]

    def doTestWindowContents(self, expected,testName=None, stripResult=None):
        """test contents of the windows, slowing down if doSleep is set
        """
        if doSleep: time.sleep(doSleep)
        contents = self.getWindowContents()
        if stripResult:
            contents, expected = contents.strip(), expected.strip()
        if contents != expected:
            mes = 'Contents of window did not match expected text\nexpected: |%s|\ngot: |%s|'% \
                  (expected, contents)
            if testName:
                mes = mes + '\ntestname %s'% testName
            self.fail(mes)
                
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

    def doTestEqualLists(self, expected, got, message):
        if expected == got:
            return
        self.fail("Fail in doTestEqualLists: %s\nexpected: %s\ngot: %s"% (message, expected, got))

    def doTestSplitApartLines(self, func, input, expected):
        got = func(input)
        if expected == got:
            return
        self.fail("Fail in doTestSplitApartLines: %s\nexpected: %s\ngot: %s"% (input, expected, got))
        
        

    def doTestEqualDicts(self, expected, got, message):
        if expected == got:
            return
        self.fail("Fail in doTestEqualDicts: %s\nexpected: %s\ngot: %s"% (message, expected, got))

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
    # Test extra functions of NatLink (getUser, getAllUsers)

    def testGetAllUsersEtc(self):
        self.log("testGetAllUsersEtc", 0) # not to DragonPad!
        currentUser = natlink.getCurrentUser()[0]
        
        allUsers = natlink.getAllUsers()
        print 'all Users: %s'% allUsers
        
        self.assert_(currentUser in allUsers, "currentUser should be in allUsers list")
        
        
##        try:
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
        self.wait()
        natlink.playString('This is a test')
        testWindowContents('This is a test','playString')

        natlink.playString('{ctrl+a}{ctrl+c}{end}{ctrl+v}{backspace 9}')
        testWindowContents('This is a testThis i','playString')

        natlink.playString('{ctrl+a}{del}')
        natlink.playString('testing',hook_f_shift)
        testWindowContents('Testing','playString')

        natlink.playString(' again')
        natlink.playString('a{ctrl+c}{del}',hook_f_ctrl)
        # paste contents via menu command using alt:
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
        
        # now try accented characters and unicode strings:
        natlink.playString('ge\xe9\xfatest{backspace}')
        testWindowContents('ge\xe9\xfates','playString')
        #
        ## open and close a dialog
        natlinkutils.playString("{ctrl+a}Testing dialog window")
        testWindowContents('Testing dialog window')
        natlinkutils.playString('{ctrl+o}{esc}')
        testWindowContents('Testing dialog window')

        natlink.playString('{ctrl+a}{del}')
        testWindowContents('','playString empty')



    def testNatlinkutilsPlayString(self):
        """this version captions accented and unicode characters (possibly)
        
        Can also work around the double or drop first character by using the shift key trick
        
        Works with SendInput (mdl), if option has been chosen in natlinkutils
                
        """
        self.log("testNatlinkutilsPlayString", 0) # not to DragonPad!
        testForException =self.doTestForException
        testWindowContents = self.doTestWindowContents

        natlinkutils.playString('This is a test')
        testWindowContents('This is a test','playString')
        # here play with the sleeps necessary:
        natlinkutils.playString('{ctrl+a}{ctrl+c}{end}{ctrl+v}')
        if doSleep: time.sleep(doSleep)
        natlinkutils.playString('{backspace 9}')
        testWindowContents('This is a testThis i','playString')

        natlinkutils.playString('{ctrl+a}{del}')
        natlinkutils.playString('testing',hook_f_shift)
        testWindowContents('Testing','playString')

        natlinkutils.playString(' again')
        testWindowContents('Testing again','playString')
        natlinkutils.playString('a{ctrl+c}{del}',hook_f_ctrl)
        # paste contents via menu command using alt:
        # this one is sent through to natlink.playString:
        natlinkutils.playString('ep',hook_f_alt)
        if doSleep: self.wait()
        testWindowContents('Testing again\r\n','playString')

        natlinkutils.playString('a{ctrl+c}{del}',hook_f_rightctrl)
        natlinkutils.playString('ep',hook_f_rightalt)
        if doSleep: self.wait()
        natlinkutils.playString('now hook rightctrl',hook_f_rightshift)
        testWindowContents('Testing again\r\n\r\nNow hook rightctrl','playString')

        # this one should be handled by the SendKeys of Mark:
        natlinkutils.playString('{backspace 26} with only SendKeys')
        testWindowContents('Testing with only SendKeys','playString')
        natlinkutils.playString('{ctrl+a}{ctrl+c}{del}')
        # paste contents via menu command using alt:
        natlinkutils.playString('{alt+e}p')
        testWindowContents('Testing with only SendKeys\r\n','playString')

        # now try accented characters and unicode strings:
        natlinkutils.playString('{ctrl+a}{del}ge\xe9\xfatest{backspace}')
        testWindowContents('ge\xe9\xfates','playString')
        natlinkutils.playString('{ctrl+a}{del}')
        testWindowContents('','playString empty')

        natlinkutils.playString('simple string')
        testWindowContents('simple string','natlinkutils.playString')        

        natlinkutils.playString('{ctrl+a}{del}')
        testWindowContents('','empty window playString')        


        natlinkutils.playString(u'\u0041-xyz-\u00e9-abc-')
        testWindowContents('A-xyz-\xe9-abc-','natlinkutils.playString')


        #
        ## open and close a dialog
        natlinkutils.playString("{ctrl+a}Testing dialog window")
        testWindowContents('Testing dialog window')
        natlinkutils.playString('{ctrl+o}{esc}')
        testWindowContents('Testing dialog window')
        

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
        dictObj = natlink.DictObj()
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
        callTest.doTestTextChange(moduleInfo,(0,0,'Hello',5,5))
        natlink.recognitionMimic(['there'])
##        self.wait()
        ##              012345678901
        testFuncReturn('Hello there',"dictObj.getText(0)",locals())
        callTest.doTestTextChange(moduleInfo,(5,5,' there',11,11))

        dictObj.setTextSel(0,5)
        natlink.recognitionMimic(['and'])
        testFuncReturn('And there',"dictObj.getText(0)",locals())
        
    #v5/9
    # version 9 gived (???)) (0, 6, 'And ', 3, 3) here:
    # version 10 gives (0, 6, 'And ', 4, 4) here:
        if DNSVersion <= 9:
            callTest.doTestTextChange(moduleInfo,(0,6,'And ',3, 3))
        else:
            callTest.doTestTextChange(moduleInfo,(0,6,'And ',4, 4))
    #else
##        callTest.doTestTextChange(moduleInfo,(0,5,'And',3,3))

        dictObj.setTextSel(3,3)
        if DNSVersion < 11:
            natlink.recognitionMimic([r',\comma'])
        else:
            natlink.recognitionMimic([r',\comma\comma'])
            
##        self.wait()
        testFuncReturn('And, there',"dictObj.getText(0)",locals())
        callTest.doTestTextChange(moduleInfo,(3,3,',',4,4))


        # lots of problems, must be sorted out, QH, august 2011
        return


        dictObj.setTextSel(5)
        natlink.recognitionMimic(['another','phrase'])
##        self.wait()
        testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
        # unimacro version stops here, no beginCallback:::
        
        
        # versions 10 and 11 seem to have an intermediate result, just selecting with empty text
        # this is also apparent in _kaiser_dictation, not tested very thorough...
        #callTest.doTestTextChange(moduleInfo,(4,4,'', 4, 10))
        
        # from here problems, should be sorted out (QH, august 2011, working on Dragon 11)
        return
    
    
        callTest.doTestTextChange(moduleInfo,(4,10,' another phrase',19,19))
    #else        callTest.doTestTextChange(moduleInfo,(5,10,'another phrase',19,19))

        natlink.recognitionMimic(['more'])
##        self.wait()
        testFuncReturn('And, another phrase more',"dictObj.getText(0)",locals())
        callTest.doTestTextChange(moduleInfo,(19,19,' more',24,24))

        # the scratch that command undoes one recognition
        natlink.recognitionMimic(['scratch','that'])
##        self.wait()
        testFuncReturn('And, another phrase',"dictObj.getText(0)",locals())
        callTest.doTestTextChange(moduleInfo,(19,24,'',19,19))

        # NatSpeak optimizes the changed block so we only change 'ther' not
        # 'there' -- the last e did not change.
        natlink.recognitionMimic(['scratch','that'])
        self.wait()
        
        testFuncReturn('And, there',"dictObj.getText(0)",locals())
        callTest.doTestTextChange(moduleInfo,(5,18,'ther',5,10))

        # fill the buffer with a block of text
        # char index:    0123456789 123456789 123456789 123456789 123456789 123456789 
        dictObj.setText('This is a block of text.  Lets count one two three.  All done.',0)
        dictObj.setTextSel(0,0)
        dictObj.setVisibleText(0)

        # ok, test selection command
        natlink.recognitionMimic(['select','block','of','text'])
##        self.wait()
        
        testFuncReturn((10,23),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,(10,10,'',10,23))
        
        natlink.recognitionMimic(['select','one','through','three'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,(37,37,'',37,50))

        # text selection of non-existant text
        testForException(natlink.MimicFailed,"natlink.recognitionMimic(['select','helloxxx'])")
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,None)

        # now we clamp down on the visible range and prove that we can select
        # within the range but not outside the range
        dictObj.setVisibleText(10,50)
        dictObj.setTextSel(0,0)
        
        natlink.recognitionMimic(['select','one','through','three'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,(37,37,'',37,50))

        #This is a block of text.  Lets count one two three.  All done.
        natlink.recognitionMimic(['select','this','is'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,None)

        natlink.recognitionMimic(['select','all','done'])
##        self.wait()
        testFuncReturn((37,50),"dictObj.getTextSel()",locals())
        callTest.doTestTextChange(moduleInfo,None)
            
        # close the calc (now done in tearDown)
##        natlink.playString('{Alt+F4}')


    def testRecognitionMimicCommands(self):
        """test different phrases with commands, from own grammar
        
        explore when the recognitionMimic fails
        
        At the moment Febr 2018, commands with listst seem to fail (QH) TODO
        """
        class TestGrammar(GrammarBase):

            gramSpec = """
                <runone> exported = mimic runone;
                <runtwo> exported = mimic two {colors};
                <runthree> exported = mimic three <extraword>;
                <runfour> exported = mimic four <extrawords>;
                <runfive> exported = mimic five <extralist>;
                <runsix> exported = mimic six {colors}+;
                <runseven> exported = mimic seven <wordsalternatives>;
                <runeight> exported = mimic eight <wordsalternatives> [<wordsalternatives>+];
                <optional>  = very | small | big;
                <extralist> = {furniture};
                <extraword> = painting ;
                <extrawords> = modern painting ;
                <wordsalternatives> = house | tent | church | tower;
            """       
            def initialize(self):
                self.load(self.gramSpec, allResults=1)
                self.activateAll()
                self.setList('colors', ['red', 'green', 'blue'])
                self.setList('furniture', ['table', 'chair'])
                self.testNum = 0

            def resetExperiment(self):
                # self.sawBegin = 0
                self.recogType = None
                # self.words = []
                # self.fullResults = []
                # self.error = None

            def gotBegin(self,moduleInfo):
                self.resetExperiment()

            def gotResultsObject(self,recogType,resObj):
                self.recogType = recogType

        self.log("test recognitionMimicCommands, version: %s"% DNSVersion, 1)
        self.clearDragonPad()
        self.doTestWindowContents("")
        testCommandRecognition = self.doTestCommandRecognition
        testGram = TestGrammar()
        testGram.initialize()

        ## ruleone:
        testCommandRecognition(['hello', 'world'], shouldWork=0, testGram=testGram)  
        testCommandRecognition(['mimic', 'runone'], shouldWork=1, testGram=testGram)  

        #  <runthree> exported = mimic three <extraword>;
        testCommandRecognition(['mimic', 'three', 'painting'], shouldWork=1, testGram=testGram)  
         
        # <runfour> exported = mimic four <extrawords>;
        testCommandRecognition(['mimic', 'four', 'modern', 'painting'], shouldWork=1, testGram=testGram)  

        # <runfive> exported = mimic five <extralist>; ## fails DPI15
        # testCommandRecognition(['mimic', 'five', 'table'], shouldWork=1, testGram=testGram)  

        # <runseven> exported = mimic seven <wordsalternatives>;
        testCommandRecognition(['mimic', 'seven', 'tent'], shouldWork=1, testGram=testGram)  
        testCommandRecognition(['mimic', 'seven', 'tower'], shouldWork=1, testGram=testGram)  

        # <runeight> exported = mimic eight <wordsalternatives> [<wordsalternatives>+];
        testCommandRecognition(['mimic', 'eight', 'tower'], shouldWork=1, testGram=testGram)  
        testCommandRecognition(['mimic', 'eight', 'tower', 'tent'], shouldWork=1, testGram=testGram)  
        testCommandRecognition(['mimic', 'eight', 'tower', 'tent', 'house', 'tower', 'tent', 'house', 'tower', 'church'], shouldWork=1, testGram=testGram)  

        ## ruletwo  fails DPI15
        testGram.testNum = 2
        testCommandRecognition(['mimic', 'two', 'green'], shouldWork=1, testGram=testGram)  


    #---------------------------------------------------------------------------
       
    def testRecognitionMimic(self):
        """test different phrases with spoken forms,
        
        since Dragon 11, lots of things have changed here, so it seems good to make a special
        test for this.
        
        Results are stripped (no spacing at start or end) before testing.
        
        Assume US English User, but UK now also works.
        
        If DragonPad does not come up, close down Dragon (all instances) and retry.
        """
        self.log("test recognitionMimic, version: %s"% DNSVersion, 1)
        self.clearDragonPad()
        testMimicResult = self.doTestMimicResult
        self.doTestWindowContents("")

        if DNSVersion == 12:
            words = 'test'
            expected = 'Test'
            testMimicResult(words, expected)

            words = ['hello', 'testing']
            expected = 'Test hello testing'
            testMimicResult(words, expected)
            return


        if DNSVersion >= 11:
            # spelling letters (also see voicecode/sr_interface)
            total = []
            self.log("Test recognition mimic of characters (adding up in the Dragonpad window)")
            for word, expected in [(r'a\determiner', 'A'),
                         (r'A\letter', 'A A'),
                         # (r'A\letter\alpha', 'A AA'), ## not in DPI15 (any more)
                         (r'a\lowercase-letter\lowercase A', 'A A a'),
                         # (r'a\lowercase-letter\lowercase alpha', 'A AAaa'), # not in DPI 15
                         (r'A\uppercase-letter\uppercase A', 'A A a A'),
                         # (r'A\uppercase-letter\uppercase alpha', 'A AAaaAA'), ## not in DPI15 (any more)
                         ([r'I\letter'], 'A A a A I'),
                         ([r'I\pronoun'], 'A A a A I I'),
                         ([r'X\letter', r'I\pronoun', r'Y\letter'], 'A A a A I I X I Y'),
                         ]:
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                    total.append(word)
                else:
                    words = word[:]
                    total.extend(words)
                self.log("try to mimic %s (expect: %s)"% (words, expected))
                testMimicResult(words, expected)
            
            time.sleep(0.5)
            self.clearDragonPad()
            # total string in once:
            self.log('testing total: %s (expecting: %s)'% (total, expected))
            # the letters stick together if pronounced in one utterance: 
            expected = 'A AaAI I X I Y' 
            testMimicResult(total, expected)
            self.clearDragonPad()
            
            
            ## numbers:            
            for word, expected in [(r'one\pronoun', 'One'),
                         (r'one\number', 'One'),
                         (['two', 'three', 'four', 'five'], '2345'), 
                         (['six', 'seven', 'eight', 'nine'], '6789')]:
            
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                    total.append(word)
                else:
                    words = word[:]
                    total.extend(words)
                testMimicResult(words, expected)
                self.clearDragonPad()

            # control characters:
            for word, expected in [(r'.\period\full stop', '.'),
                        (r'.\dot\dot', '.'), 
                        (r',\comma\comma', ','),
                        ([r'\caps-on\caps on', 'hello', 'world'], 'Hello World'),
                        ([r'\all-caps-on\all caps on', 'hello', 'world'], 'HELLO WORLD')]:
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                else:
                    words = word[:]
                testMimicResult(words, expected)
                self.clearDragonPad()

            # try shorter forms:
            for word, expected in [
                        ([r'\caps-on', 'hello', 'world'], 'Hello World'),
                        ([r'\all-caps-on', 'hello', 'world'], 'HELLO WORLD')]:
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                else:
                    words = word[:]
                testMimicResult(words, expected)
                self.clearDragonPad()
                
        else:
            # NatSpeak <= 10:
            # spelling letters (also see voicecode/sr_interface)
            total = []
            for word, expected in [(r'a', 'A'),
                         (r'A.', 'A A.'),
                         (r'a\alpha', 'A A. a'),
                         ([r'I.', r'i\india'], 'A A. a I. i'),
                         ]:
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                    total.append(word)
                else:
                    words = word[:]
                    total.extend(words)
                testMimicResult(words, expected)
            
            time.sleep(0.5)
            self.clearDragonPad()
            # total string in once:
            expected = 'A A. a I. i' # not clear why now a space at end of result.
            testMimicResult(total, expected)
            self.clearDragonPad()
            
            
            ## numbers:            
            for word, expected in [(r'one', 'One'),
                         #(r'1\one', 'One'),
                         (['two', 'three', 'four', 'five'], '2345'), 
                         (['six', 'seven', 'eight', 'nine'], '6789')]:
            
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                    total.append(word)
                else:
                    words = word[:]
                    total.extend(words)
                testMimicResult(words, expected)
                self.clearDragonPad()

            # control characters:
            for word, expected in [(r'.\full-stop', '.'),
                        (r'.\dot', '.'), 
                        (r',\comma', ','),
                        ([r'\Caps-On', 'hello', 'world'], 'Hello World'),
                        ([r'\All-Caps-On', 'hello', 'world'], 'HELLO WORLD')]:
                if type(word) in (six.text_type, six.binary_type):
                    words = [word]
                else:
                    words = word[:]
                testMimicResult(words, expected)
                self.clearDragonPad()
            # end of testing recognitionMimic for NatSpeak <= 10    

        
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
        
        
        with Dragon 11:
            DNSVersion is used to separate tests, eg in Dragon 11
            letters have become A\\letter or A\\letter\\alpha etc
            AND existing words seem to return only 8, so only testing word existence
            
        
        """
        self.log("testWordFuncs", 1)
        # getWordInfo #
        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        testFuncPronsReturn = self.doTestFuncPronsReturn
        testFuncReturnAlt = self.doTestFuncReturnAlternatives
        testFuncReturnWordFlag = self.doTestFuncReturnWordFlag
        # two alternatives permitted (QH)
        testFuncReturnNoneOr0 = self.doTestFuncReturnNoneOr0
        testForException(TypeError,"natlink.getWordInfo()")
        testForException(TypeError,"natlink.getWordInfo(1)")
        testForException(TypeError,"natlink.getWordInfo('hello','flags')")
        testForException(natlink.ValueError,"natlink.getWordInfo('hello',-1)")
        testForException(natlink.ValueError,"natlink.getWordInfo('hello',8)")
        testForException(natlink.InvalidWord,"natlink.getWordInfo('a\\b\\c\\d\\f')")
        if DNSVersion <= 11:
            # unclear why 'bbbbbbbbbbbbbbbbbbbbbbbbbbbb' is accepted by Dragon 12 QH/Rudiger febr 2013
            testForException(natlink.InvalidWord,"natlink.getWordInfo('b'*200)")

        # Assumptions:
        #
        # (1) User has not modified wordInfo flags of common words
        # (2) FrotzBlatz is not in the vocabulary
        # (3) Szymanski has not been moved to the dictation state
        # (4) HeLLo (with that capitalization) is not in the vocabulary

        # version 10 gives  8 in next test ("word cannot be deleted"), the list of  arguments give valid alternative\
        # return values...
        # Dragon 11 seems to give only 8 as return, in other words, only word existence can be tested with this mechanism...
        normalWordInfo = (0, 8) # accepted alternatives for a function call (must be a tuple)
            
        testFuncReturnAlt(normalWordInfo, "natlink.getWordInfo('hello')")
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello',0)") # same as call above
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello',1)") # also look in backup dictionary
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello',2)") # consider non-dictation words (???)
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello',3)") # 1 and 2 together
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('Hello',4)") # search case insensitive
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hELLo',4)") # search case insensitive
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hellO',5)") # case insensitive with above combinations
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('heLLo',6)")
        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello',7)")

        if DNSVersion >= 11:
            commaWord = r',\comma\comma'
            hyphenWord = r'-\hyphen\hyphen'
        else:
            commaWord = r',\comma'
            hyphenWord = r'-\hyphen'
            
        
        if DNSVersion < 11:
            testFuncReturnWordFlag(dgnwordflag_nodelete+dgnwordflag_no_space_before + dgnwordflag_no_space_next,
                       "natlink.getWordInfo(r'%s')"% hyphenWord)
            testFuncReturnWordFlag(dgnwordflag_nodelete+dgnwordflag_no_space_before,
                       "natlink.getWordInfo(r'%s')"% commaWord)
        else: # in Dragon 11 only 8 as return value
            testFuncReturn(8, "natlink.getWordInfo('%s')"% hyphenWord)
            testFuncReturn(8, "natlink.getWordInfo('%s')"% commaWord)
            
        # extra words:
        if DNSVersion >= 11:
            # spelling letters (also see voicecode/sr_interface)
            for word in [r'a\determiner', r'A\letter', r'A\letter\letter A',
                         r'a\lowercase-letter\lowercase A',
                         #r'a\lowercase-letter\lowercase alpha',
                         r'A\uppercase-letter\uppercase A',
                         #r'A\uppercase-letter\uppercase alpha',
                         r'I\letter', r'I\pronoun', r'I\letter\letter I',
                         ]:
                cmdLine = "natlink.getWordInfo(r'%s')"% word
                testFuncPronsReturn(normalWordInfo, cmdLine)  # accept 0 or 8.

            # numbers:            
            for word in [r'one\pronoun', r'one\number', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                         'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred']:
                cmdLine = "natlink.getWordInfo(r'%s')"% word
                testFuncReturn(8, cmdLine)

            for word in [r'.\period\period', r'.\dot\dot', r',\comma\comma',
                         r'\new-paragraph\new paragraph']:
                cmdLine = "natlink.getWordInfo(r'%s')"% word
                testFuncReturn(8, cmdLine)
                



            ## spell mode letters:
            #for word in [r'u\spelling-letter\U', '\xf6\\spelling-letter\\O umlaut',
            #                '\xfc\\spelling-letter\\U umlaut',
            #                '\xfc\\spelling-letter\\uniform umlaut']:
            #    cmdLine = "natlink.getWordInfo(r'%s')"% word
            #    testFuncReturn(8, cmdLine)



        #testFuncReturnWordFlag(dgnwordflag_nodelete+dgnwordflag_title_mode,
        #               "natlink.getWordInfo('and')")
        #
        # this none/0 stuff is nonsense
        #if this test does not pass, the word FrotzBlatz is (erroneously) inserted in your vocab. Do not worry,
        #just run the tests from a clean user profile
        testFuncReturn(None, "natlink.getWordInfo('FrotzBlatz',0)")
        testFuncReturn(None, "natlink.getWordInfo('FrotzBlatz',7)")

            


        
        #
        #sw my dict _has_ Szymanski
        #
        testWord = 'Szymanskii'
        if not natlink.getWordInfo(testWord) is None:
            print 'word not in active vocabulary'
            natlink.deleteWord(testWord)
        testFuncReturn(None, "natlink.getWordInfo('%s',0)"% testWord)

        #
        #
        #testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',0)")
        #testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',6)")
        #testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        #testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        #testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',5)")
        #
        testFuncReturn(None,"natlink.getWordInfo('HeLLo',0)") # strange capitalization
        testFuncReturnAlt(normalWordInfo, "natlink.getWordInfo('HeLLo',4)")  # case insensitive search
        
        # setWordInfo
        if DNSVersion < 11:
            testForException(TypeError,"natlink.setWordInfo()")
            testForException(TypeError,"natlink.setWordInfo(1)")
            testForException(TypeError,"natlink.setWordInfo('hello')")
            testForException(TypeError,"natlink.setWordInfo('hello','')")
    
            testFuncReturnAlt(normalWordInfo, "natlink.getWordInfo('hello')")
            natlink.setWordInfo('hello',dgnwordflag_nodelete)
            testFuncReturn(dgnwordflag_nodelete,"natlink.getWordInfo('hello')")
            natlink.setWordInfo('hello',0)
            natlink.setWordInfo('hello',dgnwordflag_nodelete)
            # nodelete_flag is not cleared in version 10:
            testFuncReturn(dgnwordflag_nodelete, "natlink.getWordInfo('hello')")
    
            testForException(natlink.UnknownName,"natlink.setWordInfo('FrotzBlatz',0)")
            testForException(natlink.UnknownName,"natlink.setWordInfo('Szymanskii',0)") 
            testForException(natlink.InvalidWord,"natlink.setWordInfo('a\\b\\c\\d\\f',0)")
        
        # addWord #

        testForException(TypeError,"natlink.addWord()")
        testForException(TypeError,"natlink.addWord(1)")
        testForException(TypeError,"natlink.addWord('FrotzBlatz','hello')")
        testForException(natlink.InvalidWord,"natlink.addWord('a\\b\\c\\d\\f')")

        testFuncReturnAlt(normalWordInfo,"natlink.getWordInfo('hello')")
    ## version 8: problems
    ## version 15: 
        testFuncReturn(0,"natlink.addWord('hello',dgnwordflag_nodelete)")
        testFuncPronsReturn(normalWordInfo,"natlink.getWordInfo('hello')") ## 0 or 8
        
        #testFuncReturnNoneOr0("natlink.setWordInfo('FrotzBlatz')")
        #testFuncReturnWordFlag(1,"natlink.addWord('FrotzBlatz',dgnwordflag_useradded)")
        # The first time we run this code, the extra internal use only flag
        # 0x20000000 is added to this word.  But if ytou run the test suite
        # twice without shuttong down NatSpeak the flag will disappear.
        #testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")

        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',0)")
        testFuncReturnNoneOr0("natlink.getWordInfo('Szymanskii',1)")
        
        if DNSVersion < 11:
            ## period just seems to return 8 in DPI15. Should be investigated TODO!
            testFuncReturnWordFlag(dgnwordflag_is_period,"natlink.getWordInfo(r'.\period\period')")
            testFuncReturnWordFlag(1,"natlink.addWord('Szymanskii',dgnwordflag_is_period)")
            testFuncReturnWordFlag(dgnwordflag_is_period,"natlink.getWordInfo('Szymanskii')")
        else:
            testFuncReturnWordFlag(1,"natlink.addWord('Szymanskii')")

        
        # deleteWord #
        testForException(TypeError,"natlink.deleteWord()")
        testForException(TypeError,"natlink.deleteWord(1)")
        if DNSVersion < 11: 
            testFuncReturn(dgnwordflag_is_period+dgnwordflag_DNS8newwrdProp,"natlink.getWordInfo('Szymanskii')")
        natlink.deleteWord('Szymanskii')
        testFuncReturn(None, "natlink.getWordInfo('Szymanskii',0)")
        
        if DNSVersion < 11:
            # word not in active or backup dict:
            testFuncReturn(None, "natlink.getWordInfo('Szymanskii',1)")  # looking in backup dictionary broken in Dragon 11
        
        if DNSVersion < 11:
            # word FrotzBlatz never added, so is not there (???) in the past
            # was the word added or activated when setting the word info??
            #testFuncReturn(dgnwordflag_useradded,"natlink.getWordInfo('FrotzBlatz')&~0x20000000")
            pass
        if not natlink.getWordInfo('FrotzBlatz') is None:
            natlink.deleteWord('FrotzBlatz')
        testFuncReturn(None, "natlink.getWordInfo('FrotzBlatz')")

        testForException(natlink.UnknownName,"natlink.deleteWord('FrotzBlatz')")
        testForException(natlink.UnknownName,"natlink.deleteWord('Szymanskii')")
        testForException(natlink.InvalidWord,"natlink.deleteWord('a\\b\\c\\d\\f')")

    #---------------------------------------------------------------------------
    # Here we test the ability to load and unload macro files under various
    # conditions.  The way we test that a file is loaded is to test that a
    # command has been defined using recognitionMimic
    
    # august 2011, QH, added check for a command recognition. Some of the recogs are dictate
    # and were therefore recognised while not expected.
    # note with these dictate recognitions, the results box and the screen show quite different texts
    # (to be studied!, eg why is PYTHON in the results box and python (as dictate) appears in the screen??
    # in Dragon 12 it appears you should turn off the option: "Use Dictation Box for unsupported applications"!!
    # otherwise the Dictation Box opens when doing invalid commands in the Calc program...

    # September 2015: add unimacroDirectory in between baseDirectory and userDirectory
    # Febr 2018: convert to binary added (QH)

    def testNatlinkUtilsFunctions(self):
        """test utility functions of natlinkutils
     
        getModifierKeyCodes: transforms modifiers ctrl alt (or menu) and shift into
        a list of playEvent keycodes
        """
        # constants from from natlinkutils:        
        vk_shift = 0x10
        vk_control = 0x11
        vk_menu = 0x12      # alt-key


        func = getModifierKeyCodes
        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        testFuncReturn(None,"getModifierKeyCodes('')",locals())
        testFuncReturn([vk_control],"getModifierKeyCodes('ctrl')",locals())
        testFuncReturn([vk_menu],"getModifierKeyCodes('alt')",locals())
        testFuncReturn([vk_menu],"getModifierKeyCodes('menu')",locals())
        testFuncReturn([vk_shift],"getModifierKeyCodes('shift')",locals())
        testFuncReturn([vk_control],"getModifierKeyCodes('ctrl+')",locals())
        testFuncReturn([vk_control, vk_shift, vk_menu],"getModifierKeyCodes('ctrl+shift+alt+')",locals())
        # should not want this: testFuncReturn([vk_control, vk_shift, vk_menu],"getModifierKeyCodes('ctrl shift alt menu shift ')",locals())

        testFuncReturn(None,"getModifierKeyCodes([])",locals())
        testFuncReturn([vk_control],"getModifierKeyCodes(['ctrl'])",locals())
        testFuncReturn([vk_menu],"getModifierKeyCodes(['alt'])",locals())
        testFuncReturn([vk_menu, vk_shift],"getModifierKeyCodes(['alt','shift'])",locals())

        testForException(KeyError, "getModifierKeyCodes('typo')")

    def testNatLinkMain(self):

        # through this grammar we get the recogtype:
        recCmdDict = RecordCommandOrDictation()
        recCmdDict.initialize()

        try:
            testRecognition = self.doTestRecognition
            coreDirectory = os.path.split(sys.modules['natlinkutils'].__dict__['__file__'])[0]
            userDirectory = natlink.getCurrentUser()[1]
            baseDirectory = natlinkmain.baseDirectory
            unimacroDirectory = natlinkmain.unimacroDirectory
            userDirectory = natlinkmain.userDirectory
            toggleMicrophone = self.toggleMicrophone
            # Basic test of globals.  Make sure that our macro file is not
            # loaded.  Then load the file and make sure it is loaded.
    
            mes = '\n'.join(['testNatLinkMain testing\n',
                   'clearing previous macro files from:',
                   '\tuserDirectory: %s'% userDirectory,
                   '\tunimacroDirectory: %s'% unimacroDirectory,
                   '\tbaseDirectory: %s\n\n'% baseDirectory])
            natlink.playString(mes)
            ## for extra safety:
            self.clearTestFiles()
            toggleMicrophone()
     
            self.log('create jMg1, seventeen', 'seventeen')
            createMacroFile(baseDirectory,'__jMg1.py', 'seventeen')
            # direct after create no recognition yet
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seventeen'],recCmdDict, 0)
            
            toggleMicrophone()
            # after toggle it should be in:
            # does not work qh:
            #testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seventeen'],recCmdDict, 1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 0)
            self.log('create jMg1, one', 'one')
            
            createMacroFile(baseDirectory,'__jMg1.py','one')
             #here the recognition is already there, should not be though...
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 0)
    
            self.log('\ntoggle mic, to get jMg1 in loadedGrammars', 1)
            toggleMicrophone()
            self.log('\nnext one should be recognised as a command, not text\n', 1)
        
            ## this one sucks. When running as isolated test, 10 times fine.
            ## when run with all tests together, no recognistion...
        
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 1)
            self.lookForDragonPad()

            # now separate two parts. Note this cannot be checked here together,this is automated testing from python six this is automated testing from python one this is automated testing from python two this is automated testing from python three this is automated testing from python four this is automated testing from python five this is automated testing from python seven this is automated testing from python eight
            # because changes in natlinkmain take no effect when done from this
            # program!
            if natlinkmain.checkForGrammarChanges:
                # Modify the macro file and make sure the modification takes effect
                # even if the microphone is not toggled.
                self.log('\nNow change grammar file jMg1 to "two", check for changes at each utterance', 1)
                createMacroFile(baseDirectory,'__jMg1.py','two')
                self.wait(2)
                ## with checking at each utterance next two lines should pass
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','two'],recCmdDict, 1)
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 0)
            else:
                self.log('\nNow change grammar file jMg1 to 2, no recognise immediate, only after mic toggle', 1)
                createMacroFile(baseDirectory,'__jMg1.py','two')
                # If next line fails, the checking is immediate, in spite of checkForGrammarChanges being on:
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','two'],recCmdDict, 0)
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 1)
                toggleMicrophone(1)
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','two'],recCmdDict, 1)
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 0)
    
            # Make sure a user specific file also works
            # now with extended file names (glob.glob, request of Mark Lillibridge) (QH):
            self.log('now new grammar file: %s'% specialFilenameGlobal, 1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seven'],recCmdDict, 0)
            createMacroFile(userDirectory,specialFilenameGlobal+'.py','seven')
            toggleMicrophone()
            if userDirectory:
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seven'],recCmdDict, 1)
            else:
                # no userDirectory, so this can be no recognition
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seven'],recCmdDict, 0)
    
            self.log('now new grammar file: %s'% spacesFilenameGlobal, 1)
            # should be unknown command:
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','thirty'],recCmdDict, 0)
            createMacroFile(userDirectory,spacesFilenameGlobal+'.py','thirty')
            # no automatic update of commands:
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','thirty'],recCmdDict, 0)
            toggleMicrophone()
            if userDirectory:
                # only after mic toggle should the grammar be recognised:
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','thirty'],recCmdDict, 1)
            else:
                self.log('this test cannot been done if there is no userDirectory')
    
            self.log('now new grammar file (should not be recognised)... %s'% "_.py", 1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','eight'],recCmdDict, 0)
            createMacroFile(userDirectory,"_.py",'eight')
            toggleMicrophone()
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','eight'],recCmdDict, 0)
    
            # Make sure user specific files have precidence over global files
            self.log('now new grammar file: jMg2, four', 1)
    
            createMacroFile(baseDirectory,'__jMg2.py','four')
            createMacroFile(userDirectory,'__jMg2.py','three')
            toggleMicrophone()
            # this one seems to go wrong if the dictation box is automatically loaded for non-standard applications, switch
            # this option off for the test-speech profile:
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','three'],recCmdDict, 1)
    
            # Make sure that we do the right thing with application specific
            # files.  They get loaded when the application is activated.
            self.log('now new grammar file: calc_jMg1, five', 1)
    
            createMacroFile(baseDirectory,'calc__jMg1.py','five')
            createMacroFile(userDirectory,'calc__jMg1.py','six')
            toggleMicrophone()
            if userDirectory:
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','five'],recCmdDict, 0)
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','six'],recCmdDict, 0)
            else:
                # userDirectory not there, so 'six' never recognised
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','six'],recCmdDict, 0)
                # 5 (base dir recognised because userdirectory is not there):
                testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','five'],recCmdDict, 1)
                self.log("without a userDirectory (Unimacro) switched on, this test is useless")

            self.lookForCalc()
    ##        natlink.execScript('AppBringUp "calc"')
            # priority for user macro file:
    
            # more intricate filename:
            createMacroFile(baseDirectory,specialFilenameCalc+'.py','eight')
            toggleMicrophone()
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','eight'],recCmdDict, 1)
    
            # filenames with spaces (not valid)
            createMacroFile(baseDirectory,spacesFilenameCalcInvalid+'.py','fourty')
            toggleMicrophone()
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','fourty'], recCmdDict,  0)
            # filenames with spaces (valid)
            createMacroFile(baseDirectory,spacesFilenameCalcValid+'.py','fifty')
            time.sleep(3)
            toggleMicrophone()
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','fifty'],recCmdDict, 1)
            
            #other filenames:
    ##        createMacroFile(baseDirectory,'calc.py', '9')  # chances are calc is already there, so skip now...
            createMacroFile(baseDirectory,'calc_.py', 'ten')
            # this name should be invalid:
            createMacroFile(baseDirectory,'calculator.py', 'eleven')
            toggleMicrophone()
    ##        testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','9'],1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','ten'],recCmdDict, 1)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','eleven'],recCmdDict, 0)
            
            self.killCalc()
            ### seems to go correct, no calc window any more, so rule six (specific for calc) should NOT respond
            #was a problem: OOPS, rule 6 remains valid, must be deactivated in gotBegin, user responsibility:
            #was a problem: testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','six'],recCmdDict, 1)
            # no recognition because calc is not there any more:
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','six'],recCmdDict, 0)
            
        ##        natlink.playString('{Alt+F4}')
    #-----------------------------------------------------------
            # clean up any files created during this test
            safeRemove(baseDirectory,'__jMg1.py')
            safeRemove(baseDirectory,'__jMg2.py')
            safeRemove(userDirectory,'__jMg2.py')
            safeRemove(userDirectory,specialFilenameGlobal+'.py')
            safeRemove(baseDirectory,'calc__jMg1.py')
            safeRemove(baseDirectory,'calc_.py')
            safeRemove(baseDirectory,'calculator.py')
            safeRemove(userDirectory,'calc__jMg1.py')
            safeRemove(baseDirectory,specialFilenameCalc+'.py')
            toggleMicrophone()
    
            # now that the files are gone, make sure that we no longer recognize
            # from them
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','one'],recCmdDict, 0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','two'],recCmdDict, 0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','three'],recCmdDict, 0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','four'],recCmdDict, 0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','five'],recCmdDict, 0)
            # some of the specialFilename cases:
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','seven'],recCmdDict, 0)
            testRecognition(['this', 'is', 'automated', 'testing', 'from', 'python','eight'],recCmdDict, 0)
    
    ## is done in tearDown:
    ##        # make sure no .pyc files are lying around
    ##        safeRemove(baseDirectory,'__jMg1.pyc')
    ##        safeRemove(baseDirectory,'__jMg2.pyc')
    ##        safeRemove(userDirectory,'__jMg2.pyc')
    ##        safeRemove(baseDirectory,'calc__jMg1.pyc')
        finally:
            recCmdDict.unload()
            

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

        if DNSVersion >= 11:
            natlink.playString('Dragon 11 getWordProns seems not valid any more...')
            print 'Dragon 11 getWordProns seems not valid any more...'
            time.sleep(1)
            return


        testForException = self.doTestForException
        testFuncReturn = self.doTestFuncReturn
        testFuncReturnAlternatives = self.doTestFuncReturnAlternatives
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
        testFuncReturnAlternatives((['an','and','~'],['an', 'and', '~', '~d']) ,"natlink.getWordProns('and')")
        testFuncReturnAlternatives((['Dat'], ['Dat', 'Dut']),"natlink.getWordProns('that')")
        testFuncReturnAlternatives((['on'], ['on', '{n']),"natlink.getWordProns('on')")


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

    def doTestRecognition(self, words,shouldWork=1, log=None):
        if shouldWork:
            natlink.recognitionMimic(words)
            if log:
                self.log("recognised: %s"% words)
        else:
            self.doTestForException(natlink.MimicFailed,"natlink.recognitionMimic(words)",locals())
            if log:
                self.log("did not recognise (as expected): %s"% words)


    def doTestCommandRecognition(self, words, shouldWork=1, log=None, testGram=None):
        """test if a recognition is recognised as command
        
        needs the testGram for the results!!
        
        Be sure the testing grammar is loaded with allResult=1, so
        the recognitionMimic can check for dictate recognition
        
        shouldWork can be 0 or 1, 'self', 'other', 'reject' (recogType in gotResultsObject), or None if grammar is not loaded yet
        
        see: testRecognitionChangingRulesExclusive  (Febr 2018 QH)
        """
        if not shouldWork in (0, 1, None, 'self', 'other', 'reject', 'exclusive'):
            raise TestError('doTestCommandRecognition, shouldWork has invalid value: %s'% shouldWork)
        try:
            natlink.recognitionMimic(words)
        except natlink.MimicFailed:
            if shouldWork == 0:
                return  # succes
            else:
                self.fail("===test failed: MimicFailed, but expected %s (words: %s)"% (shouldWork, words))
        ## mimic ok, now result:
        recogType = testGram.recogType
        if recogType == shouldWork:
            return # ok
        if testGram.recogType is None:
            raise TestError('recognition mimic succeeded, but got no recogType from testGram, words: %s'% words)
        if shouldWork == 1:
            if recogType == 'self':
                return # ok
            else:
                self.fail("recognition mimic succeeded, but got wrong recogType from testGram '%s', words: %s (expected 'self'"% (recogType, words))
        elif shouldWork == 0:
            if recogType == 'self':
                self.fail("recognition mimic succeeded, but got wrong recogType from testGram %s, words: %s (expected 'reject' or 'other'"% (recogType, words))
            else:
                return # reject and other is ok
        
    def _doTheCommandRecognition(self, words, shouldWork=1):
        """do the mimic and report back, mimicFailed.
        """
        if shouldWork:
            try:
                natlink.recognitionMimic(words)
            except natlink.MimicFailed:
                self.fail("command recognition should have worked: %s"% words)
            if log:
                self.log("command recognised as was expected: %s"% words)
        else:
            try:  #hello world
                natlink.recognitionMimic(words)
            except natlink.MimicFailed:
                return # expect to fail
            # ShouldBeCommandError is passed on...
#

    def doTestMimicResult(self, words, expected):
        """test the mimic of words (a list) and check the expected window contents
        """
        try:
            natlink.recognitionMimic(words)
        except natlink.MimicFailed:
            self.fail('TestMimicResult, recognitionMimic failed for words: "%s"'% words)
            
        self.doTestWindowContents(expected, testName="TestMimicResult for words: %s"% words,
                                  stripResult=1)

    #---------------------------------------------------------------------------
    # Test the splitApartLines function of gramparser
    # has to be developed (QH, 2018)
    
    # def testSplitApartLines(self):
    #     self.log("testSplitApartLines", 1)
    #     func = gramparser.splitApartLines
    #     self.doTestSplitApartLines(func, 'hello', ['hello', '\x00'])
        
    
    
    #---------------------------------------------------------------------------
    # Test the Grammar parser

    def testParser(self):
        self.log("testParser", 1)

        def testGrammarError(exceptionType,gramSpec):
            try:
                parser = gramparser.GramParser([gramSpec])
                parser.doParse()
                parser.checkForErrors()
            except exceptionType:
                return
            raise TestError,'Expecting an exception parsing grammar '+gramSpec

        # here we try a few illegal grammars to make sure we catch the errors
        # 
        testGrammarError(gramparser.SyntaxError,'badrule;')
        testGrammarError(gramparser.SyntaxError,'badrule = hello;')
        testGrammarError(gramparser.SyntaxError,'= hello;')
        testGrammarError(gramparser.SyntaxError,'<rule> error = hello;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello')
        testGrammarError(gramparser.LexicalError,'<rule exported = hello;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = ;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = [] hello;')
        testGrammarError(gramparser.GrammarError,'<rule> = hello;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello ];')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello {};')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello <>;')
        testGrammarError(gramparser.GrammarError,'<rule> exported = <other>;')
        testGrammarError(gramparser.SymbolError,'<rule> exported = one; <rule> exported = two;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello | | goodbye;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello ( ) goodbye;')
        testGrammarError(gramparser.SyntaxError,'<rule> exported = hello "" goodbye;')
        
    #---------------------------------------------------------------------------
    # Here we test recognition of command grammars using GrammarBase    

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
        testForException(gramparser.SyntaxError,"testGram.load('badrule;')",locals())
        testForException(gramparser.GrammarError,"testGram.load('<rule> = hello;')",locals())

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
        testGram.gramObj.deactivate('start')
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
            testForException(gramparser.GrammarError, "testGram.activate('%s')"% rule, locals())
            # activate after all unactive:
            testGram.deactivateAll()
            testGram.activate(rule)
            testActiveRules(testGram, [rule])
            prev = rule

        rule = 'one'
        testGram.activate(rule)
        testForException(gramparser.GrammarError, "testGram.activate('%s')"% rule, locals())
        testGram.deactivateAll()
        testActiveRules(testGram, [])

        for SET in (['one', 'three', 'four'], ['three'], ['one', 'three', 'four'], ['one', 'three']):
            testGram.activateSet(SET)
            testActiveRules(testGram, SET)
            ##with original version of natlinkutils.py you get:
            ##AssertionError: Active rules not as expected:
            ##expected: ['three'], got: ['one', 'three']
            ##fix around line 420 (copy.copy) in natlinkutils.py, QH
    
        ## test exceptlist feature:
        ## ['one', 'three', 'four'] are the exported rules
        testGram.activateAll(exceptlist=['one'])
        testActiveRules(testGram, ['three', 'four'])
        testGram.activateAll(exceptlist=None)
        testActiveRules(testGram, ['one', 'three', 'four'])
        testGram.deactivateAll()
        testActiveRules(testGram, [])
        # extra in exceptlist does not matter:
        testGram.activateAll(exceptlist=['one', 'two', 'three', 'four', 'five'])
        testActiveRules(testGram, [])
        testGram.activateAll(exceptlist=['three', 'four'])
        testActiveRules(testGram, ['one'])
        testGram.activateAll(exceptlist=['one', 'three'])
        testActiveRules(testGram, ['four'])
        
        # test (new, 2010) function deactivateSet
        testGram.activateAll(exceptlist=['one'])
        testActiveRules(testGram, ['three', 'four'])
        testGram.deactivateSet(['three'])
        testActiveRules(testGram, ['four'])
        testGram.deactivateSet(['four'])
        testActiveRules(testGram, [])
        # non existing rule:
        testForException(gramparser.GrammarError,"testGram.deactivateSet(['five'])",locals())
        # trick for this:
        testGram.deactivateSet(['five'], noError=1)
        testActiveRules(testGram, [])

        testGram.activateAll()
        testGram.deactivateSet(['four', 'three'])
        testActiveRules(testGram, ['one'])

        # must pass a list to deactivateset
        testForException(TypeError,"testGram.deactivateSet('five')",locals())
        testForException(TypeError,"testGram.activateSet('four')",locals())

        testGram.unload()
        testForException(gramparser.SyntaxError,"testGram.load('badrule;')",locals())
        testForException(gramparser.GrammarError,"testGram.load('<rule> = hello;')",locals())

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

    def testGrammarRecognitions(self):
        self.log("testGrammarRecognitions", 1)

        # Create a lot of grammars to test the actual recognition results
        class TestGrammar(GrammarBase):

            def loadAndActivate(self, gramSpec):
                self.load(gramSpec)
                self.activateAll(exclusive=1)
                
            def __init__(self):
                GrammarBase.__init__(self)
                
            def gotBegin(self,moduleInfo):
                self.words = []

            def gotResults(self,words,fullResults):
                self.words = words
                self.fullResults = fullResults

        testGram = TestGrammar()
        testRecognition = self.doTestRecognition

        ## test possible error in _repeat grammar:
        ## do the brackets work as expected?? (QH, july 2012)
        gramSpec = "<hello> exported = hello world;"
        self.log("loading gramSpec: %s"% gramSpec, 1)
        testGram.loadAndActivate(gramSpec)
        recog = ["hello", "world"]
        testRecognition(recog, 1)
        self.log('got: %s'% " ".join(recog), 1)
        testGram.unload()

        ## test second example:
        gramSpec = "<hello> exported = hello | world;"
        self.log("loading gramSpec: %s"% gramSpec, 1)
        testGram.loadAndActivate(gramSpec)
        testRecognition(["hello", "world"], 0, log=1)
        testRecognition(["hello"], 1, log=1)
        testRecognition(["world"], 1, log=1)
        self.log('got: hello and world apart', 1)
        testGram.unload()
        
        # ## test problematic line from _repeat grammar:
        # gramSpec = "<endRepeating> exported = stop [herhaal|herhalen] | OK;"
        # self.log("loading gramSpec: %s"% gramSpec, 1)
        # testGram.loadAndActivate(gramSpec)
        # testRecognition(["stop"], 1, log=1)
        # testRecognition(["stop", "herhaal"], 1, log=1)
        # testRecognition(["stop", "herhalen"], 1, log=1)
        # testRecognition(["OK"], 1, log=1)
        # self.log('got: all stop recognitions', 1)
        # # refuse:
        # testRecognition(["stop", "herhaal", "OK"], 0, log=1)
        # testRecognition(["stop", "OK"], 0, log=1)
        # testRecognition(["herhaal"], 0, log=1)
        # self.log('refused all forbidden recognitions', 1)
        
        testGram.unload()
        

    def testDgndictationEtc(self):
        self.log("testDgndictationEtc", 1)

        # Create a simple command grammar.  This grammar simply gets the results
        # of the recognition and saves it in member variables.  It also contains
        # code to check for the results of the recognition.

        # only in DragonPad, test the imported rules dgndictation, dgnletters and dgnwords        
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

        testGram.unload()
        testGram.resetExperiment()

    # test working of dgnwords:
    # because of a clash with one of the Unimacro grammars 'dictate' in now made 'DICTOOOTE'
        if DNSVersion <= 10:
            # broken with Dragon 11
            self.log("testing dgnwords")
            testGram.load("""<dgnwords> imported;
                          <Start> exported = DICTOOOTE word <dgnwords>;""")
            testGram.activateAll(window=0)
            testRecognition(['DICTOOOTE','word','hello'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'word', 'hello'],
                                     [('DICTOOOTE', 'Start'), ('word', 'Start'), ('hello', 'dgnwords')])
            testGram.unload()
            testGram.resetExperiment()
      
    # test working of dgnletters:
    # dgnletters stp[
        testGram.load("""<dgnletters> imported;
                      <Start> exported = DICTOOOTE letters <dgnletters>;""")
        testGram.activateAll(window=0)
        if DNSVersion < 11:
            testRecognition(['DICTOOOTE','letters','b',])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'letters', 'b\\\\l'],
                                     [('DICTOOOTE', 'Start'), ('letters', 'Start'),
                                        ('b\\\\l', 'dgnletters')])

        elif DNSVersion >= 11:
            # Dragon 11, 12
            testRecognition(['DICTOOOTE','letters', r'b\spelling-letter\B'])
            testGram.checkExperiment(1, 'self', ['DICTOOOTE','letters', r'b\spelling-letter\B'],
                                    [('DICTOOOTE', 'Start'), ('letters', 'Start'), ('b\\spelling-letter\\B', 'dgnletters')])

            testRecognition(['DICTOOOTE','letters',r'b\spelling-letter\bravo', r'!\spelling-exclamation-mark\exclamation mark'])
            testGram.checkExperiment(1, 'self', ['DICTOOOTE','letters',r'b\spelling-letter\bravo', r'!\spelling-exclamation-mark\exclamation mark'],
                                    [('DICTOOOTE', 'Start'), ('letters', 'Start'), ('b\\spelling-letter\\bravo', 'dgnletters'),
                                     ('!\\spelling-exclamation-mark\\exclamation mark', 'dgnletters')])
            
            
            testRecognition(['DICTOOOTE', 'letters', r'c\spelling-letter\C', r'd\spelling-letter\delta', ',\spelling-comma\comma'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'letters', r'c\spelling-letter\C', r'd\spelling-letter\delta', ',\spelling-comma\comma'],
                                    [('DICTOOOTE', 'Start'), ('letters', 'Start'), ('c\\spelling-letter\\C', 'dgnletters'),
                                        ('d\\spelling-letter\\delta', 'dgnletters'), (',\\spelling-comma\\comma', 'dgnletters')])
            
        else:
            self.log("pass the test of dgnletters")
        testGram.unload()
        testGram.resetExperiment()
      
    # test working of dgndictation:
        self.log("testing dgndictation")
        testGram.load("""<dgndictation> imported;
                      <Start> exported = DICTOOOTE <dgndictation>;""")
        testGram.activateAll(window=0)
        
        ## take a strange "trigger" word, because otherwise there is a conflict with some
        ## Unimacro grammar:
        testRecognition(['DICTOOOTE','hello'])
        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello'],
                                 [('DICTOOOTE', 'Start'), ('hello', 'dgndictation')])
        testRecognition(['DICTOOOTE','hello', 'there'])
        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello', 'there'],
                                 [('DICTOOOTE', 'Start'), ('hello', 'dgndictation'), ('there', 'dgndictation')])
        testGram.unload()
        testGram.resetExperiment()
      
    # try combinations of the three:
        self.log("testing dgndictation etc combinations")
        if DNSVersion != 11:
            testGram.load("""<dgndictation> imported;
                            <dgnletters> imported;
                            <dgnwords> imported;
                           <Start1> exported = DICTOOOTE <dgndictation>;
                           <Start2> exported = DICTOOOTE letters <dgnletters>;
                           <Start3> exported = DICTOOOTE word <dgnwords>;
                          """)
        else:
            # Dragon 11 seems to have lost <dgnwords>:
            testGram.load("""<dgndictation> imported;
                            <dgnletters> imported;
                            <dgnwords> imported;
                           <Start1> exported = DICTOOOTE <dgndictation>;
                           <Start2> exported = DICTOOOTE letters <dgnletters>;
                          """)
            
        testGram.activateAll(window=0)
        testRecognition(['DICTOOOTE','hello','there'])
        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello', 'there'],
                                 [('DICTOOOTE', 'Start1'), ('hello', 'dgndictation'), ('there', 'dgndictation')])
        if DNSVersion < 11:
            testRecognition(['DICTOOOTE','letters','b\\bravo', 'k\\kilo'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'letters', 'b\\bravo\\h', 'k\\kilo\\h'],
                                     [('DICTOOOTE', 'Start2'), ('letters', 'Start2'), ('b\\bravo\\h', 'dgnletters'), ('k\\kilo\\h', 'dgnletters')])
        elif DNSVersion < 15:   # probably 14
            testRecognition(['DICTOOOTE','letters',r'b\spelling-letter\bravo', r'k\spelling-letter\K'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'letters', r'b\spelling-letter\bravo', r'k\spelling-letter\K'],
                                     [('DICTOOOTE', 'Start2'), ('letters', 'Start2'), ('b\\spelling-letter\\bravo', 'dgnletters'),
                                        ('k\\spelling-letter\\K', 'dgnletters')])
        else:
            testRecognition(['DICTOOOTE','letters',r'b\spelling-letter\bravo', r'k\spelling-letter\K'])
            testGram.checkExperiment(1,'self', ['DICTOOOTE', 'letters', r'b\spelling-letter\bravo', r'k\spelling-letter\K'],
                                     [('DICTOOOTE', 'Start2'), ('letters', 'Start2'), ('b\\spelling-letter\\bravo', 'dgndictation'),
                                                ('k\\spelling-letter\\K', 'dgndictation')])


        testRecognition(['DICTOOOTE','word','hello'])
        if DNSVersion != 11:
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'word', 'hello'],
                                     [('DICTOOOTE', 'Start3'), ('word', 'Start3'), ('hello', 'dgnwords')])
        else:
            # Dragon 11, <dgnwords> no longer works:
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'word', 'hello'],
                                    [('DICTOOOTE', 'Start1'), ('word', 'dgndictation'), ('hello', 'dgndictation')])

        testGram.unload()
        testGram.resetExperiment()

    # try combinations of the three:
    # not dgnwords is pointless here, dgndictation overrules:
        self.log("testing dgndictation combined in one rule")
        testGram.load("""<dgndictation> imported;
                        <dgnletters> imported;
                        <dgnwords> imported;
                       <Start> exported = DICTOOOTE (<dgndictation>|<dgnletters>|<dgnwords>);
                      """)
        testGram.activateAll(window=0)
        testRecognition(['DICTOOOTE','hello','there'])
        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello', 'there'],
                                 [('DICTOOOTE', 'Start'), ('hello', 'dgndictation'), ('there', 'dgndictation')])
        if DNSVersion < 11:
            testRecognition(['DICTOOOTE','b\\bravo', 'k\\kilo'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'b\\bravo\\h', 'k\\kilo\\h'],
                                     [('DICTOOOTE', 'Start'), ('b\\bravo\\h', 'dgnletters'), ('k\\kilo\\h', 'dgnletters')])
        elif DNSVersion < 14:
            # also see above for dgnletters!
            testRecognition(['DICTOOOTE', r'b\spelling-letter\bravo', r'k\spelling-letter\K'])
            testGram.checkExperiment(1,'self', ['DICTOOOTE', r'b\spelling-letter\bravo', r'k\spelling-letter\K'],
                                     [('DICTOOOTE', 'Start'), ('b\\spelling-letter\\bravo', 'dgnletters'),
                                      ('k\\spelling-letter\\K', 'dgnletters')])
        else:
            # 14 and above:
            # also see above for dgnletters!
            testRecognition(['DICTOOOTE', r'b\spelling-letter\bravo', r'k\spelling-letter\K'])
            testGram.checkExperiment(1,'self', ['DICTOOOTE', r'b\spelling-letter\bravo', r'k\spelling-letter\K'],
                                     [('DICTOOOTE', 'Start'), ('b\\spelling-letter\\bravo', 'dgndictation'),
                                      ('k\\spelling-letter\\K', 'dgndictation')])

## this experiment sometimes shows the rule dgndictation and sometimes dgnwords
## so, better not test here!!
## not mix them!!
##        testRecognition(['DICTOOOTE','hello'])
##        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello'],
##                                 [('DICTOOOTE', 'Start'), ('hello', 'dgndictation')])

        testGram.unload()
        testGram.resetExperiment()

    # try others mixing of rules:
        self.log("testing dgndictation mixing of rules")
        testGram.load("""<Start> exported = <Start1>|<Start2>| hello | <dummyrule>;
                    <dummyrule> = dummy rule;
                       <Start1> exported = DICTOOOTE <dgndictation>;
                        <dgndictation> imported;
                        <dgnletters> imported;
                       <Start2> exported = DICTOOOTE letters <dgnletters>;
                      """)
        testGram.activateAll(window=0)
        testRecognition(['DICTOOOTE','hello','there'])
        testGram.checkExperiment(1,'self',['DICTOOOTE', 'hello', 'there'],
                                 [('DICTOOOTE', 'Start1'), ('hello', 'dgndictation'), ('there', 'dgndictation')])
        if DNSVersion < 11:
            testRecognition(['DICTOOOTE','letters','b\\bravo', 'k\\kilo'])
            testGram.checkExperiment(1,'self',['DICTOOOTE', 'letters', 'b\\bravo\\h', 'k\\kilo\\h'],
                                     [('DICTOOOTE', 'Start2'), ('letters', 'Start2'), ('b\\bravo\\h', 'dgnletters'), ('k\\kilo\\h', 'dgnletters')])
        else:
            pass
            # we believe this test will pass with correct letters!


        testRecognition(['hello'])
        testGram.checkExperiment(1,'self',['hello'],
                                 [('hello', 'Start')])
        testRecognition(['dummy', 'rule'])
        testGram.checkExperiment(1,'self',['dummy', 'rule'],
                                 [('dummy', 'dummyrule'), ('rule', 'dummyrule')])

        testGram.unload()
        testGram.resetExperiment()

    def testRecognitionChangingRulesExclusive(self):
        self.log("testRecognitionChangingRulesExclusive", 1)

        # Create a simple command grammar.
        # activate different rules
        # make exclusive and change the activated rules
        # see if the rules are recognised correct
        # for exclusive global rules it seems to work.
        # the test grammar is activated with allResults = 1, so callsback at
        # every recognition.
        # this seems also to work for exclusive grammar rules.
        # with application specific rules, this mechanism seems not to work
        # either the activation of the rules is incorrect, or the allResults flag does not work
        #

        class TestGrammar(GrammarBase):

            def __init__(self):
                GrammarBase.__init__(self)
                self.resetExperiment()

            def resetExperiment(self):
                self.recogType = None

            def gotBegin(self,moduleInfo):
                self.resetExperiment()

            def gotResultsObject(self,recogType,resObj):
                self.recogType = recogType
        
        testGram = TestGrammar()
        # this test function must have testGram=testGram passed, for correct report of
        # the recogtype. self = recognition by this grammar
        # reject = not recognized, other = dictate or other grammar.
        testCommandRecognition = self.doTestCommandRecognition
        testRecognition = self.doTestRecognition
        testForException = self.doTestForException
        testActiveRules = self.doTestActiveRules
        testValidRules = self.doTestValidRules

        # testGram.unload()
        # testGram.resetExperiment()

    # test working of dgnwords:
        self.log("testing changing exclusive rules")
        # grammar not loaded yet
        testActiveRules(testGram, dict())
        testValidRules(testGram, [])
        self.assertEquals(testGram.isExclusive(), False)
        self.assertEquals(testGram.isActive(), False)
        self.assertEquals(testGram.isLoaded(), False)
        
        gramSpec = """
            <one> exported = xclusaif rule one;
            <two> exported = normal rule two;
            <three> exported = normal rule three;
            <four> exported = xclusaif rule four;
        """
        testGram.load(gramSpec, allResults=1)
        
        # loaded, not active yet:
        testValidRules(testGram, ['one', 'two', 'three', 'four'])
        # testActiveRules(testGram, dict())
        # self.assertEquals(testGram.isExclusive(), False)
        # self.assertEquals(testGram.isActive(), False)
        # self.assertEquals(testGram.isLoaded(), True)
        # 
        # self.log("\n=== grammar loaded, but not active yet...", doPlaystring=1)
        # 
        # testCommandRecognition(['xclusaif', 'rule', 'one'], 0, testGram=testGram)
        # self.assertEquals(testGram.isExclusive(), False)
        # 
        # # try setting exclusive with no rules on:
        # testGram.setExclusive(1)
        # self.assertEquals(testGram.isExclusive(), True)
        # 
        # # not activated yet, check if dictate is recognised:
        # self.log("\n=== grammar is now exclusive but not active yet, so leaves through recognitions...", doPlaystring=1)
        # 
        # testCommandRecognition(['xclusaif', 'rule', 'one'], 0, testGram=testGram)
        # testRecognition(['normal', 'rule', 'two'])
        # testRecognition(['scratch', 'that'])
        # testRecognition(['normal', 'rule', 'three'])
        # testRecognition(['scratch', 'that'])
        # 
        # # activate one, should be exclusive now:
        # self.log("\n=== activate rule one now, grammar should be exclusive now...", doPlaystring=1)
        # testGram.activate('one')
        # expActRules = dict(one=0)
        # testActiveRules(testGram, expActRules)
        # self.assertEquals(testGram.isExclusive(), True)
        # 
        # testCommandRecognition(['normal', 'rule', 'two'], 0, testGram=testGram) # no recognition, exclusive is on
        # testCommandRecognition(['xclusaif', 'rule', 'one'], 1, testGram=testGram)  # this is the exclusive command
        # testRecognition(['normal', 'rule', 'two'], 0)
        # testRecognition(['scratch', 'that'], 0)
        # 
        # self.log("\n=== activateSet['one', 'four'] grammar should still be exclusive ...", doPlaystring=1)
        # testGram.activateSet(['one', 'four'])
        # expActRules = dict(one=0, four=0)
        # testActiveRules(testGram, expActRules)
        # self.assertEquals(testGram.isExclusive(), True)
        # 
        # testCommandRecognition(['normal','rule','three'], shouldWork=0, testGram=testGram, log=1)  
        # testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)  
        # testCommandRecognition(['xclusaif','rule','four'], shouldWork=1, testGram=testGram, log=1)  
        # 
        # testCommandRecognition(['hello', 'world'], shouldWork=0, testGram=testGram)  
        # 
        # self.log("\n=== switch off exclusive mode, keep set ['one', 'four'] ...", doPlaystring=1)
        # testGram.setExclusive(0)
        # expActRules = dict(one=0, four=0)
        # testActiveRules(testGram, expActRules)
        # self.assertEquals(testGram.isExclusive(), False)
        # 
        # testCommandRecognition(['normal','rule','three'], shouldWork='other', testGram=testGram, log=1)  
        # testRecognition(['scratch', 'that'])
        # testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)
        # testCommandRecognition(['normal', 'rule', 'two'], shouldWork=0, testGram=testGram, log=1)
        # testRecognition(['scratch', 'that'])
        # testRecognition(['normal', 'rule', 'two'])
        # testRecognition(['scratch', 'that'])
        # 
        # testCommandRecognition(['xclusaif','rule','four'], shouldWork=1, testGram=testGram, log=1)  
        # testCommandRecognition(['hello', 'world'], shouldWork='other', testGram=testGram)  
        # testRecognition(['scratch', 'that'])
        # 
        # self.log("\n=== switch off exclusive mode, keep set ['one', 'four'] ...", doPlaystring=1)
        # testGram.setExclusive(0)
        # testCommandRecognition(['normal','rule','three'], shouldWork=0, testGram=testGram, log=1)  
        # testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)  
        # 
        # self.log("\n=== switch on 'one' and 'three' for dragonpad and 'two', 'three' and 'four'  (non exclusive)...", doPlaystring=1)
        testGram.deactivateAll()
        thisHndle = natlink.getCurrentModule()[2] # test, this is my python ide, komode
        self.lookForDragonPad()
        dragonpadHndle = natlink.getCurrentModule()[2]
        # expActRules = dict(one=0, four=0)
        expActRules = dict()
        testActiveRules(testGram, expActRules)
        testGram.activate('one', window=dragonpadHndle)
        # expActRules = dict(one=dragonpadHndle, four=0)
        expActRules = dict(one=dragonpadHndle)
        testActiveRules(testGram, expActRules)
        # # this one removes a global rule (four):
        # testGram.activateSet(['one', 'three'], window=dragonpadHndle)
        # expActRules = dict(one=dragonpadHndle, three=dragonpadHndle)
        # testActiveRules(testGram, expActRules)
        # 
        self.lookForCalc()
        calcHndle = natlink.getCurrentModule()[2]
        expActRules = dict(one=dragonpadHndle)
        testActiveRules(testGram, expActRules)
        self.log('now active for dragonpad: one (%s)'% dragonpadHndle)
        ## this one
        
        testGram.activate('two', window=calcHndle)
        self.log('activate two calc (%s)'% calcHndle)
        expActRules = dict(one=dragonpadHndle, two=calcHndle)
        testActiveRules(testGram, expActRules)

        self.log('activate two, three, four calc')
        testGram.activateSet(['two', 'three', 'four'], window=calcHndle)
        testGram.deactivate('two')
        testGram.deactivate('three')
        
        expActRules = dict(one=dragonpadHndle, four=calcHndle)
        testActiveRules(testGram, expActRules)
        
        self.lookForDragonPad()
        dragonpadHndle = natlink.getCurrentModule()[2]
        self.log("\n=== switch on Dragonpad again, with rule one...", doPlaystring=1)
        testGram.deactivateAll()  # try this
        expActRules = dict()
        testActiveRules(testGram, expActRules)
        
        testGram.activateSet(['four'], window=self.komodoHndle)  # not exclusive, this does not work in the test.
        testGram.activateSet(['one'], window=dragonpadHndle)  # not exclusive, this does not work in the test.
        expActRules = dict(one=dragonpadHndle, four=self.komodoHndle)
        # expActRules = dict(one=dragonpadHndle)
        testActiveRules(testGram, expActRules)
        self.assertEquals(testGram.isExclusive(), False)

        # from here it goes wrong:
        ## nothing exclusive here, but only for dragonpad window:
        testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)  

        testCommandRecognition(['hello', 'world'], shouldWork=0, testGram=testGram)
        testCommandRecognition(['normal','rule','three'], shouldWork=0, testGram=testGram)
                # apparently exclusive grammars do not callback in an
                # allResults grammar, but mimic works.
                # strange...

        self.lookForCalc()
        calcHndle = natlink.getCurrentModule()[2]
        expActRules = dict(one=dragonpadHndle, four=self.komodoHndle)
        testActiveRules(testGram, expActRules)
        self.log('now active for dragonpad: one, three (%s)'% dragonpadHndle)

        testCommandRecognition(['normal','rule','two'], shouldWork=0, testGram=testGram) 

        testGram.activate('two', window=calcHndle)
        self.log('activate two calc (%s)'% calcHndle)
        expActRules = dict(one=dragonpadHndle, two=calcHndle, four=self.komodoHndle)
        testActiveRules(testGram, expActRules)
        
        testCommandRecognition(['normal','rule','two'], shouldWork=1, testGram=testGram) 
       
        self.log('activate two, three, four calc')
        testGram.activateSet(['two', 'three', 'four'], window=calcHndle)
        expActRules = dict(one=dragonpadHndle, two=calcHndle, three=calcHndle, four=calcHndle)
        testActiveRules(testGram, expActRules)
        # note: nothing exclusive here, this seems not to work for window specific rules:
        testCommandRecognition(['hello', 'world'], shouldWork=0, testGram=testGram)
        testCommandRecognition(['normal','rule','three'], shouldWork=1, testGram=testGram)
        testCommandRecognition(['normal','rule','two'], shouldWork=1, testGram=testGram) 


        testGram.setExclusive(0)
        self.lookForDragonPad()
        dragonpadHndle2 = natlink.getCurrentModule()[2]
        if dragonpadHndle2 != dragonpadHndle:
            raise TestError("hndles DragonPad not same, expected them to be so")
        testGram.setExclusive(1)

        expActRules = dict(one=dragonpadHndle, four=self.komodoHndle)
        testActiveRules(testGram, expActRules)
        
        self.log("\n=== Now exclusive with rule one for Dragonpad...", doPlaystring=1)
        testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)
        self.log("\n=== Rule one passed exclusive...", doPlaystring=1)

        testCommandRecognition(['normal','rule','two'], shouldWork=0, testGram=testGram, log=1)  
        testCommandRecognition(['normal','rule','three'], shouldWork=0, testGram=testGram, log=1)  
        testCommandRecognition(['xclusaif','rule','four'], shouldWork=0, testGram=testGram, log=1)  

        self.log("\n=== Rules two three four passed exclusive...", doPlaystring=1)

        testGram.setExclusive(0)
        self.log("\n=== Non exclusive with rule one for Dragonpad...", doPlaystring=1)
        testCommandRecognition(['xclusaif','rule','one'], shouldWork=1, testGram=testGram, log=1)
        self.log("\n=== Rule one passed non exclusive...", doPlaystring=1)
        
        
        
        testCommandRecognition(['normal','rule','two'], shouldWork=0, testGram=testGram, log=1)  
        testCommandRecognition(['normal','rule','three'], shouldWork=0, testGram=testGram, log=1)  
        testCommandRecognition(['xclusaif','rule','four'], shouldWork=0, testGram=testGram, log=1)  

        self.log("\n=== Rules two three four passed non exclusive...", doPlaystring=1)

        
        testGram.unload()
        testGram.resetExperiment()


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
##        time.sleep(5) # let the calculator recover from last test
        natlink.execScript('AppBringUp "calc"')
        calcWindow = natlink.getCurrentModule()[2]
        print natlink.getCurrentModule()
        
        # Activate the grammar and try a test recognition
        testGram.load()
        testGram.activate(window=calcWindow)
        self.wait()
        
        if DNSVersion < 11:
            period = r'.\period'
        else:
            period = r'.\period\period'
        
        testRecognition(['this','is','a','test',period])
        if DNSVersion < 11:
            testGram.checkExperiment(1,'self',['this','is','a','test', period])
        else:
            testGram.checkExperiment(1,'self', ['this', 'is', 'a\\determiner', 'test', '.\\period\\period'])
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
        testForException(natlink.WrongType,"testGram.gramObj.appendList('list','one')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.setSelectText('')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.getSelectText()",locals())
        
        # clean up
        testGram.unload()
        otherGram.unload()
##        the test must close calc! now closed in tearDown...
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
        #time.sleep(5) # let the calculator recover from last test
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
        ## buffer has program name of calc inserted... TODO (Febr 2018)
        ## input : buffer (above)
        ## output : a simple strisWOW64\calc.exe   
        ## or : a simple striocument or a simple stri
        testGram.setSelectText(buffer)
        gotBuffer = testGram.getSelectText()
        self.assertEqual(buffer, gotBuffer, 
                         'getSelectText should receive the same as set by setSelectText, not:\n'
                         'expected: %s\n'
                         'got: %s'%
                         (buffer, gotBuffer))
        testGram.activate(window=calcWindow)

        testRecognition(['Select','text'])
        testGram.checkExperiment(1,'self',['Select','text'],19,23)
        
        testRecognition(['Correct','simple','Through','of'])
        testGram.checkExperiment(1,'self',['Correct','simple','Through','of'],2,18)

        testRecognition(['Insert Before','simple'])
        testGram.checkExperiment(1,'self',['Insert Before','simple'],2,8)
        
        testRecognition(['Correct','a','Through','of'])
        
        if DNSVersion < 11:
            aResult = 'a'
        else:
            aResult = 'a\\determiner'

            
        testGram.checkExperiment(1,'self',['Correct',aResult,'Through','of'],0,18)
        testGram.unload()

        ##QH more throughWords:
        #         01234567890123456789012345678
        buffer = 'a more complicated string of text.'
        testGram.load(['Select'],throughWords=['Through', 'Until'])
        testGram.setSelectText(buffer)
        testGram.activate(window=calcWindow)

        recog = ['Select','complicated','string']
        testRecognition(recog)
        testGram.checkExperiment(1,'self',recog,7,25)
        
        recog = ['Select','more', 'Through', 'of']
        testRecognition(recog)
        testGram.checkExperiment(1,'self',recog,2,28)
        if DNSVersion < 11:
            aResult = 'a'
        else:
            aResult = 'a\\determiner'
            
        recog = ['Select',aResult, 'more', 'Until', 'of']
        testRecognition(recog)
        
            
        
        testGram.checkExperiment(1,'self',recog,0,28)

        # test for command failures
        testForException(TypeError,"testGram.gramObj.setSelectText(1)",locals())
        testForException(TypeError,"testGram.gramObj.setSelectText('text','text')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.emptyList('list')",locals())
        testForException(natlink.WrongType,"testGram.gramObj.appendList('list','one')",locals())
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
    # Try a slightly enhanced way of calling the rules, also giving nextWords, nextRule,
    # prevWords, prevRule, and also fullResults and seqsAndRules as instance variables.
    # QH, april 2010:
    # Added test for self.rulesByName dict...

    def testNextPrevRulesAndWords(self):
        self.log("testNextPrevRulesAndWords", 1)
        testForException = self.doTestForException
        testwordsByRule = self.doTestEqualDicts
        class TestGrammar(GrammarBase):

            gramSpec = """
                #<run> exported = test [<optional>+] {colors}+ <extra> [<optional>];
                #<run> exported = test {colors}+ <extra>;
                <run> exported = test blue chair;
                <optional>  = very | small | big;
                <extra> = {furniture};
            """

            def resetExperiment(self):
                self.results = []
                self.allNextRules = []
                self.allPrevRules = []
                self.allNextWords = []
                self.allPrevWords = []

            def checkExperiment(self,expected):
                if self.results != expected:
                    raise TestError, "Grammar failed to get recognized\n   Expected = %s\n   Results = %s"%( str(expected), str(self.results) )
                self.resetExperiment()
        
            def initialize(self):
                self.load(self.gramSpec, allResults=1)
                self.activateAll()
                self.resetExperiment()
                # self.setList('colors', ['red', 'green', 'blue'])
                # self.setList('furniture', ['table', 'chair'])
                self.testNum = 0
                
            def gotResults_run(self,words,fullResults):
                self.results.extend(words)
                self.allNextRules.append(self.nextRule)
                self.allPrevRules.append(self.prevRule)
                self.allNextWords.append(self.nextWords)
                self.allPrevWords.append(self.prevWords)
       
            def gotResults_optional(self,words,fullResults):
                self.results.extend(words)
                self.allNextRules.append(self.nextRule)
                self.allPrevRules.append(self.prevRule)
                self.allNextWords.append(self.nextWords)
                self.allPrevWords.append(self.prevWords)

            def gotResults_extra(self,words,fullResults):
                self.results.extend(words)
                self.allNextRules.append(self.nextRule)
                self.allPrevRules.append(self.prevRule)
                self.allNextWords.append(self.nextWords)
                self.allPrevWords.append(self.prevWords)

                
        testEqualLists = self.doTestEqualLists
        testGram = TestGrammar()
        testGram.initialize()
        testGram.testNum = 1
        #natlink.recognitionMimic(['test', 'very', 'big', 'blue', 'chair'])
        natlink.recognitionMimic(['test', 'blue', 'chair'])
        testEqualLists([None, 'run', 'optional', 'run'], testGram.allPrevRules, "first experiment, prev rules")
      
        testEqualLists(['optional', 'run', 'extra', None], testGram.allNextRules, "first experiment, next rules")
        testEqualLists([[], ['test'], ['very', 'big'], ['blue']], testGram.allPrevWords, "first experiment, prev words")
        testEqualLists([['very', 'big'], ['blue'], ['chair'], []], testGram.allNextWords, "first experiment, next words")
        # test fullResults and seqsAndRules:
        testEqualLists([('test', 'run'), ('very', 'optional'), ('big', 'optional'), ('blue', 'run'), ('chair', 'extra')],
                        testGram.fullResults, "first experiment, fullResults")
        testEqualLists([(['test'], 'run'), (['very', 'big'], 'optional'), (['blue'], 'run'), (['chair'], 'extra')],
                        testGram.seqsAndRules, "first experiment, seqsAndRules")
        # check total and reset:
        
        # check dict wordsByRule (new jan 2012)
        expDict = {'optional': ['very', 'big'], 'run': ['test', 'blue'], 'extra': ['chair']}
        testwordsByRule(expDict, testGram.wordsByRule, 'RulesByName not as expected')
        testGram.checkExperiment(['test', 'very', 'big', 'blue', 'chair'])


        # more words, less rules
        natlink.recognitionMimic(['test', 'red', 'green', 'blue', 'table'])
        testEqualLists([None, 'run'], testGram.allPrevRules, "second experiment, prev rules")
        testEqualLists(['extra', None], testGram.allNextRules, "second experiment, next rules")
        testEqualLists([[], ['test', 'red', 'green', 'blue']], testGram.allPrevWords, "second experiment, prev words")
        testEqualLists([['table'], []], testGram.allNextWords, "second experiment, next words")
        # test fullResults and seqsAndRules:
        testEqualLists([('test', 'run'), ('red', 'run'), ('green', 'run'),
                                  ('blue', 'run'), ('table', 'extra')],
                         testGram.fullResults, "first experiment, fullResults")
        testEqualLists([(['test', 'red', 'green', 'blue'], 'run'), (['table'], 'extra')],
                         testGram.seqsAndRules, "first experiment, seqsAndRules")

        # check dict wordsByRule (new jan 2012)
        expDict = {'run': ['test', 'red', 'green', 'blue'], 'extra': ['table']}
        testwordsByRule(expDict, testGram.wordsByRule, 'RulesByName not as expected')

        # check total and reset:
        testGram.checkExperiment(['test', 'red', 'green', 'blue', 'table'])

        # more words, optional at two places (see wordsByRule):
        natlink.recognitionMimic(['test', 'very', 'green', 'table', 'small'])
        testEqualLists([None, 'run', 'optional', 'run', 'extra'], testGram.allPrevRules, "third experiment, prev rules")
        testEqualLists(['optional', 'run', 'extra', 'optional', None], testGram.allNextRules, "third experiment, next rules")
        testEqualLists([[], ['test'], ['very'], ['green'], ['table']], testGram.allPrevWords, "third experiment, prev words")
        testEqualLists([['very'], ['green'], ['table'], ['small'], []]
                                    , testGram.allNextWords, "third experiment, next words")
        # test fullResults and seqsAndRules:
        testEqualLists([('test', 'run'), ('very', 'optional'), ('green', 'run'),
                            ('table', 'extra'), ('small', 'optional')],
                         testGram.fullResults, "third experiment, fullResults")
        testEqualLists([(['test'], 'run'), (['very'], 'optional'), (['green'], 'run'),
                            (['table'], 'extra'), (['small'], 'optional')],
                         testGram.seqsAndRules, "third experiment, seqsAndRules")
        
        # check dict wordsByRule (new jan 2012)
        expDict = {'optional': ['very', 'small'], 'run': ['test', 'green'], 'extra': ['table']}
        testwordsByRule(expDict, testGram.wordsByRule, 'third experiment, RulesByName not as expected')
        # check total and reset:
        testGram.checkExperiment(['test', 'very', 'green', 'table', 'small'])

        testGram.unload()

    ## check if all goes well with a recursive call (by recognitionMimic) in the same grammar
    ## a problem was reported Febr 2013 by Mark Lillibridge concerning a Vocola grammar

    def testNextPrevRulesAndWordsRecursive(self):
        self.log("testNextPrevRulesAndWordsRecursive", 1)
        testForException = self.doTestForException
        testwordsByRule = self.doTestEqualDicts
        class TestGrammar(GrammarBase):

            gramSpec = """
                <run> exported = recursivetest {colors} [<recursive>] <extra>;
                <recursive> = continue;
                <extra> = extra;
            """

            def resetExperiment(self):
                self.results = []
                self.allNextRules = []
                self.allPrevRules = []
                self.allNextWords = []
                self.allPrevWords = []
                self.cbdList = []  # record also the callbackDepths

            def checkExperiment(self,expected):
                if self.results != expected:
                    raise TestError, "Grammar failed to get recognized\n   Expected = %s\n   Results = %s"%( str(expected), str(self.results) )
                self.resetExperiment()
        
            def initialize(self):
                self.load(self.gramSpec)
                self.activateAll()
                self.resetExperiment()
                self.setList('colors', ['red', 'green', 'blue'])
                self.testNum = 0
                
            def gotResults_run(self,words,fullResults):
                self.results.extend(words)
                cbd = natlink.getCallbackDepth()
                self.cbdList.append('%s: %s'% ('run', cbd))
                if cbd == 1:
                    self.allNextRules.append(self.nextRule)
                    self.allPrevRules.append(self.prevRule)
                    self.allNextWords.append(self.nextWords)
                    self.allPrevWords.append(self.prevWords)
            
            def gotResults_extra(self,words,fullResults):
                self.results.extend(words)
                cbd = natlink.getCallbackDepth()
                self.cbdList.append('%s: %s'% ('extra', cbd))
                if cbd == 1:
                    self.allNextRules.append(self.nextRule)
                    self.allPrevRules.append(self.prevRule)
                    self.allNextWords.append(self.nextWords)
                    self.allPrevWords.append(self.prevWords)
                    
            def gotResults_recursive(self,words,fullResults):
                self.results.extend(words)
                cbd = natlink.getCallbackDepth()
                self.cbdList.append('%s: %s'% ('recursive', cbd))
                if cbd == 1:
                    self.allNextRules.append(self.nextRule)
                    self.allPrevRules.append(self.prevRule)
                    self.allNextWords.append(self.nextWords)
                    self.allPrevWords.append(self.prevWords)
                    natlink.recognitionMimic('recursive', 'green', 'extra')

        testEqualLists = self.doTestEqualLists
        testGram = TestGrammar()
        testGram.initialize()
        testGram.testNum = 1
        ## why does not this rule mimic correct?
        ## QH Febr 2018 TODO
        natlink.recognitionMimic(['recursivetest', 'green', 'extra'])
        testEqualLists([None, 'run'], testGram.allPrevRules, "first experiment, prev rules, not yet recursive")
        testEqualLists(['extra', None], testGram.allNextRules, "first experiment, next rules, not yet recursive")
        testEqualLists([[], ['recursive', 'green']], testGram.allPrevWords, "first experiment, prev words, not yet recursive")
        testEqualLists([['extra'], []], testGram.allNextWords, "first experiment, next words, not yet recursive")
        testEqualLists(['run: 1', 'extra: 1'], testGram.cbdList, "first experiment, callback depth, not yet recursive")
        
        # test fullResults and seqsAndRules:
        testEqualLists([('recursive', 'run'), ('green', 'run'), ('extra', 'extra')],
                        testGram.fullResults, "first experiment, fullResults")
        testEqualLists( [(['recursive', 'green'], 'run'), (['extra'], 'extra')],
                        testGram.seqsAndRules, "first experiment, seqsAndRules")
        # check total and reset:
        
        # check dict wordsByRule (new jan 2012)
        expDict =  {'run': ['recursive', 'green'], 'extra': ['extra']}

        testwordsByRule(expDict, testGram.wordsByRule, 'RulesByName not as expected, recursive')
        testGram.checkExperiment(['recursive', 'green', 'extra'])   ## all words recognised


        # now also call the recursive rule:
        natlink.recognitionMimic(['recursive', 'red', 'continue', 'extra'])
        testEqualLists(['run: 1', 'recursive: 1', 'run: 2', 'extra: 2', 'extra: 1'],
                        testGram.cbdList, "second experiment, callback depth, recursive")
        
        ### the following four are only take for callbackDepth == 1
        testEqualLists([None, 'run', 'recursive'], testGram.allPrevRules, "second experiment, prev rules, recursive")
        testEqualLists(['recursive', 'extra', None],
                      testGram.allNextRules, "second experiment, next rules, recursive")
        testEqualLists([[], ['recursive', 'red'], ['continue']],
            testGram.allPrevWords, "second experiment, prev words, recursive")
        testEqualLists([['continue'], ['extra'], []],
            testGram.allNextWords, "second experiment, next words, recursive")
        # test fullResults and seqsAndRules:
        testEqualLists([('recursive', 'run'), ('green', 'run'), ('extra', 'extra')],
                         testGram.fullResults, "first experiment, fullResults")
        testEqualLists([(['recursive', 'green'], 'run'), (['extra'], 'extra')],
                         testGram.seqsAndRules, "first experiment, seqsAndRules")

        # check dict wordsByRule (new jan 2012)
        expDict = {'run': ['recursive', 'green'], 'extra': ['extra']}
        testwordsByRule(expDict, testGram.wordsByRule, 'RulesByName not as expected, recursive')

        # check total and reset:
        # here both recognitions are recorded (first and second recursive recognitionMimic):
        testGram.checkExperiment(['recursive', 'red', 'continue', 'recursive', 'green', 'extra', 'extra'])

        testGram.unload()

    ##def toggleMicrophone(wait=0):
    ##    natlink.setMicState('on')
    ##    natlink.setMicState('off')
    ##    time.sleep(wait)
    def toggleMicrophone(self, w=0.1):
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

    def testNestedMimics(self):
        self.log("testNestedMimics", 1)
        testForException = self.doTestForException
        class TestGrammar(GrammarBase):

            gramSpec = """
                <run> exported = testtestrun ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 ) ;
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
                    raise TestError("Grammar failed to get recognized\n   Expected = %s\n   Results = %s"%( str(expected), str(self.results) ))
                self.resetExperiment()
        
            def initialize(self):
                self.load(self.gramSpec)
                self.activateAll()
                self.resetExperiment()

            def gotResults_run(self,words,fullResults):
                self.results.append('run')
                natlink.recognitionMimic(['test','test',words[1]])

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
        natlink.recognitionMimic(['testtestrun','1'])
        testGram.checkExperiment(['run','1'])
        
        natlink.recognitionMimic(['testtestrun','2'])
        testGram.checkExperiment(['run','2','1'])

        natlink.recognitionMimic(['testtestrun','3'])
        testGram.checkExperiment(['run','3','1'])
        
        natlink.recognitionMimic(['testtestrun','4'])
        testGram.checkExperiment(['run','4','3','1'])
        
        if DNSVersion < 12:
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
        #self.log("hit callbacktester")
        if self.sawTextChange == None:
            self.sawTextChange = (delStart,delEnd,newText,selStart,selEnd)
        elif self.sawTextChange != (delStart,delEnd,newText,selStart,selEnd):
            ds, de, nt, ss, se = self.sawTextChange
            raise TestError('CallbackTester  more runs gives different results,\nexpected: %s,%s,"%s",%s,%s\ngot:  %s,%s,"%s",%s,%s'%
                           (ds, de, nt, ss, se, delStart,delEnd,newText,selStart,selEnd ))
        

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
    def doTestTextChange(self,moduleInfo,textChange):
        if self.sawBegin != moduleInfo:
            raise TestError("Wrong results from begin callback\n  saw: %s\n  expecting: %s"%(repr(self.sawBegin),repr(moduleInfo)))
        if self.sawTextChange != textChange:
            raise TestError("Wrong results from change callback\n  saw: %s\n  expecting: %s"%(repr(self.sawTextChange),repr(textChange)))
        self.reset()
    
    # Tests the contents of the object.  For this test we assume that we saw
    # both a begin callback and a results callback with the indicated values
    def doTestResults(self,moduleInfo,results):
        if self.sawBegin != moduleInfo:
            raise TestError("Wrong results from begin callback\n  saw: %s\n  expecting: %s"%(repr(self.sawBegin),repr(moduleInfo)))
        if self.sawResults == None and results != None:
            raise TestError("Did not see results callback")
        if self.sawResults != None and self.sawResults[0] != results:
            raise TestError("Wrong results from results callback\n  saw: %s\n  expecting: %s "%(repr(self.sawResults[0]),repr(results)))
        self.reset()

class RecordCommandOrDictation(GrammarBase):
    """through this class you can collect if which type of recognition was there
    
    if self.hadRecog == '', initialize was called, but no recognition
    if self.hadRecog in 'gotbegin', 'dictation' or 'command', the state
        (no recognition, dictate or command) is given
    """
    gramSpec = '<dummycommand> exported = {emptylist};'
    def initialize(self):
        self.load(self.gramSpec, allResults=1)
        self.activateAll()
        self.hadRecog = ''
    def gotBegin(self,moduleInfo):
        self.hadRecog = 'getbegin'
    def gotResultsObject(self, recogType, resObj):
        try:
            words = resObj.getWords(0)
        except (natlink.OutOfRange, IndexError):
            self.hadRecog = 'norecog'
            return
        if recogType == 'self':
            raise TestError("grammar RecordCommandOrDictation should never hit itself: %s"% recogType)
        if recogType == 'other':
            self.hadRecog = 'command'
        else:
            self.hadRecog = 'dictate'
    
    def __init__(self):
        GrammarBase.__init__(self)

    # change callback of DictObj
    def onTextChange(self,delStart,delEnd,newText,selStart,selEnd):
        # because of the bug in NatSpeak where we can get two change
        # callbacks in a row, especially when dealing with scratch that, we
        # ignore all but the first callback
        if self.sawTextChange == None:
            self.sawTextChange = (delStart,delEnd,newText,selStart,selEnd)
        elif self.sawTextChange != (delStart,delEnd,newText,selStart,selEnd):
            ds, de, nt, ss, se = self.sawTextChange
            raise TestError('CallbackTester  more runs gives different results,\nexpected: %s,%s,"%s",%s,%s\ngot:  %s,%s,"%s",%s,%s'%
                           (ds, de, nt, ss, se, delStart,delEnd,newText,selStart,selEnd ))
        

    # begin callback of natlink,GramObj and DictObj
    def onBegin(self,moduleInfo):
        self.sawBegin = moduleInfo


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
    gramSpec = '<Start> exported = this is automated testing from python %s;'
    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()
        self.hadRecog = 0
    def gotBegin(self,moduleInfo):
        self.hadRecog = 0
    def gotResults(self,words, fullResults):
        self.hadRecog = 1
    
        
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

    note print depends on the state of natlink: where it goes or disappears...
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

def clearClipboard():
    """clears the clipboard

    No input parameters, no result,

    """
    import win32clipboard
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
    finally:
        win32clipboard.CloseClipboard()    


logFile = None

def run():
    global logFile, natconnectOption
    logFile = open(logFileName, "w")
    log("log messages to file: %s"% logFileName)
    log('starting unittestNatlink')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def test....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    suite = unittest.makeSuite(UnittestNatlink, 'test')
##    natconnectOption = 0 # no threading has most chances to pass...
    log('\nstarting tests with threading: %s\n'% natconnectOption)
    result = unittest.TextTestRunner().run(suite)
    dumpResult(result, logFile=logFile)
    
    logFile.close()

if __name__ == "__main__":
    run()
