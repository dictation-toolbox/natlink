#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# unittestNatlinktimer.py
#   This script performs tests of the Natlinktimer module
#   natlinktimer.py, for multiplexing timer instances acrross different grammars
#   Quintijn Hoogenboom, summer 2020
#

import sys
import unittest
import time
import traceback        # for printing exceptions

from pathqh import path

import natlink
from natlinkutils import GrammarBase
import natlinktimer

class TestError(Exception):
    pass
ExitQuietly = 'ExitQuietly'


# try some experiments more times, because gotBegin sometimes seems
# not to hit
nTries = 10
natconnectOption = 1 # or 1 for threading, 0 for not. Seems to make difference
                     # with spurious error (if set to 1), missing gotBegin and all that...
def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    return a str...
    """
    baseFolder = path(".").normpath()
    return baseFolder

thisDir = getBaseFolder(globals())

logFileName = path(thisDir)/"Natlinktimertestresult.txt"

# make different versions testing possible:
import natlinkstatus
nlstatus = natlinkstatus.NatlinkStatus()
DNSVersion = nlstatus.getDNSVersion()

#---------------------------------------------------------------------------
# These tests should be run after we call natConnect
class UnittestNatlinktimer(unittest.TestCase):
    def setUp(self):
        if not natlink.isNatSpeakRunning():
            raise TestError('NatSpeak is not currently running')
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
            natlinktimer.stopTimerCallback()
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
        raise TestError('Expecting an exception to be raised calling '+command)
                
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
        self.assertEqual(expected, actual, 'Function call "%s" returned unexpected result\nExpected: %s, got: %s'%
                          (command, expected, actual))

    def testSingleTimer(self):
        testName = "testSingleTimer"
        self.log(testName)

        # Create a simple command grammar.
        # This grammar then sets the timer, and after 3 times expires

        class TestGrammar(GrammarBase):

            def __init__(self):
                GrammarBase.__init__(self)
                self.resetExperiment()

            def resetExperiment(self):
                self.Hit = 0
                self.MaxHit = 5
                self.sleepTime = 0 # to be specified by calling instance, the sleeping time after each hit
                self.results = []

            def report(self):
                """print the results lines
                """
                for line in self.results:
                    print(line)

            def doTimer(self):
                self.results.append(f'doTimer {self.Hit}')
                self.Hit +=1
                log(f"hit {self.Hit}")
                time.sleep(self.sleepTime/1000)  # sleep 10 milliseconds
                if self.Hit == self.MaxHit:
                    expectElapsed = self.Hit * self.interval
                    print(f"expect duration of this timer: {expectElapsed}")
                    natlinktimer.removeTimerCallback(self.doTimer)
                ## try to shorten interval:
                currentInterval = self.grammarTimer.interval
                if currentInterval > 150:
                    newInterval = currentInterval - 10
                    return newInterval

        testGram = TestGrammar()
        testGram.interval = 200
        testGram.sleepTime = 30  # all milliseconds now
        testGram.grammarTimer = natlinktimer.setTimerCallback(testGram.doTimer, interval=testGram.interval, debug=1)
        for i in range(5):
            if testGram.Hit >= testGram.MaxHit :
                printInfo = str(testGram.grammarTimer)
                self.log(f"timer seems to be ready. results: {printInfo}")
                break
            wait(1000)
        else:
            self.log(f"waiting time expired, results got: {testGram.results}")
        testGram.report()
        self.log("End of %s"% testName)
   
def wait(tmilli=100):
    """wait milliseconds via waitForSpeech loop of natlink
    
    default 100 milliseconds, or 0.1 second
    """
    tmilli = int(tmilli)
    natlink.waitForSpeech(tmilli)
   
def log(t, refresh=None):
    """logging is a mess, just print here...
    """
    print(t)
    # openOption = 'a' if not refresh else 'w'
    # with open(logFileName, openOption) as lf:
    #     lf.write(t + '\n')
    
#---------------------------------------------------------------------------
# run
#
# # This is the main entry point.  It will connect to NatSpeak and perform
# # a series of tests.  In the case of an error, it will cleanly disconnect
# # from NatSpeak and print the End of testSingleTimer
# def dumpResult(testResult, logFileName):
#     """dump into the logFile
#     """
#     with open(logFileName, 'a') as logFile:
#         if testResult.wasSuccessful():
#             mes = "all succesEnd of testSingleTimerful"
#             logFile.write(mes)
#             return
#         logFile.write('\n--------------- errors -----------------\n')
#         for case, tb in testResult.errors:
#             logFile.write('\n---------- %s --------\n'% case)
#             logFile.write(tb)
#             
#         logFile.write('\n--------------- failures -----------------\n')
#         for case, tb in testResult.failures:
#             logFile.write('\n---------- %s --------\n'% case)
#             logFile.write(tb)


def run():
    # log("log messages to file: %s"% logFileName)
    log('starting unittestNatlinktimer')
    suite = unittest.makeSuite(UnittestNatlinktimer, 'test')
    log('\nstarting tests with threading: %s\n'% natconnectOption)
    result = unittest.TextTestRunner().run(suite)
    # log(result)

if __name__ == "__main__":
    baseFolder = getBaseFolder()
    log(f"baseFolder: {baseFolder}", refresh=True)
    log("no log file, just printing on console")
    run()
