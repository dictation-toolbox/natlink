#
# testConfigureFunctions
#   This module tests a lot of the configure things, but
#   regrettably not all.
#
#  (C) Copyright Quintijn Hoogenboom, 2008-2009
#
#----------------------------------------------------------------------------


import sys, unittest, win32api, os, win32con, copy, shutil
import natlinkconfigfunctions, natlinkstatus
reload(natlinkconfigfunctions)

testinifile1 = os.path.join("C:\\", "testinifile.ini")

Accessories = 'Accessories'
## for Dutch windows system:
##Accessories = 'Bureau-accessoires'

# need this bunch to get connection with the core folder...
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
##        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
##        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder:
        baseFolder = os.getcwd()
##        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

def getCoreDir(thisDir):
    """get the natlink core folder, relative from the current folder

    This folder should be relative to this with ../macrosystem/core and should contain
    natlinkmain.py and natlink.dll and natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'macrosystem', 'core') )
    if not os.path.isdir(coreFolder):
        print 'not a directory: %s'% coreFolder
        return thisDir
    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
    if not os.path.isfile(dllPath):
        print 'natlink.dll not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
#-----------------------------------------------------

thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'appending %s to pythonpath...'% coreDir
    sys.path.append(coreDir)
# now we can import:::
import natlinkcorefunctions, RegistryDict
reload(natlinkcorefunctions)

class TestError(Exception):
    pass

class TestConfigureFunctions(unittest.TestCase):
    """test INI file functions from win32api

    and other functions used in the core of natlink


    first: the WriteProfileVal functions, for getting and setting and deleting
           inifile  values

    second: testing the natlinkcorefunctions:
            getExtendedEnv etc.

    third: test the settings/clearings of the userregnl section of Software/Natlink
           the tests are all going through the CLI (command line interface) functions,
           like cli = CLI()
           and then cli.do_u(path/to/userdirectory) or cli.do_U("dummy") (to clear path) etc.

            these tests are near the bottom of this module. No effect on natlink is tested, only the
            correct working on the registry...
    (at each test the registry settings are recorded, and afterwards put back again)

    Note enableNatlink is NOT tested here, as it does a register of a dll (which maybe should
    not be done too often) and works through INI files anyway, not through the registry.

    """
    def setUp(self):
        # for setting getting values test:
        f1 = open(testinifile1, 'w')
        f1.close()
        self.usergroup = "SOFTWARE\Natlink"
##    lmgroup = "SOFTWARE\Natlink"
        self.Userregnl = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, self.usergroup)
        self.backupUserregnl = dict(self.Userregnl)

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
        self.assert_(os.path.isdir(tmpTest), "Could not make test folder: %s"% tmpTest)
        self.tmpTest = tmpTest



    def tearDown(self):

        #  for setting getting values test:        
        if os.path.isfile(testinifile1):
            os.remove(testinifile1)
        self.restoreRegistrySettings(self.backupUserregnl,
                RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, self.usergroup))
        shutil.rmtree(self.tmpTest)
        pass

    def restoreRegistrySettings(self, backup, actual):
        for key in actual:
            if key not in backup:
                del actual[key]
        actual.update(backup)
        pass      

    def checkUserregnl(self, key, value, mess=""):
        userregnltest = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, self.usergroup)
        if value != None:
            if key in userregnltest:
                actual = userregnltest[key]
                self.assert_(value == actual, "userregnl has not expected result for key: %s, expected: %s, got %s\n%s"%
                             (key, value, actual, mess))
            else:
                self.fail("userregnl does not have expected key: %s\n%s"% (key, mess))
        else:
            if key in userregnltest:
                self.fail("userregnl should not have this key: %s\n%s"% (key, mess))
            


    def test_setting_values(self):
        """this test is needed, because deleting a key from inifile is not trivial.

        See below, deleting a section I couldn't get to work
        """
        f1 = open(testinifile1, 'w')
        f1.close()
        win32api.WriteProfileVal('s1', 'k1','v1', testinifile1)
        win32api.WriteProfileVal('s1', 'k2','v2', testinifile1)
        win32api.WriteProfileVal('s2', 'kk1','vv1', testinifile1)
        section = win32api.GetProfileSection('s1', testinifile1)
        expected = ['k1=v1', 'k2=v2']
        self.assert_(expected == section, "section |%s| not as expected: |%s|"% (section, expected))

        # this call deletes a key:::::    
        win32api.WriteProfileVal('s1', 'k2',None, testinifile1)
        section = win32api.GetProfileSection('s1', testinifile1)
        expected = ['k1=v1']
        self.assert_(expected == section, "section |%s| after deleted keys is not as expected: |%s|"% (section, expected))
                
        
    def test_getExtendedEnv(self):
        """Test the different functions in natlinkcorefunctions that do environment variables

        Assume if HOME is set in os.environ (system environment variables), it is identical to PERSONAL.

        This is quite complicated        

        """
        # get HOME from os.environ, or CSLID: PERSONAL, ~ taken as HOME...
        home = natlinkcorefunctions.getExtendedEnv("HOME")
        self.assert_(os.path.isdir(home), "home should be a folder, not: |%s|"% home)
        home2 = natlinkcorefunctions.getExtendedEnv("~")
        self.assert_(home == home2, "home2 (~) should be same as HOME (%s), not: |%s|"%
                     (home,home2))

        # check spaces and erroneous spaces around such a variable:        
        personal = natlinkcorefunctions.getExtendedEnv("PERSONAL")
        personal2 = natlinkcorefunctions.getExtendedEnv("%PERSONAL%")  # erroneous call, but allowed
        personal3 = natlinkcorefunctions.getExtendedEnv("  PERSONAL     ")  # erroneous call, but allowed
        personal4 = natlinkcorefunctions.getExtendedEnv(" % PERSONAL %    ")  # erroneous call, but allowed
        self.assert_(personal == home, "PERSONAL should be same as HOME (%s), not: |%s|"%
                     (home,personal))
        self.assert_(personal2 == personal, "PERSONAL should allow %% signs in it")
        self.assert_(personal3 == personal, "PERSONAL should allow spaces signs around it")
        self.assert_(personal4 == personal, "PERSONAL should allow spaces and %% signs around it")

        # unknown CSIDL_ variable should give ValueError:
        self.assertRaises(ValueError, natlinkcorefunctions.getExtendedEnv, 'ABACADABRA')

    def test_expandAndSubstituteEnv(self):
        """Test expanding and substituting back env variables

        This is done in different combinations, with private envDict AND using the global recentEnv

        Sometimes you should call getAllFolderEnvironmentVariables,

        As you see the different combinations are quite tricky, but they seem to work.

        """

        # try expanding paths and putting back, using global recentEnv
        filename = '~/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded)
        self.assert_(expanded != filename, "expandEnvVariableAtStart did not work on: %s"% filename)
        self.assert_(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))
        # %HOME% should be brought back to ~:
        filename2 = '%HOME%/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename2)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded)
        self.assert_(expanded != filename2, "expandEnvVariableAtStart did not work on: %s"% filename2)
        self.assert_(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))

        # try expanding paths and putting back, using a local envDict:
        filename = '~/speech/index.html'
        envDict = {}
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename, envDict)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded, envDict)
        self.assert_(expanded != filename, "expandEnvVariableAtStart did not work on: %s"% filename)
        self.assert_(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
                     (filename, squeezed))
        # %HOME% should be brought back to ~:
        filename2 = '%HOME%/speech/index.html'
        expanded = natlinkcorefunctions.expandEnvVariableAtStart(filename2, envDict)
        squeezed = natlinkcorefunctions.substituteEnvVariableAtStart(expanded, envDict)
        self.assert_(expanded != filename2, "expandEnvVariableAtStart did not work on: %s"% filename2)
        self.assert_(squeezed == os.path.normpath(filename), "substitute back does not produce identical result: %s, %s"%
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
        self.assert_(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assert_(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assert_(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assert_(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))

        # try above with private envDict:
        filenamePrograms = '%COMMON_PROGRAMS%/speech/example.exe'
        filenameStartmenu = '%COMMON_STARTMENU%/inside_startmenu.exe'
        envDict = {}
        expandedPrograms = natlinkcorefunctions.expandEnvVariableAtStart(filenamePrograms, envDict)
        expandedStartmenu = natlinkcorefunctions.expandEnvVariableAtStart(filenameStartmenu, envDict)
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assert_(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assert_(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assert_(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assert_(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
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
        self.assert_(expandedPrograms != filenamePrograms, "expandEnvVariableAtStart did not work on: %s"% filenamePrograms)
        self.assert_(expandedStartmenu != filenameStartmenu, "expandEnvVariableAtStart did not work on: %s"% filenameStartmenu)
        self.assert_(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assert_(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))
        
        # clear recentEnv, no result:
        natlinkcorefunctions.clearRecentEnv()
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu)
        self.assert_(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assert_(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))

        # fill recentEnv again, all is well again:
        natlinkcorefunctions.getAllFolderEnvironmentVariables(fillRecentEnv=1)
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu)
        self.assert_(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assert_(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))


        # again with private envDict, should NOT produce result:        
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assert_(squeezedPrograms == expandedPrograms, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenamePrograms, expandedPrograms))
        self.assert_(squeezedStartmenu == expandedStartmenu, "substitute back did not work, envDict was cleared: %s, %s"%
                     (filenameStartmenu, expandedStartmenu))


        # now update envDict and try again, now it works:
        envDict = natlinkcorefunctions.getAllFolderEnvironmentVariables()
        squeezedPrograms = natlinkcorefunctions.substituteEnvVariableAtStart(expandedPrograms, envDict)
        squeezedStartmenu = natlinkcorefunctions.substituteEnvVariableAtStart(expandedStartmenu, envDict)
        self.assert_(squeezedPrograms == os.path.normpath(filenamePrograms), "substitute back does not produce identical result: %s, %s"%
                     (filenamePrograms, squeezedPrograms))
        self.assert_(squeezedStartmenu == os.path.normpath(filenameStartmenu), "substitute back does not produce identical result: %s, %s"%
                     (filenameStartmenu, squeezedStartmenu))

    # now for the real work, the install functions:
    def test_enableDisableNatlinkDebugOutput(self):
        """This option should set DebugOutput in the registry to 0 or 1
        """
        key = "NatlinkDebug"
        cli = natlinkconfigfunctions.CLI()
        cli.do_g("dummy")
        
        self.checkUserregnl(key, 1, "setting debug output natlink")
        cli.do_G("dummy")
        self.checkUserregnl(key, 0, "clearing debug output natlink")
        cli.do_g("dummy")
        self.checkUserregnl(key, 1, "setting debug output natlink")
        
    # now for the real work, the install functions:
    def test_enableDisableNatlinkmainDebugLoadDebugCallback(self):
        """This option should set DebugLoad and DebugCallback for natlinkmain on and off
        """
        key = "NatlinkmainDebugLoad"
        cli = natlinkconfigfunctions.CLI()
        cli.do_x("dummy")
        
        self.checkUserregnl(key, 1, "setting natlinkmain debug load on")
        cli.do_X("dummy")
        self.checkUserregnl(key, 0, "clearing natlinkmain debug load")

        key = "NatlinkmainDebugCallback"
        cli = natlinkconfigfunctions.CLI()
        cli.do_y("dummy")
        
        self.checkUserregnl(key, 1, "setting natlinkmain debug callback on")
        cli.do_Y("dummy")
        self.checkUserregnl(key, 0, "clearing natlinkmain debug callback")


        
        
    def test_setClearDNSInstallDir(self):
        """This option should set or clear the natspeak install directory
        """
        key = "DNSInstallDir"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)
        # not a valid folder:
        cli.do_d("notAValidFolder")
        self.checkUserregnl(key, old, "DNSInstallDir, nothing should be changed yet")

        # folder does not have Programs:
        cli.do_d(self.tmpTest)
        self.checkUserregnl(key, old, "DNSInstallDir, empty directory should not change DNSInstallDir")

        # now change:
        programDir = os.path.join(self.tmpTest, 'Program')
        os.mkdir(programDir)
        cli.do_d(self.tmpTest)
        self.checkUserregnl(key, self.tmpTest, "DNSInstallDir should be changed now")

        # now clear:
        cli.do_D("dummy")
        self.checkUserregnl(key, None, "DNSInstallDir should be cleared now")
        

        
    def test_setClearDNSIniDir(self):
        """This option should set or clear the natspeak INI files directory
        """
        key = "DNSIniDir"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)
        # not a valid folder:
        cli.do_c("notAValidFolder")
        self.checkUserregnl(key, old, "DNSIniDir, nothing should be changed yet")

        # folder does not have INI files in yet:
        cli.do_c(self.tmpTest)
        self.checkUserregnl(key, old, "DNSIniDir, empty directory should not change DNSIniDir")

        # now change:
        nssystemini = os.path.join(self.tmpTest, 'nssystem.ini')
        win32api.WriteProfileVal("dummy", "dummy", "dummy", nssystemini)
        cli.do_c(self.tmpTest)
        self.checkUserregnl(key, old, "DNSIniDir, should not be changed yet, nsapps still missing")
        nsappsini = os.path.join(self.tmpTest, 'nsapps.ini')
        win32api.WriteProfileVal("dummy", "dummy", "dummy", nsappsini)
        cli.do_c(self.tmpTest)
        self.checkUserregnl(key, self.tmpTest, "DNSIniDir, should be changed now")

        # now clear:
        cli.do_C("dummy")
        self.checkUserregnl(key, None, "DNSInstallDir should be cleared now")
        

        
    def test_setClearUserDirectory(self):
        """This option should set or clear the natlink user directory
        """
        testName = 'test_setClearUserDirectory'
        key = "UserDirectory"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)
        # not a valid folder:
        cli.do_n("notAValidFolder")
        self.checkUserregnl(key, old, "%s, nothing should be changed yet"% testName)

        # change userdirectory
        cli.do_n(self.tmpTest)
        self.checkUserregnl(key, self.tmpTest, "%s, UserDirectory should be changed now"% testName)

        # now clear:
        cli.do_N("dummy")
        self.checkUserregnl(key, None, "%s UserDirectory should be cleared now"% testName)
        

    def test_setClearVocolaUserDirectory(self):
        """This option should set or clear the vocola user directory
        """
        testName = 'test_setClearVocolaUserDirectory'
        key = "VocolaUserDirectory"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)
        # not a valid folder:
        cli.do_v("notAValidFolder")
        self.checkUserregnl(key, old, "%s, nothing should be changed yet"% testName)

        # change userdirectory
        cli.do_v(self.tmpTest)
        self.checkUserregnl(key, self.tmpTest, "%s, VocolaUserDirectory should be changed now"% testName)

        # now clear:
        cli.do_V("dummy")
        self.checkUserregnl(key, None, "%s VocolaUserDirectory should be cleared now"% testName)
        
    def test_setClearVocolaCommandFilesEditorAndUsesSimpscrp(self):
        """This option should set or clear the vocola command files editor
        in combination with VocolaUsesSimpscrp
        """
        testName = 'test_setClearVocolaCommandFilesEditorAndUsesSimpscrp'
        keySimpscrp = "VocolaUsesSimpscrp"
        key = "VocolaCommandFilesEditor"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)

        # use simpscrp:
        cli.do_s("dummy")
        self.checkUserregnl(keySimpscrp, 1, "VocolaUsesSimpscrp should be 1 now %s"% testName)
        cli.do_S("dummy")
        self.checkUserregnl(keySimpscrp, 0, "VocolaUsesSimpscrp should be 0 now %s"% testName)
        
        # switch on and do test of editor:
        cli.do_s("dummy")
        self.checkUserregnl(keySimpscrp, 1, "VocolaUsesSimpscrp should be 1 now %s"% testName)
        
        # not a valid folder:
        cli.do_w("not a valid file")
        self.checkUserregnl(key, old, "%s, nothing should be changed yet"% testName)

        # change to notepad:
        wordpad = os.path.join(natlinkcorefunctions.getExtendedEnv("PROGRAMFILES"), 'Windows NT',
                               Accessories, "wordpad.exe")
        if not os.path.isfile(wordpad):
            raise IOError("Test error, cannot find wordpad on: %s"% wordpad)
        
        cli.do_w(wordpad)
        self.checkUserregnl(key, wordpad, "%s, VocolaCommandFilesEditor should be changed now"% testName)

        # now clear:
        cli.do_W("dummy")
        self.checkUserregnl(key, None, "%s VocolaUserDirectory should be cleared now"% testName)

                
    def test_setClearUnimacroIniFilesEditor(self):
        """This option should set or clear the unimacro INI files editor
        """
        testName = 'test_setClearUnimacroIniFilesEditor'
        key = "UnimacroIniFilesEditor"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)

        
        # not a valid folder:
        cli.do_p("not a valid file")
        self.checkUserregnl(key, old, "%s, nothing should be changed yet"% testName)

        # change to notepad:
        wordpad = os.path.join(natlinkcorefunctions.getExtendedEnv("PROGRAMFILES"), 'Windows NT',
                            Accessories, "wordpad.exe")
        if not os.path.isfile(wordpad):
            raise IOError("Test error, cannot find wordpad on: %s"% wordpad)
        
        cli.do_p(wordpad)
        self.checkUserregnl(key, wordpad, "%s, UnimacroIniFilesEditor should be changed now"% testName)

        # now clear:
        cli.do_P("dummy")
        self.checkUserregnl(key, None, "%s UnimacroIniFilesEditor should be cleared now"% testName)


    def test_setClearUnimacroUserDirectory(self):
        """This option should set or clear the unimacro (ini files) user directory
        """
        testName = 'test_setClearUnimacroUserDirectory'
        key = "UnimacroUserDirectory"
        cli = natlinkconfigfunctions.CLI()
        old = self.Userregnl.get(key, None)
        # not a valid folder:
        cli.do_o("notAValidFolder")
        self.checkUserregnl(key, old, "%s, nothing should be changed yet"% testName)

        # change userdirectory
        cli.do_o(self.tmpTest)
        self.checkUserregnl(key, self.tmpTest, "%s, UnimacroUserDirectory should be changed now"% testName)

        # now clear:
        cli.do_O("dummy")
        self.checkUserregnl(key, None, "%s UnimacroUserDirectory should be cleared now"% testName)
        
                

    # Testing addition vocola options
    def test_enableDisableExtraVocolaOptions(self):
        """This option should set and cleared the settings for additional vocola options
        """
        key = "VocolaTakesLanguages"
        cli = natlinkconfigfunctions.CLI()
        cli.do_b("dummy")
        
        self.checkUserregnl(key, 1, "setting vocola takes languages")
        cli.do_B("dummy")
        self.checkUserregnl(key, 0, "clearing vocola takes languages")


        
        
##    def test_RegistrySettings(self):
##        """test if registry settings are saved and restored correctly
##
##        make a backup in setup, and restore in teardown, see example with Userregnl.
##
##        If you doubt about the working, step through this test function and see what happens
##        
##        """
##        
##        self.Userregnl['testtt'] = 'hello new test'
##        for key in self.Userregnl:
##            del self.Userregnl[key]
##            break
##        print 'things should be the same, test by hand'
##                
##

def _run():
     unittest.main()
    

if __name__ == "__main__":
    _run()
