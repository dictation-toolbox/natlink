from __future__ import unicode_literals
"""

tests the different functions in utilsqh. Excluding the path class, these have a separate unittest file

currently:
    test_environment_variables: testing substition of (extended) environment variables AND
                                        substitution back in at front (of a filename)


                                        

"""

import unittest
import TestCaseWithHelpers
import os, os.path
import utilsqh
import time

baseFolder = utilsqh.getValidPath("(C|D):/projects/unittest/testutilsqh")

class TestError(Exception):
    pass

class UtilsqhTest(TestCaseWithHelpers.TestCaseWithHelpers):
      
    def setUp(self):
        if not baseFolder.isdir():
            raise TestError("no valid basefolder: %s"% baseFolder)
                
    def tearDown(self):
        pass
    

    def xxxxtest_environment_variables(self):

        # check getExtendedEnv, substituting ~ to HOME, PERSONAL, 
        # probably somewhere in NatLink now
        homeVariable = utilsqh.getExtendedEnv("~")
        homeVariableDuplicate = utilsqh.getExtendedEnv("HOME")
        self.assert_(len(homeVariable) > 0, "homeVariable was not caught")
        self.assert_equal(homeVariable, homeVariableDuplicate,"to ways of getting home variable should be equal" )

        personalVariable = utilsqh.getExtendedEnv("PERSONAL")
        self.assert_equal(homeVariable, personalVariable,"personalVariable should also default to homeVariable" )

        # check reversing the process, return back into a foldername with
        # substituteEnvVariableAtStart

        personalReversed = utilsqh.substituteEnvVariableAtStart(personalVariable)
        homeReversed = utilsqh.substituteEnvVariableAtStart(personalVariable)
        self.assert_equal(personalReversed, "~", "substitute back of home variable does not work")
        self.assert_equal(homeReversed, "~", "substitute back of home variable does not work")

        # case insensitive:
        afterHome = os.path.join(homeVariable, 'folder', 'file.txt')
        afterHome = afterHome.lower()
        afterHomeReversed = utilsqh.substituteEnvVariableAtStart(afterHome)
        expected = r"~\folder\file.txt"
        self.assert_equal(expected, afterHomeReversed, "substitute back Home variable fails")

        # unknown filename should return same result:
        unknown = r"X:\abc\def.txt"
        unknownReversed = utilsqh.substituteEnvVariableAtStart(unknown)
        self.assert_equal(unknown, unknownReversed, "unknown should reverse the same")

        # try most of CSIDL variables:
        for c in ('APPDATA', 'RECENT', 'SENDTO', 'STARTUP', 'HISTORY', 'FONTS',
                  'COMMON_APPDATA', 'COMMON_STARTUP', 'COOKIES', 'FAVORITES',
                  'TEMPLATES', 'NETHOOD', 'PRINTHOOD', 'INTERNET_CACHE', 'DESKTOP'):
            envVariable = utilsqh.getExtendedEnv(c)
            envVariableReversed = utilsqh.substituteEnvVariableAtStart(envVariable)
            reversedExpected = "%" + c + "%"
            self.assert_equal(envVariableReversed, reversedExpected,  
                              "getting and reversing env variable |%s| should produce equal results, with percent signs"% c)
            
        # try to get all environment vars, that result in a folder:
        D = utilsqh.getAllFolderEnvironmentVariables()
        # to see them::::
##        print D
        self.assert_('APPDATA' in D, "getAllFolderEnvironmentVariables, APPDATA should (at least) be in")
        
    def tttest_get_newest_file(self):
        """check file dates, returns first with largest mod date
        """
        # first 3 identical, noot is different
        aap = os.path.join(baseFolder, 'aap.txt')
        aap2 = os.path.join(baseFolder, 'aap2.txt')
        aap3 = os.path.join(baseFolder, 'aap3.txt')
    
        func = utilsqh.GetNewestFile
        utilsqh.touch(aap2)
        utilsqh.touch(aap)
        files = [aap, aap2]
        self.assert_equal(aap, func(*files), 'GetNewestFile identical date, should be first: %s'% files)

        time.sleep(2)
        utilsqh.touch(aap2)
        
        files = [aap, aap2, aap3]
        self.assert_equal(aap2, func(*files), 'GetNewestFile should be aap2: %s'% files)

        time.sleep(2)
        utilsqh.touch(aap)

        files = [aap, aap2, aap3]
        self.assert_equal(aap, func(*files), 'GetNewestFile should be aap: %s'% files)

        files = [aap]
        self.assert_equal(aap, func(*files), 'GetNewestFile (one file) should be 1: %s'% files)

        files = []
        self.assert_equal(None, func(*files), 'GetNewestFile (no files) should be None: %s'% files)



    def tttest_identical_files(self):
        """test if more files are identical
        """
        # first 3 identical, noot is different
        aap = os.path.join(baseFolder, 'aap.txt')
        aap2 = os.path.join(baseFolder, 'aap2.txt')
        aap3 = os.path.join(baseFolder, 'aap3.txt')
        noot = os.path.join(baseFolder, 'noot.txt')
        func = utilsqh.IsIdenticalFiles
        files = [aap, aap2]
        self.assert_equal(1, func(*files), 'IsIdenticalFiles should be 1: %s'% files)
        
        files = [aap, noot]
        self.assert_equal(0, func(*files), 'IsIdenticalFiles should be 0: %s'% files)

        files = [aap]
        self.assert_equal(1, func(*files), 'IsIdenticalFiles (one file) should be 1: %s'% files)

        files = []
        self.assert_equal(None, func(*files), 'IsIdenticalFiles (no files) should be None: %s'% files)

        files = [aap, aap2, noot]
        self.assert_equal(None, func(*files), 'IsIdenticalFiles (3 files not identical) should be None: %s'% files)
        
        files = [aap, aap2, aap3]
        self.assert_equal(1, func(*files), 'IsIdenticalFiles (3 files identical) should be 1: %s'% files)

    def test_peekahead(self):
        """test the peekable object
        """
        for inputList in [
            [1,2,3],
                
            ['aa', 'bb'],
            
            ['\u00C4rgument', 'BBnormaal']
            ]:
        
            print 'test peekable for %s'% inputList
            it = utilsqh.peekable(inputList)
            expected = inputList
            result = list(it)
        self.assert_equal(expected, result, 'iterator does not give expected result\nexpected: %s\nresult:   %s\n----'%
                          (expected, result))
        it = utilsqh.peekable(inputList)
        nextItem = it.next()
        print 'nextItem: %s'% nextItem

    def test_readAnythingNotepad(self):
        """test files with encodings
        in latin-1, PU1 and PU2 characters give trouble, test with vervelendequotes.txt
        """
        # formaten met kladblok, notepad:
        files = ['vervelendequotescp1252.txt',  
                 'vervelendequotesutf-8.txt', 'echtenotepadtest.txt']      # two files with notepad saved.
                                                    # zg unicode varianten willen niet.
                                                    # eerste save, zonder speciale tekens, ANSI, maar gevonden als utf-8.
                                                    # bij speciale tekens wordt cp1252 gevonden
        expText = u"""test
-\u2018Onderbuikgevoel\u2019: 
 Er gaat ergens een zacht belletje af..."""
        inputEncoding = ['cp1252','utf-8','cp1252']
        
        for filename, expEncoding in zip(files, inputEncoding):
            inputfile = baseFolder/filename
            gotEnc, gotBom, gotText = utilsqh.readAnything(inputfile)
            self.assert_equal(expEncoding, gotEnc, 'encoding does not match expected: %s\nexpected: %s\ngot: %s'%
                              (filename, expEncoding, gotEnc))
            self.assert_equal(expText, gotText, 'text should be equal, file: %s\nexpected: %s\ngot: %s'%
                              (filename, expText, gotText))

#     def test_readAnythingWord(self):
#         """test files with encodings
#         in latin-1, PU1 and PU2 characters give trouble, test with vervelendequotes.txt
#         """
#         # formaten met word:
#         files = ['testmetwordcp1252.txt',  
#                  'testmetwordutf-8.txt']      # two files with notepad saved.
#                                                     # zg unicode varianten willen niet.
#         expText = u"""test
# -\u2018Onderbuikgevoel\u2019: 
#  Er gaat ergens een zacht belletje af..."""
#         inputEncoding = ['cp1252','utf-8']
#         
#         for filename, expEncoding in zip(files, inputEncoding):
#             inputfile = baseFolder/filename
#             gotEnc, gotText = utilsqh.readAnything(inputfile)
#             self.assert_equal(expEncoding, gotEnc, 'encoding does not match expected: %s\nexpected: %s\ngot: %s'%
#                               (filename, expEncoding, gotEnc))
#             self.assert_equal(expText, gotText, 'text should be equal, file: %s\nexpected: %s\ngot: %s'%
#                               (filename, expText, gotText))
# 

    def test_readAnythingWin32pad(self):
        """test files with encodings, win32pad.
        in latin-1, PU1 and PU2 characters give trouble, test with vervelendequotes.txt
        """
        # formaten met kladblok, notepad:
        files = ['winpadtest.txt']
              ###   'winpadtestunicode.txt']      # two files with win32pad saved
        expText = u"""test
-\u2018Onderbuikgevoel\u2019: 
 Er gaat ergens een zacht belletje af..."""
        inputEncoding = ['cp1252'] ###, 'ISO-8852-2'] krijg de zg unicode saves niet aan de praat.
        
        for filename, expEncoding in zip(files, inputEncoding):
            inputfile = baseFolder/filename
            gotEnc, gotBom, gotText = utilsqh.readAnything(inputfile)
            self.assert_equal(expEncoding, gotEnc, 'encoding does not match expected: %s\nexpected: %s\ngot: %s'%
                              (filename, expEncoding, gotEnc))
            self.assert_equal(expText, gotText, 'text should be equal, file: %s\nexpected: %s\ngot: %s'%
                              (filename, expText, gotText))

        
        
if __name__ == "__main__":
    print 'starting utilsqhtest'
    reload(utilsqh)
    unittest.main()
