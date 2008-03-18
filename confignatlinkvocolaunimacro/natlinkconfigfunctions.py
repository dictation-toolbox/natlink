#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# natlinkconfigfunctions.py
#   This module performs the configuration functions.
#   called from natlinkconfig (a wxPython GUI),
#   or directly, see below
#
#   Quintijn Hoogenboom, January 2008
#
"""

With the functions in this module natlink can be configured.

This can be done in three ways:
-Through the command line interface (CLI) which is started automatically
 when this module is run (with Pythonwin, IDLE, or command line of python)
-On the command line, using one of the different command line options 
-Through the configure GUI (natlinkconfig.py), which calls into this module
 This last one needs wxPython to be installed.

*** the core directory is relative to this directory ...
    ...and will be searched for first.

Afterwards can be set:

DNSInstallDir
    - if not found in one of the predefined subfolders of %PROGRAMFILES%,
      this directory can be set in HKCU\Software\Natlink.
      Functions: setDNSInstallDir(path) (d path) and clearDNSInstallDir() (D)
      
DNSIniDir
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKCU\Software\Natlink.
      Functions: setDNSIniDir(path) (c path) and clearDNSIniDir() (C)

When natlink is enabled natlink.dll is registered with
      win32api.WinExec("regsrvr32 /s pathToNatlinkdll") (silent)

It can be unregistered through function unregisterNatlinkDll() see below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (e)/disableNatlink() (E)

setUserDirectory(path) (n path) or clearUserDirectory() (N)
    
etc.

More at the bottom, with the CLI description...     

"""
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
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder:
        baseFolder = os.getcwd()
        print 'baseFolder was empty, take wd: %s'% baseFolder
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
##    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
##    if not os.path.isfile(dllPath):
##        print 'natlink.dll not found in core directory: %s'% coreFolder
##        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
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
#-----------------------------------------------------

import os, sys, win32api, shutil
thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'inserting %s to pythonpath...'% coreDir
    sys.path.insert(0, coreDir)

# from core directory, use registry entries from CURRENT_USER/Software/Natlink:
import natlinkstatus, natlinkcorefunctions, RegistryDict

import os, os.path, sys, getopt, cmd, types, string, win32con

class NatlinkConfig(natlinkstatus.NatlinkStatus):
    """performs the configuration tasks of natlink

    userregnl got from natlinkstatus, as a Class (not instance) variable, so
    should be the same among instances of this class...
    """
    def checkNatlinkDllFile(self):
        """see if natlink.dll is in core directory, if not copy from correct version
        """
        coreDir2 = self.getCoreDirectory()
        if coreDir2.lower() != coreDir.lower():
            fatal_error('ambiguous core directory,\nfrom this module: %s\from status in natlinkstatus: %s'%
                                              (coreDir, coreDir2))
        dllFile = os.path.join(coreDir, 'natlink.dll')
        if not os.path.isfile(dllFile):
            self.copyNatlinkDllPythonVersion()
            self.checkPythonPathAndRegistry()            

    def copyNatlinkDllPythonVersion(self):
        """copy the natlink.dll from the correct version"""
        dllFile = os.path.join(coreDir, 'natlink.dll')
        if os.path.isfile(dllFile):
            self.unregisterNatlinkDll()
            os.remove(dllFile)
        pythonVersion = self.getPythonVersion().replace(".", "")
        dllVersionFile = os.path.join(coreDir, 'natlink%s.dll'% pythonVersion)
        if os.path.isfile(dllVersionFile):
            try:
                shutil.copyfile(dllVersionFile, dllFile)
            except:
                fatal_error("could not copy %s to %s"% (dllVersionFile, dllFile))
        
                        

 
    def checkPythonPathAndRegistry(self):
        """checks if core directory and base directory are there

        1. in the sys.path
        2. in the registry keys of HKLM\SOFTWARE\Python\PythonCore\2.3\PythonPath\NatLink

        If this last key is not there or empty
        ---set paths of baseDirectory and coreDirectory
        ---register natlink.dll
        It is probably the first time to run this program.

        If the settings are conflicting, either
        ---you want to reconfigure natlink in a new place (these direcotories)
        ---you ran this program from a wrong place, exit and start again from the correct directory

        """
        self.checkedUrgent = None
        print "checking PythonPathAndRegistry"
        lmPythonPathDict, PythonPathSectionName = self.getHKLMPythonPathDict()
        coreDir2 = self.getCoreDirectory()
        if coreDir2.lower() != coreDir.lower():
            fatal_error('ambiguous core directory,\nfrom this module: %s\from status in natlinkstatus: %s'%
                                              (coreDir, coreDir2))

        baseDir = os.path.join(coreDir, '..')
        pathString = ';'.join(map(os.path.normpath, [coreDir, baseDir]))                                            
##        if lmPythonPath:
##            print 'lmPythonPath: ', lmPythonPath.keys()
        if not 'NatLink' in lmPythonPathDict:
            # first time install, silently register
            self.registerNatlinkDll(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
        
        lmNatlinkPathDict = lmPythonPathDict['NatLink']
        Keys = lmNatlinkPathDict.keys()
        if not Keys:
            # first time install Section is there, but apparently empty
            self.registerNatlinkDll(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
        if Keys != [""]:
            if '' in Keys:
                Keys.remove("")
            fatal_error("The registry section of the pythonPathSection of HKEY_LOCAL_MACHINE:\n\tHKLM\%s\ncontains invalid keys: %s, remove them with the registry editor (regedit)\nAnd rerun this program"%
                        (PythonPathSectionName+r'\NatLink', Keys))
            

        # now section has default "" key, proceed:            
        oldPathString = lmNatlinkPathDict[""]
        if not oldPathString:
            # empty setting, silently register
            self.registerNatlinkDll(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
            
        if oldPathString == pathString:
            return 1 # OK
        ## now for something more serious:::
        text = \
"""
The PythonPath for Natlink does not match in registry with what this program expects

---settings in Registry: %s
---wanted settings: %s

You probably just installed natlink in a new location
and you run the config program for the first time.

If you want the new settings, (re)register natlink.dll (r)

And rerun this program...

Close NatSpeak (including Quick Start Mode), and all other python applications before rerunning this program,
Possibly you have to restart your computer.

If you do NOT want these new settings, simply close this program and run
from the correct place.
"""% (oldPathString, pathString)
        self.warning(text)
        self.checkedUrgent = 1
            
    def warning(self,text):
        """is currently overloaded in GUI"""
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60
        return T
    

    def message(self, text):
        """prints message, can be overloaded in configureGUI
        """
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60

    def getHKLMPythonPathDict(self):
        """returns the dict that contains the PythonPath section of HKLM
        """
        version = self.getPythonVersion()
        if not version:
            fatal_error("no valid python version available")
        pythonPathSectionName = r"SOFTWARE\Python\PythonCore\%s\PythonPath"% version
        lmPythonPathDict = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, pythonPathSectionName)
        return lmPythonPathDict, pythonPathSectionName
        
    def setNatlinkInPythonPathRegistry(self):
        """sets the HKLM setting of the Python registry

        do this only when needed...

        """
        lmPythonPathDict, pythonPathSectionName = self.getHKLMPythonPathDict()
        baseDir = os.path.join(coreDir, '..')
        pathString = ';'.join(map(os.path.normpath, [coreDir, baseDir]))
        NatlinkSection = lmPythonPathDict.get('NatLink', None)
        if NatlinkSection:
            oldPath = NatlinkSection.get('', '')
        else:
            oldPath = ''
        if oldPath.lower() != pathString.lower():
            try:
                lmPythonPathDict['NatLink']  = {'': pathString}
            except:
                self.warning("cannot set PythonPath for natlink in registry, probably you have insufficient rights to do this")

        
    def clearNatlinkFromPythonPathRegistry(self):
        """clears the HKLM setting of the Python registry"""
        lmPythonPathDict, pythonPathSectionName = self.getHKLMPythonPathDict()
        baseDir = os.path.join(coreDir, '..')
        pathString = ';'.join(map(os.path.normpath, [coreDir, baseDir]))                                            
        if 'NatLink' in lmPythonPathDict.keys():
            try:
                del lmPythonPathDict['NatLink']
            except:
                self.warning("cannot clear python path for natlink in registry (HKLM section), probably you have insufficient rights to do this")

    def printRegistrySettings(self):
        print "CURRENT_USER\\Natlink registry settings:"
        Keys = self.userregnl.keys()
        Keys.sort()
        for k in self.userregnl:
            print "\t%  s:\t%s"% (k, self.userregnl[k])
        print "-"*60


    def setDNSInstallDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSInstallDir'
        if os.path.isdir(new_dir):
            programDir = os.path.join(new_dir, 'Program')
            if os.path.isdir(programDir):
                print 'set DNS Install Directory to: %s'% new_dir
                self.userregnl[key] = new_dir
            else:
                mess =  "setDNSInstallDir, directory misses a Program subdirectory: %s"% new_dir
                print mess
                return mess
        else:
            mess = "setDNSInstallDir, not a valid directory: %s"% new_dir
            print mess
            return mess
        
    def clearDNSInstallDir(self):
        """clear in registry local_machine\natlink\natlinkcore

        """
        key = 'DNSInstallDir'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            mess = 'NatSpeak Install directory was not set in registry, natlink part'
            print mess
            return mess
        
    def setDNSIniDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSIniDir'
        if os.path.isdir(new_dir):
            # check ini files:
            nssystem = os.path.join(new_dir, self.NSSystemIni)
            nsapps = os.path.join(new_dir, self.NSAppsIni)
            if not os.path.isfile(nssystem):
                mess = 'folder %s does not have the inifile %s'% (new_dir, self.NSSystemIni)
                print mess
                return mess
            if not os.path.isfile(nsapps):
                mess =  'folder %s does not have the inifile %s'% (new_dir, self.NSAppsIni)
                print mess
                return mess
            self.userregnl[key] = new_dir
        else:
            mess = "setDNSIniDir, not a valid directory: %s"% new_dir
            print mess
            return mess
            
        
    def clearDNSIniDir(self):
        """clear in registry local_machine\natlink\

        """
        key = 'DNSIniDir'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            mess = 'DNS ini files directory was not set in registry'
            print mess
            return mess

    def setUserDirectory(self, v):
        key = 'UserDirectory'
        if os.path.isdir(v):
            print 'set natlinkuserdir to %s'% v
            self.userregnl[key] = v
        else:
            print 'no a valid directory: %s'% v
            
        
    def clearUserDirectory(self):
        key = 'UserDirectory'
        if key in self.userregnl:
            print 'clearing natlink user directory...'
            del self.userregnl[key]
        else:
            print 'natlink user directory key was not set...'
            
      
    def enableNatlink(self, silent=None):
        """register natlink.dll and set settings in nssystem.ini and nsapps.ini

        """
        self.registerNatlinkDll(silent=1)
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        value1 = self.value1
        win32api.WriteProfileVal(section1, key1, value1, nssystemini)
        nsappsini = self.getNSAPPSIni()
        section2 = self.section2
        key2 = self.key2
        value2 = self.value2
        win32api.WriteProfileVal(section2, key2, value2, nsappsini)
        if not silent:
            print 'natlink enabled, restart NatSpeak'

    def disableNatlink(self, silent=None):
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        # trick with None, see testConfigureFunctions...
        # this one disables natlink:
        win32api.WriteProfileVal(section1, key1, None, nssystemini)
        
        nsappsini = self.getNSAPPSIni()
        section2 = self.section2
        key2 = self.key2
        win32api.WriteProfileVal(section2, key2, None, nsappsini)
        # leaving empty section, sorry, did not find the way to delete a section...
        if not silent:
            print 'natlink disabled, restart NatSpeak'
            print 'Note natlink.dll is NOT UNREGISTERED, but this is not necessary either'
        
    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        return self.userregnl.get(key, None)

    def setVocolaUserDir(self, v):
        key = 'VocolaUserDirectory'
        if os.path.isdir(v):
            print 'set vocola user dir to %s'% v
            self.userregnl[key] = v
        else:
            print 'not a valid directory: %s'% v

    def clearVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        if key in self.userregnl:
            del self.userregnl[key]
            self.disableVocolaUnimacroActions()
        else:
            print 'was not set: %s'% key

    def setVocolaCommandFilesEditor(self, v):
        key = "VocolaCommandFilesEditor"
        if v and os.path.isfile(v) and v.endswith(".exe"):
            self.userregnl[key] = v
        else:
            print 'invalid path, not a file or no .exe file: %s'% v
            

    def clearVocolaCommandFilesEditor(self):
        key = "VocolaCommandFilesEditor"
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'was not set: %s'% key
            
    def setVocolaUsesSimpscrp(self, v):
        key = "VocolaUsesSimpscrp"
        self.userregnl[key] = v

    def registerNatlinkDll(self, silent=None):
        """register natlink.dll

        if silent, do through win32api, and not report. This is done whenever natlink is enabled.

        if NOT silent, go through os.system, and produce a message window.

        Also sets the pythonpath in the HKLM pythonpath section        
        """
        # give fatal error if python is not OK...
        dummy, dummy = self.getHKLMPythonPathDict()        
        DllPath = os.path.join(coreDir, "natlink.dll")
        if not os.path.isfile(DllPath):
            fatal_error("Dll file not found in core folder: %s"% DllPath)

        baseDir = os.path.join(coreDir, '..')

        if silent:
            try:
                import win32api
            except:
                fatal_error("cannot import win32api, please see if win32all of python is properly installed")
            
            try:
                win32api.WinExec('regsvr32 /s "%s"'% DllPath)
            except:
                fatal_error("cannot register |%s|"% DllPath)                    
        else:
            # os.system:
            os.system('regsvr32 "%s"'% DllPath)
        self.setNatlinkInPythonPathRegistry()

    def unregisterNatlinkDll(self, silent=None):
        """unregister explicit, should not be done normally
        """
        dummy, dummy = self.getHKLMPythonPathDict()        
        DllPath = os.path.join(coreDir, "natlink.dll")
        if os.path.isfile(DllPath):

            if silent:
                try:
                    import win32api
                except:
                    fatal_error("cannot import win32api, please see if win32all of python is properly installed")
                
                try:
                    win32api.WinExec('regsvr32 /s /u "%s"'% DllPath)
                except:
                    pass
            else:
                # os.system:
                os.system('regsvr32 /u "%s"'% DllPath)
        self.clearNatlinkFromPythonPathRegistry()
        # and remove the natlink.dll (there remain pythonversion ones 23, 24 and 25)
        os.remove(DllPath)

    def enableDebugLoadOutput(self):
        """setting registry key so debug output of loading of natlinkmain is given

        """
        key = "NatlinkmainDebugLoad"
        self.userregnl[key] = 1
        

    def disableDebugLoadOutput(self):
        """disables the natlink debug output of loading of natlinkmain is given
        """
        key = "NatlinkmainDebugLoad"
        self.userregnl[key] = 0

    def enableDebugCallbackOutput(self):
        """setting registry key so debug output of callback functions of natlinkmain is given

        """
        key = "NatlinkmainDebugCallback"
        self.userregnl[key] = 1
        

    def disableDebugCallbackOutput(self):
        """disables the natlink debug output of callback functions of natlinkmain
        """
        key = "NatlinkmainDebugCallback"
        self.userregnl[key] = 0
        
    def enableDebugOutput(self):
        """setting registry key so debug output is in natspeak logfile

        not included in configure GUI, as Natspeak/Natlink.dll seems not to respond
        to this option...
        """
        key = "NatlinkDebug"
        self.userregnl[key] = 1
        

    def disableDebugOutput(self):
        """disables the natlink lengthy debug output to natspeak logfile
        """
        key = "NatlinkDebug"
        self.userregnl[key] = 0

    def enableVocolaUnimacroActions(self):
        """setting registry  unimacro actions can be used in vocola

        """
        key = "VocolaTakesUnimacroActions"
        uscFile = 'usc.vch'
        self.userregnl[key] = 1
        # also copy usc.vch from unimacro folder to VocolaUserDirectory
        fromFolder = os.path.join(self.getUserDirectory(), 'vocola_compatibility')
        toFolder = self.getVocolaUserDir()
        if os.path.isdir(fromFolder):
            fromFile = os.path.join(fromFolder,uscFile)
            if os.path.isfile(fromFile):
                if os.path.isdir(toFolder):
                    toFile = os.path.join(toFolder, uscFile)
                    print 'copy %s from %s to %s'%(uscFile, fromFolder, toFolder)
                    try:
                        shutil.copyfile(fromFile, toFile)
                    except:
                        pass
                    else:
                        return
        mess = "could not copy file %s from %s to %s"%(uscFile, fromFolder, toFolder)
        print mess
        return mess
        

    def disableVocolaUnimacroActions(self):
        """disables unimacro actions can be used in vocola
        """
        key = "VocolaTakesUnimacroActions"
        self.userregnl[key] = 0
        
                
    def enableVocolaTakesLanguages(self):
        """setting registry  so vocola can divide different languages

        """
        key = "VocolaTakesLanguages"
        self.userregnl[key] = 1
        

    def disableVocolaTakesLanguages(self):
        """disables so vocola cannot take different languages
        """
        key = "VocolaTakesLanguages"
        self.userregnl[key] = 0
        
                



def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about natlink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "aAbBxXyYiIDCeEUdVrRgGzZW"
    shortArgOptions = "c:u:v:w:"  
    if Options:
        if type(Options) == types.StringType:
            Options = Options.split(" ", 1)
        Options = map(string.strip, Options)                
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, shortOptions+shortArgOptions)
    except getopt.GetoptError:
        print 'invalid option: %s'% `Options`
        cli.usage()
        return

    if args:
        print 'should not have extraneous arguments: %s'% `args`
    for o, v in options:
        funcName = 'do_%s'% o, None
        func = getattr(cli, 'do_%s'% o, None)
        if not func:
            print 'option %s not found in cli functions: %s'% (o, funcName)
            cli.usage()
            continue
        if o in shortOptions:
            func(None) # dummy arg
        elif o in shortArgOptions:
            func(v)
        else:
            print 'options should not come here'
            cli.usage()

          
class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self, Config=None):
        cmd.Cmd.__init__(self)
        self.prompt = 'natlink config> '
        self.info = 'type u for usage'
        if Config:
            self.config = Config   # initialised instance of NatlinkConfig
        else:
            self.config = NatlinkConfig()
        self.config.checkNatlinkDllFile()
        self.config.checkPythonPathAndRegistry()
        self.checkedConfig = self.config.checkedUrgent

    def usage(self):
        """gives the usage of the command line options or options when
        the command line interface  (CLI) is used
        """
        print '-'*60
        print \
"""Usage either as command line options like '-i' or in an interactive
session using the CLI ( command line interface). 

i - info, print information about the natlink status
I - reginfo,  print information about the natlink registry settings

d/D - set/clear dnsinstalldir, the directory where NatSpeak is installed
c/C - set/clear dnsinidir, the directory where NatSpeak ini files are located

e/E - enable/disable natlink

n/N - set/clear userdirectory, the directory of the user grammar files of natlink (eg unimacro)

v/V - set/clear vocoloauserdir, the user directory for vocola user files.
      This also enables/disables vocola
w/W = set path for opening vocola command files, or clear
s/S = Vocola uses Simpscrp (default is OFF, S)

r/R - (un)registernatlink, the natlink.dll file(should not be necessary to do)
g/G - enable/disable debugoutput: natlink debug output in natlink log file
z/Z - silently enables natlink and registers, or disables natlink and unregisters
      (for installer, to be done/tested)
      
x/X - enable/disable debug load output of natlinkmain (keep at 0 (X) normally)
y/Y - enable/disable debug callback output of natlinkmain (keep at 0 (Y) normally)

a/A - enable/disable unimacro actions in vocola
b/B - enable/disable distinction between languages for vocola user files

u/usage - give this list
q   - quit
help command: give more explanation on command
        """
        print '='*60

    # info----------------------------------------------------------
    def do_i(self, arg):
        S = self.config.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart NatSpeak'
        print S
    def do_I(self, arg):
        # registry settings:
        self.config.printRegistrySettings()

    def help_i(self):
        print '-'*60
        print \
"""The command info (i) gives an overview of the settings that are
currently set inside the natlink system

The command reginfo (I) gives all the registry settings
that are used by the natlink system (HKCU\Software\Natlink)

They are set by either the natlink/vocola/unimacro installer
or by functions that are called by the CLI (command line interface).

Settings and registry settings are only "refreshed" into natlink after
you restart NatSpeak.
"""
        print '='*60
    help_I = help_i

    # DNS install directory------------------------------------------
    def do_d(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Change NatSpeak directory to: %s"% arg
            return self.config.setDNSInstallDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    

    def do_D(self, arg):
        print "Clear NatSpeak directory in registry"
        return self.config.clearDNSInstallDir()

    def help_d(self):
        print '-'*60
        print \
"""Set (d path) or clear (D) the directory where natspeak is installed.

Setting is only needed when NatSpeak is not found at one of the "normal" places.
So setting is often not needed.

When you have a pre-8 version of NatSpeak, setting this option might work.

After you clear this setting, Natlink will, at starting time, again
search for the NatSpeak install directory in the "normal" place(s).
"""
        print '='*60
    help_D = help_d

    # DNS ini directory-----------------------------------------
    def do_c(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Change NatSpeak Ini files directory to: %s"% arg
            return self.config.setDNSIniDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    


    def do_C(self, arg):
            print "Clear NatSpeak Ini files directory in registry"
            return self.config.clearDNSIniDir()
    def help_c(self):
        print '-'*60
        print \
"""Set (c path) of clear (C) the directory where natspeak ini file locations
(nssystem.ini and nsapps.ini) are located.

Only needed if these cannot be found in the normal place(s):
-if you have an "alternative" place where you keep your speech profiles
-if you have a pre-8 version of NatSpeak.

After Clearing this registry entry Natlink will, when it is started by NatSpeak,
again search for its ini files in the "default/normal" place(s).
"""
        print '='*60
    help_C = help_c
    
    # User Directories -------------------------------------------------
    def do_n(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Set Natlink User Directory to %s"% arg
            self.config.setUserDirectory(arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def do_N(self, arg):
        print "Clears Natlink User Directory"
        self.config.clearUserDirectory()
    
    def help_n(self):
        print '-'*60
        print \
"""Sets (n) or clears (N) the user directory of natlink.
This will often be the folder where unimacro is located.

When you clear this registry entry you probably disable unimacro, as
unimacro is located in the natlink user directory.

Vocola will still be on, BUT not with possibilities to use
unimacro shorthand commands and met actions.
"""
        print '='*60

    help_N = help_n
        
    # enable natlink------------------------------------------------
    def do_e(self, arg):
        print "Enable natlink"
        self.config.enableNatlink()
    def do_E(self, arg):
        print "Disable Natlink"
        self.config.disableNatlink()

    def help_e(self):
        print '-'*60
        print \
"""enable natlink (e) or disable natlink (E)

When you enable natlink the necessary settings in nssystem.ini and nsapps.ini
are done.

After you restart natspeak, natlink should start, showing
the window 'Messages from Python Macros'.

When you enable natlink, the file natlink.dll is (re)registered silent. Use
the options r/R to register/unregister natlink.dll explicit.
(see help r, but most often not needed)

When you disable natlink, the necessary  settings in nssystem.ini and nsapps.ini
are cleared. 

After you restart natspeak, natlink should NOT START ANY MORE
So the window 'Messages from Python Macros' is NOT SHOWN.

Note: when you disable natlink, the natlink.dll file is NOT unregistered.
It is not called any more by natspeak, as its declaration is removed from
the Global Clients section of nssystem.ini.
"""
        print "="*60
        
        
    help_E = help_e
  
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        if os.path.isdir(arg):
            print "Setting vocola user directory to %s\nand (therewith) Enable Vocola"% arg
            self.config.setVocolaUserDir(arg)
        else:
            print 'Please specifiy a valid path for VocolaUserDirectory'
            
    def do_V(self, arg):
        print "Clearing vocola user directory and (therewith) Disable Vocola"
        self.config.clearVocolaUserDir()

    def help_v(self):
        print '-'*60
        print \
"""set/clear vocola userdirectory (v path/V) and also enable/disable Vocola

Vocola is meant to be user with a VocolaUserDirectory. Therefore natlinkmain will not
enable Vocola if no VocolaUserDirectory is set.

"""
        print '='*60

    help_V = help_v

    # Vocola Command Files Editor-----------------------------------------------
    def do_w(self, arg):
        if os.path.isfile(arg) and arg.endswith(".exe"):
            print "Setting Setting Vocola Command Files editor to %s"% arg
            self.config.setVocolaCommandFilesEditor(arg)
        else:
            print 'Please specifiy a valid path for vocola command files editor'
            
    def do_W(self, arg):
        print "Clear vocola commands file editor, go back to default simpscrp"
        self.config.clearVocolaCommandFilesEditor()

    def do_s(self, arg):
        print "Set Vocola Uses Simpscrp (and by default uses dedicated editor"
        self.config.setVocolaUsesSimpscrp(1)
            
    def do_S(self, arg):
        print "Clears Vocola Uses Simpscrp, so use python functions instead and Notepad as default editor"
        self.config.setVocolaUsesSimpscrp(0)

    def help_w(self):
        print '-'*60
        print \
"""set/clear vocola  command files editor (w path/W)

By default a utility called "simpscrp"  or "notepad" is used,
see also option s/S.

You can specify a program you like eg
TextPad, NotePad++, UltraEdit, win32pad.


Uses Simpscrp (s) or NOT (S)
This utility runs the Vocola default editor and controls
the calling of the vcl2py translator.
Simpscrp sometimes gives trouble, so if you disable, this is
handled by python functions.

"""
        print '='*60

    help_W = help_w
    help_s = help_w
    help_S = help_w
    

    # enable/disable natlink debug output...
    def do_g(self, arg):
        print "Enable natlink debug output to natspeak logfile "
        self.config.enableDebugOutput()
    def do_G(self, arg):
        print "Disable natlink debug output to natspeak logfile"
        self.config.disableDebugOutput()

    def help_g(self):
        print '-'*60
        print \
"""enables (g)/disables (G) natlink debug output (in the natspeak log file)
this can be a lot of lines, so preferably disable this one!

Currently it is not clear if this option does anything at all!
But the simplest thing is to keep it Disabled, so the setting
NatlinkDebug is kept to 0
"""
        print '='*60

    help_G = help_g
    # enable/disable natlink debug output...
    def do_x(self, arg):
        print "Enable natlinkmain debug load output to messages of pythom macros window"
        self.config.enableDebugLoadOutput()
    def do_X(self, arg):
        print "Disable natlinkmain debug load output to messages of pythom macros window"
        self.config.disableDebugLoadOutput()
    # enable/disable natlink debug output...
    def do_y(self, arg):
        print "Enable natlinkmain debug Callback output to messages of pythom macros window"
        self.config.enableDebugCallbackOutput()
    def do_Y(self, arg):
        print "Disable natlinkmain debug Callback output to messages of pythom macros window"
        self.config.disableDebugCallbackOutput()



    def help_x(self):
        print '-'*60
        print \
"""enables (x)/disables (X) natlinkmain debug load output
enables (y)/disables (Y) natlinkmain debug callback output

This is sometimes lengthy output to the
"Messages from Python Macros" window.

Mainly used when you suspect problems with the working 
of natlink, so keep off (X and Y) most of the time.
"""
        print '='*60

    help_y = help_x
    help_X = help_x
    help_Y = help_x
    
    # register natlink.dll
    def do_r(self, arg):
        print "(Re) register natlink.dll"
        self.config.registerNatlinkDll()
    def do_R(self, arg):
        print "Unregister natlink.dll and disable Natlink"
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkDll()
    def do_z(self, arg):
        """register silent and enable natlink"""
        self.config.registerNatlinkDll(silent=1)
        self.config.enableNatlink(silent=1)
        
    def do_Z(self, arg):
        """(SILENT) Unregister natlink.dll and disable Natlink"""
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkDll(silent=1)

    def help_r(self):
        print '-'*60
        print \
"""registers (r)/ unregisters (R) natlink.dll explicitly.

(Registring is also done (silent) when you enable natlink, so is mostly NOT NEEDED!)

But if you do (-r or -R) a message dialog shows up to inform you what happened.
When you unregister, natlink is also disabled.

If you want to (silent) enable natlink and register silent use -z,
To disable natlink and unregister (silent) use Z
"""
        print '='*60
    help_R = help_r
    help_z = help_r
    help_Z = help_r
    

    def enableVocolaUnimacroActions(self):
        """setting registry  unimacro actions can be used in vocola

        """
        key = "VocolaTakesUnimacroActions"
        self.userregnl[key] = 1
        

    def disableVocolaUnimacroActions(self):
        """disables unimacro actions can be used in vocola
        """
        key = "VocolaTakesUnimacroActions"
        self.userregnl[key] = 0


    # different Vocola options
    def do_b(self, arg):
        print "Enable Vocola different user directory's for different languages"
        self.config.enableVocolaTakesLanguages()
    def do_B(self, arg):
        print "Disable Vocola different user directory's for different languages"
        self.config.disableVocolaTakesLanguages()

    def help_b(self):
        print '-'*60
        print \
"""Enable (b)/disable (B) different vocola user directory's

If enabled, vocola will look into a subdirectory "xxx" of
VocolaUserDirectory IF the language code of 
the user speech profiles is different from "enx".

So for English users this option will have no effect.

If for the first time commands are opened in for example a
Dutch speech profile (language code "nld") a subdirectory "nld" 
is made and all vocola user files are copied into this folder.
"""
        print '='*60

    help_B = help_b

    def do_a(self, arg):
        print "Enable Vocola taking unimacro actions"
        self.config.enableVocolaUnimacroActions()
    def do_A(self, arg):
        print "Disable Vocola taking unimacro actions"
        self.config.disableVocolaUnimacroActions()

    def help_a(self):
        print '-'*60
        print \
"""Enable (a)/disable (A) the use of unimacro actions.

This will only have the effect when unimacro is also on,
meaning the userDirectory of natlink points to the unimacro
grammar files.

Two things can done then:
-use unimacro shorthand commands like W(), BRINGUP() etc
-use meta actions like <<fileopen>> etc

Currency needs the include file usc.vsh to work
"""
        print '='*60
    help_A = help_a

    # enable/disable natlink debug output...


    def default(self, line):
        print 'no valid entry: %s, press u or usage for list of commands'% line
        print

    def do_quit(self, arg):
        sys.exit()
    do_q = do_quit
    def do_usage(self, arg):
        self.usage()
    do_u = do_usage
    def help_u(self):
        print '-'*60
        print \
"""u and usage give the list of commands
lowercase commands usually set/enable something
uppercase commands usually clear/disable something
Informational commands: i and I
"""
    help_usage = help_u
    
    
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
      cli = CLI()
      cli.info = "type u for usage"
      try:
          cli.cmdloop()
      except (KeyboardInterrupt, SystemExit):
          pass
    else:
      _main()

