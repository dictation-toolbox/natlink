#
# natlinkstatus.py
#   This module gives the status of Natlink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008/January 2018/extended for python3, Natlink5.0.1 Febr 2022
#
#pylint:disable=C0302, C0116, R0201, R0902, R0904, R0912, W0107, E1101
"""The following functions are provided in this module:

The functions below are put into the class NatlinkStatus.

The functions below should not change anything in settings, only  get information.

getDNSInstallDir:
    removed, not needed any more

getDNSIniDir:
    returns the directory where the NatSpeak INI files are located,
    notably nssystem.ini and nsapps.ini. Got from loader.

getDNSVersion:
    returns the in the version number of NatSpeak, as an integer. So ..., 13, 15, ...
    no distinction is made here between different subversions.
    got indirectly from loader

getWindowsVersion:
    see source below

get_language: 
    returns the 3 letter code of the language of the speech profile that
    is open: 'enx', 'nld', "fra", "deu", "ita", "esp"

    get it from loader (property), is updated when user profile changes (on_change_callback)
    returns 'enx' when Dragon is not running.
    
get_profile, get_user:
    returns the directory of the current user profile information and
    returns the name of the current user
    This information is collected from natlink.getCurrentUser(), or from
    the args in on_change_callback, with type == 'user'

get_load_on_begin_utterance and set_load_on_begin_utterance:
    returns value of this property of the natlinkmain (loader) instance.
    True or False, or a (small) positive int, decreasing each utterance.
    
    or
    explicitly set this property.
    
getPythonVersion:
    return two character version, so without the dot! eg '38',
    
    Note, no indication of 32 bit version, so no '38-32'


getUserDirectory: get the Natlink user directory, 
    Especially Dragonfly users will use this directory for putting their grammar files in.
    Also users that have their own custom grammar files can use this user directory

getUnimacroDirectory: get the directory where the Unimacro system is.
    When git cloned, relative to the Core directory, otherwise somewhere or in the site-packages (if pipped). This grammar will (and should) hold the _control.py grammar
    and needs to be included in the load directories list of James' natlinkmain

getUnimacroGrammarsDirectory: get the directory, where the user can put his Unimacro grammars. This directory will be
    located in the `ActiveGrammars` subdirectory of the `~/.unimacro' or `%NATLINK_USERDIR%/.unimacro`).

getUnimacroUserDirectory: get the directory of Unimacro INI files, if not return '' or
      the Unimacro user directory

getVocolaDirectory: get the directory where the Vocola system is. When cloned from git, in Vocola, relative to
      the Core directory. Otherwise (when pipped) in some site-packages directory. It holds (and should hold) the
      grammar _vocola_main.py.

getVocolaUserDirectory: get the directory of Vocola User files, if not return ''
    (if run from natlinkconfigfunctions use getVocolaDirectoryFromIni, which checks inifile
     at each call...)

getVocolaGrammarsDirectory: get the directory, where the compiled Vocola grammars are/will be.
    This will be the `CompiledGrammars` subdirectory of `~/.vocolaGrammars` or
    `%NATLINK_USERDIR%/.vocola`.

getVocolaTakesLanguages: additional settings for Vocola

new 2014/2022
getDNSName: return "NatSpeak" for versions <= 11 and "Dragon" for 12 (on) (obsolete in 2022)
getAhkExeDir: return the directory where AutoHotkey is found (only needed when not in default)
getAhkUserDir: return User Directory of AutoHotkey, not needed when it is in default.
get_language and other properties, see above.

"""
import os
import sys
import stat
import platform
import logging
from typing import Any
from pathlib import Path

from natlink import _natlink_core as natlink

from natlinkcore import loader
from natlinkcore import config
from natlinkcore import singleton

## setup a natlinkmain instance, for getting properties from the loader:
## note, when loading the natlink module via Dragon, you can call simply:
# # # natlinkmain = loader.NatlinkMain()

## setting up Logger and Config is needed, when running this for test:
Logger = logging.getLogger('natlink')
Config = config.NatlinkConfig.from_first_found_file(loader.config_locations())
natlinkmain = loader.NatlinkMain(Logger, Config)

# the possible languages (for get_language), now in loader

shiftKeyDict = {"nld": "Shift",
                "enx": 'shift',
                "fra": "maj",
                "deu": "umschalt",
                "ita": "maiusc",
                "esp": "may\xfas"}

thisDir, thisFile = os.path.split(__file__)

class NatlinkStatus(metaclass=singleton.Singleton):
    """this class holds the Natlink status functions.
    
    This class is a Singleton, which means that all instances are the same object.

    Some information is retrieved from the loader, the natlinkmain (Singleton) instance.
    
    In natlinkconfigfunctions.py, NatlinkStatus is subclassed for configuration purposes.
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    known_directory_options = ['userdirectory', 'dragonflyuserdirectory',
                               'unimacrodirectory', 'unimacrogrammarsdirectory',
                               'vocoladirectory', 'vocolagrammarsdirectory']

    def __init__(self):
        """initialise all instance variables, in this singleton class, hoeinstance
        """
        self.natlinkmain = natlinkmain  # global
        self.DNSVersion = None
        self.DNSIniDir = None
        self.NatlinkDirectory = None    # CoreDirectory and NatlinkDirectory same...
        self.CoreDirectory = None
        self.UserDirectory = None
        ## Unimacro:
        self.UnimacroDirectory = None
        self.UnimacroUserDirectory = None
        self.UnimacroGrammarsDirectory = None
        ## Vocola:
        self.VocolaUserDirectory = None
        self.VocolaDirectory = None
        self.VocolaGrammarsDirectory = None
        ## AutoHotkey:
        self.AhkUserDir = None
        self.AhkExeDir = None

        if self.NatlinkDirectory is None:
            self.NatlinkDirectory = thisDir
            self.CoreDirectory = thisDir   # maybe becoming obsolete

    def refresh(self):
        """rerun the __init__, refreshing all variables
        
        This should be done only from the natlinkconfigfunctions.py, in the configure phase of Natlink
        """
        self.__init__()

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
    
    def getPythonVersion(self):
        """get the version of python

        Check if the version is supported on the "lower" side.
        
        length 2, without ".", so "38" etc.
        """
        version = sys.version[:3]
        version = version.replace(".", "")
        return version

    @property
    def user(self) -> str:
        return  self.natlinkmain.user
    @property
    def profile(self) -> str:
        return  self.natlinkmain.profile
    @property
    def language(self) -> str:
        return  self.natlinkmain.language

    @property
    def load_on_begin_utterance(self) -> Any:
        """inspect current value of this loader setting
        """
        return  self.natlinkmain.load_on_begin_utterance
    
    def get_user(self):
        return  self.user

    def get_profile(self):
        return  self.profile

    def get_language(self):
        return  self.language
    
    def get_load_on_begin_utterance(self):
        return self.load_on_begin_utterance
    
    def getDNSIniDir(self):
        """get the path (one above the users profile paths) where the INI files
        should be located

        """
        # first try if set (by configure dialog/natlinkinstallfunctions.py) if regkey is set:
        if self.DNSIniDir is not None:
            return self.DNSIniDir

        self.DNSIniDir = loader.get_config_info_from_registry("dragonIniDir")
        return self.DNSIniDir

    
    def getDNSVersion(self):
        """find the correct DNS version number (as an integer)

        2022: extract from the dragonIniDir setting in the registry, via loader function

        """
        if self.DNSVersion is not None:
            return self.DNSVersion
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
        self.DNSVersion = version
        return self.DNSVersion
    
    def VocolaIsEnabled(self):
        """Return True if Vocola is enables
        
        To be so,
        1. the VocolaUserDirectory (where the vocola command files (.vcl) are located)
        should be defined in the user config file
        2. the VocolaDirectory should be found, and hold '_vocola_main.py'
        
        """
        isdir = os.path.isdir
        vocUserDir = self.getVocolaUserDirectory()
        if vocUserDir and isdir(vocUserDir):
            vocDir = self.getVocolaDirectory()
            vocGrammarsDir = self.getVocolaGrammarsDirectory()
            if vocDir and isdir(vocDir) and vocGrammarsDir and isdir(vocGrammarsDir):
                return True
        return False

    
    def UnimacroIsEnabled(self):
        """UnimacroIsEnabled: see if UnimacroDirectory and UnimacroUserDirectory are there

        _control.py should be in the UnimacroDirectory. 
        """
        isdir = os.path.isdir
        uDir = self.getUnimacroDirectory()
        if not uDir:
            # print('no valid UnimacroDirectory, Unimacro is disabled')
            return False
        if isdir(uDir):
            files = os.listdir(uDir)
            if not '_control.py' in files:
                print(f'UnimacroDirectory is present ({uDir}), but not "_control.py" grammar file')
                return  False # _control.py should be in Unimacro directory

        uuDir = self.getUnimacroUserDirectory()
        if not uuDir:
            return False
        ugDir = self.getUnimacroGrammarsDirectory()
        if not (ugDir and isdir(ugDir)):
            print(f'UnimacroGrammarsDirectory ({ugDir}) not present, please create')
            return False
        return True            

    
    def UserIsEnabled(self):
        userDir = self.getUserDirectory()
        if userDir:
            return True
        return False

    def getNatlinkIni(self):
        """return the path of the natlink.ini file
        """
        path = loader.config_locations()[0]
        if not os.path.isfile(path):
            raise OSError(f'getNatlinkIni: not a valid file: "{path}"')
        return path
    
    def getNatlinkUserDirectory(self):
        """get the directory where "natlink.ini" should be stored
        
        This must be a local directory, default `~`, but can be changed by
        setting `NATLINK_USERDIR` to for example `~/Documents`.
        
        Other directories that are created and checked by packages, and should be local, can be
        stored here, for example `VocolaGrammarsDirectory` (VocolaGrammars) and
        `UnimacroGrammarsDirectory` (UnimacroGrammars).
        """
        natlink_ini_path = Path(self.getNatlinkIni())
        natlink_user_dir = natlink_ini_path.parent
        return str(natlink_user_dir)
    
    def getUnimacroUserDirectory(self):
        isdir, abspath = os.path.isdir, os.path.abspath
        if self.UnimacroUserDirectory is not None:
            return self.UnimacroUserDirectory
        key = 'unimacrouserdirectory'
        value =  self.natlinkmain.getconfigsetting(section="unimacro", option=key)
        if not value:
            self.UnimacroUserDirectory = ''
            return ''
        if isdir(value):
            self.UnimacroUserDirectory = value
            return abspath(value)
        # for future use:
        expanded = loader.expand_path(value)
        if expanded and isdir(expanded):
            self.UnimacroUserDirectory = expanded
            return abspath(expanded)
        # nothing or wrong directory:
        print(f'invalid path for UnimacroUserDirectory: "{value}", return ""')

        self.UnimacroUserDirectory = ''
        return ''
    
    
    def getUnimacroDirectory(self):
        """return the path to the UnimacroDirectory
        
        This is the directory where the _control.py grammar is, and
        is normally got via `pip install unimacro`

        """
        # When git cloned, relative to the Core directory, otherwise somewhere or in the site-packages (if pipped).
        join, isdir, isfile, abspath = os.path.join, os.path.isdir, os.path.isfile, os.path.abspath
        if self.UnimacroDirectory is not None:
            return self.UnimacroDirectory
        uDir = join(sys.prefix, "lib", "site-packages", "unimacro")
        if isdir(uDir):
            uFile = "_control.py"
            controlGrammar = join(uDir, uFile)
            if isfile(controlGrammar):
                self.UnimacroDirectory = abspath(uDir)
                return self.UnimacroDirectory
            # print(f'UnimacroDirectory found: "{uDir}", but no valid file: "{uFile}", return ""')
            return ""
        # print('UnimacroDirectory not found in "lib/site-packages/unimacro", return ""')
        self.UnimacroDirectory = ""
        return ""
        
    
    def getUnimacroGrammarsDirectory(self):
        """return the path to the directory where the ActiveGrammars of Unimacro are located.
        
        Expected in "UnimacroGrammars" of the natlink user directory
        (May 2022)

        """
        if self.UnimacroGrammarsDirectory is not None:
            return self.UnimacroGrammarsDirectory
        
        natlink_user_dir = self.getNatlinkUserDirectory()
        
        um_grammars_dir = Path(natlink_user_dir)/'UnimacroGrammars'
        if not um_grammars_dir.is_dir():
            um_grammars_dir.mkdir()
        um_grammars_dir = str(um_grammars_dir)
        self.UnimacroGrammarsDirectory = um_grammars_dir

        return um_grammars_dir
    
    def getNatlinkDirectory(self):
        """return the path of the NatlinkDirectory
        """
        return self.NatlinkDirectory

    def getCoreDirectory(self):
        """return the path of the coreDirectory, same as NatlinkDirectory, obsolete
        """
        return self.CoreDirectory
    
    def getUserDirectory(self):
        """return the path to the Natlink User directory

        this one is not any more for Unimacro, but for User specified grammars, also Dragonfly

        should be set in configurenatlink, otherwise ignore...
        """
        isdir, abspath = os.path.isdir, os.path.abspath
        if not self.UserDirectory is None:
            return self.UserDirectory
        key = 'UserDirectory'
        value =  self.natlinkmain.getconfigsetting(section='directories', option=key)
        if value and isdir(value):
            self.UserDirectory = abspath(value)
            return self.UserDirectory
        expanded = config.expand_path(value)
        if expanded and isdir(expanded):
            self.UserDirectory = abspath(expanded)
            return self.UserDirectory
            
        print('invalid path for UserDirectory: "%s"'% value)
        self.UserDirectory = ''
        return ''

    
    
    def getVocolaUserDirectory(self):

        isdir, abspath = os.path.isdir, os.path.abspath
        if self.VocolaUserDirectory is not None:
            return self.VocolaUserDirectory
        key = 'vocolauserdirectory'
        section = 'vocola'
        value =  self.natlinkmain.getconfigsetting(section=section, option=key)
        if not value:
            self.VocolaUserDirectory = ''
            return ''

        if isdir(value):
            self.VocolaUserDirectory = abspath(value)
            return value
        # for future use:
        expanded = config.expand_path(value)
        if expanded and isdir(expanded):
            self.VocolaUserDirectory = abspath(expanded)
            return self.VocolaUserDirectory

        print(f'invalid path for VocolaUserDirectory: "{value}"')
        self.VocolaUserDirectory = ''
        return ''
    
    def getVocolaDirectory(self):
        isdir, isfile, join, abspath = os.path.isdir, os.path.isfile, os.path.join, os.path.abspath
        if self.VocolaDirectory is not None:
            return self.VocolaDirectory

        ## try in site-packages:
        vocDir = join(sys.prefix, "lib", "site-packages", "vocola2")
        if not isdir(vocDir):
            # print('VocolaDirectory not found in "lib/site-packages/vocola2", return ""')
            self.VocolaDirectory = ''
            return ''
        vocFile = "_vocola_main.py"
        checkGrammar = join(vocDir, vocFile)
        if not isfile(checkGrammar):
            print(f'VocolaDirectory found in "{vocDir}", but no file "{vocFile}" found, return ""')
            self.VocolaDirectory = ''
            return ''

        self.VocolaDirectory = abspath(vocDir)
        return self.VocolaDirectory

    
    def getVocolaGrammarsDirectory(self):
        """return the VocolaGrammarsDirectory, but only if Vocola is enabled
        
        If so, the subdirectory VocolaGrammars is created if not there yet.
        
        The path of this "VocolaGrammars" directory is returned.
        
        If Vocola is not enabled, or anything goes wrong, return ""
        
        """
        if self.VocolaGrammarsDirectory is not None:
            return self.VocolaGrammarsDirectory
        
        natlink_user_dir = self.getNatlinkUserDirectory()
        
        voc_grammars_dir = Path(natlink_user_dir)/'VocolaGrammars'
        if not voc_grammars_dir.is_dir():
            voc_grammars_dir.mkdir()
        voc_grammars_dir = str(voc_grammars_dir)
        self.VocolaGrammarsDirectory = voc_grammars_dir

        return voc_grammars_dir
    
    def getAhkUserDir(self):
        return self.getAhkUserDirFromIni()

    
    def getAhkUserDirFromIni(self):
        isdir, abspath = os.path.isdir, os.path.abspath
        key = 'AhkUserDir'
        value =  self.natlinkmain.getconfigsetting(section='autohotkey', option=key)
        if not value:
            self.AhkUserDir = ''
            return value
            
        if isdir(value):
            self.AhkUserDir = abspath(value)
            return value
        expanded = config.expand_path(value)
        if expanded and isdir(expanded):
            self.AhkUserDir= abspath(expanded)
            return self.AhkUserDir
  
        print(f'invalid path for AhkUserDir: "{value}", return ""')
        self.AhkUserDir = ''
        return ''
    
    
    def getAhkExeDir(self):
        if not self.AhkExeDir is None:
            return self.AhkExeDir
        return self.getAhkExeDirFromIni()

    
    def getAhkExeDirFromIni(self):
        isdir, abspath = os.path.isdir, os.path.abspath
        key = 'AhkExeDir'
        value =  self.natlinkmain.getconfigsetting(section='autohotkey', option=key)
        if not value:
            self.AhkExeDir = ''
            return ''
        if isdir(value):
            self.AhkExeDir = abspath(value)
            return value
        expanded = config.expand_path(value)
        if expanded and isdir(expanded):
            self.AhkExeDir = abspath(expanded)
            return self.AhkExeDir

        print(f'invalid path for AhkExeDir: "{value}", return ""')
        self.AhkExeDir = ''
        return ''

    def getExtraGrammarDirectories(self):
        """record grammar directories that are unknown to natlinkstatus and natlinkconfigfunctions
        
        These directories can be entered "manually" in the `natlink.ini` file
        """
        result = self.natlinkmain.getconfigsetting(section='directories')
        return [s for s in result if s not in self.known_directory_options]

    def getUnimacroIniFilesEditor(self):
        key = 'UnimacroIniFilesEditor'
        value =  self.natlinkmain.getconfigsetting(section='unimacro', option=key)
        if not value:
            value = 'notepad'
        if self.UnimacroIsEnabled():
            return value
        return ''
    
    def getShiftKey(self):
        """return the shiftkey, for setting in natlinkmain when user language changes.

        used for self.playString in natlinkutils, for the dropping character bug. (dec 2015, QH).
        """
        ## TODO: must be windows language...
        windowsLanguage = 'enx'  ### ??? TODO QH
        try:
            return "{%s}"% shiftKeyDict[windowsLanguage]
        except KeyError:
            print(f'no shiftKey code provided for language: "{windowsLanguage}", take empty string.')
            return ""

    # get additional options Vocola
    
    def getVocolaTakesLanguages(self):
        """gets and value for distinction of different languages in Vocola
        If Vocola is not enabled, this option will also return False
        """
        key = 'vocolatakeslanguages'
        return  self.natlinkmain.getconfigsetting(section="vocola", option=key, func='getboolean')
    
    def getVocolaTakesUnimacroActions(self):
        """gets and value for optional Vocola takes Unimacro actions
        If Vocola is not enabled, this option will also return False
        """
        key = 'VocolaTakesUnimacroActions'
        return  self.natlinkmain.getconfigsetting(section="vocola", option=key, func='getboolean')

    
    def getInstallVersion(self):
        version = loader.get_config_info_from_registry("version")
        return version
    
    @staticmethod  
    def getDNSName():
        """return NatSpeak for versions <= 11, and Dragon for versions >= 12
        """
        return "Dragon"

    
    def getNatlinkStatusDict(self):
        """return actual status in a dict
        
        Most values come via properties...
        
        """
        D = {}
        # properties:
        D['user'] = self.get_user()
        D['profile'] = self.get_profile()
        D['language'] = self.get_language()
        D['load_on_begin_utterance'] = self.get_load_on_begin_utterance()

        for key in ['DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'PythonVersion',
                    'DNSName', 'NatlinkIni', 'NatlinkUserDirectory',
                    'UnimacroDirectory', 'UnimacroUserDirectory', 'UnimacroGrammarsDirectory',
                    'VocolaDirectory', 'VocolaUserDirectory', 'VocolaGrammarsDirectory',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'UnimacroIniFilesEditor',
                    'ExtraGrammarDirectories',
                    'InstallVersion',
                    # 'IncludeUnimacroInPythonPath',
                    'AhkExeDir', 'AhkUserDir']:
##                    'BaseTopic', 'BaseModel']:
            func_name = f'get{key[0].upper() + key[1:]}'
            func = getattr(self, func_name, None)
            if func:
                D[key] = func()
            else:
                print(f'no valid function for getting key: "{key}" ("{func_name}")')

        D['NatlinkDirectory'] = self.getNatlinkDirectory()
        D['UserDirectory'] = self.getUserDirectory()
        D['vocolaIsEnabled'] = self.VocolaIsEnabled()

        D['unimacroIsEnabled'] = self.UnimacroIsEnabled()
        D['userIsEnabled'] = self.UserIsEnabled()
        return D

    
    def getNatlinkStatusString(self):
        L = []
        D = self.getNatlinkStatusDict()
        L.append('--- properties:')
        self.appendAndRemove(L, D, 'user')
        self.appendAndRemove(L, D, 'profile')
        self.appendAndRemove(L, D, 'language')
        self.appendAndRemove(L, D, 'load_on_begin_utterance')

        # Natlink::
        L.append('')
        for key in ['NatlinkDirectory', 'InstallVersion', 'NatlinkIni', 'NatlinkUserDirectory']:
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

        # system:
        L.append('system information:')
        for key in ['DNSIniDir', 'DNSVersion', 'DNSName',
                    'WindowsVersion', 'PythonVersion']:
            self.appendAndRemove(L, D, key)

        # forgotten???
        if D:
            L.append('remaining information:')
            for key in list(D.keys()):
                self.appendAndRemove(L, D, key)

        return '\n'.join(L)

    
    def appendAndRemove(self, List, Dict, Key, text=None):
        if text:
            List.append(text)
        else:
            value = Dict[Key]
            if value is None or value == '':
                value = '-'
            if len(Key) <= 6:
                List.append(f'\t{Key}\t\t\t{value}')
            elif len(Key) <= 13:
                List.append(f'\t{Key}\t\t{value}')
            else:
                List.append(f'\t{Key}\t{value}')
        del Dict[Key]
        
def getFileDate(modName):
    #pylint:disable=C0321
    try: return os.stat(modName)[stat.ST_MTIME]
    except OSError: return 0        # file not found

def main():
    status = NatlinkStatus()

    Lang = status.get_language()
    print(f'language: "{Lang}"')
    print(status.getNatlinkStatusString())
    print(f'load_on_begin_utterance: {status.get_load_on_begin_utterance()}')
    dns_version = status.getDNSVersion()
    print(f'DNSVersion: {dns_version} (type: {type(dns_version)})')
 
if __name__ == "__main__":
    natlink.natConnect()
    main()
    natlink.natDisconnect()
