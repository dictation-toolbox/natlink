__version__ = "3.9echo"
# coding=latin-1
#
# natlinkstatus.py
#   This module gives the status of NatLink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008
#
#----------------------------------------------------------------------------
# version 3.9: changing to ini files instead of registry
#              and get python path directly...
#              making ready for python2.6
#              minor change to NewStdout and NewStderr in natlinkmain
# version 3.7: changed userDirectory to UserDirectory in the getNatlinkStatusDict function.
#              no influence on the natlinkstatus.getUserDirectory() function.


"""The following functions are provided in this module:
(to be used by either natlinkmain.py or natlinkconfigfunctions.py)

The functions below are put into the class NatlinkStatus.
The natlinkconfigfunctions can subclass this class, and
the configurenatlink.py (GUI) again sub-subclasses this one.


The following  functions manage information that changes at changeCallback time
(when a new user opens)

setUserInfo(args) put username and directory of speech profiles of the last opened user in this class.
getUsername: get active username (only if NatSpeak/NatLink is running)
getDNSuserDirectory: get directory of user speech profile (only if NatSpeak/NatLink is running)


The functions below should not change anything in settings, only  get information.

getDNSInstallDir:
    returns the directory where NatSpeak is installed.
    if the registry key NatspeakInstallDir exists(CURRENT_USER/Software/Natlink),
    this path is taken (if it points to a valid folder)
    Otherwise one of the default paths is taken,
    %PROGRAMFILES%\Nuance\... or %PROGRAMFILES%\ScanSoft\...
    It must contain at least a Program subdirectory

getDNSIniDir:
    returns the directory where the NatSpeak INI files are located,
    notably nssystem.ini and nsapps.ini.
    If the registry key NatspeakIniDir exists (CURRENT_USER/Software/Natlink),
    and the folder exists and the needed INI files are in this folder this path is returned.
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
    is open (only possible when NatSpeak/NatLink is running)

getPythonVersion:
    new nov 2009: return first three characters of python full version ('2.5')
#    returns, as a string, the python version. Eg. "2.3"
#    If it cannot find it in the registry it returns an empty string
#(getFullPythonVersion: get string of complete version info).


getUserDirectory: get the NatLink user directory, Unimacro will be there. If not return ''
    (if run from natlinkconfigfunctions use getUserDirectoryFromIni, which checks inifile
     at each call...)

getVocolaUserDirectory: get the directory of Vocola User files, if not return ''
    (if run from natlinkconfigfunctions use getVocolaDirectoryFromIni, which checks inifile
     at each call...)

getUnimacroUserDirectory: get the directory of Unimacro INI files, if not return '' or
      the Unimacro user directory

NatlinkIsEnabled:
    return 1 or 0 whether NatLink is enabled or not
    returns None when strange values are found 
    (checked with the INI file settings of NSSystemIni and NSAppsIni)

getNSSYSTEMIni(): get the path of nssystem.ini
getNSAPPSIni(): get the path of nsapps.ini

getBaseModelBaseTopic:
    return these as strings, not ready yet, only possible when
    NatSpeak/NatLink is running.

getDebugLoad:
    get value from registry, if set do extra output of natlinkmain at (re)load time
getDebugCallback:
    get value from registry, if set do extra output of natlinkmain at callbacks is given
getDebugOutput:
    get value from registry, output in log file of DNS, should be kept at 0
    

getVocolaTakesLanguages: additional settings for Vocola
"""


import os, re, win32api, win32con, sys
import RegistryDict, natlinkcorefunctions
# for getting generalised env variables:

from win32com.shell import shell, shellcon


VocIniFile  = r"Vocola\Exec\vocola.ini"
NSExt73Path  = "ScanSoft\NaturallySpeaking"
NSExt8Path  = "ScanSoft\NaturallySpeaking8"
NSExt9Path  = "Nuance\NaturallySpeaking9"
NSExt10Path  = "Nuance\NaturallySpeaking10"
DNSrx = re.compile(r"^NaturallySpeaking\s+(\d+\.\d+)$")
DNSPaths = [NSExt10Path, NSExt9Path, NSExt8Path, NSExt73Path]
DNSVersions = [10,9,8,7]

# utility functions: 
# report function:
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print 'natlinkconfigfunctions fails because of fatal error:'
    print message
    print
    print 'This can (hopefully) be solved by (re)installing NatLink'
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
             '2/6/0':  'Vista',
             '2/6/1':  '7'
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
    """this class holds the NatLink status functions

    so, can be called from natlinkmain.

    in the natlinkconfigfunctions it is subclassed for installation things
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    usergroup = "SOFTWARE\Natlink"
##    lmgroup = "SOFTWARE\Natlink"
    userregnlOld = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, usergroup)
##    regnl = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, group)

    userregnl = natlinkcorefunctions.NatlinkstatusInifileSection()

    ### from previous modules, needed or not...
    NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"

    NSSystemIni  = "nssystem.ini"
    NSAppsIni  = "nsapps.ini"
    ## setting of nssystem.ini if NatLink is enabled...
    ## this first setting is decisive for NatSpeak if it loads NatLink or not
    section1 = "Global Clients"
    key1 = ".Natlink"
    value1 = 'Python Macro System'

    ## setting of nsapps.ini if NatLink is enabled...
    ## this setting is ignored if above setting is not there...
    section2 = ".Natlink"
    key2 = "App Support GUID"
    value2 = NATLINK_CLSID    

    userArgs = [None, None]

    # for quicker access (only once lookup in a run)
    UserDirectory = None
    UnimacroUserDirectory = None
    VocolaUserDirectory = None


    def __init__(self):

        # for the migration from registry to ini files:
        if self.userregnl.firstUse:
            if self.userregnlOld:
                self.copyRegSettingsToInifile(self.userregnlOld, self.userregnl)
            else:
                print 'ERROR: no natlinkstatus.ini found and no (old) registry settings, run natlinkconfig.py'
   
   
    def checkSysPath(self):
        """add base and user directory to sys.path
        
        if user directory is NOT unimacro directory, also try to add
        unimacro directory to the path.
        
        (the registry is out of use, only the core directory is in the
        PythonPath \ NatLink setting, for natlink be able to be started.
        """
        coreDir = natlinkcorefunctions.getBaseFolder()
        if coreDir.lower().endswith('core'):
            baseDir = os.path.normpath(os.path.join(coreDir, ".."))
            self.InsertToSysPath(coreDir)
        else:
            baseDir = None
            print 'non expected core directory %s, cannot find baseDirectory'% coreDir
        userDir = self.getUserDirectory()
        # special for other user directories, insert also unimacro for actions etc.
        if userDir and userDir.lower().endswith('unimacro'):
            self.InsertToSysPath(userDir)
        else:
            includeUnimacro = self.getIncludeUnimacroInPythonPath()
            if  includeUnimacro:
                if not baseDir:
                    print 'no baseDir found, cannot "IncludeUnimacroInPythonPath"'
                    return
                unimacroDir = os.path.join(baseDir, '..', '..', 'unimacro')
                unimacroDir = os.path.normpath(unimacroDir)
                if os.path.isdir(unimacroDir):
                    self.InsertToSysPath(unimacroDir)
                else:
                    print 'no valid UnimacroDir found(%s), cannot "IncludeUnimacroInPythonPath"'% \
                        unimacroDir

    def InsertToSysPath(self, newdir):
        """leave "." in the first place if it is there"""
        if not newdir: return
        newdir = os.path.normpath(newdir)
        if newdir in sys.path: return
        if sys.path[0] in ("", "."):
            sys.path.insert(1, newdir)
        else:
            sys.path.insert(0, newdir)
        print 'inserted in sys.path: %s'% newdir
            
   
    def copyRegSettingsToInifile(self, reg, ini):
        """for firsttime use, copy values from 
        """
        for k,v in reg.items():
            ini.set(k, v)
        #except:
        #    print 'could not copy settings from registry into inifile. Run natlinkconfigfunctions...'

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
        """get the path (one above the users profile paths) where the INI files
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
        print 'no valid DNS INI files Dir found, please provide one in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)'

        
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
            if version.find('.') > 0:
                version = int(version.split('.')[0])
                return version
            else:
                return int(version[0])

        try:
            # older versions:        
            # try falling back on registry:
            r= RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER,"Software\ScanSoft")
            if "NaturallySpeaking8" in r:
                DNSversion = 8
            elif "NaturallySpeaking 7.1" in r or "NaturallySpeaking 7.3":
                DNSversion = 7
            else:
                DNSversion = 5
        except:
            DNSversion = 10

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
        print 'no valid DNS Install Dir found, please provide one in natlinkconfigfunctions (option "d") or in natlinkconfig  GUI (info panel)'
        


    #def getPythonFullVersion(self):
    #    """get the version string from sys
    #    """
    #    version2 = sys.version
    #    return version2
    
    def getPythonVersion(self):
        """get the version of python from the registry
        """
        version = sys.version[:3]
        return version
        #regSection = "SOFTWARE\Python\PythonCore"
        #try:
        #    r= RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, regSection)
        #except ValueError:
        #    return ''
        #versionKeys = r.keys()
        #decorated = [(len(k), k) for k in versionKeys]
        #decorated.sort()
        #decorated.reverse()
        #versionKeysSorted = [k for (dummy,k) in decorated]
        #
        #version2 = self.getPythonFullVersion()
        #for version1 in versionKeysSorted:        
        #    if version2.startswith(version1):
        #        return version1
        #if versionKeys:
        #    print 'ambiguous python version:\npython (module sys) gives full version: "%s"\n' \
        #      'the registry gives (in HKLM/%s): "%s"'% (version2,regSection, versionKeys)
        #else:
        #    print 'ambiguous python version:\npython (module sys) gives full version: "%s"\n' \
        #      'the registry gives (in HKLM/%s) no keys found in that section'% (version2, regSection)
        #version = version2[:3]
        #print 'use version %s'% version
        return version

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
        print "Cannot find proper NSSystemIni file"
        print 'Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)'
                
    def getNSAPPSIni(self):
        inidir = self.getDNSIniDir()
        if inidir:
            nsappsini = os.path.join(inidir, self.NSAppsIni)
            if os.path.isfile(nsappsini):
                return os.path.normpath(nsappsini)
        print "Cannot find proper NSAppsIni file"
        print 'Try to correct your DNS INI files Dir, in natlinkconfigfunctions (option "c") or in natlinkconfig  GUI (info panel)'


    def NatlinkIsEnabled(self, silent=None):
        """check if the INI file settings are correct

    in  nssystem.ini check for:

    [Global Clients]
    .NatLink=Python Macro System
    
    in nsapps.ini check for
    [.NatLink]
    App Support GUID={dd990001-bb89-11d2-b031-0060088dc929}

    if both settings are set, return 1
    (if nssystem.ini setting is set, you also need the nsapps.ini setting)
    if nssystem.ini setting is NOT set, return 0

    if nsapps.ini is set but nssystem.ini is not, NatLink is NOT enabled, still return 0
    
    if nssystem.ini is set, but nsapps.ini is NOT, there is an error, return None and a
    warning message, UNLESS silent = 1.

        """
        nssystemini = self.getNSSYSTEMIni()
        actual1 = win32api.GetProfileVal(self.section1, self.key1, "", nssystemini)


        nsappsini = self.getNSAPPSIni()
        actual2 = win32api.GetProfileVal(self.section2, self.key2, "", nsappsini)
        if self.value1 == actual1:
            if self.value2 == actual2:
                # enabled:
                return 1
            else:
                # 
                mess = ['Error while checking if NatLink is enabled, unexpected result: ',
                        'nssystem.ini points to NatlinkIsEnabled:',
                        '    section: %s, key: %s, value: %s'% (self.section1, self.key1, actual1),
                        'but nsapps.ini points to NatLink is not enabled:',
                      '    section: %s, key: %s, value: %s'% (self.section2, self.key2, actual2),
                      '    should have value: %s'% self.value2]
                if not silent:
                    self.warning(mess)
                return None # error!
        elif actual1:
            if not silent:
                self.warning("unexpected value of nssystem.ini value: %s"% actual1)
            # unexpected value, but not enabled:
            return 0
        else:
            # GUID in nsapps may be defined, natspeak first checks nssystem.ini
            # so NatLink NOT enabled
            return 0
        self.warning("unexpected, natlinkstatus should not come here!")
        return None


    def warning(self, text):
        "to be overloaded in natlinkconfigfunctions and configurenatlink"
        if isinstance(text, basestring):
            print text
        else:
            # probably list:
            print '\n'.join(text)


    def VocolaIsEnabled(self):
        vocDir = self.getVocolaUserDirectory()
        if vocDir:
            return 1

    def UnimacroIsEnabled(self):
        """UnimacroIsEnabled: see if UserDirectory is there and

        _control.py is in this directory
        """
        userDir = self.getUserDirectory()
        if userDir and os.path.isdir(userDir):
            files = os.listdir(userDir)
            if '_control.py' in files:
                return 1

    def getUserDirectory(self):
        """return the path to the NatLink user directory

        should be set in configurenatlink, otherwise ignore...
        """
        if not self.UserDirectory is None: return self.UserDirectory
        return self.getUserDirectoryFromIni()

    def getUserDirectoryFromIni(self):
        """get the UserDirectory from the ini file
        """
        key = 'UserDirectory'
        value = self.userregnl.get(key, '')
        if value:
            if os.path.isdir(value):
                value2 = os.path.normpath(value)
                print 'UserDirectory: %s'% value2
                self.__class__.UserDirectory = value2
                return value2
            else:
                value2 = natlinkcorefunctions.expandEnvVariables(value)
                    ## can possibly take expandEnvVariable (which can also hold env variables in
                    ## the middle of the string )
                if os.path.isdir(value2):
                    value2 = os.path.normpath(value2)
                    print 'UserDirectory (expanded): %s'% value2
                    self.__class__.UserDirectory = value2
                    return value2
                elif value2:
                    print 'Invalid UserDirectory: %s (ignore value)'% value2
                else:
                    print 'No UserDirectory specified'
                    
        self.__class__.UserDirectory = ''
        return ''

    def getVocolaUserDirectory(self):
        if not self.VocolaUserDirectory is None: return self.VocolaUserDirectory
        return self.getVocolaUserDirectoryFromIni()

    def getVocolaUserDirectoryFromIni(self):
        key = 'VocolaUserDirectory'
        
        value = self.userregnl.get(key, '')
        if value:
            if os.path.isdir(value):
                value2 = os.path.normpath(value)
                self.__class__.VocolaUserDirectory = value2
                return value2
            else:
                value2 = natlinkcorefunctions.expandEnvVariables(value)
                ## can possibly take expandEnvVariable (which can also hold env variables in
                ## the middle of the string )
                if os.path.isdir(value2):
                    value2 = os.path.normpath(value2)
                    self.__class__.VocolaUserDirectory = value2
                    print 'VocolaUserDirectory (expanded): %s'% value2
                    return value2
                elif value2:
                    print 'not a valid VocolaUserDirectory: %s (ignore value)'% value2
                else:
                    print 'No VocolaUserDirectory specified'
        self.__class__.VocolaUserDirectory = ''
        return ''

    def getUnimacroUserDirectory(self):
        if self.UnimacroUserDirectory != None: return self.UnimacroUserDirectory
        return self.getUnimacroUserDirectoryFromIni()
        
    def getUnimacroUserDirectoryFromIni(self):
        key = 'UnimacroUserDirectory'
        value = self.userregnl.get(key, '')
        if value:
            if os.path.isdir(value):
                value2 = os.path.normpath(value)
                self.__class__.UnimacroUserDirectory = value2
                return value2
            else:
                value2 = natlinkcorefunctions.expandEnvVariables(value)
                ## can possibly take expandEnvVariable (which can also hold env variables in
                ## the middle of the string )
                if os.path.isdir(value2):
                    value2 = os.path.normpath(value2)
                    print 'Take UnimacroUserDirectory (expanded): %s'% value2
                    self.__class__.UnimacroUserDirectory = value2
                    return value2
                else:
                    value3 = self.getUserDirectory()
                    print 'not a valid UnimacroUserDirectory:' \
                          '%s. Take default: %s'% (value2, value3)
                    self.__class__.UnimacroUserDirectory = value3
                    return value3
        elif self.UnimacroIsEnabled():
            value4 = self.getUserDirectory()
            print '\nTake UserDirectory for UnimacroUserDirectory: %s\n'\
                  '---Consider to change this to eg a subdirectory of your\n'\
                  'Documents directory (like "[My ]Documents\\Natlink\\Unimacro")---\n'% value4
            self.__class__.UnimacroUserDirectory = value4                
            return value4
        else:
            self.__class__.UnimacroUserDirectory = ""
            return ""
        raise Exception("should not come here, could not find a valid UnimacroUserDirectory")

    def getUnimacroIniFilesEditor(self):
        key = 'UnimacroIniFilesEditor'
        value = self.userregnl.get(key, '')
        if not value:
            value = 'notepad'
        if self.UnimacroIsEnabled():
            return value
        else:
            return ''

    def getLastUsedAcoustics(self):
        """get name of last used acoustics,
        
        used by getLanguage, getBaseModel and getBaseTopic
        """
        dir = self.getDNSuserDirectory()
        if dir is None:
            print 'probably no speech profile on'
            return
        #dir = r'D:\projects'  # for testing (at bottom of file)
        if not os.path.isdir(dir):
            raise ValueError('not a valid DNSuserDirectory: |%s|, check your configuration'% dir)
        optionsini = os.path.join(dir, 'options.ini')
        if not os.path.isfile(optionsini):
            raise ValueError('not a valid options inifile found: |%s|, check your configuration'% optionsini)
        
        section = "Options"
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filename=optionsini)
        keyname = "Last Used Acoustics"
        keyToModel = inisection.get(keyname)
        if not keyToModel:
            raise ValueError('no keyToModel value in options inifile found: (key: |%s|), check your configurationfile %s'%
                             (keyToModel, optionsini))
        return keyToModel

    def getLastUsedTopic(self):
        """get name of last used topic,
        
        used by getBaseTopic
        """
        dir = self.getDNSuserDirectory()
        #dir = r'D:\projects'  # for testing (at bottom of file)
        if not os.path.isdir(dir):
            raise ValueError('not a valid DNSuserDirectory: |%s|, check your configuration'% dir)
        optionsini = os.path.join(dir, 'options.ini')
        if not os.path.isfile(optionsini):
            raise ValueError('not a valid options inifile found: |%s|, check your configuration'% optionsini)
        
        section = "Options"
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filename=optionsini)
        keyname = "Last Used Topic"
        keyToModel = inisection.get(keyname)
        if not keyToModel:
            raise ValueError('no keyToModel value in options inifile found: (key: |%s|), check your configurationfile %s'%
                             (keyToModel, optionsini))
        return keyToModel
    

    def getBaseModelBaseTopic(self):
        """extract BaseModel and BaseTopic of current user
        
        for historical reasons here,
        better use getBaseModel and getBaseTopic separate...
        """
        return self.getBaseModel(), self.getBaseTopic()

    def getBaseModel(self):
        """getting the base model, '' if error occurs
        """
        dir = self.getDNSuserDirectory()
        #dir = r'D:\projects'   # for testing, see bottom of file
        keyToModel = self.getLastUsedAcoustics()
        acousticini = os.path.join(dir, 'acoustic.ini')
        section = "Base Acoustic"
        basesection = natlinkcorefunctions.InifileSection(section=section,
                                                         filename=acousticini)
        BaseModel = basesection.get(keyToModel, "")
        return BaseModel
    

        return self.getBaseModelBaseTopic()[0]

    def getBaseTopic(self):
        """getting the base topic, '' if error occurs
        """
        dir = self.getDNSuserDirectory()
        #dir = r'D:\projects'   # for testing, see bottom of file
        keyToModel = self.getLastUsedTopic()
        if not keyToModel:
            print 'Warning, no valid key to topic found'
            return ''
        topicsini = os.path.join(dir, 'topics.ini')
        section = "Base Topic"
        topicsection = natlinkcorefunctions.InifileSection(section=section,
                                                         filename=topicsini)
        BaseTopic = topicsection.get(keyToModel, "")
        return BaseTopic


    def getLanguage(self):
        """this can only be run if natspeak is running

        The directory of the user speech profiles must be passed.
        So this function should be called at changeCallback when a new user
        is opened.
        """
        dir = self.getDNSuserDirectory()
        if dir is None:
            print 'probably no speech profile on'
            return
        #dir = r'D:\projects' # for testing, see bottom of file
        keyToModel = self.getLastUsedAcoustics()
        acousticini = os.path.join(dir, 'acoustic.ini')
        section = "Base Acoustic"        
        if not os.path.isfile(acousticini):
            print 'getLanguage: Warning, language of the user cannot be found, acoustic.ini not a file in directory %s'% dir
            return 'yyy'
        inisection = natlinkcorefunctions.InifileSection(section=section,
                                                         filename=acousticini)
        lang = inisection.get(keyToModel)
        if not lang:
            print 'getLanguage: Warning, no model specification string for key %s found in "Base Acoustic" of inifile: %s'% (keyToModel, acousticini)
            return 'zzz'
        lang =  lang.split("|")[0].strip()
        if not lang:
            print 'getLanguage: Warning, no valid specification of language string (key: %s) found in "Base Acoustic" of inifile: %s'% (lang, acousticini)
            return 'www'
        if lang in languages:
            return languages[lang]
        else:
            print 'getLanguage: Language: %s not found in languageslist: %s, take "xxx"'% \
                    (lang, languages)
            return 'xxx'

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

    def getIncludeUnimacroInPythonPath(self):
        """gets the value of alway include Unimacro directory in PythonPath"""
        
        key = 'IncludeUnimacroInPythonPath'
        value = self.userregnl.get(key, None)
        return value

    # get additional options Vocola
    def getVocolaTakesLanguages(self):
        """gets and value for distinction of different languages in Vocola"""
        
        key = 'VocolaTakesLanguages'
        value = self.userregnl.get(key, None)
        return value

    def getVocolaTakesUnimacroActions(self):
        """gets and value for optional Vocola takes Unimacro actions"""
        
        key = 'VocolaTakesUnimacroActions'
        value = self.userregnl.get(key, None)
        return value
    
    def getInstallVersion(self):
        return __version__

    def getNatlinkDllRegistered(self):
        value = self.userregnl.get('NatlinkDllRegistered', None)
        return value

    def getNatlinkStatusDict(self):
        """return actual status in a dict"""
        D = {}
        for key in ['userName', 'DNSuserDirectory', 'DNSInstallDir',
                    'DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'DNSFullVersion', 
                    'PythonVersion',
                    
                    'DebugLoad', 'DebugCallback', 'CoreDirectory',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'UnimacroIniFilesEditor',
                    'NatlinkDebug', 'InstallVersion', 'NatlinkDllRegistered',
                    'IncludeUnimacroInPythonPath']:
##                    'BaseTopic', 'BaseModel']:
            keyCap = key[0].upper() + key[1:]
            execstring = "D['%s'] = self.get%s()"% (key, keyCap)
            exec(execstring)
        D['UserDirectory'] = self.getUserDirectoryFromIni()
        D['VocolaUserDirectory'] = self.getVocolaUserDirectoryFromIni()
        D['UnimacroUserDirectory'] = self.getUnimacroUserDirectoryFromIni()
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
        # NatLink::
        
        if D['natlinkIsEnabled']:
            self.appendAndRemove(L, D, 'natlinkIsEnabled', "---NatLink is enabled")
            key = 'CoreDirectory'
            self.appendAndRemove(L, D, key)
            key = 'InstallVersion'
            self.appendAndRemove(L, D, key)

            ## Vocola::
            if D['vocolaIsEnabled']:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is enabled")
                for key in ('VocolaUserDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is disabled")
                for key in ('VocolaUserDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    del D[key]
                    
            ## Unimacro or UserDirectory:
            if D['unimacroIsEnabled']:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is enabled")
                for key in ('UserDirectory',):
                    self.appendAndRemove(L, D, key)
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is disabled")
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor'):
                    del D[key]
                if D['UserDirectory']:
                    L.append('but UserDirectory is defined:')
                    for key in ('UserDirectory',):
                        self.appendAndRemove(L, D, key)
                else:
                    del D['UserDirectory']
            ## remaining NatLink options:
            L.append('other NatLink info:')
            for key in ('DebugLoad', 'DebugCallback', 'NatlinkDebug'):
                self.appendAndRemove(L, D, key)
    
        else:
            # NatLink disabled:
            if D['natlinkIsEnabled'] == 0:
                self.appendAndRemove(L, D, 'natlinkIsEnabled', "---NatLink is disabled")
            else:
                self.appendAndRemove(L, D, 'natlinkIsEnabled', "---NatLink is disabled (strange value: %s)"% D['natlinkIsEnabled'])
            key = 'CoreDirectory'
            self.appendAndRemove(L, D, key)
            for key in ['DebugLoad', 'DebugCallback',
                    'VocolaTakesLanguages',
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
            value = Dict[Key]
            if value == None or value == '':
                value = '-'
            List.append("\t%s\t%s"% (Key,value))
        del Dict[Key]

if __name__ == "__main__":
    status = NatlinkStatus()
    status.checkSysPath()
    print status.getNatlinkStatusString()
    lang = status.getLanguage()
    
    # next things only testable when changing the dir in the functions above
    # and copying the ini files to this dir...
    # they normally run only when natspeak is on (and from NatSpeak)
    #print 'language (test): |%s|'% lang    
    #print status.getBaseModelBaseTopic()
    #print status.getBaseModel()
    #print status.getBaseTopic()