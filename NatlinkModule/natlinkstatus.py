#
# natlinkstatus.py
#   This module gives the status of Natlink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008/January 2018/extended for python3, Natlink5.0.1 Febr 2022
#
#pylint:disable=C0302, C0116, R0201, R0902, R0904, R0912, W0107
"""The following functions are provided in this module:

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
    removed, not needed any more

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
import sys
import stat
import platform
import configparser
import logging
from natlink import loader
from natlink import config

## setup a natlinkmain instance, for getting properties from the loader:
Logger = logging.getLogger('natlink')
Config = config.NatlinkConfig.from_first_found_file(loader.config_locations())
natlinkmain = loader.NatlinkMain(Logger, Config)
natlinkmain.setup_logger()
lang = natlinkmain.language

print(f'language from NatlinkMain: "{natlinkmain.language}"')

# adapt here
VocIniFile  = r"Vocola\Exec\vocola.ini"



lowestSupportedPythonVersion = 38

# utility functions:
## report function:
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print()
    print('natlinkconfigfunctions fails because of fatal error:')
    print()
    print(message)
    print()
    print('This can (hopefully) be solved by closing Dragon and then running the Natlink/Unimacro/Vocola Config program with administrator rights.')
    print()
    if new_raise:
        raise ValueError("fatal error in natlinkstatus.py")

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

thisDir, thisFile = os.path.split(__file__)


class NatlinkStatus:
    """this class holds the Natlink status functions

    so, can be called from natlinkmain.

    in the natlinkconfigfunctions it is subclassed for installation things
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    config = configparser.ConfigParser()

    ### from previous modules, needed or not...
    NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"

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

    userArgsDict = {}


    DNSVersion = None
    DNSIniDir = None
    CoreDirectory = None
    NatlinkDirectory = None
    UserDirectory = None
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

    @classmethod
    def __init__(cls, skipSpecialWarning=None):

        cls.skipSpecialWarning = skipSpecialWarning

        if cls.CoreDirectory is None:
            cls.CoreDirectory = thisDir

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

    @classmethod
    def setUserInfo(cls, args):
        """set username and userdirectory at change callback user
        
        args[0] = username
        args[1] = Current directory for user profile (in programdata/nuance etc)
                  extract for example userLanguage ('Nederlands') from acoustics.ini and options.ini

        if the three letter "language" ('enx', 'nld' etc) is not found there is an error in this module: 'languages' dict.
        English dialects are detected if the userLanguage is '.... English'.
        
        if there is no connection with natlink (no speech profile on, when debugging) language 'tst' is returned in getLanguage
        
        """
        # print("setUserInfo, args: %s"% repr(args))
        if len(args) < 2:
            print('UNEXPECTED ERROR: natlinkstatus, setUserInfo: length of args to small, should be at least 2: %s (%s)'% (len(args), repr(args)))
            return ''

        userName = args[0]
        cls.userArgsDict['userName'] = userName
        DNSuserDirectory = args[1]
        cls.userArgsDict['DNSuserDirectory'] = DNSuserDirectory
        try:
            return cls.userArgsDict['userLanguage']
        except KeyError:
            return ''
        userLanguage = cls.getUserLanguage()
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
        cls.userArgsDict['language'] = language
        cls.userArgsDict['userLanguage'] = userLanguage
        # cls.userArgsDict['userTopic'] = cls.getUserTopic() # will be the basetopic...
        print(f'setUserInfo: language: "{language}", userLanguage: "{userLanguage}"')

    @classmethod
    def clearUserInfo(cls):
        cls.userArgsDict.clear()

    @classmethod
    def getUserName(cls):
        try:
            return cls.userArgsDict['userName']
        except KeyError:
            return ''

    @classmethod
    def getDNSuserDirectory(cls):
        try:
            return cls.userArgsDict['DNSuserDirectory']
        except KeyError:
            return ''
        
    @staticmethod    
    def getWindowsVersion():
        """extract the windows version

        return 1 of the predefined values above, or just return what the system
        call returns
        """
        wVersion = platform.platform()
        if '-' in wVersion:
            return wVersion.split('-')[1]
        print('Warning, probably cannot find correct Windows Version... (%s)'% wVersion)
        return wVersion

    @classmethod
    def getPythonVersion(cls):
        """get the version of python

        Check if the version is supported on the "lower" side.
        
        length 2, without ".", so "38" etc.
        """
        version = sys.version[:3]
        version = version.replace(".", "")
        if int(version) < lowestSupportedPythonVersion:
            versionReadable = version[0] + "." + version[1]
            lspv = str(lowestSupportedPythonVersion)
            lspvReadable = lspv[0] + "." + lspv[1]
            raise ValueError('getPythonVersion, current version is: "%s".\nPython versions before "%s" are not any more supported by Natlink.\nIf you want to run NatLink on Python2.7, please use the older version of NatLink at SourceForge (https://sourceforge.net/projects/natlink/)'% (versionReadable, lspvReadable))
        return version

    @classmethod
    def getDNSIniDir(cls):
        """get the path (one above the users profile paths) where the INI files
        should be located

        """
        # first try if set (by configure dialog/natlinkinstallfunctions.py) if regkey is set:
        if cls.DNSIniDir is not None:
            return cls.DNSIniDir

        cls.DNSIniDir = loader.get_config_info_from_registry("dragonIniDir")
        return cls.DNSIniDir

    @classmethod
    def getDNSVersion(cls):
        """find the correct DNS version number (as an integer)

        2022: extract from the dragonIniDir setting in the registry, via loader function

        """
        if cls.DNSVersion is not None:
            return cls.DNSVersion
        dragonIniDir = loader.get_config_info_from_registry("dragonIniDir")
        if dragonIniDir:
            try:
                version = int(dragonIniDir[-2:])
            except ValueError:
                print('getDNSVersion, invalid version found "{dragonIniDir[-2:]}", return 0')
                version = 0
        else:
            print(f'Error, cannot get dragonIniDir from registry, unknown DNSVersion "{dragonIniDir}", return 0')
            version = 0
        cls.DNSVersion = version
        return cls.DNSVersion

    @classmethod
    def getNSSYSTEMIni(cls):
        inidir = cls.getDNSIniDir()
        if inidir:
            nssystemini = os.path.join(inidir, cls.NSSystemIni)
            if os.path.isfile(nssystemini):
                return os.path.normpath(nssystemini)
        print("Cannot find proper NSSystemIni file")
        print('Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)')
        return ''

    @classmethod
    def getNSAPPSIni(cls):
        inidir = cls.getDNSIniDir()
        if inidir:
            nsappsini = os.path.join(inidir, cls.NSAppsIni)
            if os.path.isfile(nsappsini):
                return os.path.normpath(nsappsini)
        print("Cannot find proper NSAppsIni file")
        print('Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)')
        return ''

    @classmethod
    def NatlinkIsEnabled(cls):
        """check if the coreDir of Natlink install is there
        
        If so (starting from release 5.0.0.), we assume Natlink is enabled.
        
        When you want to disable, remove your Natlink install from Program in Windows.
        """
        if cls.NatlinkIsEnabled is not None:
            return cls.NatlinkIsEnabled

        had_reg_key = loader.get_config_info_from_registry("coreDir")
        if had_reg_key:
            cls.NatlinkIsEnabled = True
        else:
            cls.NatlinkIsEnabled = True
        return cls.NatlinkIsEnabled            

    @classmethod
    def VocolaIsEnabled(cls):
        """Return True if Vocola is enables
        
        To be so,
        1. the VocolaUserDirectory (where the vocola command files (*.vcl) are located)
        should be defined in the user config file
        2. the VocolaDirectory should be found, and hold '_vocola_main.py'
        
        """
        isdir = os.path.isdir
        if not cls.NatlinkIsEnabled():
            cls.VocolaIsEnabled = False
            return False
        vocUserDir = cls.getVocolaUserDirectory()
        if vocUserDir and isdir(vocUserDir):
            vocDir = cls.getVocolaDirectory()
            vocGrammarsDir = cls.getVocolaGrammarsDirectory()
            if vocDir and isdir(vocDir) and vocGrammarsDir and isdir(vocGrammarsDir):
                return True
        return False

    @classmethod
    def UnimacroIsEnabled(cls):
        """UnimacroIsEnabled: see if UserDirectory is there and

        _control.py is in this directory
        """
        isdir = os.path.isdir
        if not cls.NatlinkIsEnabled():
            return False
        uuDir = cls.getUnimacroUserDirectory()
        if not uuDir:
            return False
        uDir = cls.getUnimacroDirectory()
        if not uDir:
            # print('no valid UnimacroDirectory, Unimacro is disabled')
            return False
        if uDir and isdir(uDir):
            files = os.listdir(uDir)
            if not '_control.py' in files:
                return  False # _control.py should be in Unimacro directory
        ugDir = cls.getUnimacroGrammarsDirectory()
        if ugDir and isdir(ugDir):
            return True  # Unimacro is enabled...            
        return False                

    @classmethod
    def UserIsEnabled(cls):
        if not cls.NatlinkIsEnabled():
            return False
        userDir = cls.getUserDirectory()
        if userDir:
            return True
        return False

    @classmethod
    def getUnimacroUserDirectory(cls):
        isdir = os.path.isdir
        if cls.UnimacroUserDirectory is not None:
            return cls.UnimacroUserDirectory
        key = 'UnimacroUserDirectory'
        value = cls.getconfigsetting(key)
        if value and isdir(value):
            cls.UnimacroUserDirectory = value
            return value
        print(f'invalid directory for "{key}": "{value}%s"')
        cls.UnimacroUserDirectory = ''
        return ''
    
    @classmethod
    def getUnimacroDirectory(cls):
        """return the path to the Unimacro Directory
        
        This is the directory where the _control.py grammar is.

        When git cloned, relative to the Core directory, otherwise somewhere or in the site-packages (if pipped).
        
        This directory needs to be included in the load directories list of James' natlinkmain
        (August 2020)

        note that if using unimacro from a git clone area Unimacro will be in a /src subdirectory.
        when installed as  a package, that will not be the case.

        """
        join, isdir, isfile, normpath = os.path.join, os.path.isdir, os.path.isfile, os.path.normpath
        if cls.UnimacroDirectory is not None:
            return cls.UnimacroDirectory
        uDir = join(sys.prefix, "lib", "site-packages", "unimacro")
        if isdir(uDir):
            uFile = "_control.py"
            controlGrammar = join(uDir, uFile)
            if isfile(controlGrammar):
                cls.UnimacroDirectory = normpath(uDir)
                return cls.UnimacroDirectory
            print(f'UnimacroDirectory found: "{uDir}", but no valid file: "{uFile}", return ""')
            return ""
        print('UnimacroDirectory not found in "lib/site-packages/unimacro", return ""')
        cls.UnimacroDirectory = ""
        return ""
        
    @classmethod
    def getUnimacroGrammarsDirectory(cls):
        """return the path to the directory where the ActiveGrammars of Unimacro are located.
        
        Expected in "ActiveGrammars" of the UnimacroUserDirectory
        (August 2020)

        """
        isdir, join, normpath = os.path.isdir, os.path.join, os.path.normpath
        if cls.UnimacroGrammarsDirectory is not None:
            return cls.UnimacroGrammarsDirectory
        
        uuDir = cls.getUnimacroUserDirectory()
        if uuDir and isdir(uuDir):
            ugDir = join(uuDir, "ActiveGrammars")
            if not isdir(ugDir):
                os.mkdir(ugDir)
            if isdir(ugDir):
                ugFiles = [f for f in ugDir.listdir() if f.endswith(".py")]
                if not ugFiles:
                    print(f"UnimacroGrammarsDirectory: {ugDir} has no python grammar files (yet), please populate this directory with the Unimacro grammars you wish to use, and then toggle your microphone")
                
                try:
                    del cls.UnimacroGrammarsDirectory
                except AttributeError:
                    pass
                cls.UnimacroGrammarsDirectory= normpath(ugDir)
                return cls.UnimacroGrammarsDirectory

        try:
            del cls.UnimacroGrammarsDirectory
        except AttributeError:
            pass
        cls.UnimacroGrammarsDirectory= ""   # meaning is not set, for future calls.
        return cls.UnimacroGrammarsDirectory

    @classmethod
    def getCoreDirectory(cls):
        """return the path of the coreDirectory, MacroSystem/core
        """
        return cls.CoreDirectory

    @classmethod
    def getNatlinkDirectory(cls):
        """return the path of the NatlinkDirectory, two above the coreDirectory
        """
        return cls.NatlinkDirectory

    @classmethod
    def getUserDirectory(cls):
        """return the path to the Natlink User directory

        this one is not any more for Unimacro, but for User specified grammars, also Dragonfly

        should be set in configurenatlink, otherwise ignore...
        """
        isdir = os.path.isdir
        if not cls.NatlinkIsEnabled:
            return ""
        if not cls.UserDirectory is None:
            return cls.UserDirectory
        key = 'UserDirectory'
        value = cls.getconfigsetting(key)
        if value and isdir(value):
            cls.UserDirectory = value
            return cls.UserDirectory
        print('invalid path for UserDirectory: "%s"'% value)
        cls.UserDirectory = ''
        return ''

    @classmethod
    def getVocolaUserDirectory(cls):
        isdir = os.path.isdir
        if cls.VocolaUserDirectory is not None:
            return cls.VocolaUserDirectory
        key = 'VocolaUserDirectory'

        value = cls.getconfigsetting(key)
        if value and isdir(value):
            cls.VocolaUserDirectory = value
            return value
        print(f'invalid path for VocolaUserDirectory: "{value}"')
        cls.VocolaUserDirectory = ''
        return ''

    @classmethod
    def getVocolaDirectory(cls):
        isdir, isfile, join, normpath = os.path.isdir, os.path.isfile, os.path.join, os.path.normpath
        if cls.VocolaDirectory is not None:
            return cls.VocolaDirectory

        ## try in site-packages:
        vocDir = join(sys.prefix, "lib", "site-packages", "vocola2")
        if not isdir(vocDir):
            print('VocolaDirectory not found in "lib/site-packages/vocola2", return ""')
            cls.VocolaDirectory = ''
            return ''
        vocFile = "_vocola_main.py"
        checkGrammar = join(vocDir, vocFile)
        if not isfile(checkGrammar):
            print(f'VocolaDirectory found in "{vocDir}", but no file "{vocFile}" found, return ""')
            cls.VocolaDirectory = ''
            return ''

        cls.VocolaDirectory = normpath(vocDir)
        return cls.VocolaDirectory

    @classmethod
    def getVocolaGrammarsDirectory(cls):
        """return the VocolaGrammarsDirectory, but only if Vocola is enabled
        
        If so, the subdirectory CompiledGrammars is created if not there yet.
        
        The path of this "CompiledGrammars" directory is returned.
        
        If Vocola is not enabled, or anything goes wrong, return ""
        
        """
        isdir, normpath = os.path.isdir, os.path.normpath
        if cls.VocolaGrammarsDirectory is not None:
            return cls.VocolaGrammarsDirectory

        vUserDir = cls.getVocolaUserDirectory()
        if not vUserDir:
            cls.VocolaGrammarsDirectory = ''
            return ''
        vgDir = isdir(vUserDir, "CompiledGrammars")
        if not isdir(vgDir):
            os.mkdir(vgDir)
        if not isdir(vgDir):
            print('getVocolaGrammarsDirectory, could not create directory "{vgdir}"')
            cls.VocolaGrammarsDirectory = ''
            return ''
        
        cls.VocolaGrammarsDirectory = normpath(vgDir)
        return cls.VocolaGrammarsDirectory

    @classmethod
    def getAhkUserDir(cls):
        if not cls.AhkUserDir is None:
            return cls.AhkUserDir
        return cls.getAhkUserDirFromIni()

    @classmethod
    def getAhkUserDirFromIni(cls):
        isdir = os.path.isdir
        key = 'AhkUserDir'

        value = cls.getconfigsetting(key)
        if value and isdir(value):
            cls.AhkUserDir = value
            return value
        print('invalid path for AhkUserDir: "{value}"')
        cls.AhkUserDir = ''
        return ''
    
    @classmethod
    def getAhkExeDir(cls):
        if not cls.AhkExeDir is None:
            return cls.AhkExeDir
        return cls.getAhkExeDirFromIni()

    @classmethod
    def getAhkExeDirFromIni(cls):
        isdir = os.path.isdir
        key = 'AhkExeDir'
        value = cls.getconfigsetting(key)
        if value and isdir(value):
            cls.AhkExeDir = value
            return value
        print(f'invalid path for AhkExeDir: "{value}"')
        cls.AhkExeDir = ''
        return ''

    @classmethod
    def getUnimacroIniFilesEditor(cls):
        key = 'UnimacroIniFilesEditor'
        value = cls.getconfigsetting(key)
        if not value:
            value = 'notepad'
        if cls.UnimacroIsEnabled():
            return value
        return ''

    @classmethod
    def getLanguage(cls):
        """get language, userLanguage info from acoustics ini file
        """
        value = natlinkmain.language
        return value

    @classmethod
    def getShiftKey(cls):
        """return the shiftkey, for setting in natlinkmain when user language changes.

        used for cls.playString in natlinkutils, for the dropping character bug. (dec 2015, QH).
        """
        ## TODO: must be windows language...
        language = cls.getLanguage()
        try:
            return "{%s}"% shiftKeyDict[language]
        except KeyError:
            print('no shiftKey code provided for language: %s, take empty string.'% language)
            return ""

    # get additional options Vocola
    @classmethod
    def getVocolaTakesLanguages(cls):
        """gets and value for distinction of different languages in Vocola
        If Vocola is not enabled, this option will also return False
        """
        key = 'VocolaTakesLanguages'
        if cls.VocolaIsEnabled():
            value = cls.getconfigsetting(key, None)
            return value
        return False

    @classmethod
    def getVocolaTakesUnimacroActions(cls):
        """gets and value for optional Vocola takes Unimacro actions
        If Vocola is not enabled, this option will also return False
        """
        key = 'VocolaTakesUnimacroActions'
        if cls.VocolaIsEnabled():
            value = cls.getconfigsetting(key, None)
            return value
        return False

    @classmethod
    def getInstallVersion(cls):
        version = loader.get_config_info_from_registry("version")
        return version
    
    @staticmethod  
    def getDNSName():
        """return NatSpeak for versions <= 11, and Dragon for versions >= 12
        """
        return "Dragon"

    @classmethod
    def getNatlinkStatusDict(cls, force=None):
        """return actual status in a dict
        
        force can be passed as True, when called from the config GUI program
        
        """
        D = {}

        for key in ['userName', 'DNSuserDirectory', 
                    'DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'PythonVersion',
                    'DNSName',
                    'UnimacroDirectory', 'UnimacroUserDirectory', 'UnimacroGrammarsDirectory',
                    'VocolaDirectory', 'VocolaUserDirectory', 'VocolaGrammarsDirectory',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'UnimacroIniFilesEditor',
                    'InstallVersion',
                    # 'IncludeUnimacroInPythonPath',
                    'AhkExeDir', 'AhkUserDir']:
##                    'BaseTopic', 'BaseModel']:
            if force:
                setattr(cls, key, None)
            keyCap = key[0].upper() + key[1:]
            funcName = f'get{keyCap}'
            func = getattr(cls, funcName)
            D[key] = func()
            # execstring = "D['%s'] = cls.get%s()"% (key, keyCap)
            # exec(execstring)
        D['CoreDirectory'] = cls.CoreDirectory
        D['UserDirectory'] = cls.getUserDirectory()
        D['natlinkIsEnabled'] = cls.NatlinkIsEnabled()
        D['vocolaIsEnabled'] = cls.VocolaIsEnabled()

        D['unimacroIsEnabled'] = cls.UnimacroIsEnabled()
        D['userIsEnabled'] = cls.UserIsEnabled()
        # extra for information purposes:
        D['NatlinkDirectory'] = cls.NatlinkDirectory
        return D

    @classmethod
    def getNatlinkStatusString(cls):
        L = []
        D = cls.getNatlinkStatusDict()
        if D['userName']:
            L.append('user speech profile:')
            cls.appendAndRemove(L, D, 'userName')
            cls.appendAndRemove(L, D, 'DNSuserDirectory')
        else:
            del D['userName']
            del D['DNSuserDirectory']
        # Natlink::

        if D['natlinkIsEnabled']:
            cls.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is enabled")
            key = 'CoreDirectory'
            cls.appendAndRemove(L, D, key)
            key = 'InstallVersion'
            cls.appendAndRemove(L, D, key)

            ## Vocola::
            if D['vocolaIsEnabled']:
                cls.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is enabled")
                for key in ('BaseDirectory', 'VocolaUserDirectory', 'VocolaDirectory',
                            'VocolaGrammarsDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    cls.appendAndRemove(L, D, key)
            else:
                cls.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is disabled")
                for key in ('VocolaUserDirectory', 'VocolaDirectory',
                            'VocolaGrammarsDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    del D[key]

            ## Unimacro:
            if D['unimacroIsEnabled']:
                cls.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is enabled")
                for key in ('UnimacroUserDirectory', 'UnimacroDirectory', 'UnimacroGrammarsDirectory'):
                    cls.appendAndRemove(L, D, key)
                for key in ('UnimacroIniFilesEditor',):
                    cls.appendAndRemove(L, D, key)
            else:
                cls.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is disabled")
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor',
                            'UnimacroDirectory', 'UnimacroGrammarsDirectory'):
                    del D[key]
            ##  UserDirectory:
            if D['userIsEnabled']:
                cls.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are enabled")
                for key in ('UserDirectory',):
                    cls.appendAndRemove(L, D, key)
            else:
                cls.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are disabled")
                del D['UserDirectory']

            ## remaining Natlink options:
            L.append('other Natlink info:')

        else:
            # Natlink disabled:
            if D['natlinkIsEnabled'] == 0:
                cls.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is disabled")
            else:
                cls.appendAndRemove(L, D, 'natlinkIsEnabled', "---Natlink is disabled (strange value: %s)"% D['natlinkIsEnabled'])
            key = 'CoreDirectory'
            cls.appendAndRemove(L, D, key)
            for key in ['DebugLoad', 'DebugCallback',
                    'VocolaTakesLanguages',
                    'vocolaIsEnabled']:
                del D[key]
        # system:
        L.append('system information:')
        for key in ['DNSIniDir', 'DNSVersion', 'DNSName',
                    'WindowsVersion', 'PythonVersion']:
            cls.appendAndRemove(L, D, key)

        # forgotten???
        if D:
            L.append('remaining information:')
            for key in list(D.keys()):
                cls.appendAndRemove(L, D, key)

        return '\n'.join(L)

    @classmethod
    def appendAndRemove(cls, List, Dict, Key, text=None):
        if text:
            List.append(text)
        else:
            value = Dict[Key]
            if value is None or value == '':
                value = '-'
            List.append("\t%s\t%s"% (Key,value))
        del Dict[Key]
        
    # def addToPath(self, directory):
    #     """add to the python path if not there yet
    #     """
    #     isdir = os.path.isdir
    #     Dir2 = isdir(directory)
    #     if not Dir2.isdir():
    #         print(f"natlinkstatus, addToPath, not an existing directory: {directory}")
    #         return
    #     Dir3 = Dir2.normpath()
    #     if Dir3 not in sys.path:
    #         print(f"natlinkstatus, addToPath: {Dir3}")
    #         sys.path.append(Dir3)

    @classmethod
    def getconfigsetting(cls, key, inifilepath=None, section=None):
        """get from natlink.ini file
        
        default section = "directories"
        """
        if inifilepath is None:
            # take default natlink.ini from  natlink config module:
            Config = config.NatlinkConfig.from_first_found_file(loader.config_locations())
            inifilepath = Config.config_path
            ini = configparser.ConfigParser()
            ini.read(inifilepath)
        else:
            # take ini file from filename:
            ini = configparser.ConfigParser()
            ini.read(inifilepath)
        section = section or "directories"
        value = ini.get(section, key, fallback=None)
        
        if value is None:
            print(f'warning, no value returned from ini file "{inifilepath}", section "{section}", key: "{key}"...')
        
        return value

def getFileDate(modName):
    #pylint:disable=C0321
    try: return os.stat(modName)[stat.ST_MTIME]
    except OSError: return 0        # file not found

def main():
    print(f"{sys.argv[0]}  __name__ :  {__name__}")
    status = NatlinkStatus()

    # next things only testable when changing the dir in the functions above
    print(status.getLanguage())


    print(status.getNatlinkStatusString())
    lang = status.getLanguage()
    print('language: %s'% lang)

    # exapmles, for more tests in ...
    # print('\n====\nexamples of expanding ~ and %...% variables:')
    # short = path("~/Quintijn")
    # AddExtendedEnvVariables()
    # addedListNatlinkVariables = AddNatlinkEnvironmentVariables()
    # print('All "NATLINK" extended variables:')
    # print('\n'.join(addedListNatlinkVariables))



 
if __name__ == "__main__":
    main()
    pass
