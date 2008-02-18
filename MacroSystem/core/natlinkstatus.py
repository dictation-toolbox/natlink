__version__ = "3.1.beta"
#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# natlinkstatus.py
#   This module gives the status of natlink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008
#
#----------------------------------------------------------------------------


""" the following functions are provided in this module:
( to be used by either natlinkmain.py or natlinkconfigfunctions.py

The functions below are put into the class NatlinkStatus.
The natlinkconfigfunctions can subclass this class, and
the configurenatlink.py (GUI) again sub-subclasses this one.


The following  functions manage information that changes at changeCallback time
(when a new user opens)

setUserInfo(args) put username and directory of speech profiles of the last opened user in this class.
getUsername: get active username (only if NatSpeak/natlink is running)
getDNSuserDirectory: get directory of user speech profile (only if NatSpeak/natlink is running)


The functions below should not change anything in settings, only  get information.

getDNSInstallDir:
    returns the directory where NatSpeak is installed.
    if the registry key NatspeakInstallDir exists(CURRENT_USER/Software/Natlink),
    this path is taken (if it points to a valid folder)
    Otherwise one of the default paths is taken,
    %PROGRAMFILES%\Nuance\... or %PROGRAMFILES%\ScanSoft\...
    It must contain at least a Program subdirectory

getDNSIniDir:
    returns the directory where the NatSpeak Inifiles are located,
    notably nssystem.ini and nsapps.ini.
    If the registry key NatspeakIniDir exists (CURRENT_USER/Software/Natlink),
    and the folder exists and the needed inifiles are in this folder this path is returned.
    Otherwise it is looked for in %COMMON_APPDATA%\Nuance\... or %COMMON_APPDATA%\Scansoft\...

getDNSVersion:
    returns the in the version number of NatSpeak, as an integer. So 9, 8, 7, ... (???)
    note distinction is made here between different subversions.
(getDNSFullVersion: get longer version string)
.
getWindowsVersion:
    see source below

getLanguage:
    returns the 3 letter code of the language of the speech profile that
    is open (only possible when NatSpeak/natlink is running)

getPythonVersion:
    returns, as a string, the python version. Eg. "2.3"
    If it cannot find it in the registry it returns an empty string
(getFullPythonVersion: get string of complete version info).


getUserDirectory: get the natlink user directory, unimacro will be there. If not return ''

getVocolaUserDirectory: get the directory of Vocola User files, if not return ''

NatlinkIsEnabled:
    return 1 or 0 whether natlink is enabled or not
    returns None when strange values are found 
    (checked with the Ini file settings of NSSystemIni and NSAppsIni)

getNSSYSTEMIni(): get the path of nssystem.ini
getNSAPPSIni(): get the path of nsapps.ini

getBaseModelBaseTopic:
    return these as strings, not ready yet, only possible when
    NatSpeak/natlink is running.

getDebugLoad:
    get value from registry, if set do extra output of natlinkmain at (re)load time
getDebugCallback:
    get value from registry, if set do extra output of natlinkmain at callbacks is given
getDebugOutput:
    get value from registry, output in log file of DNS, should be kept at 0
    

getVocolaTakesUnimacroActions
getVocolaTakesLanguages: additional settings for vocola
"""


import os, re, win32api, win32con, sys
import RegistryDict, natlinkcorefunctions
# for getting generalised env variables:

from win32com.shell import shell, shellcon


VocIniFile  = r"Vocola\Exec\vocola.ini"
NSExt73Path  = "ScanSoft\NaturallySpeaking"
NSExt8Path  = "ScanSoft\NaturallySpeaking8"
NSExt9Path  = "Nuance\NaturallySpeaking9"
DNSrx = re.compile(r"^NaturallySpeaking\s+(\d+\.\d+)$")
DNSPaths = [NSExt9Path, NSExt8Path, NSExt73Path]
DNSVersions = [9,8,7]

# utility functions:
# report function:
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print 'natlinkconfigfunctions fails because of fatal error:'
    print message
    print
    print 'This can (hopefully) be solved by (re)installing natlink'
    print 
    if new_raise:
        raise new_raise
    else:
        raise

# of course for extracting the windows version:
Wversions = {'1/4/10': '98',
             '2/3/51': 'NT351',
             '2/4/0':  'NT4',
             '2/5/0':  '2000',
             '2/5/1':  'XP',
             '2/6/0':  'Vista'
             }

# the possible languages (for getLanguage)
languages = {"Nederlands": "nld",
             "Français": "fra",
             "Deutsch": "deu",
             "UK English": "enx",
             "US English": "enx",
             "Australian English": "enx",
             "Indian English": "enx",
             "SEAsian English": "enx",
             "Italiano": "ita"}

class NatlinkStatus(object):
    """this class holds the natlink status functions

    so, can be called from natlinkmain.

    in the natlinkconfigfunctions it is subclassed for installation things
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    usergroup = "SOFTWARE\Natlink"
##    lmgroup = "SOFTWARE\Natlink"
    userregnl = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, usergroup)
##    regnl = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, group)

    ### from previous modules, needed or not...
    NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"

    NSSystemIni  = "nssystem.ini"
    NSAppsIni  = "nsapps.ini"
    ## setting of nssystem.ini if natlink is enabled...
    ## this first setting is decisive for NatSpeak if it loads natlink or not
    section1 = "Global Clients"
    key1 = ".Natlink"
    value1 = 'Python Macro System'

    ## setting of nsapps.ini if natlink is enabled...
    ## this setting is ignored if above setting is not there...
    section2 = ".Natlink"
    key2 = "App Support GUID"
    value2 = NATLINK_CLSID    

    userArgs = [None, None]

    def setUserInfo(self, args):
        """set username and userdirectory at change callback user
        """
        self.userArgs[0] = args[0]
        self.userArgs[1] = args[1]
        

    def clearUserInfo(self):
        self.userArgs[0] = None
        self.userArgs[1] = None

    def getUserName(self):
        return self.userArgs[0]
    def getDNSuserDirectory(self):
        return self.userArgs[1]
        
 
    def getWindowsVersion(self):
        """extract the windows version

        return 1 of the predefined values above, or just return what the system
        call returns
        """
        tup = win32api.GetVersionEx()
        version = "%s/%s/%s"% (tup[3], tup[0], tup[1])
        try:
            return Wversions[version]
        except KeyError:
            print 'natlinkstatus.getWindowsVersion: (yet) unknown Windows version: %s'% version
            return  version

    def getDNSIniDir(self):
        """get the path (one above the users profile paths) where the ini files
        should be located
        """
        # first try if set (by configure dialog/natlinkinstallfunctions.py) if regkey is set:
        key = 'DNSIniDir'
        P = self.userregnl.get(key, '')
        if P:
            os.path.normpath(P)
            if os.path.isdir(P):
                return P
        
        # first try in allusersprofile/'application data'
        allusersprofile = natlinkcorefunctions.getExtendedEnv('ALLUSERSPROFILE')
        trunkPath = os.path.join(os.environ['ALLUSERSPROFILE'], 'Application Data')
        for dnsdir in DNSPaths:
            cand = os.path.join(trunkPath, dnsdir)
            if os.path.isdir(cand):
                nssystem = os.path.join(cand, self.NSSystemIni)
                nsapps = os.path.join(cand, self.NSAppsIni)
                if os.path.isfile(nssystem) and os.path.isfile(nsapps):
                    return os.path.normpath(cand)
        raise IOError("no valid DNS Install Dir found")
        
    def getDNSFullVersion(self):
        """find the Full version string of DNS

        empty if not found, eg for older versions
        """    
        dnsPath = self.getDNSInstallDir()
        # for 9:
        iniDir = self.getDNSIniDir()
        if not iniDir:
            return 0
        nssystemini = self.getNSSYSTEMIni()
        nsappsini = self.getNSAPPSIni()
        if nssystemini and os.path.isfile(nssystemini):
            version =win32api.GetProfileVal( "Product Attributes", "Version" , "",
                                          nssystemini)

            return version
        return ''

    
    def getDNSVersion(self):
        """find the correct DNS version number (integer)

        for versions 8 and 9 look in NSSystemIni, take from DNSFullVersion
        for 9 in Documents and Settings
        for 8 in Program Folder

        for earlier versions try the registry, the result is uncertain.    

        """
        version = self.getDNSFullVersion()
        if version:
            return int(version[0])

        # older versions:        
        # try falling back on registry:
        r= RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER,"Software\ScanSoft")
        if "NaturallySpeaking8" in r:
            DNSversion = 8
        elif "NaturallySpeaking 7.1" in r or "NaturallySpeaking 7.3":
            DNSversion = 7
        else:
            DNSversion = 5
        return DNSversion


    def getDNSInstallDir(self):
        """get the folder where natspeak is installed

        try from the list DNSPaths, look for 9, 8, 7.
        """
        key = 'DNSInstallDir'
        P = self.userregnl.get(key, '')
        if P:
            os.path.normpath(P)
            if os.path.isdir(P):
                return P
                
        pf = natlinkcorefunctions.getExtendedEnv('PROGRAMFILES')
        if not os.path.isdir(pf):
            raise IOError("no valid folder for program files: %s"% pf)
        for dnsdir in DNSPaths:
            cand = os.path.join(pf, dnsdir)
            if os.path.isdir(cand):
                programfolder = os.path.join(cand, 'Program')
                if os.path.isdir(programfolder):
                    return os.path.normpath(cand)
        raise IOError("no valid DNS Install Dir found")


    def getPythonFullVersion(self):
        """get the version string from sys
        """
        version2 = sys.version
        return version2
    
    def getPythonVersion(self):
        """get the version of python from the registry
        """
        try:
            r= RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE,"SOFTWARE\Python\PythonCore")
        except ValueError:
            return ''
        version1 = r.keys()[0]
        version2 = self.getPythonFullVersion()
        if version2.startswith(version1):
            return version1
        
        print 'ambiguous version, sys: %s, registry: %s'% (version2, version1)
        version = version2[:2]
        print 'use version %s'% version
        return version

    def getCoreDirectory(self):
        """return this directory
        """
        return natlinkcorefunctions.getBaseFolder()
    

    def getCoreDirectory(self):
        """return this directory
        """
        return natlinkcorefunctions.getBaseFolder()

    def getNSSYSTEMIni(self):
        inidir = self.getDNSIniDir()
        if inidir:
            nssystemini = os.path.join(inidir, self.NSSystemIni)
            if os.path.isfile(nssystemini):
                return os.path.normpath(nssystemini)
        raise IOError("Cannot find proper NSSystemIni file")
                
    def getNSAPPSIni(self):
        inidir = self.getDNSIniDir()
        if inidir:
            nsappsini = os.path.join(inidir, self.NSAppsIni)
            if os.path.isfile(nsappsini):
                return os.path.normpath(nsappsini)
        raise IOError("Cannot find proper NSAppsIni file")


    def NatlinkIsEnabled(self):
        """check if the ini file settings are correct

    in  nssystem.ini check for:

    [Global Clients]
    .NatLink=Python Macro System
    is
    in nsapps.ini check for
    [.NatLink]
    App Support GUID={dd990001-bb89-11d2-b031-0060088dc929}

        """
        nssystemini = self.getNSSYSTEMIni()
        actual1 = win32api.GetProfileVal(self.section1, self.key1, "", nssystemini)


        nsappsini = self.getNSAPPSIni()
        actual2 = win32api.GetProfileVal(self.section2, self.key2, "", nsappsini)
        if self.value1 == actual1 and self.value2 == actual2:
            return 1
        elif self.value1 != actual1 and self.value2 != actual2:
            return 0
        elif self.value1 == actual1:
            print 'unexpected result: nssystem.ini equal, nsapps DIFFER\n' \
                  'actual: %s\n' \
                  'expected: %s'% (actual2, value2)
        elif self.value2 == actual2:
            print 'unexpected result: nssystem.ini DIFFER, nsapps equal\n' \
                  'actual: %s\n' \
                  'expected: %s'% (actual1, value1)
        else:
            print 'NatlinkIsEnabled: should not come here...'

    def VocolaIsEnabled(self):
        vocDir = self.getVocolaUserDirectory()
        if vocDir:
            return 1

    def UnimacroIsEnabled(self):
        """UnimacroIsEnabled: see if userDirectory is there and

        _control.py is in this directory
        """
        userDir = self.getUserDirectory()
        if userDir and os.path.isdir(userDir):
            files = os.listdir(userDir)
            if '_control.py' in files:
                return 1

    def getUserDirectory(self):
        """return the path to the Natlink user directory

        should be set in configurenatlink, otherwise ignore...
        """
        key = 'UserDirectory'
        value = self.userregnl.get(key, '')
        if value:
            if os.path.isdir(value):
                return os.path.normpath(value)
            else:
                print '-'*60
                print 'Invalid userDirectory (of natlink user grammar files, often unimacro): %s'% value
                print 'Return NO userDirectory'
                print 'Run  configurenatlink to fix if you like'
                print '-'*60
        else:
            print 'userDirectory (of user grammars in Natlink, mostly unimacro) is NOT SET.'
            print "Run configurenatlink to fix, or leave it like this"
        # fall through: 
        return ''

    def getVocolaUserDirectory(self):
        key = 'VocolaUserDirectory'
        value = self.userregnl.get(key, '')
        if value:
            if os.path.isdir(value):
                return os.path.normpath(value)
            else:
                print '-'*60
                print 'Invalid VocolaUserDirectory (of vocola user files): %s'% value
                print 'Return NO VocolaUserDirectory'
                print 'Run  configurenatlink to fix if you like'
                print '-'*60
        else:
            print 'VocolaUserDirectory (of vocola user files) is NOT SET.'
            print 'regard Vocola as being DISABLED'
            print "Run configurenatlink to fix, or leave it like this"
        # fall through: 
        return ''

    def getVocolaCommandFilesEditor(self):
        key = 'VocolaCommandFilesEditor'
        value = self.userregnl.get(key, '')
        if value:
            print 'use %s for editing vocola command files'% value
        else:
            if self.getVocolaUsesSimpscrp():
                print 'use default (simpscrp) for editing vocola command files'
                value = 'simpscrp'
            else:
                print 'use default (notepad) for editing vocola command files'
                value = 'notepad'
        return value

    def getVocolaUsesSimpscrp(self):
        key = 'VocolaUsesSimpscrp'
        value = self.userregnl.get(key, 1)
        return value

    def getBaseModelBaseTopic(self):
        """to be done"""
        return "tobedone", "tobedone"
        if debugLoad: print 'extract BaseModel from DNSuserDirectory: %s'% dir
        keyToModel = win32api.GetProfileVal( "Options", "Last Used Acoustics", "voice" , dir+"\\options.ini" )
        BaseModel = win32api.GetProfileVal( "Base Acoustic", keyToModel , "" , dir+"\\acoustic.ini" )
        if debugLoad: print 'extract BaseTopic from DNSuserDirectory: %s'% dir
        keyToModel = win32api.GetProfileVal( "Options", "Last Used Topic", "" , dir+"\\options.ini" )
        if keyToModel:
            BaseTopic = win32api.GetProfileVal( "Base Topic", keyToModel , "" , dir+"\\topics.ini" )
        else:
            BaseTopic = "not found in ini files"
    ##    basetopics = win32api.GetProfileVal( "Base Acoustic", "voice" , "" , dir+"\\topics.ini" )

    def getBaseModel(self):
        return self.getBaseModelBaseTopic()[0]
    def getBaseTopic(self):
        return self.getBaseModelBaseTopic()[1]


    def getLanguage(self):
        """this can only be run if natspeak is running

        The directory of the user speech profiles must be passed.
        So this function should be called at changeCallback when a new user
        is opened.
        """
        dir = self.getDNSuserDirectory()
        if not dir:
            print 'no dir yet???%s'% dir
            return 'zzz'
        acousticini = os.path.join(dir, 'acoustic.ini')
        if not os.path.isfile(acousticini):
            print 'Warning,  language of the user cannot be found, acoustic.ini not a file'
            return 'yyy'
        lang = win32api.GetProfileVal( "Base Acoustic", "voice" , "" , acousticini)
        lang =  lang.split("|")[0].strip()
        if lang in languages:
            return languages[lang]
        else:
            print "Found unknown language in acoustic.ini:", lang
            return "xxx"

    # get different debug options for natlinkmain:   
    def getDebugLoad(self):
        """gets value for extra info at loading time of natlinkmain"""
        key = 'NatlinkmainDebugLoad'
        value = self.userregnl.get(key, None)
        return value
    def getDebugCallback(self):
        """gets value for extra info at callback time of natlinkmain"""
        key = 'NatlinkmainDebugCallback'
        value = self.userregnl.get(key, None)
        return value

    def getNatlinkDebug(self):
        """gets value for debug output in DNS logfile"""
        key = 'NatlinkDebug'
        value = self.userregnl.get(key, None)
        return value

    # get additional options vocola
    def getVocolaTakesLanguages(self):
        """gets and value for distinction of different languages in vocola"""
        
        key = 'VocolaTakesLanguages'
        value = self.userregnl.get(key, None)
        return value
    
    def getVocolaTakesUnimacroActions(self):
        """gets the value for taking unimacro actions
        will only take effect when unimacro is on (in userDirectory)
        """
        
        key = 'VocolaTakesUnimacroActions'
        value = self.userregnl.get(key, None)
        if value:
            if self.UnimacroIsEnabled():
                return value

    def getInstallVersion(self):
        return __version__

    def getNatlinkStatusDict(self):
        """return actual status in a dict"""
        D = {}
        for key in ['userName', 'DNSuserDirectory', 'DNSInstallDir',
                    'DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'DNSFullVersion', 'PythonFullVersion',
                    'PythonVersion', 'userDirectory',
                    'DebugLoad', 'DebugCallback', 'CoreDirectory',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'VocolaUserDirectory', 'VocolaCommandFilesEditor',
                    'VocolaUsesSimpscrp',
                    'NatlinkDebug', 'InstallVersion']:
##                    'BaseTopic', 'BaseModel']:
            keyCap = key[0].upper() + key[1:]
            execstring = "D['%s'] = self.get%s()"% (key, keyCap)
            exec(execstring)
        D['natlinkIsEnabled'] = self.NatlinkIsEnabled()
        D['vocolaIsEnabled'] = self.VocolaIsEnabled()
        D['unimacroIsEnabled'] = self.UnimacroIsEnabled()
        return D
        
    def getNatlinkStatusString(self):
        L = []
        D = self.getNatlinkStatusDict()
        if D['userName']:
            L.append('user speech profile:')
            self.appendAndRemove(L, D, 'userName')
            self.appendAndRemove(L, D, 'DNSuserDirectory')
        else:
            del D['userName']
            del D['DNSuserDirectory']
        # natlink::
        
        if D['natlinkIsEnabled']:
            self.appendAndRemove(L, D, 'natlinkIsEnabled', "---natlink is enabled")
            key = 'CoreDirectory'
            self.appendAndRemove(L, D, key)
            key = 'InstallVersion'
            self.appendAndRemove(L, D, key)

            ## vocola::
            if D['vocolaIsEnabled']:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---vocola is enabled")
                for key in ('VocolaUserDirectory','VocolaCommandFilesEditor',
                            'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions', 'VocolaUsesSimpscrp'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---vocola is disabled")
                for key in ('VocolaUserDirectory','VocolaCommandFilesEditor', 'VocolaTakesLanguages', 'VocolaTakesUnimacroActions'):
                    del D[key]
                    
            ## unimacro or userDirectory:
            if D['unimacroIsEnabled']:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---unimacro is enabled")
                for key in ('userDirectory',):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---unimacro is disabled")
                if D['userDirectory']:
                    L.append('but userDirectory is defined:')
                    for key in ('userDirectory',):
                        self.appendAndRemove(L, D, key)
                else:
                    del D['userDirectory']
            ## remaining natlink options:
            L.append('other natlink info:')
            for key in ('DebugLoad', 'DebugCallback'):
                self.appendAndRemove(L, D, key)
    
        else:
            # natlink disabled:
            self.appendAndRemove(L, D, 'natlinkIsEnabled', "---natlink is disabled")
            key = 'CoreDirectory'
            self.appendAndRemove(L, D, key)
            for key in ['DebugLoad', 'DebugCallback',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'vocolaIsEnabled']:
                del D[key]
        # system:
        L.append('system information:')
        for key in ['DNSInstallDir',
                    'DNSIniDir', 'DNSVersion',
                    'WindowsVersion', 'PythonVersion']:
            self.appendAndRemove(L, D, key)

        # forgotten???
        if D:
            L.append('remaining information:')
            for key in D.keys():
                self.appendAndRemove(L, D, key)

        return '\n'.join(L)

            
    def appendAndRemove(self, List, Dict, Key, text=None):
        if text:
            List.append(text)
        else:
            List.append("\t%s\t%s"% (Key,Dict[Key]))
        del Dict[Key]

if __name__ == "__main__":
    status = NatlinkStatus()
    print status.getNatlinkStatusString()
