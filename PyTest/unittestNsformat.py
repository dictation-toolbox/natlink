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

    def wait(self, t=1):
        time.sleep(t)

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
    #---------------------------------------------------------------------------
    # here we test the nsformat functions, (provided by Joel Gould, now in Core directory)
    # in order to format a recognition (of DictGram) into a string, preserving the state
    # of the formatting flags
    def testNsformat(self):
        self.log("testNsformat")
        pass
        testFuncReturn = self.doTestFuncReturn

        expected1 = ('Hello', ())
        testFuncReturn(expected1, 'formatWords(["hello"], %s)'% None, locals())

        expected2 = (' again.', (9, 4))
        testFuncReturn(expected2, 'formatWords(["again", r".\period"], expected1[1])', locals())

        expected3 = ('  New sentence', ())
        testFuncReturn(expected3, 'formatWords(["new", "sentence"], expected2[1])', locals())

        #example from Joels original test:
        words = [r'\Caps-On', 'as', 'you', 'can', 'see', r',\comma',
                'this', 'yours truly', 'seems', 'to', 'work', r'\Caps-Off', 'well']
        expected4 = ('As You Can See, This Yours Truly Seems to Work well', ())
        testFuncReturn(expected4, 'formatWords(words, None)', locals())



    def testFormatWord(self):
        """all words with normal (0) state as input.
        
        .\point results in ' .'
        """
        words =             ['.', r'.\period', r'.\point', r',\comma', r':\colon', r'-\hyphen', 'normal']
        formattedExpected = [' .', '.',        ' .',       ',',        ':',        '-', ' normal']
        stateExpected =      [(), (9, 4),      (8, 10),    (),       (),           (8,), ()]
        for word, expectedWord, expectedState in zip(words,  formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=None, stateFlags=0)
            print 'stateFlages after formatting of %s: %s (%s)'% (word, `newState`, `showStateFlags(newState)`)
            self.assert_(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assert_(expectedState == newState, "state after %s (%s) not as expected\nActual: %s, Expected: %s"%
                         (word, formattedResult, `newState`, `expectedState`))
        
    def testFlagsLike(self):
        """tests the different predefined flags in nsformat"""
        for w,t in [(r'.\period', 'period'),
                    (r',\comma', 'comma'),
                    (r'-\hyphen', 'hyphen'),
                    (r':\colon', 'colon'),
                    ( (10,), 'number'),
                   ]:
            varInNsformat = 'flags_like_%s'% t
            if type(w) == types.TupleType:
                flags = w
            else:
                wInfo = natlink.getWordInfo(w)
                self.assert_(wInfo != None, "word info for word: %s could not be found. US user???"% w)
                flags = wordInfoToFlags(wInfo)
                flags.discard(3)
                flags = tuple(flags) # no delete flag not interesting
            fromNsFormat = globals()[varInNsformat]
            self.assert_(fromNsFormat == flags, "flags_like variable |%s| not as expected\nIn nsformat.py: %s (%s)\nFrom actual word infoExpected: %s (%s)"%
                         (varInNsformat, fromNsFormat, showStateFlags(fromNsFormat), flags, showStateFlags(flags)))
    def testInitializeStateFlags(self):
        """test helper functions of nsformat"""
        result = initializeStateFlags()
        expected = ()
        self.assert_(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))

        result = initializeStateFlags(flag_cond_no_space)
        expected = (10,)
        self.assert_(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))
        
        result = initializeStateFlags(flag_cond_no_space, flag_no_formatting)
        expected = (10, 18)
        self.assert_(expected == result, "initialised state flags not as expected\nActual: %s, Expected: %s"%
                     (result, expected))
        readable = showStateFlags(result)
        expectedReadable = ('flag_cond_no_space', 'flag_no_formatting')
        self.assert_(expectedReadable == readable, "initialised state flags readable were not as expected\nActual: %s, Expected: %s"%
                     (readable, expectedReadable))
        
            
            
    def testFormatNumbers(self):
        """words with input of previous word, influencing numbers, to be kept together
        
        """
        words =             [r'3\three', r'.\point', r'5\five', r'by', r'4\four', 'centimeter',
                             r',\comma', 'proceeding']
        formattedExpected = [' 3', '.',        '5', ' by', ' 4', ' centimeter', ',', ' proceeding']
        wordInfos = [(flag_cond_no_space,), None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, None, None]
        stateExpected = [(10,), (8, 10), (10,), (), (10,), (), (), (), ()]
        newState = 0
        totalResult = []
        for word, info, expectedWord, expectedState in zip(words,  wordInfos, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=info, stateFlags=newState)
            totalResult.append(formattedResult)
            print 'showStateFlages of %s: %s'% (word, `showStateFlags(newState)`)
            self.assert_(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assert_(expectedState == newState, "state of %s (%s) not as expected\nActual: %s, expected: %s"%
                         (word, formattedResult, `newState`, `expectedState`))
        expected = " 3.5 by 4 centimeter, proceeding"
        actual = ''.join(totalResult)
        self.assert_(expected == actual, "total result of first test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))




        # point without flag_cond_no_space around:
        words =             [r'the', r'.\point', r'is', r'.\period']
        formattedExpected = ['The', ' .',        'is', '.']
        stateExpected =     [(),   (8, 10),      (),  (9, 4)]
        newState = None  # start of buffer
        totalResult = []
        for word, expectedWord, expectedState in zip(words, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=None, stateFlags=newState)
            totalResult.append(formattedResult)
            print 'showStateFlages of %s: %s'% (word, `showStateFlags(newState)`)
            self.assert_(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assert_(expectedState == newState, "state of %s (%s) not as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, `newState`, `expectedState`))

        expected = "The .is."
        actual = ''.join(totalResult)
        self.assert_(expected == actual, "total result of second test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))


        # words, numbers, words
        words =             [r'the', r'test', r'is', r'3\three', r'.\point', r'4\four', 'by', r'5\five', 'centimeter']
        wordInfos = [None, None, None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, (flag_cond_no_space,), None, None, None]
        formattedExpected = ['The', ' test', ' is', ' 3', '.', '4', ' by', ' 5', ' centimeter']
        stateExpected =     [(),      (),      (),  (10,), (8, 10), (10,), (), (10,), ()]
        newState = None  # start of buffer
        totalResult = []
        for word, wordInfo, expectedWord, expectedState in zip(words, wordInfos, formattedExpected, stateExpected):
            ## all starting with stateFlags 0, normal formatting behaviour:
            formattedResult, newState = formatWord(word, wordInfo=wordInfo, stateFlags=newState)
            totalResult.append(formattedResult)
            print 'showStateFlages of %s: %s'% (word, `showStateFlags(newState)`)
            self.assert_(formattedResult == expectedWord,
                         "word |%s| not formatted as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, expectedWord))
            self.assert_(expectedState == newState, "state of %s (%s) not as expected\nActual: |%s|, expected: |%s|"%
                         (word, formattedResult, `newState`, `expectedState`))

        expected = "The test is 3.4 by 5 centimeter"
        actual = ''.join(totalResult)
        self.assert_(expected == actual, "total result of third test not as expected\nActual: |%s|, expected: |%s|"%
                         (actual, expected))
            
            
            
   
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
    # the test names to her example def test....
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
