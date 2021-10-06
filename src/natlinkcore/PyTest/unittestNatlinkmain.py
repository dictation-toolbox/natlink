#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
"""unittestNatlinkmain

Tests the loading and unloading of grammar files, as is done in natlinkmain.py

This test file was formerly in "unittestNatlink" and before that in "testnatlink.py".

It is now a separate file, which should run in TEST mode, which means that ...

"""
#pylint:disable=C0302, C0115, C0116, R0902, R0904, R0201, R0913, R0915, W0201, W0702, W0622, W0621
import sys
import os
import unittest
import time
import shutil
from pathlib import Path
from natlinkcore import natlink
from natlinkcore import natlinkstatus
from natlinkcore import natlinkmain  
from natlinkcore import getNatlinkUserDirectory

import natlinkcore  ## getThisDir
from natlinkcore.natlinkutils import getBaseName
from natlinkcore.natlinkutils import GrammarBase
# from natlinkcore import natlinkutils
from dtactions.sendkeys import sendkeys
import win32gui
import win32clipboard   # clearClipboard, refactor
## try debugview:
from pydebugstring.output import outputDebugString
# make different versions testing possible:
status = natlinkstatus.NatlinkStatus()
DNSVersion = status.getDNSVersion()

thisDir = natlinkcore.getThisDir(__file__)
coreDir = natlinkcore.getNatlinkDirectory()
# appending to path if necessary:
# if not os.path.normpath(coreDir) in sys.path:
#     print('inserting %s to pythonpath...'% coreDir)
#     sys.path.insert(0, coreDir)

natconnectOption = 0 # or 1 for threading, 0 for not. Seems to make difference
                     # at least some errors in testNatlinkMain seem to be raised when set to 0
doSleep = 0.2
## getWindowContents has a sleep of 0.2 all the time...
# set to a small (time) number if some tests should be slowed down
                     # eg doTestWindowContents
                     # especially after a paste action, some pause should be set..
                     # 0.1 seems to fit, 0.05 seems to be too short...
                     # see testNatlinkutilsPlayString and testPlayString

class TestError(Exception):
    """TestError"""
class ShouldBeCommandError(Exception):
    """ShouldBeCommandError"""
ExitQuietly = 'ExitQuietly'

# try some experiments more times, because gotBegin sometimes seems not to hit
nTries = 10
logFileName = str(Path(thisDir)/"testresult.txt")

## try more special file names, test in testNatlinkMain:
spacesFilenameGlobal = '_with spaces'
spacesFilenameCalcInvalid = 'calc with spaces' # must be only "calc" or "calc_ ajajajaja"
spacesFilenameCalcValid = 'calc_with underscore'   
specialFilenameCalc = 'calc_JMg+++&_'
specialFilenameGlobal = '__jMg_$&^_abc'

# These tests should be run after we call natConnect
class UnittestNatlinkmain(unittest.TestCase):
    def setUp(self):
        outputDebugString('setting up UnittestNatlinkmain')
        self.makeEmptyTestDirectory()  ## 
        if not natlink.isNatSpeakRunning():
            raise TestError('NatSpeak is not currently running')
        self.connect()
        # remember user and get DragonPad in front:
        self.user = natlink.getCurrentUser()[0]
        self.setMicState = "off"
        self.IDEHndle = natlink.getCurrentModule()[2]
        self.lookForDragonPad()
        self.commandModeState = False
        # self.lookForWord()
        
    def tearDown(self):
        try:
            # give message:
            self.setMicState = "off"
            if self.commandModeState:
                self.setCommandMode(0)
            # kill things
            self.killCalc()
            self.lookForDragonPad()
            sendkeys("\n\ntearDown, reopen user: '%s'"% self.user)
            # self.clearTestFiles()
            self.clearDragonPad()
            # reopen user:
            #natlink.openUser(self.user)
            #self.killDragonPad()
        finally:
            self.disconnect()
        
    def connect(self):
        # start with 1 for thread safety when run from pythonwin:
        natlink.natConnect(natconnectOption)
        # natlinkmain.start_natlink()

    def disconnect(self):
        natlink.natDisconnect()
        
    def log(self, t, doPlaystring=None):
        # displayText seems not to work:
        natlink.displayText(t, 0)
        if doPlaystring:
            sendkeys(t+'\n')
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
            mod, _title, _hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            print('mod: %s'% mod)
            if mod == 'winword':
                print('got word after %s steps'% i)
                break
            i += 1
        sendkeys("{ctrl+a}{ctrl+c}")
        self.wait(1)
        t = natlink.getClipboard()
        if t:
            sendkeys("{ctrl+n}")
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
            mod, _title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            # print 'mod: %s'% mod
            if mod == "natspeak":
                break
            i += 1
            print('waiting for DragonPad: %s'% i)
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
        mod, _title, _hndle = natlink.getCurrentModule()
        mod = getBaseName(mod)
        print('mod: %s'% mod)
        if mod != "natspeak":
            raise TestError("clearDragonPad: DragonPad should be in the foreground, not: %s"% mod)
        sendkeys("{ctrl+a}{del}")
        time.sleep(0.2)
    
    def lookForCalc(self):
        """start/find Calc"""
        try:
            self.CalcHndle
        except AttributeError:
            self.CalcHndle = None
        if self.CalcHndle:
            hndle = self.CalcHndle
            try:
                win32gui.SetForegroundWindow(hndle)
            except Exception as exc:
                raise TestError("cannot get Calc back into foreground, hndle: %s"% hndle) from exc
    
            # wait for the right window to appear:        
            i = 0
            while i < 10:
                time.sleep(0.1)
                mod, _title, hndle = natlink.getCurrentModule()
                mod = getBaseName(mod)
                if mod in ["calc", "ApplicationFrameHost"]:
                    return hndle
                i += 1
            raise TestError("in lookForCalc, cannot get back to Calc window, have: %s"% mod)

        ## now for new Calc window:
        natlink.execScript('AppBringUp "calc"')
        
        # wait for the window:
        i = 0
        while i < 10:
            time.sleep(0.1)
            print('waiting for calc window %s'% i)
            mod, _title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod in ["calc", "ApplicationFrameHost"]:
                break
            i += 1
        else:
            raise TestError("Not the correct application: %s is brought to the front, should be calc"% mod)
        self.CalcMod = mod
        print('setting CalcHndle: %s'% hndle)
        self.CalcHndle = hndle
        return hndle

    def emptyDragonPad(self):
        """assume DragonPad is in front already"""
        sendkeys('{ctrl+a}{del}')
        self.doTestWindowContents('')
        

    def killDragonPad(self):
        print('going to kill DragonPad')
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
        except Exception as exc:
            raise TestError("cannot get DragonPad foreground, hndle: %s"% hndle) from exc

        # wait for the right window to appear:        
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, _title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod == "natspeak":
                break
            i += 1
        else:
            raise TestError("in killDragonPad, could not get back to DragonPad window, have: %s"% mod)

        sendkeys("{alt+f4}")
        print('closing dragonpad')
        # wait for the window to disappear (possibly get child window y n dialog)
        i = 0
        while i < 10:
            time.sleep(0.1)
            mod, _title, hndle = natlink.getCurrentModule()
            if hndle != self.DragonPadHndle:
                break
            i += 1
        else:
            raise TestError("in killDragonPad, could not close the DragonPad window")
        del self.DragonPadHndle

        # if gets into child window press n (not save)
##        mod, _title, hndle = natlink.getCurrentModule()
##        sys.stderr.write('mod, _title, hndle: %s, %s, %s'% (mod, _title, hndle))
##        if mod != "natspeak":
##            return   # finished
        
        if not self.isTopWindow(hndle):
            sendkeys("n")
            time.sleep(0.1)
        mod, _title, hndle = natlink.getCurrentModule()
        if not self.isTopWindow(hndle):
            raise TestError("in killDragonPad, did not return to a top window")

    
    def killCalc(self):
        try:
            wantHndle = self.CalcHndle
        except AttributeError:
            # not active:
            return
        if not win32gui.IsWindow(wantHndle):
            self.log("killCalc, not a valid window: %s"% wantHndle)
            return
        i = 0
        while i < 10:
            try:
                win32gui.SetForegroundWindow(wantHndle)
            except:
                pass
            time.sleep(0.1)
            mod, _title, hndle = natlink.getCurrentModule()
            mod = getBaseName(mod)
            if mod in ["calc", "ApplicationFrameHost"] and hndle == wantHndle :
                break
            sendkeys("{alt+tab!}")
            i += 1
        else:
            raise TestError("in killCalc, could not get back to Calc window")
        if i:
            print('got calc after %s steps')
        sendkeys("{alt+f4!}")
        self.CalcHndle = None
        time.sleep(0.5)

    def makeEmptyTestDirectory(self):
        """clear all in the test directory

        """
        _userdir = getNatlinkUserDirectory()
        self.testDirectory = Path(_userdir)/"Test"
        if self.testDirectory.is_dir():
            shutil.rmtree(self.testDirectory)
        self.testDirectory.mkdir()

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
        if t < 0:
            t = t*-1
        
        wmilli = round(t*1000) if t < 50 else round(t)
        if wmilli < 25:
            wmilli = 25
        self.log("calling wait with t: %s, wmilli: %s"% (t, wmilli))
        natlink.waitForSpeech(-wmilli)   # smaller values (< 50 are times 1000, so always milliseconds.)
        ##time.sleep(t)

    def setCommandMode(self, onOrOff):
        """set command mode on(1) or off(0) via recognitionMimic
        """
        if onOrOff:
            natlink.recognitionMimic(['command', 'mode', 'on'])
            self.wait(1)
            self.commandModeState = True
        else:
            natlink.recognitionMimic(['command', 'mode', 'off'])
            self.wait(1)
            self.commandModeState = False

    #---------------------------------------------------------------------------
    def doTestRecognition(self, words, shouldWork=1, log=None):
        #pylint:disable=W0621
        if shouldWork:
            try:
                natlink.recognitionMimic(words)
            except natlink.MimicFailed:
                self.fail("doTestRecognition, Should have been recognised: %s"% words)
            else:            
                if log:
                    self.log("recognised: %s"% words)
        else:
            try:
                natlink.recognitionMimic(words)
            except natlink.MimicFailed:
                if log:
                    self.log('recognitionMimic "%s" not recognized, as expected' % words)
            except Exception as exc:
                raise TestError(f'recognitionMimic "{words}", expecting another exception "{natlink.MimicFailed}", "{exc}"') from exc
            else:
                raise TestError('recognitionMimic of "%s" should have failed'% words)


    def doTestForException(self, exceptionType,command,localVars=None):
        #pylint:disable=W0122, W0123
        localVars = localVars or {}
        try:
            exec(command,globals(),localVars)
        except exceptionType:
            return
        except Exception as exc:
            excType = sys.exc_info()[0]
            raise TestError('Expecting another exception %s, got exception %s, while parsing grammar %s'% (exceptionType, excType,command)) from exc
        else:
            raise TestError('Expecting exception %s, command: %s'% (exceptionType, command))


    def doTestActiveRules(self, gram, expected):
        """gram must be a grammar instance, sort the rules to be expected and got
        """
        got = gram.activeRules
        if isinstance(got, dict):
            raise TestError('doTestActiveRules, activeRules should be a dict, not: %s (%s)'% (repr(got), type(got)))
        if not isinstance(expected, dict):
            raise TestError('doTestActiveRules, expected should be a dict, not: %s (%s)'% (repr(expected), type(expected)))
        
        self.assertEqual(expected, got,
                         'Active rules not as expected:\nexpected: %s, got: %s'%
                         (expected, got))

    def doTestValidRules(self, gram, expected):
        """gram must be a grammar instance, sort the rules to be expected and got
        """
        got = gram.validRules
        if isinstance(got, list):
            raise TestError('doTestValidRules, activeRules should be a list: %s (%s)'% (repr(got), type(got)))
        if not isinstance(expected, list):
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
        use sendkeys, and insert pauses 
        """
        clearClipboard()
        self.wait(0.2)
        sendkeys('{ctrl+end}x{ctrl+a}')
        self.wait(0.2)
        sendkeys('{ctrl+c}')
        self.wait(0.2)
        contents = natlink.getClipboard()
        self.wait(0.2)
        sendkeys('{ctrl+end}{backspace}')
        if contents == '':
            return ''
        if contents[-1:] !='x':
            raise TestError('Failed to read the contents of the NatSpeak window: |%s|'% repr(contents))
        return contents[:-1]

    def doTestWindowContents(self, expected,testName=None, stripResult=None):
        """test contents of the windows, slowing down if doSleep is set
        """
        if doSleep:
            time.sleep(doSleep)
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
        #pylint:disable=W0122, W0123
        if localVars is None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if actual != expected:
            time.sleep(1)
        self.assertEqual(expected, actual, 'Function call "%s" returned unexpected result\nExpected: %s, got: %s'%
                          (command, expected, actual))
    
    def doTestFuncReturnAlternatives(self, expected,command,localVars=None):
        
        # account for different values in case of [None, 0] (wordFuncs)
        # expected is a tuple of alternatives, which one of them should be equal to expected
        #pylint:disable=W0122, W0123
        if localVars is None:
            actual = eval(command)
        else:
            actual = eval(command, globals(), localVars)

        if not isinstance(expected, tuple):
            raise TestError("doTestFuncReturnAlternatives, invalid input %s, tuple expected"% repr(expected))
        for exp in expected:
            if actual == exp:
                break
        else:
            self.fail('Function call "%s" returned unexpected result\nnot one of expected values: %s\ngot: %s'%
                          (command, repr(expected), actual))


    def doTestFuncReturnNoneOr0(self, command,localVars=None):
        # account for different values in case of [None, 0] (wordFuncs)
        #pylint:disable=W0122, W0123
        if localVars is None:
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
        sendkeys('{alt+esc!}')

    #---------------------------------------------------------------------------
    def testUserDirectory(self):
        """test the workings of natlinkmain, loading and unloading of grammar files
        
        when microphone toggles, new files should be in, note the toggleMicrophone function uses
        natlink.waitForSpeech in order to let the callback of the Mic on (and off) come through.
        
        """
        testRecognition = self.doTestRecognition
        ## setup test directory:
        self.userDirectory = self.testDirectory/"userDirectory"
        self.userDirectory.mkdir()
        print(f'userDirectory created: {userDirectory}, is_dir: {userDirectory.is_dir()}')
        toggleMicrophone = self.toggleMicrophone()
        # Basic test of globals.  Make sure that our macro file is not
        # loaded.  Then load the file and make sure it is loaded.
        ## set microphone off:
        natlink.setMicState('off')

    def tttestRest(self):

  
        self.log('create jMg1, seventeen', 'seventeen')
        testRecognition = self.doTestRecognition
        createMacroFile(baseDirectory,'__jMg1.py', 'seventeen')
        # direct after create no recognition yet
        testRecognition(['strangeword', 'Natlink', 'commands','seventeen'], 0, log=1)
        
        toggleMicrophone()

        # after toggle it should be in:
        testRecognition(['strangeword', 'Natlink', 'commands','seventeen'], 1)
        testRecognition(['strangeword', 'Natlink', 'commands','one'], 0, log=1)
        self.log('create jMg1, one', 'one')
        
        createMacroFile(baseDirectory,'__jMg1.py','one')
        #here the grammar is created, but not should not be recognised by Natlink yet
        testRecognition(['strangeword', 'Natlink', 'commands','one'], 0, log=1)

        self.log('\ntoggle mic, to get jMg1 in loadedGrammars', 1)
        toggleMicrophone()
    
        ## after toggling, this one should hit:    
        testRecognition(['strangeword', 'Natlink', 'commands','one'], 1, log=1)
        self.lookForDragonPad()

        # now separate two parts. Note this cannot be checked here together,
        # because changes in natlinkmain take no effect when done from this
        # program!
        if natlinkmain.checkForGrammarChanges:
            # Modify the macro file and make sure the modification takes effect
            # even if the microphone is not toggled.
            self.log('\nNow change grammar file jMg1 to "two", check for changes at each utterance', 1)
            createMacroFile(baseDirectory,'__jMg1.py','two')
            self.wait(0.5)    #natlink.waitForSpeech(500)
            ## with checking at each utterance next two lines should pass
            testRecognition(['strangeword', 'Natlink', 'commands','two'], 1, log=1)
            testRecognition(['strangeword', 'Natlink', 'commands','one'], 0, log=1)
        else:
            self.log('\nNow change grammar file jMg1 to 2, no recognise immediate, only after mic toggle', 1)
            createMacroFile(baseDirectory,'__jMg1.py','two')
            self.wait(0.5)
            # natlink.waitForSpeech(500)
            # If next line fails, the checking is immediate, in spite of checkForGrammarChanges being on:
            testRecognition(['strangeword', 'Natlink', 'commands','two'], 0, log=1)
            testRecognition(['strangeword', 'Natlink', 'commands','one'], 1, log=1)
            toggleMicrophone(1)
            testRecognition(['strangeword', 'Natlink', 'commands','two'], 1, log=1)
            testRecognition(['strangeword', 'Natlink', 'commands','one'], 0, log=1)

        # Make sure a user specific file also works
        # now with extended file names (glob.glob, request of Mark Lillibridge) (QH):
        self.log('now new grammar file: %s'% specialFilenameGlobal, 1)
        testRecognition(['strangeword', 'Natlink', 'commands','seven'], 0, log=1)
        createMacroFile(userDirectory,specialFilenameGlobal+'.py','seven')
        toggleMicrophone()
        if userDirectory:
            testRecognition(['strangeword', 'Natlink', 'commands','seven'], 1, log=1)
        else:
            # no userDirectory, so this can be no recognition
            testRecognition(['strangeword', 'Natlink', 'commands','seven'], 0, log=1)

        self.log('now new grammar file: %s'% spacesFilenameGlobal, 1)
        self.log('See if this file is accepted (with thirty)', 1)

        # should be unknown command:
        testRecognition(['strangeword', 'Natlink', 'commands','thirty'], 0, log=1)
        createMacroFile(userDirectory,spacesFilenameGlobal+'.py','thirty')
        # no automatic update of commands:
        testRecognition(['strangeword', 'Natlink', 'commands','thirty'], 0, log=1)
        toggleMicrophone()
        if userDirectory:
            # only after mic toggle should the grammar be recognised:
            testRecognition(['strangeword', 'Natlink', 'commands','thirty'], 1)
        else:
            self.log('this test cannot been done if there is no userDirectory')

        self.log('now new grammar file (should not be recognised)... %s'% "_.py", 1)
        testRecognition(['strangeword', 'Natlink', 'commands','eight'], 0, log=1)
        createMacroFile(userDirectory,"_.py",'eight')
        toggleMicrophone()
        testRecognition(['strangeword', 'Natlink', 'commands','eight'], 0, log=1)

        # Make sure user specific files have precidence over global files

        if userDirectory:
            self.log('now new grammar file: jMg2, four', 1)
    
            createMacroFile(baseDirectory,'__jMg2.py','four')
            createMacroFile(userDirectory,'__jMg2.py','three')
            toggleMicrophone()
            # this one seems to go wrong if the dictation box is automatically loaded for non-standard applications, switch
            # this option off for the test-speech profile:
            testRecognition(['strangeword', 'Natlink', 'commands','three'], 1, log=1)
        else:
            self.log("not userDirectory, cannot test order of command recognition between baseDirectory and userDirectory")

        # Make sure that we do the right thing with application specific
        # files.  They get loaded when the application is activated.
        self.log('now new grammar file: calc_jMg1, five', 1)
        createMacroFile(baseDirectory,'calc__jMg1.py','five')
        if userDirectory:
            self.log("userDirectory: %s"% userDirectory)
            self.log('and create in userDirectory new grammar file: calc_jMg1, six', 1)
            createMacroFile(userDirectory,'calc__jMg1.py','six')
            self.lookForCalc()
            toggleMicrophone()
            print('loadedFiles: %s'% natlinkmain.loadedFiles)
            self.log(' grammar with six (userDirectory) should take precedence over five (baseDirectory)', 1)
            testRecognition(['strangeword', 'Natlink', 'commands','five'], 0, log=0)
            testRecognition(['strangeword', 'Natlink', 'commands','six'], 1, log=0)
        else:
            self.log("without a userDirectory (Unimacro) switched on, this test is unneeded, so not done...")

        self.lookForCalc()
        # priority for user macro file:

        # more intricate filename:
        createMacroFile(baseDirectory,specialFilenameCalc+'.py','eight')
        self.log("work to be done, which file names accept??? application specific")
        self.log("see if specialFilenameCalc hits: %s"% specialFilenameCalc)
        toggleMicrophone()
        testRecognition(['strangeword', 'Natlink', 'commands','eight'], 1, log=1)

        # filenames with spaces (not valid)
        self.log("work to be done, which file names accept??? application specific")
        self.log("see if spacesFilenameCalcInvalid hits: %s"% spacesFilenameCalcInvalid)
        createMacroFile(baseDirectory,spacesFilenameCalcInvalid+'.py','fourty')
        toggleMicrophone()
        ### febr 2020, python3: fails...
        testRecognition(['strangeword', 'Natlink', 'commands','fourty'], 0, log=1)
        # filenames with spaces (valid)
        createMacroFile(baseDirectory,spacesFilenameCalcValid+'.py','fifty')
        toggleMicrophone()
        testRecognition(['strangeword', 'Natlink', 'commands','fifty'], 1, log=1)
        
        #other filenames:
##        createMacroFile(baseDirectory,'calc.py', '9')  # chances are calc is already there, so skip now...
        createMacroFile(baseDirectory,'calc_.py', 'ten')
        # this name should be invalid:
        createMacroFile(baseDirectory,'calculator.py', 'eleven')
        toggleMicrophone()
##        testRecognition(['strangeword', 'Natlink', 'commands','9'],1)
        testRecognition(['strangeword', 'Natlink', 'commands','ten'], 1, log=1)
        testRecognition(['strangeword', 'Natlink', 'commands','eleven'], 0, log=1)
        
        self.killCalc()
        ### seems to go correct, no calc window any more, so rule six (specific for calc) should NOT respond
        #was a problem: OOPS, rule 6 remains valid, must be deactivated in gotBegin, user responsibility:
        #was a problem: testRecognition(['strangeword', 'Natlink', 'commands','six'], 1)
        # no recognition because calc is not there any more:
        testRecognition(['strangeword', 'Natlink', 'commands','six'], 0, log=1)
        
    ##        sendkeys('{Alt+F4}')
#-----------------------------------------------------------
        # clean up any files created during this test
        toggleMicrophone()

        # now that the files are gone, make sure that we no longer recognize
        # from them
        testRecognition(['strangeword', 'Natlink', 'commands','one'], 0)
        testRecognition(['strangeword', 'Natlink', 'commands','two'], 0)
        testRecognition(['strangeword', 'Natlink', 'commands','three'], 0)
        testRecognition(['strangeword', 'Natlink', 'commands','four'], 0)
        

        # some of the specialFilename cases:
        ## why does this one still hit?
        ## do they only vanish when calc is in the foreground? (calc == ApplicationFrameHost)
        ## TODOQH  TODOMIKE 
        testRecognition(['strangeword', 'Natlink', 'commands','five'], 0)
        testRecognition(['strangeword', 'Natlink', 'commands','seven'], 0)
        testRecognition(['strangeword', 'Natlink', 'commands','eight'], 0)

    
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
        if self.sawTextChange is None:
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
        if self.sawResults is None and results is not None:
            raise TestError("Did not see results callback")
        if self.sawResults is not None and self.sawResults[0] != results:
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
        if self.sawTextChange is None:
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
    gramSpec = '<Start> exported = strangeword Natlink commands %s;'
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
    fileDate = natlinkmain.getFileDate(f)
    log('time of change of %s: %s'% (f, fileDate))
    
def log(t):
    """log to print and file if present

    note print depends on the state of natlink: where it goes or disappears...
    I have no complete insight is this, but checking the logfile afterwards
    always works (QH)
    """
    print(t)
    if logFile:
        logFile.write(t + '\n')
#---------------------------------------------------------------------------
# run
#
# This is the main entry point.  It will connect to NatSpeak and perform
# a series of tests.  In the case of an error, it will cleanly disconnect
# from NatSpeak and print the exception information,
def dumpResult(testResult):
    """dump into 
    """
    if testResult.wasSuccessful():
        mes = "all succesful"
        logFile.write(mes)
        return
    if not logFile:
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
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
    finally:
        win32clipboard.CloseClipboard()    


logFile = None

def run():
    logFile = open(logFileName, "w")
    log("log messages to file: %s"% logFileName)
    log('starting unittestNatlink')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def test....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    
    # if not in TEST mode (see natlinkstatus.py), quit
    if not status.isTesting():
        log('\nYou should go into TEST mode before running these tests\n')
    else:
        suite = unittest.makeSuite(UnittestNatlinkmain, 'test')
    ##    natconnectOption = 0 # no threading has most chances to pass...
        log('\nstarting tests with threading: %s\n'% natconnectOption)
        result = unittest.TextTestRunner().run(suite)
        dumpResult(result)
    
    logFile.close()

if __name__ == "__main__":
    run()
    