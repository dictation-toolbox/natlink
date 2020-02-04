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
import unittest
import os
import os.path
import time
import traceback        # for printing exceptions
from struct import pack

import natlink
import gramparser
from natlinkutils import *
import win32gui
class TestError(Exception):
    pass
ExitQuietly = 'ExitQuietly'

# for test trick (wordFuncs, wordProns):
NoneOr0 = [None, 0]


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
            raise TestError('NatSpeak is not currently running')
##        self.connect()
##        self.user = natlink.getCurrentUser()[0]
##        self.lookForDragonPad()


    def tearDown(self):
        pass
##        self.killDragonPad()
##        self.killCalc()
##        self.clearTestFiles()
##        natlink.openUser(self.user)
        

    def wait(self, t=None):
        time.sleep(t or 0.1)


    #---------------------------------------------------------------------------
    # These test should be run before we call natConnect

    def testPreTests(self):
        # make sure that NatSpeak is loaded into memory
        testForException = self.doTestForException
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

    def testPostTests(self):
        # make sure that NatSpeak is still loaded into memory
        testForException = self.doTestForException
        # make sure we get exceptions again assessing our functions
        testForException( natlink.NatError, "natlink.playString('')" )
        testForException( natlink.NatError, "natlink.getCurrentModule()" )

    #---------------------------------------------------------------------------
    # This utility subroutine executes a Python command and makes sure that
    # an exception (of the expected type) is raised.  Otherwise a TestError
    # exception is raised

    def doTestForException(self, exceptionType,command,localVars={}):
        try:
            exec(command,globals(),localVars)
        except exceptionType:
            return
        raise TestError('Expecting an exception to be raised calling '+command)

    #---------------------------------------------------------------------------
    # This utility subroutine will returns the contents of the NatSpeak window as
    # a string.  It works by using playString to select the contents of the
    # window and copy it to the clipboard.  We have to also add the character 'x'
    # to the end of the window to handle the case that the window is empty.

def run():
    print('starting unittestPrePost')
    unittest.main()
    

if __name__ == "__main__":
    run()
