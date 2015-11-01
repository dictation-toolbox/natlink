__version__ = "4.1oscar"
# coding=latin-1
#
# natlinkstatus.py
#   This module gives the status of NatLink to natlinkmain
#
#  (C) Copyright Quintijn Hoogenboom, February 2008
#
#----------------------------------------------------------------------------
# 4.1oscar: installer changed, extended with Unimacro, apart from UserDirectory
# 4.1november: a few small bugs
# 4.1mike: extra checks in start_configurenatlink.py
#          unimacro additions
# 4.1kilo/lima: Dragon 13!
# 4.1juliet: adapted playString function (Mark Lillibridge) via natlinkutils.playString
#            natlinkmain.py has nearly all code caught in a try except statement
# 4.1india: bugfix Vocola
# 4.1hotel:
#      more stable pyd files (hopefully)
#      installer checks for 64 bit python (forbidden)
#      many Unimacro improvements, action classes for specific programs (lines module hundred)
#      autohotkey support
#
# 4.1golf: some improvements in config program
#          new build of previous version of natlink.pyd (which was already in 4.1delta version)
#          natlinkutils.playString tries to workaround the sendkeys problem sometimes experienced.
#
# 4.1foxtrot: some changes in config program
#
# 4.1echo:
# reverted the 2.7 UNICODE pyd to the charlie version because of trouble with the delta version
#
# version 4.2delta  more stable pyd's, 2.7/dragon 12 cannot reload. All pyd versions in separate subdirectory (PYD),
#                   following Rudigers naming convention
#                   more testing on changed  (out of date) natlink.pyd file and nicer messages in config program
#                   and natlink start (Messages window)
# version 4.1charlie some experimental pyd's for dragon 12, python2.6 and python 2.7
#                    new vocola compiler all python
#                    several bugfixes in setting correct python version and pyd
#                    got rid of .bat files in config directory
# version 4.1beta: with first version of natlink26_12.pyd for Dragon 12 (thanks to Rudiger)
#                  drastic changes in old registry settings, removing the PythonPath variable
#                  also change key for previous installed pyd from NatlinkDllRegistered=25 to NatlinkPydRegistered=25;11
#                  so, include the Dragon version in this string too.
#   
# version 4.0 at last, Quintijn, oct 2011
# version 3.9sierraArnoud: a private intermediate release for Arnoud van den Eerenbeemt
#                          making search macro's across applications
# version 3.9sierra: nearly stable, but a lot of details with Dragon 11 have to
#                    be investigated
# version 3.9quebec: working to a final release, with Vocola 2.7.2
# version 3.9papa: removed system command directories vocola (mdl)
# version 3.9foxtrot: adaptation NatSpeak 11
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
    Otherwise it is looked for in %COMMON_APPDATA%\Nuance\... 
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
    changed jan 2013, return two character version, so without the dot! eg '26'
    
    new nov 2009: return first three characters of python full version ('2.5')
#    returns, as a string, the python version. Eg. "2.3"
#    If it cannot find it in the registry it returns an empty string
#(getFullPythonVersion: get string of complete version info).


getUserDirectory: get the NatLink user directory, ##Unimacro will be there. If not return '' not any more (july 2015)
    UserDirectory is now for non Unimacro grammar files, including Dragonfly.
    (if run from natlinkconfigfunctions use getUserDirectoryFromIni, which checks inifile
     at each call...) 

getUnimacroDirectory: get the directory, which should be in natlink\Unimacro. 

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

new 2014:
getDNSName: return "NatSpeak" for versions <= 11 and "Dragon" for 12 (on)
getAhkExeDir: return the directory where AutoHotkey is found (only needed when not in default)
getAhkUserDir: return User Directory of AutoHotkey, not needed when it is in default.

"""


import os, re, win32api, win32con, sys, pprint, stat
import RegistryDict, natlinkcorefunctions
import pywintypes
import time
# for getting generalised env variables:

##from win32com.shell import shell, shellcon

# adapt here
VocIniFile  = r"Vocola\Exec\vocola.ini"
NSExt73Path  = "ScanSoft\NaturallySpeaking"
NSExt8Path  = "ScanSoft\NaturallySpeaking8"
NSExt9Path  = "Nuance\NaturallySpeaking9"
NSExt10Path  = "Nuance\NaturallySpeaking10"
NSExt11Path  = "Nuance\NaturallySpeaking11"
NSExt12Path  = "Nuance\NaturallySpeaking12"
NSExt13Path  = "Nuance\NaturallySpeaking13"
DNSrx = re.compile(r"^NaturallySpeaking\s+(\d+\.\d+)$")
DNSPaths = [NSExt13Path, NSExt12Path, NSExt11Path, NSExt10Path, NSExt9Path, NSExt8Path, NSExt73Path]
DNSVersions = [13,12,11,10,9,8,7]
# augment above when a new version is there!

# utility functions: 
## report function:
#def fatal_error(message, new_raise=None):
#    """prints a fatal error when running this module"""
#    print
#    print 'natlinkconfigfunctions fails because of fatal error:'
#    print
#    print message
#    print
#    print 'This can (hopefully) be solved by closing Dragon and then running the NatLink/Unimacro/Vocola Config program with administrator rights.'
#    print 
#    if new_raise:
#        raise

# of course for extracting the windows version:
Wversions = {'1/4/10': '98',
             '2/3/51': 'NT351',
             '2/4/0':  'NT4',
             '2/5/0':  '2000',
             '2/5/1':  'XP',
             '2/6/0':  'Vista',
             '2/6/1':  '7',
             '2/6/2':  '8'
             }

# the possible languages (for getLanguage)
languages = {"Nederlands": "nld",
             "Fran\xe7ais": "fra",
             "Deutsch": "deu",
             "UK English": "enx",
             "US English": "enx",
             "Australian English": "enx",
             "Indian English": "enx",
             "SEAsian English": "enx",
             "Italiano": "ita",
             "Espa\xf1ol": "esp"}

class NatlinkStatus(object):
    """this class holds the NatLink status functions

    so, can be called from natlinkmain.

    in the natlinkconfigfunctions it is subclassed for installation things
    in the PyTest folder there are/come test functions in TestNatlinkStatus

    """
    
    ### this part is nearly obsolete, this registry section was used in version before 3.5 or so
    usergroup = "SOFTWARE"
##    lmgroup = "SOFTWARE\Natlink"
    try:
        userregnlOld = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, usergroup, flags=win32con.KEY_READ)
    except:
        userregnlOld = None
    if not userregnlOld:
        userregnlOld = None
    else:
        if 'NatLink' in userregnlOld.keys():
            userregnlOld = userregnlOld['NatLink']
        else:
            userregnlOld = None
            
        
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
    UserDirectory = None # not Unimacro!!
    BaseDirectory = None
    CoreDirectory = None
    UnimacroDirectory = None
    UnimacroUserDirectory = None
    VocolaUserDirectory = None
    AhkUserDir = None
    AhkExeDir = None
    hadWarning = []

    def __init__(self, skipSpecialWarning=None):

        ## start setting the CoreDirectory and BaseDirectory:
        CoreDirectory = natlinkcorefunctions.getBaseFolder()
        self.__class__.CoreDirectory = CoreDirectory
        self.__class__.BaseDirectory = os.path.normpath(os.path.join(CoreDirectory, '..'))


        # for the migration from registry to ini files:
        if self.userregnl.firstUse:
            if self.userregnlOld:
                self.copyRegSettingsToInifile(self.userregnlOld, self.userregnl)
            else:
                if not skipSpecialWarning:
                    print 'ERROR: no natlinkstatus.ini found and no (old) registry settings, (re)run config program'
        self.correctIniSettings() # change to newer conventions
        result = self.checkNatlinkPydFile()
        if result is None:
            if not skipSpecialWarning:
                self.warning('WARNING: invalid version of natlink.pyd found\nClose Dragon and then run the\nconfiguration program "configurenatlink.pyw" via "start_configurenatlink.py"')
            
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
        """add base and user directory to sys.path
        
        if user directory is NOT unimacro directory, also try to add
        unimacro directory to the path.
        
        (the registry is out of use, only the core directory is in the
        PythonPath \ NatLink setting, for natlink be able to be started.
        
        Also set here the CoreDirectory and BaseDirectory
        """
        CoreDirectory = self.getCoreDirectory()

        if CoreDirectory.lower().endswith('core'):
            # check the registry setting:
            try:
                regDict, sectionName = self.getHKLMPythonPathDict()
            except pywintypes.error:
                print """PythonPath setting not found in registry\n
Please try to correct this by running the NatLink Config Program (with administration rights)"""
                return
            except ValueError:
                print """NatLink setting not found or wrong in PythonPath setting in registry\n
Please try to correct this by running the NatLink Config Program (with administration rights)"""
                return

            if regDict is None:
                print """NatLink setting not found or wrong in PythonPath setting in registry\n
Please try to correct this by running the NatLink Config Program (with administration rights)"""
                return
            
            section = regDict['NatLink']
            if not section:
                print """PythonPath/Natlink setting in registry does exist.\n
Please try to correct this by running the NatLink Config Program (with administration rights)"""
                return
            setting = section['']
            if setting.lower() == CoreDirectory.lower():
                baseDir = os.path.normpath(os.path.join(CoreDirectory, ".."))
                self.InsertToSysPath(CoreDirectory)
                self.InsertToSysPath(baseDir)
            else:
                print """PythonPath/Natlink setting in registry does not match this core directory\n
registry: %s\nCoreDirectory: %s\n
Please try to correct this by running the NatLink Config Program (with administration rights)"""% (
                setting, CoreDirectory)
                return
        else:
            baseDir = None
            print 'non expected core directory %s, cannot find baseDirectory\nTry to run the Config Program with administrator rights'% CoreDirectory
        userDir = self.getUserDirectory()
        # special for other user directories, insert also unimacro for actions etc.
        if userDir: 
            self.InsertToSysPath(userDir)

    
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
     
        return 1 
         
                
    def checkNatlinkPydFile(self, fromConfig=None):
        """see if natlink.dll is in core directory, and uptodate, if not stop and point to the configurenatlink program
        
        if fromConfig, print less messages...
        
        if natlink.pyd is missing, or
        if NatlinkPydRegistered is absent or not correct, or
        if the original natlink26_12.pyd (for example) is newer than natlink.pyd
        
        # july 2013:
        now conform to the new naming conventions of Rudiger, PYD subdirectory and natlink_2.7_UNICODE.pyd etc.
        the natlink25.pyd has been moved to the PYD directory too and also is named according to the new conventions.
        
        the config program should be run.
        """
        CoreDirectory = self.getCoreDirectory()
        
        originalPyd = self.getOriginalNatlinkPydFile()   # original if previously registerd (from natlinkstatus.ini file)
        wantedPyd = self.getWantedNatlinkPydFile()       # wanted original based on python version and Dragon version
        wantedPydPath = os.path.join(CoreDirectory, 'PYD', wantedPyd)
        currentPydPath = os.path.join(CoreDirectory, 'natlink.pyd')
        
        if not os.path.isfile(wantedPydPath):
            if not fromConfig:
                print 'The wanted pyd does not exist, Dragon/python combination not valid: %s'% wantedPydPath
            return
        
        # first check existence of natlink.pyd (probably never comes here)
        if not os.path.isfile(currentPydPath):
            if not fromConfig:
                print '%s does not exist, (re)run the configuration program of NatLink'% currentPydPath
            return
        
        # check correct pyd version, with python version and Dragon version:
        if wantedPyd != originalPyd:
            if not fromConfig:
                if not originalPyd:
                    self.warning('originalPyd setting is missing in natlinkstatus.ini')
                else:
                    self.warning('incorrect originalPyd (from natlinkstatus.ini): %s, wanted: %s'% (originalPyd, wantedPyd))
            return
        # now check for updates:
        timeWantedPyd = getFileDate(wantedPydPath)
        timeCurrentPyd = getFileDate(currentPydPath)
        
        # check for newer (changed version) of original pyd:
        if timeCurrentPyd or timeWantedPyd:
            if timeWantedPyd > timeCurrentPyd:
                if not fromConfig:
                    self.warning('Current pyd file (%s) out of date, compared with\n%s'% (currentPydPath, wantedPydPath))
                return
        # all well
        return 1

    def getHKLMPythonPathDict(self, flags=win32con.KEY_READ):
        """returns the dict that contains the PythonPath section of HKLM
        
        by default read only, can be called (from natlinkconfigfunctions with
        KEY_ALL_ACCESS, so key can be created)
        
        """
        version = self.getPythonVersion()
        if not version:
            fatal_error("no valid Python version available")
            return None, None
        dottedVersion = version[0] + "." + version[1]
        pythonPathSectionName = r"SOFTWARE\Python\PythonCore\%s\PythonPath"% dottedVersion
        # key MUST already exist (ensure by passing flags=...:
        try:
            lmPythonPathDict = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, pythonPathSectionName, flags=flags)
        except:
            fatal_error("registry section for pythonpath does not exist yet: %s,  probably invalid Python version: %s"%
                             (pythonPathSectionName, version))
            return None, None
        if 'NatLink' in lmPythonPathDict.keys():
            subDict = lmPythonPathDict['NatLink']
            if isinstance(subDict, RegistryDict.RegistryDict):
                if '' in subDict.keys():
                    value = subDict['']
                    if value and type(value) in (str, unicode):
                        # all well (only the value is not tested yet):
                        pass  #OK otherwise print an error
                    else:
                        fatal_error('registry section for PythonPath should contain a folder "NatLink" with a non empty string or unicode default entry (key empty string), not: %s'%  repr(subDict))
                else:
                    fatal_error('registry section for PythonPath should contain in folder "NatLink" a default entry (key empty string), not: %s'%  repr(subDict))
            else:
                fatal_error('registry section for PythonPath should contain a folder "NatLink" with a default entry (key empty string): HKLM\\\\%s'%  pythonPathSectionName)
        else:
            fatal_error('Registry section for PythonPath should contain a folder "NatLink": HKLM\\\\%s'% pythonPathSectionName)
        return lmPythonPathDict, pythonPathSectionName

    def InsertToSysPath(self, newdir):
        """leave "." in the first place if it is there"""
        if not newdir: return
        newdir = os.path.normpath(newdir)
        if newdir in sys.path: return
        if sys.path[0] in ("", "."):
            sys.path.insert(1, newdir)
        else:
            sys.path.insert(0, newdir)
        #print 'inserted in sys.path: %s'% newdir
            
   
    def copyRegSettingsToInifile(self, reg, ini):
        """for firsttime use, copy values from 
        """
        for k,v in reg.items():
            ini.set(k, v)
        #except:
        #    print 'could not copy settings from registry into inifile. Run natlinkconfigfunctions...'

    def correctIniSettings(self):
        """change NatlinkDllRegistered to NatlinkPydRegistered
        
        the new value should have 25;12 (so python version and dragon version)
        """
        ini = self.userregnl
        oldSetting = ini.get('NatlinkDllRegistered')
        newSetting = ini.get('NatlinkPydRegistered')
        if oldSetting and not newSetting:
            if len(oldSetting) <= 2:
                dragonVersion = self.getDNSVersion()
                if dragonVersion <= 11:
                    # silently go over to new settings:
                    oldSetting = "%s;%s"% (oldSetting, dragonVersion)
            print 'correct setting from "NatlinkDllRegistered" to "NatlinkPydRegistered"'      
            ini.set('NatlinkPydRegistered', oldSetting)
            ini.delete('NatlinkDllRegistered')
        oldSetting = ini.get('UserDirectory')
        if oldSetting and oldSetting.find('Unimacro') > 0:
            ini.delete('UserDirectory')
            
            
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

    def getCoreDirectory(self):
        """return the path to coreDir or CoreDirectory
        """
        if self.CoreDirectory is None:
            return natlinkcorefunctions.getBaseFolder()
        return self.CoreDirectory

    def getOriginalNatlinkPydFile(self):
        """return the path of the original dll/pyd file
        
        "" if not registered before
        """
        setting = self.userregnl.get("NatlinkPydRegistered")
        if not setting:
            return ""
        if ";" in setting:
            pyth, drag = setting.split(";")
            pythonInFileName = pyth[0] + '.' + pyth[-1]
            pyth, drag = int(pyth), int(drag)
        else:
            pythonInFileName = setting[0] + '.' + setting[-1]
            pyth, drag = int(setting), 11  # which can also mean pre 11...
            
        if drag <= 11:
            ansiUnicode = 'ANSI'
        else:
            ansiUnicode = 'UNICODE'

        pydFilename = 'natlink_%s_%s.pyd'% (pythonInFileName, ansiUnicode)
        return pydFilename    

    def getWantedNatlinkPydFile(self):
        """return the path pyd file with correct python and Dragon version
        
        with Dragon 12 insert _12 in the original name.
        .dll is dropped.
        
        """
        pyth = self.getPythonVersion()
        drag = self.getDNSVersion()
        pythonInFileName = pyth[0] + '.' + pyth[-1]

        if drag <= 11:
            ansiUnicode = 'ANSI'
        else:
            ansiUnicode = 'UNICODE'

        pydFilename = 'natlink_%s_%s.pyd'% (pythonInFileName, ansiUnicode)
        return pydFilename    
        
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
        P = self.userregnl.get(key)
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


        note: 12.80 is also 13
        for versions 8 and 9 look in NSSystemIni, take from DNSFullVersion
        for 9 in Documents and Settings
        for 8 in Program Folder

        for earlier versions try the registry, the result is uncertain.    

        """
        version = self.getDNSFullVersion()
        if version:
            if version.find('.') > 0:
                versionList = map(int, version.split('.'))
                version = versionList[0]
                if version == 12:
                    if versionList[1] >= 80:
                        version = 13
                return version
            else:
                return int(version[0])

        try:
            # older versions:        
            # try falling back on registry:
            r= RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER,"Software\ScanSoft")
            if "NaturallySpeaking8" in r:
                DNSVersion = 8
            elif "NaturallySpeaking 7.1" in r or "NaturallySpeaking 7.3":
                DNSVersion = 7
            else:
                DNSVersion = 5
        except:
            DNSVersion = 10

        return DNSVersion

                
    def getDNSInstallDir(self):
        """get the folder where natspeak is installed

        try from the list DNSPaths, look for 9, 8, 7.
        """
        key = 'DNSInstallDir'
        P = self.userregnl.get(key)
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
        
        length 2, without ".", so "26" etc.
        """
        version = sys.version[:3]
        version = version.replace(".", "")
        if len(version) != 2:
            raise Valueerror('getPythonVersion, length of python version should be 2, not: %s ("%s")'% (len(version), version))
        if int(version) < 25:
            raise ValueError('getPythonVersion, version is: "%s" versions before "25" (Python 2.5) are not any more supported by NatLink'% version)
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

    def getPythonPath(self):
        """return the python path, for checking in config GUI
        """
        return sys.path
    def printPythonPath(self):
        pprint.pprint(self.getPythonPath())


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
        if not self.CoreDirectory:
            return
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
        if text in self.hadWarning:
            pass
        else:
            print 'Warning:'
            print text
            print
            self.hadWarning.append(text)

    def VocolaIsEnabled(self):
        if not self.NatlinkIsEnabled():
            return
        vocDir = self.getVocolaUserDirectory()
        if vocDir:
            return 1

    def UnimacroIsEnabled(self):
        """UnimacroIsEnabled: see if UserDirectory is there and

        _control.py is in this directory
        """
        if not self.NatlinkIsEnabled():
            return
        UnimacroDir = self.getUnimacroDirectory()
        UnimacroUserDir = self.getUnimacroUserDirectory()
        if not UnimacroDir:
            print 'no valid UnimacroDirectory, Unimacro is disabled'
            return
        if UnimacroUserDir and os.path.isdir(UnimacroUserDir):
            files = os.listdir(UnimacroDir)
            if '_control.py' in files:
                return 1

    def UserIsEnabled(self):
        if not self.NatlinkIsEnabled():
            return
        userDir = self.getUserDirectory()
        if userDir:
            return 1
  
    def getUnimacroDirectory(self):
        """return the path to the Unimacro Directory, starting July 2015 
        
        should be in a fixed place!
        
        """
        if not self.UnimacroDirectory is None: return self.UnimacroDirectory
        if not self.CoreDirectory:
            print 'no valid CoreDirectory, so no UnimacroDirectory'
            uDir = ''
        else:
            uDir = os.path.normpath(os.path.join(self.CoreDirectory, '..','..', '..', 'Unimacro'))
            if uDir and os.path.isdir(uDir):
                print 'UnimacroDirectory: %s'% uDir
            else:
                print 'UnimacroDirectory empty, directory not found: %s'% uDir
                uDir = ''
            
        self.__class__.UnimacroDirectory = uDir # meaning path is invalid!!
            
        return uDir 


    def getUserDirectory(self):
        """return the path to the NatLink User directory
        
        this one is not any more for Unimacro, but for User specified grammars, also Dragonfly

        should be set in configurenatlink, otherwise ignore...
        """
        if not self.NatlinkIsEnabled:
            return
        if not self.UserDirectory is None: return self.UserDirectory
        uDir = self.getUserDirectoryFromIni()
        if uDir:
            print 'UserDirectory: %s'% uDir
        return uDir 

    def getUserDirectoryFromIni(self):
        """get the UserDirectory from the ini file
        return '' if invalid path or not specified...
        """
        key = 'UserDirectory'
        value = self.userregnl.get(key)
        if value:
            Path = isValidPath(value, wantDirectory=1)
            if Path:
                self.__class__.UserDirectory = Path
                return Path
            else:
                print 'invalid path for UserDirectory: "%s"'% value
        self.__class__.UserDirectory = ''
        return ''

    def getVocolaUserDirectory(self):
        if not self.VocolaUserDirectory is None: return self.VocolaUserDirectory
        return self.getVocolaUserDirectoryFromIni()

    def getVocolaUserDirectoryFromIni(self):
        key = 'VocolaUserDirectory'
        
        value = self.userregnl.get(key)
        if value:
            Path = isValidPath(value, wantDirectory=1)
            if Path:
                self.__class__.VocolaUserDirectory = Path
                return Path
            else:
                print 'invalid path for VocolaUserDirectory: "%s"'% value
        self.__class__.VocolaUserDirectory = ''
        return ''


    def getAhkUserDir(self):
        if not self.AhkUserDir is None: return self.AhkUserDir
        return self.getAhkUserDirFromIni()

    def getAhkUserDirFromIni(self):
        key = 'AhkUserDir'
        
        value = self.userregnl.get(key)
        if value:
            Path = isValidPath(value, wantDirectory=1)
            if Path:
                self.__class__.AhkUserDir = Path
                return Path
            else:
                print 'invalid path for AhkUserDir: "%s"'% value
        self.__class__.AhkUserDir = ''
        return ''

    def getAhkExeDir(self):
        if not self.AhkExeDir is None: return self.AhkExeDir
        return self.getAhkExeDirFromIni()

    def getAhkExeDirFromIni(self):
        key = 'AhkExeDir'
        value = self.userregnl.get(key)
        if value:
            Path = isValidPath(value, wantDirectory=1)
            if Path:
                self.__class__.AhkExeDir = Path
                return Path
            else:
                print 'invalid path for AhkExeDir: "%s"'% value
        self.__class__.AhkExeDir = ''
        return ''

    def getUnimacroUserDirectory(self):
        if self.UnimacroUserDirectory != None: return self.UnimacroUserDirectory
        return self.getUnimacroUserDirectoryFromIni()
        
    def getUnimacroUserDirectoryFromIni(self):
        key = 'UnimacroUserDirectory'
        value = self.userregnl.get(key)
        if value:
            Path = isValidPath(value, wantDirectory=1)
            if Path:
                self.__class__.UnimacroUserDirectory = Path
                return Path
            else:
                print 'invalid path for %s: "%s"'% (key, value)
        self.__class__.UnimacroUserDirectory = ''
        return ''

    def getUnimacroIniFilesEditor(self):
        key = 'UnimacroIniFilesEditor'
        value = self.userregnl.get(key)
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
        lang = lang.split("(")[0].strip()
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

    # def getNatlinkDebug(self):
    #     """gets value for debug output in DNS logfile"""
    # obsolete (for a long time, 2015 and earlier)
    #     key = 'NatlinkDebug'
    #     value = self.userregnl.get(key, None)
    #     return value

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

    def getNatlinkPydRegistered(self):
        value = self.userregnl.get('NatlinkDllRegistered', None)
        return value

    def getDNSName(self):
        """return NatSpeak for versions <= 11, and Dragon for versions >= 12
        """
        if self.getDNSVersion() <= 11:
            return 'NatSpeak'
        else:
            return "Dragon"

    def getNatlinkStatusDict(self):
        """return actual status in a dict"""
        D = {}
        for key in ['userName', 'DNSuserDirectory', 'DNSInstallDir',
                    'DNSIniDir', 'WindowsVersion', 'DNSVersion',
                    'DNSFullVersion', 
                    'PythonVersion',
                    'DNSName',
                    'UnimacroDirectory',
                    'DebugLoad', 'DebugCallback',
                    'VocolaTakesLanguages', 'VocolaTakesUnimacroActions',
                    'UnimacroIniFilesEditor',
                    'InstallVersion', 'NatlinkPydRegistered',
                    'IncludeUnimacroInPythonPath',
                    'AhkExeDir', 'AhkUserDir']:
##                    'BaseTopic', 'BaseModel']:
            keyCap = key[0].upper() + key[1:]
            execstring = "D['%s'] = self.get%s()"% (key, keyCap)
            exec(execstring)
        D['CoreDirectory'] = self.CoreDirectory
        D['BaseDirectory'] = self.BaseDirectory 
        D['UserDirectory'] = self.getUserDirectoryFromIni()
        D['VocolaUserDirectory'] = self.getVocolaUserDirectoryFromIni()
        D['UnimacroUserDirectory'] = self.getUnimacroUserDirectoryFromIni()
        D['natlinkIsEnabled'] = self.NatlinkIsEnabled()
        D['vocolaIsEnabled'] = self.VocolaIsEnabled()
        D['unimacroIsEnabled'] = self.UnimacroIsEnabled()
        D['userIsEnabled'] = self.UserIsEnabled()
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
                for key in ('BaseDirectory', 'VocolaUserDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'vocolaIsEnabled', "---Vocola is disabled")
                for key in ('VocolaUserDirectory', 'VocolaTakesLanguages',
                            'VocolaTakesUnimacroActions'):
                    del D[key]
                    
            ## Unimacro:
            if D['unimacroIsEnabled']:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is enabled")
                for key in ('UnimacroDirectory',):
                    self.appendAndRemove(L, D, key)
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor'):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'unimacroIsEnabled', "---Unimacro is disabled")
                for key in ('UnimacroUserDirectory', 'UnimacroIniFilesEditor'):
                    del D[key]
            ##  UserDirectory:
            if D['userIsEnabled']:
                self.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are enabled")
                for key in ('UserDirectory',):
                    self.appendAndRemove(L, D, key)
            else:
                self.appendAndRemove(L, D, 'userIsEnabled', "---User defined grammars are disabled")
                del D['UserDirectory']

            ## remaining NatLink options:
            L.append('other NatLink info:')
            for key in ('DebugLoad', 'DebugCallback'):
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
                    'DNSIniDir', 'DNSVersion', 'DNSName',
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

def getFileDate(modName):
    try: return os.stat(modName)[stat.ST_MTIME]
    except OSError: return 0        # file not found

# for splitting the env variables:
reEnv = re.compile('(%[A-Z_]+%)', re.I)

NatLinkEnvVarDict = None
def SetInNatLinkEnvDictIfValidPath(name, filepath):
    """set if valid, otherwise DO NOT SET.
    
    If UserDirectory is not set in the configuration, it will not be set in this dict.
    """
    global NatLinkEnvVarDict
    if NatLinkEnvVarDict is None:
        NatLinkEnvVarDict = {}
    if filepath:
        filepath = os.path.normpath(filepath)
        if os.path.isdir(filepath):
            NatLinkEnvVarDict[name] = filepath
        else:
            print 'natlinkstatus.SetInNatLinkEnvDictIfValidPath:\nInvalid directory: "%s" for "%s". Set in NatLinkEnvVarDict to ""'% (filepath, name)

def createNatLinkEnvVarDict():
    """make the special NatLink variables global in this module
    """
    status = NatlinkStatus()
    CoreDirectory = status.getCoreDirectory()
    SetInNatLinkEnvDictIfValidPath("CoreDirectory", CoreDirectory)

    NATLINK = os.path.normpath(os.path.join(CoreDirectory, '..', '..'))
    SetInNatLinkEnvDictIfValidPath("NATLINK", NATLINK)
    SetInNatLinkEnvDictIfValidPath("NatLink", NATLINK)

    UNIMACRO = os.path.normpath(os.path.join(NATLINK, '..', 'Unimacro'))
    SetInNatLinkEnvDictIfValidPath("UNIMACRO", UNIMACRO)
    SetInNatLinkEnvDictIfValidPath("Unimacro", UNIMACRO)

    CoreDirectory = status.CoreDirectory
    SetInNatLinkEnvDictIfValidPath("CoreDirectory", CoreDirectory)
    BaseDirectory = status.BaseDirectory
    SetInNatLinkEnvDictIfValidPath("BaseDirectory", BaseDirectory)
        
    for var in ["UserDirectory", "UnimacroDirectory", "VocolaUserDirectory", "UnimacroUserDirectory"]:
        func = getattr(status, "get"+var, None)
        if func:
            value = func()
            SetInNatLinkEnvDictIfValidPath(var, value)
        else:
            print 'natlinkstatus.createNatLinkEnvVarDict:\nCannot find entry for "%s"'% var
            
            
def expandEnvVars(filepath): 
    """try to substitute environment variable into a path name
    
    first try the NatLink special variables
        NATLINK, NatLink, Unimacro,
        CoreDirectory, BaseDirectory (==MacroSystem), UserDirectory
        UnimacroDirectory, 
        VocolaUserDirectory, UnimacroUserDirectory

    If %...% persist, call the function in natlinkcorefunctions.
    """
    if NatLinkEnvVarDict is None:
        createNatLinkEnvVarDict()
    filepath = filepath.strip()
    
    if filepath.startswith('~'):
        folderpart = natlinkcorefunctions.getExtendedEnv('~')
        filepart = filepath[1:]
        filepart = filepart.strip('/\\ ')
        filepath = os.path.normpath(os.path.join(folderpart, filepart))
    
    if reEnv.search(filepath):
        List = reEnv.split(filepath)
        #print 'parts: %s'% List
        List2 = []
        for part in List:
            if not part: continue
            key = part.strip("%")
            if key in NatLinkEnvVarDict:
                # natlink related env variables:
                folderpart = NatLinkEnvVarDict[key]
            else:
                try:
                    # try all system env variables:
                    folderpart = natlinkcorefunctions.getExtendedEnv(part)
                except ValueError:
                    folderpart = part
            List2.append(folderpart)
        filepath = ''.join(List2)
        return os.path.normpath(filepath)
    # no match
    return filepath

def isValidPath(spec, wantFile=None, wantDirectory=None):
    """check existence of spec, allow for pseudosymbols.
    
    Return the normpath (expanded) if exists and optionally is a file or a directory
    
    ~ and %...% should be evaluated
    
    tested in testConfigfunctions.py
    """
    if not spec:
        return
    
    if not os.path.exists(spec):
        spec2 = expandEnvVars(spec)
    else:
        spec2 = spec
    spec2 = os.path.normpath(spec2)
    if os.path.exists(spec2):
        if wantDirectory and wantFile:
            raise ValueError("isValidPath, only wantFile or wantDirectory may be specified, not both!")
        if wantFile:
            if  os.path.isfile(spec2):
                return spec2
            else:
                print 'isValidPath, path exists, but is not a file: "%s"'% spec2
                return
        if wantDirectory:
            if os.path.isdir(spec2):
                return spec2
            else:
                print 'isValidPath, path exists, but is not a directory: "%s"'% spec2
                return
        return spec2


if __name__ == "__main__":
    status = NatlinkStatus()
    status.checkSysPath()
    print status.getNatlinkStatusString()
    lang = status.getLanguage()
    
    
    # exapmles, for more tests in ...
    print '\n====\nexamples of expanding ~ and %...% variables:'
    short = "~/Quintijn"
    expanded = expandEnvVars(short)
    print 'Some directory in home:', expanded
    
    # the Dragon directory:
    short = "%PROGRAMFILES%/Nuance"
    expanded = expandEnvVars(short)
    print "The dragon directory: %s"% expanded
    # the Dragon ini files directory:
    short = "%COMMON_APPDATA%/Nuance"
    expanded = expandEnvVars(short)
    print "The dragon config files: %s"% expanded

    # My UnimacroUserDirectory:
    short = "%UnimacroUserDirectory%"
    expanded = expandEnvVars(short)
    print "My UnimacroUserDirectory: %s"% expanded

    # My VocolaUserDirectory:
    short = "%VocolaUserDirectory%"
    expanded = expandEnvVars(short)
    print "My VocolaUserDirectory: %s"% expanded
    
    

    # print 'private NatLinkEnvVarDict:'
    # print NatLinkEnvVarDict


    # next things only testable when changing the dir in the functions above
    # and copying the ini files to this dir...
    # they normally run only when natspeak is on (and from NatSpeak)
    #print 'language (test): |%s|'% lang    
    #print status.getBaseModelBaseTopic()
    #print status.getBaseModel()
    #print status.getBaseTopic()
