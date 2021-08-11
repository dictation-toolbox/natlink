#
# testConfigureFunctions
#   This module tests a lot of the configure things, but
#   regrettably not all.
#
#  (C) Copyright Quintijn Hoogenboom, 2008-2009
#
#pylint:disable=C0114, C0116 W0107, R0201, R0915, R0914
#----------------------------------------------------------------------------
import os
import unittest
import shutil
from pathlib import Path
import win32api
# import win32con

import natlinkcore
from natlinkcore.ConfigureNatlink import natlinkconfigfunctions
# from natlinkcore import natlinkstatus
from natlinkcore.natlinkstatus import isValidPath ## used a lot in the test procedures!
from natlinkcore import natlinkcorefunctions
from natlinkcore.natlinkcorefunctions import InifileSection

##Accessories = 'Accessories'
## for Dutch windows system:
Accessories = 'Bureau-accessoires'

defaultFilename = "natlinkstatustest.ini"
defaultSection = 'usersettingstest'
# status = natlinkstatus.NatlinkStatus()

class NatlinkstatusTestInifileSection(InifileSection):
    """subclass with fixed filename and section"""
    
    def __init__(self):
        """get the default inifile
        
        in the .natlink directory...
        """
        natlink_ini_path=Path(natlinkcore.getNatlinkUserDirectory())
        if not natlink_ini_path.is_dir():
            raise OSError(f"Natlink folder  {natlink_ini_path} missing.")
        
        filename = 'natlinkstatus.ini'
        filepath = str(natlink_ini_path/filename)
        
        section = "usersettingstest"
        filepath = "natlinkstatustest.ini"
        InifileSection.__init__(self, section=section, filepath=filepath)

    def clear(self):
        for key in self:
            self.delete(key)

class TestError(Exception):
    "TestError"

class TestConfigureFunctions(unittest.TestCase):
    """test INI file functions from win32api

    and other functions used in the core of natlink
    the inifile settings (which go normally to natlinkstatus.ini) now go to
    natlinkstatustest.ini, in this directory.

    first: the WriteProfileVal functions, for getting and setting and deleting
           inifile  values, so the config functions.

    second: testing the natlinkcorefunctions:
            getExtendedEnv etc.
            also test isValidPath of paths which can be "extended" with ~ or %..%

    third: test the settings/clearings of the testinisection section of Software/Natlink
           the tests are all going through the CLI (command line interface) functions,
           like cli = CLI()
           and then cli.do_u(path/to/userdirectory) or cli.do_U("dummy") (to clear path) etc.

            these tests are near the bottom of this module. No effect on natlink is tested, only the
            correct working on the registry...
    (at each test the registry settings are recorded, and afterwards put back again)

    Note enableNatlink is NOT tested here, as it does a register of a pyd (=dll) (which maybe should
    not be done too often) and works through INI files anyway, not through the registry.

    """
    def setUp(self):
        """define self.tmpTest (in TMP)
            and vocolausertest and unimacrousertest in HOME directory
            raise TestError if HOME is not existent, or one of these directories already exist
        """
        ## testfolder:
        tmp = natlinkcorefunctions.getExtendedEnv("TMP")
        tmpTest = os.path.join(tmp, 'testconfig')
        if not os.path.isdir(tmp):
            raise TestError('test error, not a valid tmp folderpath: %s'% tmp)
        if os.path.exists(tmpTest):
            shutil.rmtree(tmpTest)
        if os.path.exists(tmpTest):
            raise TestError('test error, test path should not be there: %s'% tmpTest)
        
        
        os.mkdir(tmpTest)
        homeDir = isValidPath("~")
        if homeDir:
            vocolausertest = os.path.join(homeDir, "vocolausertest")
            if not isValidPath(vocolausertest):
                os.mkdir(vocolausertest)
            self.vocolausertest = vocolausertest
            unimacrousertest = os.path.join(homeDir, "unimacrousertest")
            if not isValidPath(unimacrousertest):
                os.mkdir(unimacrousertest)
            self.unimacrousertest = unimacrousertest
        else:
            raise TestError("home directory not defined: %s")
                
            
        self.assertTrue(os.path.isdir(tmpTest), "Could not make test folder: %s"% tmpTest)
        # self.tmpTest to test directory things safely:
        self.tmpTest = tmpTest
        self.cli = natlinkconfigfunctions.CLI()
        config = self.cli.config
        config.userinisection = NatlinkstatusTestInifileSection()
        config.userinisection.clear()
        self.testinisection = config.userinisection


    def tearDown(self):

        #  for setting getting values test:        
        # self.restoreRegistrySettings(self.backuptestinisection,
        # leave tmpTest en natlinkstatustest.ini (in this directory) for inspection, is refreshed at each setUp
        if os.path.isdir(self.vocolausertest):
            shutil.rmtree(self.vocolausertest)
        if os.path.isdir(self.unimacrousertest):
            shutil.rmtree(self.unimacrousertest)
        pass
    
    

    def restoreRegistrySettings(self, backup, actual):
        for key in actual:
            if key not in backup:
                del actual[key]
        actual.update(backup)
        pass      

    def checkusertestinifile(self, key, value, mess=""):
        if value and value != "0":
            if key in self.testinisection:
                actual = self.testinisection[key]
                self.assertTrue(value == actual, "testinisection has not expected result for key: %s, expected: %s, got %s\n%s"%
                             (key, value, actual, mess))
            else:
                self.fail("testinisection does not have expected key: %s\n%s"% (key, mess))
        else:
            if key in self.testinisection:
                self.fail("testinisection shoujald not have this key: %s\n%s"% (key, mess))
            
    def doTestOnOffOption(self, key, valueOn, valueOff, functionNameGet=None):
        """sets on and off the required option and checks if the config (natlinkstatus) reacts correct
        """
        cli = self.cli
        config = cli.config
        expectedOn = 1
        expectedOff = ''
        if not functionNameGet:
            functionNameGet = 'get' + key
        functionNameSetOn = 'do_' + valueOn
        functionNameSetOff = 'do_' + valueOff
        functionOn = getattr(cli, functionNameSetOn)
        functionOff = getattr(cli, functionNameSetOff)
        functionGet = getattr(config, functionNameGet)
        self.assertTrue(functionGet, "should be a function: %s"% functionNameGet)
        self.assertTrue(functionOn, "should be a function: %s"%functionNameSetOn)
        self.assertTrue(functionOff, "should be a function: %s"%functionNameSetOff)
        functionOn('dummy')        
        self.checkusertestinifile(key, 1, "setting option in inifile: %s"% key)
        shouldBeOn = functionGet()
        self.assertTrue(expectedOn == shouldBeOn, "should be on: getting option from config instance, method: %s (%s)"% (functionNameGet, key))
        functionOff('dummy')        
        self.checkusertestinifile(key, None, "clearing option in inifile: %s"% key)
        shouldBeOff = functionGet()
        self.assertTrue(expectedOff == shouldBeOff, "should be off, getting option from config instance, method: %s (%s)"% (functionNameGet, key))
        pass



    def testIsValidPath(self):
        """this tests the isValidPath function of natlinkstatus.py
        
        this function returns the (normalised) path if it exists, None if the input is invalid.
        
        """
        testinifile = os.path.join(self.tmpTest, 'inifiletest.ini')
        func = isValidPath
        
        result = func(self.tmpTest)
        self.assertTrue( result == self.tmpTest, "should exist")
        result = func(self.tmpTest, wantDirectory=1)
        self.assertTrue( result == self.tmpTest, "should exist")
        result = func(self.tmpTest, wantFile=1)
        self.assertTrue( result is None, "should fail, exists but is not a file")
        
        result = func("notValid")
        self.assertTrue( result is None, "should fail all the time")
        
        testinifile = os.path.join(self.tmpTest, 'nsapps.ini')
        f1 = open(testinifile, 'w')
        f1.close()
    
        result = func(testinifile)
        self.assertTrue( result == testinifile, "should exist")
        result = func(testinifile, wantDirectory=1)
        self.assertTrue( result is None, "should fail, is not a directory")
        result = func(testinifile, wantFile=1)
        self.assertTrue( result == testinifile,  "should exist and should be a file")
    
        # now ~ (HOME)
        homedirectory = "~"
        result = func(homedirectory)
        self.assertTrue( result is not None, "should hold some value")
        result = func(homedirectory, wantDirectory=1)
        self.assertTrue( result is not None,  "should hold some value")
        
        pass



    def test_setting_values(self):
        
        """this test is needed, because deleting a key from inifile is not trivial.

        See below, deleting a section I couldn't get to work
        """
        testinifile = os.path.join(self.tmpTest, 'inifiletest.ini')
        f1 = open(testinifile, 'w')
        f1.close()
        win32api.WriteProfileVal('s1', 'k1','v1', testinifile)
        win32api.WriteProfileVal('s1', 'k2','v2', testinifile)
        win32api.WriteProfileVal('s2', 'kk1','vv1', testinifile)
        section = win32api.GetProfileSection('s1', testinifile)
        expected = ['k1=v1', 'k2=v2']
        self.assertTrue(expected == section, "section |%s| not as expected: |%s|"% (section, expected))

        # this call deletes a key:::::    
        win32api.WriteProfileVal('s1', 'k2',None, testinifile)
        section = win32api.GetProfileSection('s1', testinifile)
        expected = ['k1=v1']
        self.assertTrue(expected == section, "section |%s| after deleted keys is not as expected: |%s|"% (section, expected))
        
    def test_getExtendedEnv(self):
        """Test the different functions in natlinkcorefunctions that do environment variables

        Assume if HOME is set in os.environ (system environment variables), it is identical to PERSONAL.

        This is quite complicated        

        """
        # get HOME from os.environ, or CSLID: PERSONAL, ~ taken as HOME...
        home = natlinkcorefunctions.getExtendedEnv("HOME")
        self.assertTrue(os.path.isdir(home), "home should be a folder, not: |%s|"% home)
        home2 = natlinkcorefunctions.getExtendedEnv("~")
        self.assertTrue(home == home2, "home2 (~) should be same as HOME (%s), not: |%s|"%
                     (home,home2))

        # check spaces and erroneous spaces around such a variable:        
        personal = natlinkcorefunctions.getExtendedEnv("PERSONAL")
        personal2 = natlinkcorefunctions.getExtendedEnv("%PERSONAL%")  # erroneous call, but allowed
        personal3 = natlinkcorefunctions.getExtendedEnv("  PERSONAL     ")  # erroneous call, but allowed
        personal4 = natlinkcorefunctions.getExtendedEnv(" % PERSONAL %    ")  # erroneous call, but allowed
        self.assertTrue(personal == home, "PERSONAL should be same as HOME (%s), not: |%s|"%
                     (home,personal))
        self.assertTrue(personal2 == personal, "PERSONAL should allow %% signs in it")
        self.assertTrue(personal3 == personal, "PERSONAL should allow spaces signs around it")
        self.assertTrue(personal4 == personal, "PERSONAL should allow spaces and %% signs around it")

        # unknown CSIDL_ variable should give ValueError:
        self.assertRaises(ValueError, natlinkcorefunctions.getExtendedEnv, 'ABACADABRA')

    def test_expandAndSubstituteEnv(self):
        """Test expanding and substituting back env variables

        This is done in different combinations, with private envDict AND using the global recentEnv

        Sometimes you should call getAllFolderEnvironmentVariables,

        As you see the different combinations are quite tricky, but they seem to work.

        """
        #pylint:disable=W0107        
        # try expanding paths and putting back, using global recentEnv
        filename = '~/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded)
        self.assertTrue(expanded != filename, "expandEnvVariableAtStart did not work on: %s"% filename)
        self.assertTrue(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))
        # %HOME% should be brought back to ~:
        filename2 = '%HOME%/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename2)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded)
        self.assertTrue(expanded != filename2, "expandEnvVariableAtStart did not work on: %s"% filename2)
        self.assertTrue(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))

        # try expanding paths and putting back, using a local envDict:
        filename = '~/speech/index.html'
        envDict = {}
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename, envDict)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded, envDict)
        self.assertTrue(expanded != filename, "expandEnvVariableAtStart did not work on: %s"% filename)
        self.assertTrue(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))
        # %HOME% should be brought back to ~:
        filename2 = '%HOME%/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename2, envDict)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded, envDict)
        self.assertTrue(expanded != filename2, "expandEnvVariableAtStart did not work on: %s"% filename2)
        self.assertTrue(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))

        # try with COMMON_PROGRAMS, which is a subdirectory of COMMON_STARTMENU
        # with substitute back, the longest pattern (COMMON_PROGRAMS) should prevail over the shorter one
        #
        filenamePrograms = '%COMMON_PROGRAMS%/speech/example.exe'
        filenameStartmenu = '%COMMON_STARTMENU%/inside_startmenu.exe'
        expandedPrograms = natlinkcorefunctions.expandEnvVariableAtStart(filenamePrograms)
        expandedStartmenu = natlinkcorefunctions.expandEnvVariableAtStart(filenameStartmenu)
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu)
        self.assertTrue(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assertTrue(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assertTrue(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assertTrue(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))

        # try above with private envDict:
        filenamePrograms = '%COMMON_PROGRAMS%/speech/example.exe'
        filenameStartmenu = '%COMMON_STARTMENU%/inside_startmenu.exe'
        envDict = {}
        expandedPrograms = natlinkcorefunctions.expandEnvVariableAtStart(filenamePrograms, envDict)
        expandedStartmenu = natlinkcorefunctions.expandEnvVariableAtStart(filenameStartmenu, envDict)
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assertTrue(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assertTrue(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assertTrue(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assertTrue(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))
        
        # substituting back should fail when  private envDict is cleared halfway!
        filenamePrograms = '%COMMON_PROGRAMS%/speech/example.exe'
        filenameStartmenu = '%COMMON_STARTMENU%/inside_startmenu.exe'
        envDict = {}
        expandedPrograms = natlinkcorefunctions.expandEnvVariableAtStart(filenamePrograms, envDict)
        expandedStartmenu = natlinkcorefunctions.expandEnvVariableAtStart(filenameStartmenu, envDict)
        # clear:    
        envDict = {}
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        # squeeze did not succed
        self.assertTrue(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assertTrue(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assertTrue(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assertTrue(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))
        
        # clear recentEnv, no result:
        natlinkcorefunctions.clearRecentEnv()
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu)
        self.assertTrue(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assertTrue(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))

        # fill recentEnv again, all is well again:
        natlinkcorefunctions.getAllFolderEnvironmentVariables(fillRecentEnv=1)
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu)
        self.assertTrue(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assertTrue(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))


        # again with private envDict, should NOT produce result:        
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assertTrue(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assertTrue(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))


        # now update envDict and try again, now it works:
        envDict = natlinkcorefunctions.getAllFolderEnvironmentVariables()
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assertTrue(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assertTrue(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))

    # now for the real work, the install functions:
    def test_enableDisableNatlinkDebugOutput(self):
        """This option should set DebugOutput in the registry to 0 or 1
        
        obsolete, NatlinkDebug is disabled (2015, even earlier, by Rudiger)
        """
        key = "NatlinkDebug"
        cli = natlinkconfigfunctions.CLI()
        cli.do_g("dummy")
        self.checkusertestinifile(key, 0, "key %s not set, obsolete option"% key)
        cli.do_G("dummy")
        self.checkusertestinifile(key, 0, "key %s not set, obsolete option"% key)
        cli.do_g("dummy")
        self.checkusertestinifile(key, 0, "key %s not set, obsolete option"% key)
        
        
    def test_setClearDNSInstallDir(self):
        """This option should set or clear the natspeak install directory
        """
        key = "DNSInstallDir"
        cli = natlinkconfigfunctions.CLI()
        old = self.testinisection.get(key, None)
        # not a valid folder:
        cli.do_d("notAValidFolder")
        self.checkusertestinifile(key, old, "DNSInstallDir, nothing should be changed yet")

        # folder does not have Programs:
        cli.do_d(self.tmpTest)
        self.checkusertestinifile(key, old, "DNSInstallDir, empty directory should not change DNSInstallDir")

        # now change:
        programDir = os.path.join(self.tmpTest, 'Program')
        os.mkdir(programDir)
        cli.do_d(self.tmpTest)
        self.checkusertestinifile(key, self.tmpTest, "DNSInstallDir should be changed now")

        # now clear:
        cli.do_D("dummy")
        self.checkusertestinifile(key, None, "DNSInstallDir should be cleared now")
        
    def test_setClearUnimacroIniFilesEditor(self):
        """This option should set or clear the editor program for Unimacro ini files
        
        default is Notepad. set to wordpad for test, which is in the "old" Program files directory.
        
        """
        key = "UnimacroIniFilesEditor"
        oldKey = "Old" + key
        cli = self.cli
        old = self.testinisection.get(key, None)
        # not a valid folder:
        cli.do_p("notAValidFolder")
        self.checkusertestinifile(key, old, "UnimacroIniFilesEditor, nothing should be changed yet")
        self.checkusertestinifile(oldKey, "", "OldUnimacroIniFilesEditor, should not be there yet")

        wordpadExe = r"C:\Program files\Windows NT\Accessories\wordpad.exe"
        if not os.path.isfile(wordpadExe):
            raise TestError("wordpadExe should be a valid file, not: %s"% wordpadExe)
        # setting the variable:
        cli.do_p(wordpadExe)
        self.checkusertestinifile(key, wordpadExe, "UnimacroIniFilesEditor, should be set now to: %s"% wordpadExe)
        self.checkusertestinifile(oldKey, "", "OldUnimacroIniFilesEditor, should not be there yet")

        # repeated has no effect:
        cli.do_p(wordpadExe)
        self.checkusertestinifile(key, wordpadExe, "UnimacroIniFilesEditor, should be set now to: %s"% wordpadExe)
        self.checkusertestinifile(oldKey, "", "OldUnimacroIniFilesEditor, should not be there yet")


        # now remove again:
        cli.do_P("dummy")
        self.checkusertestinifile(key, "", "UnimacroIniFilesEditor, should be clear now")
        self.checkusertestinifile(oldKey, wordpadExe, "OldUnimacroIniFilesEditor, should be set now to: %s"% wordpadExe)

        # repeat has no effect:
        cli.do_P("dummy")
        self.checkusertestinifile(key, "", "UnimacroIniFilesEditor, should be still clear")
        self.checkusertestinifile(oldKey, wordpadExe, "OldUnimacroIniFilesEditor, should still be set now to: %s"% wordpadExe)
        
        # setting again:
        cli.do_p(wordpadExe)
        self.checkusertestinifile(key, wordpadExe, "UnimacroIniFilesEditor, should again be set now to: %s"% wordpadExe)
        self.checkusertestinifile(oldKey, "", "OldUnimacroIniFilesEditor, should be cleared again")
    
    def test_setClearDirectoryOptions(self):
        r"""This option tests the different directory functions of natlinkconfigfunctions
        
        UserDirectory is NOT Unimacro any more.
        
        assume %HOME% and "~" point to C:\Documenten.
        assume testing with Dragon15 on a 64 bits machine
        
        
        """
        progFiles = Path(os.getenv("PROGRAMFILES"))
        if not progFiles.is_dir():
            raise OSError("program files directory not where expected")
        dnsinstalldir = progFiles/"Nuance/NaturallySpeaking15"
        if not dnsinstalldir.is_dir():
            raise OSError(f'dnsinstalldir not where expected: "{dnsinstalldir}"')

        wordpadexe = r"C:\Program Files\Windows NT\Accessories\wordpad.exe"
        if not os.path.isfile(wordpadexe):
            raise TestError("should have a path to wordpad.exe, %s does not exist"% wordpadexe)
        dummyfile = os.path.join(self.tmpTest, 'exists.txt')
        f = open(dummyfile, 'w')
        f.close()
        dummyexefile = os.path.join(self.tmpTest, 'autohotkey.exe')
        f = open(dummyexefile, 'w')
        f.close()
        
        for (key, functionLetter, testFolder) in [
            ("DNSIniDir", 'c', self.tmpTest),
            ("DNSInstallDir", 'd', dnsinstalldir),
            ("UserDirectory", 'n', self.tmpTest),
            ("UnimacroUserDirectory", 'o', self.unimacrousertest),
            ("VocolaUserDirectory", 'v', self.vocolausertest),
            ("UnimacroIniFilesEditor", "p", wordpadexe), 
            ("AhkExeDir", "h", self.tmpTest),
            ("AhkUserDir", "k", self.tmpTest)]:
            print('---- start testing "%s", letter: "%s"'% (key, functionLetter))

            oldKey = "Old" + key
            cli = self.cli
            # make clean section:
            self.testinisection.clear()
            funcSetName = 'do_'+functionLetter
            funcClearName = 'do_'+functionLetter.upper()
            funcSet = getattr(cli, funcSetName)
            funcClear = getattr(cli, funcClearName)
            # not a valid folder:
            funcSet("notAValidFolder")
            self.checkusertestinifile(key, "", "%s, should be there yet"% key)
            self.checkusertestinifile(oldKey, "", "Old%s, should not be there yet")
    
            checkTestFolder = isValidPath(testFolder)
            if not checkTestFolder:
                raise TestError("testFolder  should be a valid directory, not: %s"% testFolder)
            # setting the variable:
            funcSet(testFolder)
            if functionLetter == 'c':
                self.checkusertestinifile(key,"", "%s, nothing should be changed yet (Inifiles do not exist)"% key)
        
                #existence of these two files is checked:
                testinifile = os.path.join(self.tmpTest, 'nsapps.ini')
                f1 = open(testinifile, 'w')
                f1.close()
        
                testinifile = os.path.join(self.tmpTest, 'nssystem.ini')
                f1 = open(testinifile, 'w')
                f1.close()
        
                funcSet(testFolder)
        
            self.checkusertestinifile(key, testFolder, "%s, should be set now to: %s"% (key, testFolder))
            self.checkusertestinifile(oldKey, "", "Old%s, should not be there yet"% key)
    
            # repeated has no effect:
            funcSet(testFolder)
            self.checkusertestinifile(key, testFolder, "%s, should be set now to: %s"% (key, testFolder))
            self.checkusertestinifile(oldKey, "", "Old%s, should not be there yet"% key)
    
    
            # now remove again:
            funcClear("dummy")
            self.checkusertestinifile(key, "", "%s, should be clear now")
            self.checkusertestinifile(oldKey, testFolder, "Old%s, should be set now to: %s"% (key, testFolder))
    
            # repeat has no effect:
            funcClear("dummy")
            self.checkusertestinifile(key, "", "%s, should be still clear")
            self.checkusertestinifile(oldKey, testFolder, "Old%s, should still be set now to: %s"%  (key, testFolder))
            
            # setting again:
            funcSet(testFolder)
            self.checkusertestinifile(key, testFolder, "%s, should again be set now to: %s"% (key,  testFolder))
            self.checkusertestinifile(oldKey, "", "Old%s, should be cleared again"% key)
            print('==== end of testing "%s", letter: "%s"'% (key, functionLetter))


        

    def test_setClearVocolaUserDirectory(self):
        """This option should set or clear the vocola user directory
        """
        testName = 'test_setClearVocolaUserDirectory'
        key = "VocolaUserDirectory"
        cli = natlinkconfigfunctions.CLI()
        old = self.testinisection.get(key, None)
        # not a valid folder:
        cli.do_v("notAValidFolder")
        self.checkusertestinifile(key, old, "%s, nothing should be changed yet"% testName)

        # change userdirectory
        cli.do_v(self.tmpTest)
        self.checkusertestinifile(key, self.tmpTest, "%s, VocolaUserDirectory should be changed now"% testName)

        # now clear:
        cli.do_V("dummy")
        self.checkusertestinifile(key, None, "%s VocolaUserDirectory should be cleared now"% testName)
        
    # def test_setClearVocolaCommandFilesEditor(self):
    #     """This option should set or clear the vocola command files editor
    #     """
    #     ## not a function of config program any more, I think (QH, 2021)
    #     testName = 'test_setClearVocolaCommandFilesEditor'
    #     key = "VocolaCommandFilesEditor"
    #     cli = natlinkconfigfunctions.CLI()
    #     old = self.testinisection.get(key, None)
    # 
    #     # not a valid folder:
    #     cli.do_w("not a valid file")
    #     self.checkusertestinifile(key, old, "%s, nothing should be changed yet"% testName)
    # 
    #     # change to notepad:
    #     wordpad = os.path.join(natlinkcorefunctions.getExtendedEnv("PROGRAMFILES"), 'Windows NT',
    #                            Accessories, "wordpad.exe")
    #     if not os.path.isfile(wordpad):
    #         raise OSError("Test error, cannot find wordpad on: %s"% wordpad)
    #     
    #     cli.do_w(wordpad)
    #     self.checkusertestinifile(key, wordpad, "%s, VocolaCommandFilesEditor should be changed now"% testName)
    # 
    #     # now clear:
    #     cli.do_W("dummy")
    #     self.checkusertestinifile(key, None, "%s VocolaUserDirectory should be cleared now"% testName)
    # 
                
    def test_setClearUnimacroUserDirectory(self):
        """This option should set or clear the unimacro (ini files) user directory
        """
        testName = 'test_setClearUnimacroUserDirectory'
        key = "UnimacroUserDirectory"
        keyOld = "OldUnimacroUserDirectory"
        cli = self.cli
        old = cli.config.userinisection[key]
        self.assertTrue(old == "", "key %s should not be set at start of test: %s"% (key, testName))
        old = cli.config.userinisection[keyOld]
        self.assertTrue(old == "", "key %s should not be set at start of test: %s"% (keyOld, testName))

        # not a valid folder:
        cli.do_o("notAValidFolder")
        self.checkusertestinifile(key, old, "%s, nothing should be changed yet"% testName)
        self.checkusertestinifile(keyOld, old, "%s, nothing should be changed yet"% testName)
        
        # change userdirectory
        cli.do_o(self.tmpTest)
        self.checkusertestinifile(key, self.tmpTest, "%s, UnimacroUserDirectory should be changed now"% testName)
        self.checkusertestinifile(keyOld, old, "%s, nothing should be changed yet"% testName)

        # now clear:
        cli.do_O("dummy")
        self.checkusertestinifile(key, "", "%s UnimacroUserDirectory should be cleared now"% testName)
        self.checkusertestinifile(keyOld, self.tmpTest, "%s, Old key should be set now"% testName)

    


    # Testing addition vocola options
    def test_enableDisableOnOffOptions(self):
        """This option should set and clear the different options
        """
        key = "VocolaTakesLanguages"
        self.doTestOnOffOption(key, 'b', 'B')

        key = "IncludeUnimacroInPythonPath"
        self.doTestOnOffOption(key, 'f', 'F')
        
        key = "NatlinkmainDebugLoad"
        self.doTestOnOffOption(key, 'x', 'X', functionNameGet="getDebugLoad")
        
        key = "NatlinkmainDebugCallback"
        self.doTestOnOffOption(key, 'y', 'Y', functionNameGet="getDebugCallback")
        
        key = "VocolaTakesUnimacroActions"
        self.doTestOnOffOption(key, 'a', 'A')
        
        
##    def test_RegistrySettings(self):
##        """test if registry settings are saved and restored correctly
##
##        make a backup in setup, and restore in teardown, see example with testinisection.
##
##        If you doubt about the working, step through this test function and see what happens
##        
##        """
##        
##        self.testinisection['testtt'] = 'hello new test'
##        for key in self.testinisection:
##            del self.testinisection[key]
##            break
##        print 'things should be the same, test by hand'
##                
##

def _run():
    unittest.main()
    

if __name__ == "__main__":
    _run()
