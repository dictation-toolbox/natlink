#
# natlinkstatus.py
#   This module gives the status of Natlink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008/January 2018
#  Adapted to new directories strategy with python3, and new natlinkmain.py (James Murphy, kb100)
#
#----------------------------------------------------------------------------
# previous version history to be found in git versions up to FinalCommitWithVocola, 21-8-2020
#pylint:disable=C0302 


"""The following functions are provided in this module:
(to be used by either natlinkmain.py or natlinkconfigfunctions.py)

The functions below are put into the class NatlinkStatus.
The natlinkconfigfunctions can subclass this class, and
the configurenatlink.py (GUI) again sub-subclasses this one.

The following  functions manage information that changes at changeCallback time
(when a new user opens)

setUserInfo(args) put username and directory of speech profiles of the last opened user in this class.
getUsername: get active username (only if NatSpeak/Natlink is running)
getDNSuserDirectory: get directory of user speech profile (only if NatSpeak/Natlink is running)


The functions below should not change anything in settings, only  get information.

getDNSInstallDir:
    returns the directory where NatSpeak is installed.
    if the registry key NatspeakInstallDir exists(CURRENT_USER/Software/Natlink),
    this path is taken (if it points to a valid folder)
    Otherwise one of the default paths is taken,
    %PROGRAMFILES%/Nuance/... or %PROGRAMFILES%/ScanSoft/...
    It must contain at least a Program subdirectory or App/Program subdirectory

getDNSIniDir:
    returns the directory where the NatSpeak INI files are located,
    notably nssystem.ini and nsapps.ini.
    Can be set in natlinkstatus.ini, but mostly is got from
    %ALLUSERSPROFILE% (C:/ProgramData)

getDNSVersion:
    returns the in the version number of NatSpeak, as an integer. So 9, 8, 7, ... (???)
    note distinction is made here between different subversions.
(getDNSFullVersion: get longer version string) (obsolete, 2017, QH)
.
getWindowsVersion:
    see source below

getLanguage:
    returns the 3 letter code of the language of the speech profile that
    is open (only possible when NatSpeak/Natlink is running)

getUserLanguage:
    returns the language from changeCallback (>= 15) or config files

getUserTopic
    returns the topic of the current speech profile, via changeCallback (>= 15) or config files

getPythonVersion:
    changed jan 2013, return two character version, so without the dot! eg '26'

    new nov 2009: return first three characters of python full version ('2.5')
#    returns, as a string, the python version. Eg. "2.3"
#    If it cannot find it in the registry it returns an empty string
#(getFullPythonVersion: get string of complete version info).


getUserDirectory: get the Natlink user directory, 
    Especially Dragonfly users will use this directory for putting their grammar files in.
    Also users that have their own custom grammar files can use this user directory

getUnimacroDirectory: get the directory where the Unimacro system is.
    When git cloned, relative to the Core directory, otherwise somewhere or in the site-packages (if pipped). This grammar will (and should) hold the _control.py grammar
    and needs to be included in the load directories list of James' natlinkmain

getUnimacroGrammarsDirectory: get the directory, where the user can put his Unimacro grammars. By default
    this will be the ActiveGrammars subdirectory of the UnimacroUserDirectory.

getUnimacroUserDirectory: get the directory of Unimacro INI files, if not return '' or
      the Unimacro user directory

getVocolaDirectory: get the directory where the Vocola system is. When cloned from git, in Vocola, relative to
      the Core directory. Otherwise (when pipped) in some site-packages directory. It holds (and should hold) the
      grammar _vocola_main.py.

getVocolaUserDirectory: get the directory of Vocola User files, if not return ''
    (if run from natlinkconfigfunctions use getVocolaDirectoryFromIni, which checks inifile
     at each call...)

getVocolaGrammarsDirectory: get the directory, where the compiled Vocola grammars are/will be.
    This will normally be the "CompiledGrammars" subdirectory of the VocolaUserDirectory.

NatlinkIsEnabled:
    return 1 or 0 whether Natlink is enabled or not
    returns None when strange values are found
    (checked with the INI file settings of NSSystemIni and NSAppsIni)

getNSSYSTEMIni(): get the path of nssystem.ini
getNSAPPSIni(): get the path of nsapps.ini

getBaseModelBaseTopic:
    return these as strings, not ready yet, only possible when
    NatSpeak/Natlink is running. Obsolete 2018, use
getBaseModel
    get the acoustic model from config files (for DPI15, obsolescent)
getBaseTopic
    get the baseTopic, from ini files. Better use getUserTopic in DPI15
getDebugLoad:
    get value from registry, if set do extra output of natlinkmain at (re)load time
getDebugCallback:
    get value from registry, if set do extra output of natlinkmain at callbacks is given
getDebugOutput:
    get value from registry, output in log file of DNS, should be kept at 0

getVocolaTakesLanguages: additional settings for Vocola

new 2014:
getDNSName: return "NatSpeak" for versions <= 11 and "Dragon" for 12 (on)
getAhkExeDir: return the directory where AutoHotkey is found (only needed when not in default)
getAhkUserDir: return User Directory of AutoHotkey, not needed when it is in default.

"""
import os
import re
import sys
import pprint
import stat
import winreg
import pathlib
from pathlib import Path   # and dismiss pathqh!!
import win32api
# import time
from natlinkcore import natlinkcorefunctions
# from natlinkcore import inivars
from natlinkcore.pathqh import path
from natlinkcore import __init__
# for getting generalised env variables:

##from win32com.shell import shell, shellcon

# adapt here
VocIniFile  = r"Vocola\Exec\vocola.ini"

lowestSupportedPythonVersion = 37

DNSPaths = []
DNSVersions = list(range(19,14,-1))
for _v in DNSVersions:
    varname = "NSExt%sPath"%_v
    if "NSExt%sPath"% _v not in globals():
        globals()[varname] = "Nuance\\NaturallySpeaking%s"% _v
    DNSPaths.append(globals()[varname])

# Nearly obsolete table, for extracting older windows versions:
# newer versions go via platform.platform()
Wversions = {'1/4/10': '98',
             '2/3/51': 'NT351',
             '2/4/0':  'NT4',
             '2/5/0':  '2000',
             '2/5/1':  'XP',
             '2/6/0':  'Vista'
             }

# the possible languages (for getLanguage)
languages = {  # from config files (if not given by args in setUserInfo)
             "Nederlands": "nld",
             "Fran\xe7ais": "fra",
             "Deutsch": "deu",
             # English is detected as second word of userLanguage
             # "UK English": "enx",
             # "US English": "enx",
             # "Australian English": "enx",
             # # "Canadian English": "enx",
             # "Indian English": "enx",
             # "SEAsian English": "enx",
             "Italiano": "ita",
             "Espa\xf1ol": "esp",
             # as passed by args in changeCallback, DPI15:
             "Dutch": "nld",
             "French": "fra",
             "German": "deu",
             # "CAN English": "enx",
             # "AUS English": "enx",
             "Italian": "ita",
             "Spanish": "esp",}

shiftKeyDict = {"nld": "Shift",
                "enx": 'shift',
                "fra": "maj",
                "deu": "umschalt",
                "ita": "maiusc",
                "esp": "may\xfas"}

reportDNSIniDirErrors = True # set after one stroke to False, if errors were there (2017, february)


class NatlinkStatus:
    """this class holds the Natlink status functions

    so, can be called from natlinkmain.

    in the natlinkconfigfunctions it is subclassed for installation things
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    #pylint:disable=R0902, R0904
    ### from previous modules, needed or not...
    #this is used to enabled to the compatibility modules
    # NATLINK_CLSID must be in the correct naturally speaking ini
    #files for dragon to load natlink.
    NATLINK_CLSID = "{dd990001-bb89-11d2-b031-0060088dc929}"

    NSSystemIni  = "nssystem.ini"
    NSAppsIni  = "nsapps.ini"
    ## setting of nssystem.ini if Natlink is enabled...
    ## this first setting is decisive for NatSpeak if it loads Natlink or not
    section1 = "Global Clients"
    key1 = ".Natlink"
    value1 = 'Python Macro System'

    ## setting of nsapps.ini if Natlink is enabled...
    ## this setting is ignored if above setting is not there...
    section2 = ".Natlink"
    key2 = "App Support GUID"
    value2 = NATLINK_CLSID
    # for quicker access (only once lookup in a run)
    # NatlinkDirectory = None ## in __init__
    UserDirectory = None # for Dragonfly mainly, and for user defined grammars
    # BaseDirectory = None
    # CoreDirectory = None
    DNSInstallDir = None
    DNSVersion = None
    DNSIniDir = None
    ## Unimacro:
    UnimacroDirectory = None
    UnimacroUserDirectory = None
    UnimacroGrammarsDirectory = None
    ## Vocola:
    VocolaUserDirectory = None
    VocolaDirectory = None
    VocolaGrammarsDirectory = None
    ## AutoHotkey:
    AhkUserDir = None
    AhkExeDir = None
    hadWarning = []


    def __init__(self, skipSpecialWarning=None,devnatlink_dll=None):
        """ devnatlink_dll is the path of a dll to use rather than a published one.
        usesful during development. """

        self.devnatlink_dll = devnatlink_dll
       # print(f'natlinkstatus.__ini__, skipSpecialWarning input skipSW: {skipSpecialWarning}')
        try:
            self.__class__.skipSpecialWarning
        except AttributeError:
            self.__class__.skipSpecialWarning = skipSpecialWarning
        # print(f'natlinkstatus.__ini__, self.skipSpecialWarning after: {self.skipSpecialWarning}')
        # print(f'natlinkstatus.__ini__, self.__class__.skipSpecialWarning after: {self.__class__.skipSpecialWarning}')
        # print('-'*50)
        try:
            self.__class__.hadFatalErrors
        except AttributeError:
            self.__class__.hadFatalErrors = False
        
        try:
            self.__class__.userinisection
        except AttributeError:
            self.__class__.userinisection = natlinkcorefunctions.NatlinkstatusInifileSection()

        try:
            self.__class__.UserArgsDict
        except AttributeError:
            self.__class__.UserArgsDict = {}
        # print(f'UserArgsDict at start of instance: {self.__class__.UserArgsDict}')

        ## start setting the CoreDirectory and BaseDirectory and other variables:
        try:
            self.__class__.NatlinkDirectory
        except AttributeError:
            thisDir=pathlib.WindowsPath(__file__).parent
            # thisDirResolved = thisDir.resolve()
            coreDir=self.findInSitePackages(str(thisDir))
            self.__class__.NatlinkDirectory = self.getNatlinkDirectory(coreDir=coreDir)
            assert os.path.isdir(self.NatlinkDirectory)
        # initialize settings for this session:
        
        self.correctIniSettings() # change to newer conventions
    
        ## initialise DNSInstallDir, DNSVersion and DNSIniDir
        ## other "cached" variables, like UserDirectory, are done at first call.
        try:
            result = self.getDNSInstallDir()
        except OSError:
            result = -1
        else:
            result = result or -1
        self.__class__.DNSInstallDir = result
        self.DNSName = self.getDNSName()
            
        if result == -1:
            ## also DNSIniDir is hopeless, set value and return.
            self.__class__.DNSIniDir = result
            self.__class__.DNSVersion = result
            return
        # else:
        ## proceed with other __class__ variables:
        self.__class__.DNSVersion = self.getDNSVersion()

        ## DNSIniDir:
        try:
            result = self.getDNSIniDir()
        except OSError:
            result = -1
        else:
            result = result or -1

        self.__class__.DNSIniDir = result
        if result == -1:
            return  # serious problem.

        self.checkNatlinkPydFile()

    def getWarningText(self):
        """return a printable text if there were warnings
        """
        if self.hadWarning:
            t = 'natlinkstatus reported the following warnings:\n\n'
            t += '\n\n'.join(self.hadWarning)
            return t
        return ""

    def emptyWarning(self):
        """clear the list of warning messages
        """
        while self.hadWarning:
            self.hadWarning.pop()

    def checkSysPath(self):
        """add base, unimacro and user directory to sys.path

        if Vocola is enabled, but Unimacro is NOT and the option VocolaTakesUnimacroActions is True,
        then also include the Unimacro directory!

        (the registry is out of use, only the core directory is in the
        PythonPath / Natlink setting, for natlink be able to be started.

        """
        # print(f'checkSysPath with PythonPath setting in registry not needed any more')
        # return 1
        NatlinkDirectory = self.getNatlinkDirectory()

        if NatlinkDirectory.lower().endswith('natlinkcore'):
            # check the registry setting:
            result = self.getRegistryPythonPathNatlink()
            if not result:
                print('''Natlink setting not found in Natlink section of PythonPath setting\n
Please try to correct this by running the Natlink Config Program (with administration rights)\n''')
                return None
            _natlinkkey, natlinkvalue,  = result
            if not natlinkvalue:
                print('''Natlink setting not found in Natlink section of PythonPath setting in registry\n
Please try to correct this by running the Natlink Config Program (with administration rights)''')
                return None

            coreDirectory = Path(natlinkvalue)
            if not coreDirectory.is_dir():
                print(f'''Natlink setting "{coreDirectory}" in the registry is not a valid directory\n
Please try to correct this by running the Natlink Config Program (with administration rights)''')

        return 1


    def checkNatlinkPydFile(self):
        """see if natlink.dll is in core directory, and uptodate, if not stop and point to the configurenatlink program

        if fromConfig, print less messages...

        if natlink.pyd is missing, or
        if NatlinkPydOrigin is absent or not correct, or
        if the original natlink26_12.pyd (for example) is newer than natlink.pyd

        # july 2013:
        now conform to the new naming conventions of Rudiger, PYD subdirectory and natlink_2.7_UNICODE.pyd etc.
        the natlink25.pyd has been moved to the PYD directory too and also is named according to the new conventions.

        the config program should be run.
        """
        NatlinkDirectory = self.getNatlinkDirectory()
        pydDir = os.path.join(NatlinkDirectory, 'PYD')
        if not (pydDir and os.path.isdir(pydDir)):
            return 1

        originalPyd = self.getNatlinkPydOrigin()   # original if previously registerd (from natlinkstatus.ini file)
        _originalPydDir, originalPydFile = os.path.split(originalPyd)
        wantedPyd = self.getWantedNatlinkPydFileName()       # wanted original based on python version and Dragon version
        wantedPydPath = os.path.join(pydDir, wantedPyd)
        currentPydPath = os.path.join(NatlinkDirectory, 'natlink.pyd')

        if not os.path.isfile(wantedPydPath):
            print(f'The wanted pyd "{wantedPydPath}" does not exist, Dragon/python combination not valid.')
            return None

        # first check existence of natlink.pyd (probably never comes here)
        if not os.path.isfile(currentPydPath):
            print(f'pyd path "{currentPydPath}" does not exist...')
            return None

        # check correct pyd version, with python version and Dragon version:
        if wantedPyd != originalPydFile:
            if not originalPydFile:
                self.warning('originalPyd setting is missing in natlinkstatus.ini')
            else:
                self.fatal_error('incorrect originalPydFile (from natlinkstatus.ini): %s, wanted: %s'% (originalPydFile, wantedPyd))
            return None

        self.checkPydChanges(currentPydPath=None, wantedPydPath=None)
        return None

    def checkPydChanges(self, currentPydPath=None, wantedPydPath=None):
        """check if currentPath should be updated to wantedPath
        
        First check also different paths current compared with NatlinkPydOrigin in natlinkstatus.ini.
        Inconsistenceis lead to a fatal_error, asking the user to Re-register via config program.
        
        When the current natlink.pyd seems to be outdated (and changed), 
        a warning at startup is given, advicing the user to Re-register natlink.pyd with the config program
        """
        #pylint:disable=R0912, R0914        
        # NatlinkDirectory = self.getNatlinkDirectory()
        if  currentPydPath is None:
            currentPydPath = os.path.join(self.NatlinkDirectory, 'natlink.pyd')

        wantedPyd = self.getWantedNatlinkPydFileName()       # wanted original based on python version and Dragon version

        if wantedPydPath is None:
            wantedPydPath = os.path.join(self.NatlinkDirectory, 'PYD', wantedPyd)
        if wantedPydPath and os.path.isfile(wantedPydPath):
            wantedDir, wantedFile = os.path.split(wantedPydPath)
        else:
            self.warning(f'The needed pyd file is not found, directory: "{wantedDir}", filename: "{wantedFile}"')

        NatlinkPydOrigin = self.userinisection.get('NatlinkPydOrigin')
        if NatlinkPydOrigin and os.path.isfile(NatlinkPydOrigin):
            originalPydDir, originalPydFile = os.path.split(NatlinkPydOrigin)
            originalNatlinkcoreDir = os.path.normpath(os.path.join(originalPydDir, '..'))
        else:
            self.warning('No original pyd file found in settings "NatlinkPydOrigin"')
            return
        
        currentDir, _currentFile = os.path.split(currentPydPath)
        runFromConfig = (currentDir.endswith('ConfigureNatlink'))
        
        if wantedPyd != wantedFile:
            mess = f'Dragon or python version changed. current: {wantedPyd}, needed for this version of python or Dragon: {wantedFile}'
            self.fatal_error(mess)
            
        if originalPydFile != wantedFile:
            mess = f'Dragon or python version changed. From NatlinkPydOrigin (natlinkstatus.ini): {originalPydFile}, needed for this version of python or Dragon: {wantedFile}'
            self.fatal_error(mess)

        if originalNatlinkcoreDir.lower() != currentDir.lower():
            if runFromConfig:
                mess = [f'The program started from the subdirectory "ConfigureNatlink" of {self.NatlinkDirectory}.', '']
            else:
                ## run from natlinkstatus
                mess = [f'The program started from {self.NatlinkDirectory}.']
            
            
            mess.extend([f'This is another location than is kept in natlinkstatus.ini: {originalNatlinkcoreDir}.', '',
                    f'When you want this new location, "{self.NatlinkDirectory}",', 'you need to Re-register Natlink in the Configure Program (GUI) or CLI.',''])
            if runFromConfig:                
                mess.extend(['When you want to keep the "original location", quit the config program,',
                             f'and be sure your Dragon starts Natlink from from {originalNatlinkcoreDir}.'])
            else:
                ##natlinkstatus:
                mess.extend([f'When you want to keep the "original location", be sure your Dragon starts Natlink from from {originalNatlinkcoreDir}.'])
                
            self.fatal_error('\n'.join(mess))
            
        result = self.PydChangedContent(target=currentPydPath, wanted=wantedPydPath)
        if result:
            self.warning(result)   #ask user to re-register 
            
   
    def PydChangedContent(self, target, wanted):
        """check if the pyd file in the PYD directory has been changed and is different
        
        return True if content has been changed. A re-register should be done in the config program
        
        Otherwise, (None, False) all is well
        
        """
        #pylint:disable=R0201
        timeWanted = getFileDate(wanted)
        timeTarget = getFileDate(target)
         
        # check for newer (changed version) of original pyd:
        if timeWanted > timeTarget:
            same = open(wanted, "rb").read() == open(target, "rb").read()
            if not same:
                mess = f'Current pyd file {target} is out of date, compared with {wanted}, and not identical.'
                return mess
        return None
        
        
    def getHiveKeyReadable(self, hive):
        """return the text of the hive key
        """
        #pylint:disable=R0201, C0321
        if hive == winreg.HKEY_LOCAL_MACHINE: return 'HKLM'
        if hive == winreg.HKEY_CURRENT_USER: return 'HKCU'
        return 'HK??'

    def getRegistryPythonPathKey(self, silent=True):
        """returns the key to PythonPath setting in the registry
        
        This must be a 32-bit python version as given by sys.winver
        
        flag is winreg.KEY_READ (always read only) and KEY_WOW64_32KEY
        
        Returns the key, which can come from either
        CURRENT_USER (python installed for one user) or
        LOCAL_MACHINE (python installed for all users)
        
        """
        #pylint:disable=W0613, R0201
        dottedVersion = sys.winver
        
        pythonPathSectionName = r"SOFTWARE\Python\PythonCore\%s\PythonPath"% dottedVersion
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            key, flags = (pythonPathSectionName, winreg.KEY_WOW64_32KEY | winreg.KEY_READ)
            try:
                pythonpath_key = winreg.OpenKeyEx(hive, key, access= flags)
                if pythonpath_key:
                    return pythonpath_key
            except FileNotFoundError:
                continue
        print('no valid PythonPath/Natlink key found in registry')
        return None

    def getRegistryPythonPathNatlink(self, flags=winreg.KEY_READ, silent=True):
        """returns the path-to-core of Natlink and the PythonPath key in the registry
        
        returns a tuple (key-to-pythonpath-setting, directory_from_registry)
        (Note: order changed, December, 2020)
        
        if no Natlink key found, return None
        
        if Natlink key is found, return the directory_from_registry, mostly the middle item of a 3 tuple.
        If the value found is NOT a 3 tuple, return "Natlink value wrong type in registry"

        When setting the value, from natlinkconfigfunctions,
        pass winreg.KEY_ALL_ACCESS as flags.

        """
        #pylint:disable=R1710, W0613
        pythonpath_key = self.getRegistryPythonPathKey()
        if not pythonpath_key:
            print('no valid pythonpath key in registry found')
            return None
        for i in range(10):
            try:
                keyName = winreg.EnumKey(pythonpath_key, i)
                if keyName.lower() == 'natlink':
                    natlink_key = winreg.OpenKey(pythonpath_key, keyName)
                    for j in range(10):
                        natlink_value = winreg.EnumValue(natlink_key, j)
                        # print(f'Value from registry: {natlink_value}')
                        if isinstance(natlink_value, tuple) and len(natlink_value) == 3:
                            natlinkdir_from_registry = natlink_value[1]
                        else:
                            natlinkdir_from_registry = "Natlink value wrong type in registry"
                        
                        return natlink_key, natlinkdir_from_registry
                    #     # print(f'values: {i}, {Value}')
                    #     break
                    # else:
                    #     print(f'no valid Natlink entry found in registry section "Natlink"')
                    #     raise FileNotFoundError
                    # 
                    # if type(Value) == tuple and len(Value) == 3:
                    #     pythonpath = Value[1]
                    #     natlinkmainPath = os.path.join(pythonpath, "natlinkmain.py")
                    #     if os.path.isfile(natlinkmainPath):
                    #         if not silent:
                    #             print(f'Natlink entry found in registry section "Natlink": "{pythonpath}"')
                    #         return pythonpath, natlink_key
                    #     else:
                    #         print(f'no valid Natlink entry found in registry section "Natlink": {pythonpath}, does not contain "natlinkmain.py"')
                    #         raise FileNotFoundError
                            
            except OSError:
                pass
            return None
        
    def InsertToSysPath(self, newdir):
        """leave "." in the first place if it is there"""
        #pylint:disable=R0201
        if not newdir:
            return
        newdir = os.path.normpath(newdir)
        newdir = win32api.GetLongPathName(newdir)
        # keep the convention of capitalizing the drive letter:
        if len(newdir) > 1 and newdir[1] == ":":
            newdir = newdir[0].upper() + newdir[1:]

        if newdir in sys.path:
            return
        if sys.path[0] in ("", "."):
            sys.path.insert(1, newdir)
        else:
            sys.path.insert(0, newdir)
        #print 'inserted in sys.path: %s'% newdir

    def copyRegSettingsToInifile(self, reg, ini):
        """for firsttime use, copy values from
        """
        #pylint:disable=R0201
        for k,v in list(reg.items()):
            ini.set(k, v)
        #except:
        #    print 'could not copy settings from registry into inifile. Run natlinkconfigfunctions...'

    def correctIniSettings(self):
        """change NatlinkDllRegistered to NatlinkPydOrigin

        the new value should have 25;12 (so python version and dragon version)
        """
        ini = self.userinisection
        oldSetting = ini.get('NatlinkDllRegistered')
        newSetting = ini.get('NatlinkPydOrigin')
        if oldSetting and not newSetting:
            if len(oldSetting) <= 2:
                dragonVersion = self.getDNSVersion()
                if dragonVersion <= 11:
                    # silently go over to new settings:
                    oldSetting = "%s;%s"% (oldSetting, dragonVersion)
            print('correct setting from "NatlinkDllRegistered" to "NatlinkPydOrigin"')
            ini.set('NatlinkPydOrigin', oldSetting)
            ini.delete('NatlinkDllRegistered')
        oldSetting = ini.get('UserDirectory')
        if oldSetting and oldSetting.find('Unimacro') > 0:
            ini.delete('UserDirectory')
        oldSetting = ini.get('IncludeUnimacroInPythonPath')
        if oldSetting:
            ini.delete('IncludeUnimacroInPythonPath')

    def setUserInfo(self, args):
        """set username and userdirectory at change callback user
        
        args[0] = username
        args[1] = Current directory for user profile (in programdata/nuance etc)
                  extract for example userLanguage ('Nederlands') from acoustics.ini and options.ini

        if the three letter "language" ('enx', 'nld' etc) is not found there is an error in this module: 'languages' dict.
        English dialects are detected if the userLanguage is '.... English'.
        
        if there is no connection with natlink (no speech profile on, when debugging) language 'tst' is returned in getLanguage
        
        """
        # print(f'-----setUserInfo, args: {args}')
        if len(args) < 2:
            print('UNEXPECTED ERROR: natlinkstatus, setUserInfo: length of args to small, should be at least 2: %s (%s)'% (len(args), repr(args)))
            return

        userName = args[0]
        self.__class__.UserArgsDict['userName'] = userName
        DNSuserDirectory = args[1]
        self.__class__.UserArgsDict['DNSuserDirectory'] = DNSuserDirectory
        if len(args) == 2:
            userLanguage = self.getUserLanguageFromInifile()
            try:
                language = languages[userLanguage]
            except KeyError:
                englishDialect = userLanguage.split()[-1]
                if englishDialect == 'English':
                    language = 'enx'
                else:
                    print('natlinkstatus, setUserInfo: no language found for userLanguage: %s'% userLanguage)
                    print('=== please report to q.hoogenboom@antenna.nl ===')
                    language = ''
            print(f'setUserInfo, setting language to: {language}')
            self.__class__.UserArgsDict['language'] = language
            self.__class__.UserArgsDict['userLanguage'] = userLanguage
            self.__class__.UserArgsDict['userTopic'] = self.getUserTopic() # will be the basetopic...
        else:
            print('natlinkstatus, setUserInfo: unexpected length of args for UserArgsDict: %s (%s)'% (len(args), repr(args)))
            print('=== please report to q.hoogenboom@antenna.nl ===')

    def clearUserInfo(self):
        """clear UserInfo
        """
        self.__class__.UserArgsDict.clear()

    def getUserName(self):
        """get UserName from UserArgsDict
        """
        try:
            return self.__class__.UserArgsDict['userName']
        except KeyError:
            return ''

    def getDNSuserDirectory(self):
        """get DNSuserDirectory from UserArgsDict
        """
        try:
            return self.__class__.UserArgsDict['DNSuserDirectory']
        except KeyError:
            return ''

    def getNatlinkPydOrigin(self):
        """return the path of the original dll/pyd file

        in previous versions, this was pythonversion;dragonversion (eg 38;15).
        """
        setting = self.userinisection.get("NatlinkPydOrigin")
        return setting 
        # if not setting:
        #     return ""
        # if ";" in setting:
        #     pyth, drag = setting.split(";")
        #     pythonInFileName = pyth[0] + '.' + pyth[-1]
        #     pyth, drag = int(pyth), int(drag)
        # else:
        #     pythonInFileName = setting[0] + '.' + setting[-1]
        #     pyth, drag = int(setting), 11  # which can also mean pre 11...
        # 
        # if pyth < 17:
        #     fatal_error(f'This is Natlink for Python 3, only version 3.7 and above are supported, not: {pythonInFileName}')
        # 
        # if drag <= 11:
        #     fatal_error(f'With python version 3 only DPI 15 and above are supported, not {drag}')
        #     ansiUnicode = 'ANSI'
        # elif drag <= 14:
        #     fatal_error(f'With python version 3 only DPI 15 and above are supported, not {drag}')
        #     ansiUnicode= 'UNICODE'
        # else:
        #     ansiUnicode = 'Ver15'
        # 
        # pydFilename = 'natlink_%s_%s.pyd'% (pythonInFileName, ansiUnicode)
        # return pydFilename

    def getWantedNatlinkPydFileName(self):
        """return the filename of the pyd file that serves as NatlinkPydOrigin
        
        This filename, in the PYD subdirectory of natlinkcore is copied into the natlinkcore
        directory and registered.
        
        I things go wrong, return ""
        """
        pyth = self.getPythonVersion()
        drag = self.getDNSVersion()
        pythonInFileName = pyth[0] + '.' + pyth[-1]
        if not pyth:
            return ""
        if not drag:
            return ""
        drag, pyth = int(drag), int(pyth)
        if drag <= 11:
            ansiUnicode = 'ANSI'
        elif drag <= 14:
            ansiUnicode= 'UNICODE'
        else:
            ansiUnicode = 'Ver15'

        pydFilename = 'natlink_%s_%s.pyd'% (pythonInFileName, ansiUnicode)
        return pydFilename

    def getWindowsVersion(self):
        """extract the windows version

        return 1 of the predefined values above, or just return what the system
        call returns
        """
        #pylint:disable=R0201, C0415
        tup = win32api.GetVersionEx()
        version = "%s/%s/%s"% (tup[3], tup[0], tup[1])
        try:
            windowsVersion = Wversions[version]
        except KeyError:
            import platform
            wVersion = platform.platform()
            if '-' in wVersion:
                return wVersion.split('-')[1]
            # else:
            print(f'Warning, probably cannot find correct Windows Version... ({wVersion}')
            return wVersion
        else:
            return windowsVersion


    def getDNSIniDir(self, calledFrom=None, force=None):
        """get the path (one above the users profile paths) where the INI files
        should be located

        if force == True, refresh value (for use in config program)

        """
        #pylint:disable=W0603, W0613
        global reportDNSIniDirErrors
        # first try if set (by configure dialog/natlinkinstallfunctions.py) if regkey is set:
        if self.DNSIniDir and force is None:
            return self.DNSIniDir

        key = 'DNSIniDir'
        P = self.userinisection.get(key)
        if P:
            os.path.normpath(P)
            if os.path.isdir(P):
                return P
        # if calledFrom is None:
        #     knownDNSVersion = str(self.getDNSVersion())
        # else:
        #     knownDNSVersion = None
    
        # the nssystem.ini and nsapps.ini are in the ProgramData directory
        # version 15: C:\ProgramData\Nuance\NaturallySpeaking15\Users

        # The User profile directory, from where the properties of the current profile are got
        # were, up to DNS15.3 in the ProgramData/Users directory
        # 
        # after DNS15.5:   %LOCALAPPDATA%s\Nuance\NS15\Users
        # but the DNSIniDir is unchanged with the upgrade to DNS15.5 or 15.6
        triedPaths = []
        ProgramDataDirectory = path('%ALLUSERSPROFILE%')
        # allusersprofileAppData = path('%LOCALAPPDATA%')
        DNSVersion = self.getDNSVersion()
        # if allusersprofileAppData.isdir():
        #     usersDir = allusersprofileAppData/('Nuance/NS%s'%DNSVersion)
        #     if usersDir.isdir():
        #         DNSIniDir = usersDir.normpath()
        #         return DNSIniDir
        #     triedPaths.append(usersDir.normpath())
        # else:
        #     triedPaths.append(allusersprofileAppData.normpath())

        if ProgramDataDirectory.isdir():
            usersDir = ProgramDataDirectory/(f'Nuance/NaturallySpeaking{DNSVersion}')
            if usersDir.isdir():
                DNSIniDir = usersDir.normpath()
                return DNSIniDir
            triedPaths.append(usersDir.normpath())
        
        if not triedPaths:
            report = []
            if reportDNSIniDirErrors:
                report.append('DNSIniDir not found, did not find paths to try from for version: %s'% self.getDNSVersion())
                report.append('Please report to q.hoogenboom@antenna.nl')

        if reportDNSIniDirErrors:
            report = []
            reportDNSIniDirErrors = False
            report.append('DNSIniDir not found, tried in directories: %s'% repr(triedPaths))
            report.append('no valid DNS INI files Dir found, please provide one in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)')
            report.append('Note: The path must end with "NaturallySpeaking%s"'% self.getDNSVersion())
            print('Errors in getDNSIniDir:')
            print('\n'.join(report))
        return None
    
    def getDNSFullVersion(self):
        """find the Full version string of DNS

        empty if not found, eg for older versions
        """
        print('getDNSFullVersion nearly obsolete')
        # for 9:
        iniDir = self.getDNSIniDir(calledFrom="getDNSFullVersion")
        # print 'iniDir: %s'% iniDir
        if not iniDir:
            return 0
        nssystemini = self.getNSSYSTEMIni()
        # nsappsini = self.getNSAPPSIni()
        if nssystemini and os.path.isfile(nssystemini):
            version =win32api.GetProfileVal( "Product Attributes", "Version" , "",
                                          nssystemini)

            return version
        return ''


    def getDNSVersion(self):
        """find the correct DNS version number (as an integer)

        Version 15 is simply the int of the last two letters of the DNSInstallDir.

        note: 12.80 is also 13
        from 10 onwards, get as last two characters of the DNSInstallDir
        for versions 8 and 9 look in NSSystemIni, take from DNSFullVersion
        for 9 in Documents and Settings
        for 8 in Program Folder

        for earlier versions try the registry, the result is uncertain.

        """
        try:
            version = self.DNSVersion
        except AttributeError:
            pass
        else:
            if version:
                return version
        dnsPath = self.getDNSInstallDir()
        if dnsPath == -1:
            print('dnsPath not found, please ensure there is a proper DNSInstallDir')
            return 0
        # pos = dnsPath.rfind("NaturallySpeaking")
        # if pos == -1:
        #     print 'Cannot find "NaturallySpeaking" in dnsPath: "%s"'% dnsPath

        versionString = dnsPath[-2:]

        try:
            i = int(versionString[0])
        except ValueError:
            versionString = versionString[-1:]  # dragon 9
        except IndexError:
            print('versionString: "%s", dnsPath: "%s"'% (versionString, dnsPath))
        try:
            i = int(versionString)
        except ValueError:
            print('Cannot find versionString, dnsPath should end in two digits (or one for versions below 10): %s'% dnsPath)
            print('These digits must match the version number of Dragon!!!')
            return 0
        return i


    def getDNSInstallDir(self, force=None):
        """get the folder where natspeak is installed

        try from the list DNSPaths, look for 20, 19, 18, ...

        force == True: get a new value, for use in the config program

        """
        # caching mechanism:
        if self.DNSInstallDir and force is None:
            return self.DNSInstallDir

        ## get first time value:
        key = 'DNSInstallDir'
        P = self.userinisection.get(key)
        if P:
            if self.checkDNSProgramDir(P):
                return P
            if not self.skipSpecialWarning:
                print('-'*60)
                print('DNSInstallDir is set in natlinkstatus.ini to "%s", ...'% P)
                print('... this does not match a valid Dragon Program Directory.')
                print('This directory should hold a Program subdirectory or')
                print('or the subdirectories "App\\Program"')
                print('in which the Dragon program is located.')
                print()
                print('Please set or clear DNSInstallDir:')
                print('In Config GUI, with button in the info panel, or')
                print('Via natlinkconfigfunctions.py with option d')
                print('-'*60)
                raise OSError('Invalid value of DNSInstallDir: %s'% P)
            print('invalid DNSInstallDir: %s, but proceed...'% P)
            return ''
                
        ## get the program files (x86) directory via extended Environment variables,
        ## now in the path class. Note %PROGRAMFILES(X86)% does not work, because
        ## only [a-z0-9_] is accepted, case independent.
        pf = path('%PROGRAM_FILESX86%')
        if not pf.isdir():
            raise OSError("no valid folder for program files: %s"% pf)
        for dnsdir in DNSPaths:
            cand = pf/dnsdir
            # print('cand: %s'% cand)
            if cand.isdir():
                programfolder = cand/'Program'
                if programfolder.isdir():
                    # print('succes!: %s'% programfolder)
                    # return a str:
                    return cand.normpath()
        if not self.skipSpecialWarning:
            print('-'*60)
            print('No valid DNSInstallDir is found in the default settings of Natlink')
            print()
            print('Please exit Dragon and set a valid DNSInstallDir:')
            print('In Config GUI, with button in the info panel, or')
            print('Via natlinkconfigfunctions.py with option d')
            print('-'*60)
            raise OSError('No valid DNSInstallDir found in the default settings of Natlink')
        print('-'*60)
        print('No valid DNSInstallDir is found in the default settings of Natlink.')
        print()
        print('Please specify a valid DNSInstallDir:')
        print('In Config GUI, with button in the info panel, or')
        print('Via natlinkconfigfunctions.py with option d')
        return ''
    
    def checkDNSProgramDir(self, checkDir):
        """check if directory is a Dragon directory

        it must be a directory, and have as subdirectories App/Program (reported by Udo) or Program.
        In this subdirectory there should be natspeak.exe
        """
        #pylint:disable=R0201

        if not checkDir:
            return None
        if not os.path.isdir(checkDir):
            print('checkDNSProgramDir, %s is not a directory'% checkDir)
            return None
        programDirs = os.path.join(checkDir, 'Program'), os.path.join(checkDir, 'App', 'Program')
        for programDir in programDirs:
            programDir = os.path.normpath(programDir)
            programFile = os.path.join(programDir, 'natspeak.exe')
            if os.path.isdir(programDir) and os.path.isfile(programFile):
                return True
        print('checkDNSProgramDir, %s is not a valid Dragon Program Directory'%  checkDir)
        return None
    #def getPythonFullVersion(self):
    #    """get the version string from sys
    #    """
    #    version2 = sys.version
    #    return version2

    def getPythonVersion(self):
        """get the version of python

        Check if the version is supported on the "lower" side.
        
        length 2, without ".", so "38" etc.
        """
        #pylint:disable=R0201
        version = sys.version[:3]
        version = version.replace(".", "")
        if len(version) != 2:
            raise ValueError('getPythonVersion, length of python version should be 2, not: %s ("%s")'% (len(version), version))
        if int(version) < lowestSupportedPythonVersion:
            versionReadable = version[0] + "." + version[1]
            lspv = str(lowestSupportedPythonVersion)
            lspvReadable = lspv[0] + "." + lspv[1]
            raise ValueError('getPythonVersion, current version is: "%s".\nPython versions before "%s" are not any more supported by Natlink.\nIf you want to run NatLink on Python2.7, please use the older version of NatLink at SourceForge (https://sourceforge.net/projects/natlink/)'% (versionReadable, lspvReadable))
        return version

    def getPythonPath(self):
        """return the python path, for checking in config GUI
        """
        #pylint:disable=R0201
        return sys.path
    def printPythonPath(self):
        """print the pythonPath
        """
        #pylint:disable=R0201
        pprint.pprint(self.getPythonPath())


    def getNSSYSTEMIni(self):
        """get NSSYSTEMIni
        """
        inidir = self.getDNSIniDir()
        if inidir:
            nssystemini = os.path.join(inidir, self.NSSystemIni)
            if os.path.isfile(nssystemini):
                return os.path.normpath(nssystemini)
        print("Cannot find proper NSSystemIni file")
        print('Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)')
        return None
    def getNSAPPSIni(self):
        """get NSAPPSInin
        """
        inidir = self.getDNSIniDir()
        if inidir:
            nsappsini = os.path.join(inidir, self.NSAppsIni)
            if os.path.isfile(nsappsini):
                return os.path.normpath(nsappsini)
        print("Cannot find proper NSAppsIni file")
        print('Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)')
        return None

    def NatlinkIsEnabled(self, silent=None, force=None):
        """check if the INI file settings are correct

    in  nssystem.ini check for:

    [Global Clients]
    .Natlink=Python Macro System

    in nsapps.ini check for
    [.Natlink]
    App Support GUID={dd990001-bb89-11d2-b031-0060088dc929}

    if both settings are set, return 1
    (if nssystem.ini setting is set, you also need the nsapps.ini setting)
    if nssystem.ini setting is NOT set, return 0

    if nsapps.ini is set but nssystem.ini is not, Natlink is NOT enabled, still return 0

    if nssystem.ini is set, but nsapps.ini is NOT, there is an error, return None and a
    warning message, UNLESS silent = 1.
    
    Also check if the registry is set properly...

        """
        #pylint:disable=R0911, R0912, E0203, W0201

        if not force:
            try:
                isEnabled = self.cache_NatlinkIsEnabled
            except AttributeError:
                pass
            else:
                return isEnabled

        # result = self.getRegistryPythonPathNatlink()
        # if not result:
        #     self.cache_NatlinkIsEnabled = False
        #     return   ## registry setting not of pythonpath to core directory is not OK
        # registry_key, coredir_from_registry = result
        # 
        if self.DNSInstallDir == -1:
            self.cache_NatlinkIsEnabled = False
            return None
        if self.DNSIniDir == -1:
            self.cache_NatlinkIsEnabled = False
            return None
        if not self.NatlinkDirectory:
            self.cache_NatlinkIsEnabled = False
            return None
            
        nssystemini = self.getNSSYSTEMIni() or ''
        if not os.path.isfile(nssystemini):
            self.cache_NatlinkIsEnabled = False
            return 0
            # raise OSError("NatlinkIsEnabled, not a valid file: %s"% nssystemini)
        # filename: nssystem.ini
        # key1: .Natlink
        # section1: Global Clients
        actual1 = win32api.GetProfileVal(self.section1, self.key1, "", nssystemini)


        nsappsini = self.getNSAPPSIni()
        if not os.path.isfile(nsappsini):
            raise OSError("NatlinkIsEnabled, not a valid file: %s"% nsappsini)
        
        # filename: nsapps.ini
        # section2: .Natlink
        # key2: App Support GUID
        actual2 = win32api.GetProfileVal(self.section2, self.key2, "", nsappsini)
        if self.value1 == actual1:
            if self.value2 == actual2:
                # enabled:
                self.cache_NatlinkIsEnabled = True
                return True
            mess = ['Error while checking if Natlink is enabled, unexpected result: ',
                    'nssystem.ini points to NatlinkIsEnabled:',
                    '    section: %s, key: %s, value: %s'% (self.section1, self.key1, actual1),
                    'but nsapps.ini points to Natlink is not enabled:',
                  '    section: %s, key: %s, value: %s'% (self.section2, self.key2, actual2),
                  '    should have value: %s'% self.value2]
            if not silent:
                self.warning(mess)
            
            self.cache_NatlinkIsEnabled = False
            return None # error!
        if actual1:
            if not silent:
                self.warning("unexpected value of nssystem.ini value: %s"% actual1)
            # unexpected value, but not enabled:
            self.cache_NatlinkIsEnabled = False
            return 0
        # GUID in nsapps may be defined, natspeak first checks nssystem.ini
        # so Natlink NOT enabled
        self.cache_NatlinkIsEnabled = False
        return 0

        

    def warning(self, text):
        "to be overloaded in natlinkconfigfunctions and configurenatlink"
        if text in self.hadWarning:
            pass
        else:
            print('Warning:')
            print(text)
            print()
            self.hadWarning.append(text)

    def VocolaIsEnabled(self):
        """Return True if Vocola is enables
        
        To be so,
        1. the VocolaUserDirectory (where the vocola command files (*.vcl) are located)
        should be defined in the user config file
        2. the VocolaDirectory should be found, and hold '_vocola_main.py'
        
        """
        if not self.NatlinkIsEnabled():
            return None
        vocUserDir = self.getVocolaUserDirectory()
        if vocUserDir and path(vocUserDir).isdir():
            vocDir = self.getVocolaDirectory()
            vocGrammarsDir = self.getVocolaGrammarsDirectory()
            if vocDir and path(vocDir).isdir() and vocGrammarsDir and path(vocGrammarsDir).isdir():
                return True
        return None

    def UnimacroIsEnabled(self):
        """UnimacroIsEnabled: see if UserDirectory is there and

        _control.py is in this directory
        """
        if not self.NatlinkIsEnabled():
            return None
        uuDir = self.getUnimacroUserDirectory()
        if not uuDir:
            return None
        uDir = self.getUnimacroDirectory()
        if not uDir:
            # print('no valid UnimacroDirectory, Unimacro is disabled')
            return None
        if uDir and path(uDir).isdir():
            files = os.listdir(uDir)
            if not '_control.py' in files:
                return None  # _control.py should be in Unimacro directory
        ugDir = self.getUnimacroGrammarsDirectory()
        if ugDir and path(ugDir).isdir():
            return True  # Unimacro is enabled...            
        return None                

    def UserIsEnabled(self):
        """return 1 if Natlink is enabled and there is a UserDirectory
        """
        if not self.NatlinkIsEnabled():
            return None
        userDir = self.getUserDirectory()
        if userDir:
            return 1
        return None

    def getUnimacroUserDirectory(self):
        """return the UnimacroUserDirectory is Unimacro is enabled
        """ 
        if self.UnimacroUserDirectory is not None:
            return self.UnimacroUserDirectory
        key = 'UnimacroUserDirectory'
        value = self.userinisection.get(key)
        if value:
            PATH = isValidPath(value, wantDirectory=1)
            if PATH:
                try:
                    del self.UnimacroUserDirectory
                except AttributeError:
                    pass

                self.UnimacroUserDirectory = PATH
                return PATH
            print(f'invalid path for "{key}": "{value}"')

        try:
            del self.UnimacroUserDirectory
        except AttributeError:
            pass
        self.UnimacroUserDirectory = ''
        return ''

    def getUnimacroDirectory(self):
        """return the path to the Unimacro Directory
        
        This is the directory where the _control.py grammar is.

        When git cloned, relative to the Core directory, otherwise somewhere or in the site-packages (if pipped).
        
        This directory needs to be included in the load directories list of James' natlinkmain
        (August 2020)

        note that if using unimacro from a git clone area Unimacro will be in a /src subdirectory.
        when installed as  a package, that will not be the case.

        """
        #pylint:disable=C0415
        if not self.UnimacroDirectory is None:
            return self.UnimacroDirectory
        try:
            import unimacro
        except ImportError:
            print('Cannot find UnimacroDirectory, return ""')
            self.UnimacroDirectory = ""
            return ""

        self.UnimacroDirectory = unimacro.__path__[0]
        # print(f'UnimacroDirectory: {self.UnimacroDirectory}')
        controlGrammarFile = os.path.join(self.UnimacroDirectory, '_control.py')
        if not os.path.isfile(controlGrammarFile):
            print(f'Cannot find "_control.py" in UnimacroDirectory ({self.UnimacroDirectory}), return ""')
            self.UnimacroDirectory = ""
            return ""
        return self.UnimacroDirectory
        
    def getUnimacroGrammarsDirectory(self):
        """return the path to the directory where the ActiveGrammars of Unimacro are located.
        
        Expected in "ActiveGrammars" of the UnimacroUserDirectory
        (August 2020)

        """
        #pylint:disable=C0321
        if not self.UnimacroGrammarsDirectory is None:
            return self.UnimacroGrammarsDirectory
        
        uuDir = self.getUnimacroUserDirectory()
        if uuDir and path(uuDir).isdir():
            uuDir = path(uuDir)
            ugDir = uuDir/"ActiveGrammars"
            if not ugDir.exists():
                ugDir.mkdir()
            if ugDir.exists() and ugDir.isdir():
                ugFiles = [f for f in ugDir.listdir() if f.endswith(".py")]
                if not ugFiles:
                    print(f"UnimacroGrammarsDirectory: {ugDir} has no python grammar files (yet), please populate this directory with the Unimacro grammars you wish to use, and then toggle your microphone")
                
                try: del self.UnimacroGrammarsDirectory
                except AttributeError: pass
                self.UnimacroGrammarsDirectory= ugDir.normpath()
                return self.UnimacroGrammarsDirectory

        try: del self.UnimacroGrammarsDirectory
        except AttributeError: pass
        return self.UnimacroGrammarsDirectory

    # def getBaseDirectory(self):
    #     """return the path of the baseDirectory, MacroSystem
    #     """
    #     print("Warning: the BaseDirectory is obsolete with the python 3 version of Natlink")
    #     self.BaseDirectory = ''
    #     return self.BaseDirectory

    # def getCoreDirectory(self):
    #     """return the path of the coreDirectory, MacroSystem/core
    #     """
    #     return self.CoreDirectory

    def getNatlinkDirectory(self, coreDir=None):
        """return the path of the NatlinkDirectory
        
        if coreDir is given, check for symlink (only for developers)
        """
        if not coreDir:
            # should be preserved after first call:
            return self.NatlinkDirectory

        if str(coreDir).find("site-packages") > 0:
            cdPath = pathlib.WindowsPath(coreDir)
            if cdPath.is_symlink():
                cdResolved = cdPath.resolve()
                raise OSError(f'site-packages is symlink! {coreDir}, resolved: {cdResolved}, return {coreDir}\ndo not use --symlink with flit install')
            return os.path.normpath(str(cdPath))
        if coreDir.find('\\src\\') > 0:
            # opened from github clone, find site-packages directory
            spCoreDir = self.findInSitePackages(coreDir)
            return spCoreDir
        return None
    
    def findInSitePackages(self, cloneDir):
        """get corresponding directory in site-packages 
        
        This directory should be a symlink, otherwise the calling from the github clone directory is invalid.
        This is the situation when the package is "flit installed --symlink", so you can work in your clone and
        see the results happen. Only for developers
        
        If not found, return the input directory (cloneDir)
        
        """
        #pylint:disable=R0201
        cloneDir = str(cloneDir)
        if cloneDir.find('\\src\\') < 0:
            return cloneDir
            # raise IOErrorprint(f'This function should only be called when "\\src\\" is in the path')
        commonpart = cloneDir.split('\\src\\')[-1]
        print(f"sys.prefix {sys.prefix}  {__file__}")
        spDirectory = os.path.join(sys.prefix, 'Lib', 'site-packages', commonpart)
        spPath = pathlib.WindowsPath(spDirectory)
        if spPath.is_dir():
            if spPath.is_symlink():
                spResolve = spPath.resolve()
                if str(spResolve) == cloneDir:
                    # print(f'directory is symlink: {spPath} and resolves to {cloneDir} all right')
                    return str(spPath)
                print(f'directory is symlink: {spPath} but does NOT resolve to {cloneDir}, but to {spResolve}')
            else:
                print(f'directory is not a symlink: {spPath}')
        else:
            print('findInSitePackages, not a valid directory: {spPath}')
        return cloneDir        

    def getUserDirectory(self, force=None):
        """return the path to the Natlink User directory

        this one is not any more for Unimacro, but for User specified grammars, also Dragonfly

        should be set in configurenatlink, otherwise ignore...
        
        if force is True, ignore previous value...
        """
        if not self.NatlinkIsEnabled:
            return ''
        if force is True:
            pass
        elif not self.UserDirectory is None:
            return self.UserDirectory
        key = 'UserDirectory'
        value = self.userinisection.get(key)
        if value:
            PATH = isValidPath(value, wantDirectory=1)
            if PATH:
                self.UserDirectory = PATH
                return PATH
            print('invalid path for UserDirectory: "%s"'% value)
        self.UserDirectory = ''
        return ''

    def getVocolaUserDirectory(self):
        """return the VocolaUserDirectory
        """
        if not self.VocolaUserDirectory is None:
            return self.VocolaUserDirectory
        key = 'VocolaUserDirectory'

        value = self.userinisection.get(key)
        if value:
            PATH = isValidPath(value, wantDirectory=1)
            if PATH:
                self.VocolaUserDirectory = PATH
                return PATH
            print('invalid path for VocolaUserDirectory: "%s"'% value)
        self.VocolaUserDirectory = ''
        return ''

    def getVocolaDirectory(self):
        """return the VocolaDirectory (in the site-packages)
        """
        #pylint:disable=C0415
        if not self.VocolaDirectory is None:
            return self.VocolaDirectory
        try:
            import vocola2
        except ImportError:
            print('Cannot find VocolaDirectory, return ""')
            self.VocolaDirectory = ""
            return ""

        self.VocolaDirectory = vocola2.__path__[0]
        # print(f'VocolaDirectory: {self.VocolaDirectory}')
        controlGrammarFile = os.path.join(self.VocolaDirectory, '_vocola_main.py')
        if not os.path.isfile(controlGrammarFile):
            print(f'Cannot find "_vocola_main.py" in VocolaDirectory ({self.VocolaDirectory}), return ""')
            self.VocolaDirectory = ""
            return ""
        return self.VocolaDirectory


    def getVocolaGrammarsDirectory(self):
        """return the VocolaGrammarsDirectory, but only if Vocola is enabled
        
        If so, the subdirectory CompiledGrammars is created if not there yet.
        
        The path of this "CompiledGrammars" directory is returned.
        
        If Vocola is not enabled, or anything goes wrong, return ""
        
        """
        if not self.VocolaGrammarsDirectory is None:
            return self.VocolaGrammarsDirectory
        vUserDir = self.getVocolaUserDirectory()
        if not vUserDir:
            self.VocolaGrammarsDirectory = ''
            return ''
        vgDir = path(vUserDir)/"CompiledGrammars"
        if not vgDir.exists():
            vgDir.mkdir()
        if vgDir.exists() and vgDir.isdir():
            self.VocolaGrammarsDirectory= vgDir.normpath()
            return self.VocolaGrammarsDirectory
        ## not found:
        self.VocolaGrammarsDirectory = ""
        return ""

    def getAhkUserDir(self):
        """return the User directory of AutoHotkey
        """
        if not self.AhkUserDir is None:
            return self.AhkUserDir
        return self.getAhkUserDirFromIni()

    def getAhkUserDirFromIni(self):
        """get the AutoHotkey user directory if not yet cached
        """
        key = 'AhkUserDir'

        value = self.userinisection.get(key)
        if value:
            PATH = isValidPath(value, wantDirectory=1)
            if PATH:
                self.AhkUserDir = PATH
                return PATH
            print(f'invalid path for AhkUserDir: "{value}"')
        else:
            print(f'no path given for AhkUserDir: "{value}"')
        self.AhkUserDir = ''
        return ''

    def getAhkExeDir(self):
        """get the Exe directory of AutoHotkey
        """
        if not self.AhkExeDir is None:
            return self.AhkExeDir
        return self.getAhkExeDirFromIni()

    def getAhkExeDirFromIni(self):
        """get the Exe directory of AutoHotkey, if not yet cached
        """
        key = 'AhkExeDir'
        value = self.userinisection.get(key)
        if value:
            PATH = isValidPath(value, wantDirectory=1)
            if PATH:
                self.AhkExeDir = PATH
                return PATH
            print(f'invalid path for AhkExeDir: "{value}"')
        self.AhkExeDir = ''
        return ''

    def getUnimacroIniFilesEditor(self):
        """get the editor for Unimacro ini files
        """
        #pylint:disable=R0201
        key = 'UnimacroIniFilesEditor'
        value = self.userinisection.get(key)
        if not value:
            value = 'notepad'
        if self.UnimacroIsEnabled():
            return value
        return ''

    def _getLastUsedAcoustics(self, DNSuserDirectory):
        """get name of last used acoustics, must have DNSuserDirectory passed

        used by getLanguage, getBaseModel and getBaseTopic
        """
        #pylint:disable=R0201
        if not (DNSuserDirectory and os.path.isdir(DNSuserDirectory)):
            print('probably no speech profile on')
            return ''
        #dir = r'D:\projects'  # for testing (at bottom of file)
        optionsini = os.path.join(DNSuserDirectory, 'options.ini')
        if not os.path.isfile(optionsini):
            raise ValueError('not a valid options inifile found: |%s|, check your configuration'% optionsini)

        section = "Options"
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filepath=optionsini)
        keyname = "Last Used Acoustics"
        keyToModel = inisection.get(keyname)
        if not keyToModel:
            raise ValueError('no keyToModel value in options inifile found: (key: |%s|), check your configurationfile %s'%
                             (keyToModel, optionsini))
        return keyToModel

    def _getLastUsedTopic(self, DNSuserDirectory):
        """get name of last used topic,

        used by getBaseTopic
        """
        #pylint:disable=R0201
        # Dir = self.getDNSuserDirectory()
        # #dir = r'D:\projects'  # for testing (at bottom of file)
        if not os.path.isdir(DNSuserDirectory):
            print("_getLastUsedTopic, no DNSuserDirectory, probably no speech profile on")
            return ""
        optionsini = os.path.join(DNSuserDirectory, 'options.ini')
        if not os.path.isfile(optionsini):
            raise ValueError('not a valid options inifile found: |%s|, check your configuration'% optionsini)

        section = "Options"
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filepath=optionsini)
        keyname = "Last Used Topic"
        keyToModel = inisection.get(keyname)
        if not keyToModel:
            raise ValueError('no keyToModel value in options inifile found: (key: |%s|), check your configurationfile %s'%
                             (keyToModel, optionsini))
        return keyToModel


    # def getBaseModelBaseTopic(self, userTopic=None):
    #     """extract BaseModel and BaseTopic of current user
    #
    #     for historical reasons here,
    #     better use getBaseModel and getBaseTopic separate...
    #     """
    #     return self.getBaseModel(), self.getBaseTopic(userTopic=userTopic)

    def getBaseModel(self):
        """getting the base model, '' if error occurs
        getting obsolete in DPI15
        """
        Dir = self.getDNSuserDirectory()
        #dir = r'D:\projects'   # for testing, see bottom of file
        keyToModel = self._getLastUsedAcoustics(Dir)
        acousticini = os.path.join(Dir, 'acoustic.ini')
        section = "Base Acoustic"
        basesection = natlinkcorefunctions.InifileSection(section=section,
                                                         filepath=acousticini)
        BaseModel = basesection.get(keyToModel, "")
        # print 'getBaseModel: %s'% BaseModel
        return BaseModel

    def getBaseTopic(self):
        """getting the base topic, '' if error occurs

        with DPI15, the userTopic is given by getCurrentUser, so better use that one
        """
        Dir = self.getDNSuserDirectory()
        #dir = r'D:\projects'   # for testing, see bottom of file
        keyToModel = self._getLastUsedTopic(Dir)
        if not keyToModel:
            # print('Warning, no valid key to topic found')
            return ''
        topicsini = os.path.join(Dir, 'topics.ini')
        section = "Base Topic"
        topicsection = natlinkcorefunctions.InifileSection(section=section,
                                                         filepath=topicsini)
        BaseTopic = topicsection.get(keyToModel, "")
        # print 'getBaseTopic: %s'% BaseTopic
        return BaseTopic

    def getUserTopic(self):
        """return the userTopic.

        from DPI15 returned by changeCallback user, before identical to BaseTopic
        """
        try:
            return self.__class__.UserArgsDict['userTopic']
        except KeyError:
            return self.getBaseTopic()

    def getLanguage(self):
        """get language from UserArgsDict

        'tst' if not set, probably no speech profile on then

        """
        try:
            lang = self.__class__.UserArgsDict['language']
            return lang
        except KeyError:
            print('Serious error, natlinkstatus.getLanguage: no language found in UserArgsDict return "tst"')
            return 'tst'

    def getUserLanguage(self):
        """get userLanguage from UserArgsDict

        this is the descriptive language
        (with "dialect", like "UK English" or "Dutch")
        '' if not set, probably no speech profile on then
        """
        try:
            return self.__class__.UserArgsDict['userLanguage']
        except KeyError:
            return ''

    def getUserLanguageFromInifile(self):
        """get language, userLanguage info from acoustics ini file
        """
        Dir = self.getDNSuserDirectory()

        if not (Dir and os.path.isdir(Dir)):
            return ''
        keyToModel = self._getLastUsedAcoustics(Dir)
        acousticini = os.path.join(Dir, 'acoustic.ini')
        section = "Base Acoustic"
        if not os.path.isfile(acousticini):
            print('getLanguage: Warning, language of the user cannot be found, acoustic.ini not a file in directory %s'% dir)
            return 'yyy'
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filepath=acousticini)
        # print 'get data from section %s, key: %s, file: %s'% (section, keyToModel, acousticini)
        # print 'keys of inisection: %s'% inisection.keys()
        # print 'inisection:\n%s\n========'% repr(inisection)

        lang = inisection.get(keyToModel)
        if not lang:
            print('getLanguage: Warning, no model specification string for key %s found in "Base Acoustic" of inifile: %s'% (keyToModel, acousticini))
            print('You probably got the wrong encoding of the file, probably utf-8-BOM.')
            print('Please try to change the encoding to utf-8.')
            return 'zzz'
        lang =  lang.split("|")[0].strip()
        lang = lang.split("(")[0].strip()
        if not lang:
            print('getLanguage: Warning, no valid specification of language string (key: %s) found in "Base Acoustic" of inifile: %s'% (lang, acousticini))
            return 'www'
        return lang

    def getShiftKey(self):
        """return the shiftkey, for setting in natlinkmain when user language changes.

        used for self.playString in natlinkutils, for the dropping character bug. (dec 2015, QH).
        """
        language = self.getLanguage()
        try:
            return "{%s}"% shiftKeyDict[language]
        except KeyError:
            print('no shiftKey code provided for language: %s, take empty string.'% language)
            return ""

    # get different debug options for natlinkmain:
    def getDebugLoad(self):
        """gets value for extra info at loading time of natlinkmain"""
        key = 'NatlinkmainDebugLoad'
        value = self.userinisection.get(key, None)
        return value
    def getDebugCallback(self):
        """gets value for extra info at callback time of natlinkmain"""
        key = 'NatlinkmainDebugCallback'
        value = self.userinisection.get(key, None)
        return value

    # def getNatlinkDebug(self):
    #     """gets value for debug output in DNS logfile"""
    # obsolete (for a long time, 2015 and earlier)
    #     key = 'NatlinkDebug'
    #     value = self.userinisection.get(key, None)
    #     return value

    # def getIncludeUnimacroInPythonPath(self):
    #     """gets the value of alway include Unimacro directory in PythonPath"""
    #
    #     key = 'IncludeUnimacroInPythonPath'
    #     value = self.userinisection.get(key, None)
    #     return value

    # get additional options Vocola
    def getVocolaTakesLanguages(self):
        """gets and value for distinction of different languages in Vocola
        If Vocola is not enabled, this option will also return False
        """
        key = 'VocolaTakesLanguages'
        if self.VocolaIsEnabled():
            value = self.userinisection.get(key, None)
            return value
        return None
    
    def getVocolaTakesUnimacroActions(self):
        """gets and value for optional Vocola takes Unimacro actions
        If Vocola is not enabled, this option will also return False
        """
        key = 'VocolaTakesUnimacroActions'
        if self.VocolaIsEnabled():
            value = self.userinisection.get(key, None)
            return value
        return None
    
    def getInstallVersion(self):
        """return the version of natlinkcore
        """
        #pylint:disable=R0201, C0415
        from natlinkcore.__init__ import __version__
        return __version__
        
    def getNatlinkPydRegistered(self):
        """return True if NatlinkPyd is registered
        """
        value = self.userinisection.get('NatlinkDllRegistered', None)
        return bool(value)
  
    def getDNSName(self):
        """return NatSpeak for versions <= 11, and Dragon for versions >= 12
        """
        if self.getDNSVersion() <= 11:
            return 'NatSpeak'
        return "Dragon"

    def getNatlinkStatusDict(self, force=None):
        """return actual status in a dict
        
        force can be passed as True, when called from the config GUI program
        
        """
        D = {}

        for key in ['userName', 'DNSuserDirectory', 'language', 'DNSInstallDir',
                    'DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'PythonVersion',
                    'DNSName',
                    'UnimacroDirectory', 'UnimacroUserDirectory', 'UnimacroGrammarsDirectory',
                    'DebugLoad', 'DebugCallback',
                    'VocolaDirectory', 'VocolaUserDirectory', 'VocolaGrammarsDirectory',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'UnimacroIniFilesEditor',
                    'InstallVersion', 'NatlinkPydOrigin',
                    # 'IncludeUnimacroInPythonPath',
                    'AhkExeDir', 'AhkUserDir']:
##                    'BaseTopic', 'BaseModel']:
            if force:
                setattr(self, key, None)
            keyCap = key[0].upper() + key[1:]
            funcName = f'get{keyCap}'
            func = getattr(self, funcName)
            D[key] = func()
            # execstring = "D['%s'] = self.get%s()"% (key, keyCap)
            # exec(execstring)
        D['NatlinkDirectory'] = self.NatlinkDirectory
        D['UserDirectory'] = self.getUserDirectory(force=force)
        D['natlinkIsEnabled'] = self.NatlinkIsEnabled()
        D['vocolaIsEnabled'] = self.VocolaIsEnabled()

        D['unimacroIsEnabled'] = self.UnimacroIsEnabled()
        D['userIsEnabled'] = self.UserIsEnabled()
        # extra for information purposes:
        return D

    def getNatlinkStatusString(self):
        """get a long string with the status info
        """
        #pylint:disable=R0912
        L = []
        D = self.getNatlinkStatusDict()
        if D['userName']:
            L.append('user speech profile:')
            self.appendAndRemove(L, D, 'userName')
            self.appendAndRemove(L, D, 'DNSuserDirectory')
            self.appendAndRemove(L, D, 'language')
        else:
            del D['userName']
            del D['DNSuserDirectory']
        # Natlink::

        if D['natlinkIsEnabled']:
            self.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is enabled")
            key = 'NatlinkDirectory'
            self.appendAndRemove(L, D, key)
            key = 'InstallVersion'
            self.appendAndRemove(L, D, key)

            ## Vocola::
            if D['vocolaIsEnabled']:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is enabled")
                for key in ('VocolaUserDirectory', 'VocolaDirectory',
                            'VocolaGrammarsDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is disabled")
                for key in ('VocolaUserDirectory', 'VocolaDirectory',
                            'VocolaGrammarsDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    del D[key]

            ## Unimacro:
            if D['unimacroIsEnabled']:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is enabled")
                for key in ('UnimacroUserDirectory', 'UnimacroDirectory', 'UnimacroGrammarsDirectory'):
                    self.appendAndRemove(L, D, key)
                for key in ('UnimacroIniFilesEditor',):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is disabled")
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor',
                            'UnimacroDirectory', 'UnimacroGrammarsDirectory'):
                    del D[key]
            ##  UserDirectory:
            if D['userIsEnabled']:
                self.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are enabled")
                for key in ('UserDirectory',):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are disabled")
                del D['UserDirectory']

            ## remaining Natlink options:
            L.append('other Natlink info:')
            for key in ('DebugLoad', 'DebugCallback'):
                self.appendAndRemove(L, D, key)

        else:
            # Natlink disabled:
            if D['natlinkIsEnabled'] == 0:
                self.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is disabled")
            else:
                self.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is disabled (strange value: %s)"% D['natlinkIsEnabled'])
            # key = 'CoreDirectory'
            # self.appendAndRemove(L, D, key)
            for key in ['DebugLoad', 'DebugCallback',
                    'VocolaTakesLanguages',
                    'vocolaIsEnabled']:
                del D[key]
        # system:
        L.append('system information:')
        for key in ['DNSInstallDir',
                    'DNSIniDir', 'DNSVersion', 'DNSName',
                    'WindowsVersion', 'PythonVersion']:
            self.appendAndRemove(L, D, key)

        # forgotten???
        if D:
            L.append('remaining information:')
            for key in list(D.keys()):
                self.appendAndRemove(L, D, key)

        return '\n'.join(L)


    def appendAndRemove(self, List, Dict, Key, text=None):
        #pylint:disable=C0116, R0201

        if text:
            List.append(text)
        else:
            value = Dict[Key]
            if value in (None, ''):
                value = '-'
            List.append("\t%s\t%s"% (Key,value))
        del Dict[Key]
        
    def addToPath(self, directory):
        """add to the python path if not there yet
        """
        #pylint:disable=R0201
        Dir2 = path(directory)
        if not Dir2.isdir():
            print(f"natlinkstatus, addToPath, not an existing directory: {directory}")
            return
        Dir3 = Dir2.normpath()
        if Dir3 not in sys.path:
            print(f"natlinkstatus, addToPath: {Dir3}")
            sys.path.append(Dir3)

    def fatal_error(self, message, new_raise=None):
        """prints a fatal error when running this module"""
        ## Don't know how new_raise did its work... TODOQH
        #pylint:disable=W0613
        if not self.hadFatalErrors:
            
            print()
            print('natlinkstatus fails because of fatal error:')
            print()
            print(message)
            print()
            print('This can (hopefully) be solved by closing Dragon and then running the Natlink Config program (start_configurenatlink) with administrator rights.')
            print()
            self.__class__.hadFatalErrors = True
        # if new_raise:
        #     raise



def getFileDate(modName):
    """get date/time of file, 0 if non existent
    """
    #pylint:disable=C0321, R0201
    try: return os.stat(modName)[stat.ST_MTIME]
    except OSError: return 0        # file not found

# for splitting the env variables:
reEnv = re.compile('(%[A-Z_]+%)', re.I)

    #
    # # initialize recentEnv in natlinkcorefunctions (new 2018, 4.1uniform)
    # this is done from natlinkmain in changeCallback user:
    # natlinkstatus.AddExtendedEnvVariables()
    # natlinkstatus.AddNatLinkEnvironmentVariables(status=status)



def AddExtendedEnvVariables():
    """call to natlinkcorefunctions, called from natlinkmain at startup or user callback
    """
    natlinkcorefunctions.clearRecentEnv() # make a fresh start!
    natlinkcorefunctions.getAllFolderEnvironmentVariables(fillRecentEnv=1)


def AddNatlinkEnvironmentVariables(status=None):
    """make the special Natlink variables global in this module
    """
    if status is None:
        status = NatlinkStatus()
    D = status.getNatlinkStatusDict()
    natlinkVarsDict = {}
    for k, v in list(D.items()):
        if type(v) in (str, bytes) and os.path.isdir(v):
            k = k.upper()
            v = os.path.normpath(v)
            natlinkVarsDict[k] = v
            natlinkcorefunctions.addToRecentEnv(k, v)
    return natlinkVarsDict
    # print 'added to ExtendedEnvVariables:\n'
    # print '\n'.join(addedList)

def isValidPath(spec, wantFile=None, wantDirectory=None):
    """check existence of spec, allow for pseudosymbols.

    Return the normpath (expanded) if exists and optionally is a file or a directory

    ~ and %...% should be evaluated

    tested in testConfigfunctions.py
    """
    #pylint:disable=R0911
    if not spec:
        return None

    if os.path.exists(spec):
        spec2 = spec
    else:
        spec2 = natlinkcorefunctions.getExtendedEnv(spec)
    spec2 = os.path.normpath(spec2)
    if os.path.exists(spec2):
        if wantDirectory and wantFile:
            raise ValueError("isValidPath, only wantFile or wantDirectory may be specified, not both!")
        if wantFile:
            if  os.path.isfile(spec2):
                return spec2
            print('isValidPath, path exists, but is not a file: "%s"'% spec2)
            return None
        if wantDirectory:
            if os.path.isdir(spec2):
                return spec2
            print('isValidPath, path exists, but is not a directory: "%s"'% spec2)
            return None
        return spec2
    return None

    
def main():
    #pylint:disable=C0116
    status = NatlinkStatus()
    status.checkPydChanges()
    args = ('QEngels', 'C:\\Users\\Gebruiker\\AppData\\Local\\Nuance\\NS15\\Users\\QEngels\\current')

    status.setUserInfo(args)
    status.checkSysPath()

    print(status.getNatlinkStatusString())
    print('------ another check of the language:')
    lang = status.getLanguage()
    print('language: %s'% lang)

    # exapmles, for more tests in ...
    print('\n====\nexamples of expanding ~ and %...% variables:')
    _short = path("~/Quintijn")
    AddExtendedEnvVariables()
    addedListNatlinkVariables = AddNatlinkEnvironmentVariables()


    print('All "NATLINK" extended variables:')
    print('\n'.join(addedListNatlinkVariables))

    # voccompDir = natlinkcorefunctions.expandEnvVariableAtStart('%UNIMACRODIRECTORY%/vocola_compatibility')
    # print('%%UNIMACRODIRECTORY%%/vocola_compatibility is expanded to: %s'% voccompDir)
    # print('Is valid directory: %s'% os.path.isdir(voccompDir))
    print('\nExample: the pyd directory:')
    pydDir = natlinkcorefunctions.expandEnvVariableAtStart('%COREDIRECTORY%/pyd')
    print('%%COREDIRECTORY%%/pyd is expanded to: %s'% pydDir)
    print('Pyd directory is a valid directory: %s'% os.path.isdir(pydDir))

    # next things only testable when changing the dir in the functions above
    # and copying the ini files to this dir...
    # they normally run only when natspeak is on (and from NatSpeak)
    #print 'language (test): |%s|'% lang
    #print status.getBaseModelBaseTopic()
    print(status.getBaseModel())
    print(status.getBaseTopic())
 
if __name__ == "__main__":
    main()

