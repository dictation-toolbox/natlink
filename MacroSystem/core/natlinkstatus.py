
""" the following functions are provided in this module:
( to be used by either natlinkmain.py or natlinkinstallfunctions.py

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

getWindowsVersion:
    see source below

getPythonVersion:
    returns, as a string, the python version. Eg. "2.3"
    If it cannot find it in the registry it returns an empty string

NatlinkIsEnabled:
    return 1 or 0 whether natlink is enabled or not
    returns None when strange values are found 
    (checked with the Ini file settings of NSSystemIni and NSAppsIni)

getNSSYSTEMIni(): get the path of nssystem.ini
getNSAPPSIni(): get the path of nsapps.ini
    
"""

import os, re, win32api, win32con
import RegistryDict
# for getting generalised env variables:

from win32com.shell import shell, shellcon

NSSystemIni  = "nssystem.ini"
NSAppsIni  = "nsapps.ini"
VocIniFile  = r"Vocola\Exec\vocola.ini"
NSExt73Path  = "ScanSoft\NaturallySpeaking"
NSExt8Path  = "ScanSoft\NaturallySpeaking8"
NSExt9Path  = "Nuance\NaturallySpeaking9"
DNSrx = re.compile(r"^NaturallySpeaking\s+(\d+\.\d+)$")
DNSPaths = [NSExt9Path, NSExt8Path, NSExt73Path]
DNSVersions = [9,8,7]
NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"

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
      
# helper function:
def getFromRegdict(regdict, key, fatal=None):
    """get a key from the regdict, which was collected earlier.

    if fails, do fatal error is fatal is set,
    if fatal is not set, only print warning.

    """
    mess = 'could not find key %s in registry dict'% key
    value = None
    try:
        value = regdict[key]
    except KeyError:
        if fatal:
            fatal_error(mess, new_raise = Exception)
        else:
            return ''
    else:
        return str(value)

def getExtendedEnv(var):
    """get from environ or windows CSLID

    short version, if HOME and ~ should be recognised, use the version from utilsqh..
    """
    # for safety:
    var2 = str(var).strip("%")
    if var2 in os.environ:
        result = str(os.environ[var2])
        if result:
            return result
    # if not go on:
    try:
        CSIDL_variable =  'CSIDL_%s'% var2
        shellnumber = getattr(shellcon,CSIDL_variable, -1)
    except:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
    if shellnumber < 0:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
    try:
        result = shell.SHGetFolderPath (0, shellnumber, 0, 0)
    except:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)

    result = str(result)
    result = os.path.normpath(result)
    return result

##############################################################################33333




try:
    group = "SOFTWARE\Natlink"
    regnl = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, group)
except KeyError:
    fatal_error('cannot find registry: HKEY_LOCAL_MACHINE\\%s'% group)
    raise
try:
    group = "SOFTWARE\Natlink"
    userregnl = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, group)
except KeyError:
    userregnl = None
    print 'warning: cannot find registry for this user: HKEY_CURRENT_USTER\\%s'% group




# of course for extracting the windows version:
Wversions = {'1/4/10': '98',
             '2/3/51': 'NT351',
             '2/4/0':  'NT4',
             '2/5/0':  '2000',
             '2/5/1':  'XP',
             }

def getWindowsVersion():
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

def getDNSIniDir():
    """get the path (one above the users profile paths) where the ini files
    should be located
    """
    # first try if set (by configure dialog/natlinkinstallfunctions.py) if regkey is set:
    key = 'DNSIniDir'
    P = getFromRegdict(regnl, key)
    if P and os.path.isdir(P):
        return P
    
    # first try in allusersprofile/'application data'
    allusersprofile = getExtendedEnv('ALLUSERSPROFILE')
    trunkPath = os.path.join(os.environ['ALLUSERSPROFILE'], 'Application Data')
    for dnsdir in DNSPaths:
        cand = os.path.join(trunkPath, dnsdir)
        if os.path.isdir(cand):
            nssystem = os.path.join(cand, NSSystemIni)
            nsapps = os.path.join(cand, NSAppsIni)
            if os.path.isfile(nssystem) and os.path.isfile(nsapps):
                return cand
    raise IOError("no valid DNS Install Dir found")
    
def getDNSVersion():
    """find the correct DNS version number (integer)

    for versions 8 and 9 look in NSSystemIni,
    for 9 in Documents and Settings
    for 8 in Program Folder

    for earlier versions try the registry, the result is uncertain.    

    """    
    dnsPath = getDNSInstallDir()
    # for 9:
    iniDir = getDNSIniDir()
    if not iniDir:
        return 0
    nssystemini = getNSSYSTEMIni()
    nsappsini = getNSAPPSIni()
    if nssystemini and os.path.isfile(nssystemini):
        version =win32api.GetProfileVal( "Product Attributes", "Version" , "",
                                      nssystemini)
        if version:
            return int(version[0])
        else:
            raise ValueError("getDNSversion: cannot find version while inifile 9 exists")

    # try falling back on registry:
    r= RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER,"Software\ScanSoft")
    if "NaturallySpeaking8" in r:
        DNSversion = 8
    elif "NaturallySpeaking 7.1" in r or "NaturallySpeaking 7.3":
        DNSversion = 7
    else:
        DNSversion = 5
    return DNSversion


def getDNSInstallDir():
    """get the folder where natspeak is installed

    try from the list DNSPaths, look for 9, 8, 7.
    """
    key = 'DNSInstallDir'
    P = getFromRegdict(regnl, key)
    if P and os.path.isdir(P):
        return P
            
    pf = getExtendedEnv('PROGRAMFILES')
    if not os.path.isdir(pf):
        raise IOError("no valid folder for program files: %s"% pf)
    for dnsdir in DNSPaths:
        cand = os.path.join(pf, dnsdir)
        if os.path.isdir(cand):
            programfolder = os.path.join(cand, 'Program')
            if os.path.isdir(programfolder):
                return cand
    raise IOError("no valid DNS Install Dir found")


def getPythonVersion():
    """get the version of python from the registry
    """
    try:
        r= RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE,"SOFTWARE\Python\PythonCore")
    except ValueError:
        return ''
    return r.keys()[0]

def getNSSYSTEMIni():
    inidir = getDNSIniDir()
    if inidir:
        nssystemini = os.path.join(inidir, NSSystemIni)
        if os.path.isfile(nssystemini):
            return nssystemini
    raise IOError("Cannot find proper NSSystemIni file")
            
def getNSAPPSIni():
    inidir = getDNSIniDir()
    nsappsini = os.path.join(inidir, NSAppsIni)
    if os.path.isfile(nsappsini):
            return nsappsini
    raise IOError("Cannot find proper NSAppsIni file")


def NatlinkIsEnabled():
    """check if the ini file settings are correct

in  nssystem.ini check for:

[Global Clients]
.NatLink=Python Macro System
is
in nsapps.ini check for
[.NatLink]
App Support GUID={dd990001-bb89-11d2-b031-0060088dc929}

    """
    nssystemini = getNSSYSTEMIni()
    actual1 = win32api.GetProfileVal(section1, key1, "", nssystemini)


    nsappsini = getNSAPPSIni()
    actual2 = win32api.GetProfileVal(section2, key2, "", nsappsini)
    if value1 == actual1 and value2 == actual2:
        return 1
    elif value1 != actual1 and value2 != actual2:
        return 0
    elif value1 == actual1:
        print 'unexpected result: nssystem.ini equal, nsapps DIFFER\n' \
              'actual: %s\n' \
              'expected: %s'% (actual2, value2)
    elif value2 == actual2:
        print 'unexpected result: nssystem.ini DIFFER, nsapps equal\n' \
              'actual: %s\n' \
              'expected: %s'% (actual1, value1)
    else:
        print 'NatlinkIsEnabled: should not come here...'

def getUserDirectory():
    """return the path to the Natlink user directory

    should be set in configurenatlink, otherwise ignore...
    """
    key = 'UserDirectory'
    value = getFromRegdict(userregnl, key)
    if value:
        if os.path.isdir(value):
            return value
        else:
            print '-'*60
            print 'Invalid userDirectory (of natlink user grammar files, often unimacro): %s'% value
            print 'Return NO userDirectory'
            print 'Run  configurenatlink to fix if you like'
            print '-'*60
            return ''
    else:
        print 'userDirectory (of user grammars in Natlink, mostly unimacro) is NOT SET.'
        print "Run configurenatlink to fix, or leave it like this"
        return ''

def getVocolaUserDirectory():
    print 'coming'
    return ''


if __name__ == "__main__":
    print 'DNS Install Dir: %s'% getDNSInstallDir()
    print 'DNS Ini Dir: %s'% getDNSIniDir()
    print 'Windows version: %s'% getWindowsVersion()
    print 'DNS version: (integer) %s'% getDNSVersion()
    print 'Python version: %s'% getPythonVersion()
    nlenabled = NatlinkIsEnabled()
    if nlenabled:
        print 'Natlink is enabled...'
    elif nlenabled == 0:
        print 'Natlink is NOT enabled'
    else:
        print 'Strange result in function NatlinkIsEnabled: %s'% nlenabled

    print '(Natlink) userDir: %s'% getUserDirectory()
    
