# coding=latin-1
#
# natlinkconfigfunctions.py
#   This module performs the configuration functions.
#   called from natlinkconfig (a wxPython GUI),
#   or directly, see below
#
#   Quintijn Hoogenboom, January 2008
#
"""

With the functions in this module NatLink can be configured.

This can be done in three ways:
-Through the command line interface (CLI) which is started automatically
 when this module is run (with Pythonwin, IDLE, or command line of Python)
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
      
DNSINIDir
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKCU\Software\Natlink.
      Functions: setDNSIniDir(path) (c path) and clearDNSIniDir() (C)

When NatLink is enabled natlink.dll is registered with
      win32api.WinExec("regsrvr32 /s pathToNatlinkdll") (silent)

It can be unregistered through function unregisterNatlinkDll() see below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (e)/disableNatlink() (E)

setUserDirectory(path) (n path) or clearUserDirectory() (N)
etc.

More at the bottom, with the CLI description...

"""

ObsoleteStatusKeys = ('VocolaUsesSimpscrp', 'VocolaCommandFilesEditor')
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
    """get the NatLink core folder, relative from the current folder

    This folder should be relative to this with ../MacroSystem/core and should
    contain natlinkmain.p, natlink.dll, and natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'MacroSystem', 'core') )
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
    print 'This can (hopefully) be solved by (re)installing NatLink'
    print 
    if new_raise:
        raise new_raise
    else:
        raise
#-----------------------------------------------------

import os, sys, win32api, shutil, re
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
    """performs the configuration tasks of NatLink

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
        pythonVersion = self.getPythonVersion().replace(".", "")
        if int(pythonVersion) >= 25:
            dllFile = os.path.join(coreDir, 'natlink.pyd')
        else:
            dllFile = os.path.join(coreDir, 'natlink.dll')
        if not os.path.isfile(dllFile):
            self.copyNatlinkDllPythonVersion()
            self.checkPythonPathAndRegistry()            

    def copyNatlinkDllPythonVersion(self):
        """copy the natlink.dll from the correct version"""
        pythonVersion = self.getPythonVersion().replace(".", "")
        if int(pythonVersion) >= 25:
            dllFile = os.path.join(coreDir, 'natlink.pyd')
            dllVersionFile = os.path.join(coreDir, 'natlink%s.pyd'% pythonVersion)
        else:
            dllFile = os.path.join(coreDir, 'natlink.dll')
            dllVersionFile = os.path.join(coreDir, 'natlink%s.dll'% pythonVersion)
        if os.path.isfile(dllFile):
            self.unregisterNatlinkDll()
            os.remove(dllFile)
            
        if os.path.isfile(dllVersionFile):
            try:
                shutil.copyfile(dllVersionFile, dllFile)
                print 'copied dll/pyd file %s to %s'% (dllVersionFile, dllFile)
            except:
                fatal_error("could not copy %s to %s"% (dllVersionFile, dllFile))
        else:
            fatal_error("dllVersionFile %s is missing! Cannot copy to natlink.dll/natlink.pyd"% dllVersionFile)
            
        
                        

 
    def checkPythonPathAndRegistry(self):
        """checks if core directory and base directory are there

        1. in the sys.path
        2. in the registry keys of HKLM\SOFTWARE\Python\PythonCore\2.3\PythonPath\NatLink

        If this last key is not there or empty
        ---set paths of baseDirectory and coreDirectory
        ---register natlink.dll
        It is probably the first time to run this program.

        If the settings are conflicting, either
        ---you want to reconfigure NatLink in a new place (these directories)
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
            
        if oldPathString.lower() == pathString.lower():
            return 1 # OK
        ## now for something more serious:::
        text = \
"""
The PythonPath for NatLink does not match in registry with what this program
expects

---settings in Registry: %s
---wanted settings: %s

You probably just installed NatLink in a new location
and you ran the config program for the first time.

If you want the new settings, (re)register natlink.dll (r)

And rerun this program...

Close NatSpeak (including Quick Start Mode), and all other Python applications
before rerunning this program.  Possibly you have to restart your computer.

If you do NOT want these new settings, simply close this program and run
from the correct place.
"""% (oldPathString, pathString)
        self.warning(text)
        self.checkedUrgent = 1

    def checkIniFiles(self):
        """check if INI files are consistent
        this is done through the

        """
        result = self.NatlinkIsEnabled(silent=1)
        if result == None:
            self.disableNatlink(silent=1)
            result = self.NatlinkIsEnabled(silent=1)
            if result == None:
                text = \
"""NatLink INI file settings are inconsistently,
and cannot automatically be disabled.

Try to disable again, acquire administrator rights or report this issue
"""
                self.warning(text)
                return None
            else:
                text = \
"""NatLink INI file settings were inconsistent;
This has been repaired.

NatLink is now disabled.
"""
                self.warning(text)
        return 1
            
            
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
            fatal_error("no valid Python version available")
        pythonPathSectionName = r"SOFTWARE\Python\PythonCore\%s\PythonPath"% version
        # key MUST already exist (ensure by passing flags=...:
        try:
            lmPythonPathDict = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, pythonPathSectionName, flags=win32con.KEY_ALL_ACCESS)
        except:
            fatal_error("registry section for pythonpath does not exist yet: %s,  probably invalid Python version: %s"%
                             (pythonPathSectionName, version))
            
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
                self.warning("cannot set PythonPath for NatLink in registry, probably you have insufficient rights to do this")

        
    def clearNatlinkFromPythonPathRegistry(self):
        """clears the HKLM setting of the Python registry"""
        lmPythonPathDict, pythonPathSectionName = self.getHKLMPythonPathDict()
        baseDir = os.path.join(coreDir, '..')
        pathString = ';'.join(map(os.path.normpath, [coreDir, baseDir]))                                            
        if 'NatLink' in lmPythonPathDict.keys():
            try:
                del lmPythonPathDict['NatLink']
            except:
                self.warning("cannot clear Python path for NatLink in registry (HKLM section), probably you have insufficient rights to do this")

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
            mess = 'NatSpeak install directory was not set in registry, NatLink part'
            print mess
            return mess
        
    def setDNSIniDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSIniDir'
        if os.path.isdir(new_dir):
            # check INI files:
            nssystem = os.path.join(new_dir, self.NSSystemIni)
            nsapps = os.path.join(new_dir, self.NSAppsIni)
            if not os.path.isfile(nssystem):
                mess = 'folder %s does not have the INI file %s'% (new_dir, self.NSSystemIni)
                print mess
                return mess
            if not os.path.isfile(nsapps):
                mess =  'folder %s does not have the INI file %s'% (new_dir, self.NSAppsIni)
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
            mess = 'DNS INI files directory was not set in registry'
            print mess
            return mess

    def setUserDirectory(self, v):
        key = 'UserDirectory'
        if os.path.isdir(v):
            print 'set NatLinkUserDir to %s'% v
            self.userregnl[key] = v
        else:
            print 'no a valid directory: %s'% v
            
        
    def clearUserDirectory(self):
        key = 'UserDirectory'
        if key in self.userregnl:
            print 'clearing NatLink user directory...'
            del self.userregnl[key]
        else:
            print 'NatLink user directory key was not set...'
            
      
    def enableNatlink(self, silent=None):
        """register natlink.dll and set settings in nssystem.INI and nsapps.ini

        """
        self.registerNatlinkDll(silent=1)
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        value1 = self.value1
        win32api.WriteProfileVal(section1, key1, value1, nssystemini)
        result = self.NatlinkIsEnabled(silent=1)
        if result == None:
            nsappsini = self.getNSAPPSIni()
            section2 = self.section2
            key2 = self.key2
            value2 = self.value2
            win32api.WriteProfileVal(section2, key2, value2, nsappsini)
            result = self.NatlinkIsEnabled(silent=1)
            if result == None:
                text = \
"""cannot set the nsapps.ini setting in order to complete enableNatlink.

Possibly you need administrator rights to do this
"""
                if not silent:
                    self.warning(text)
                return                
        result = self.NatlinkIsEnabled(silent=1)
        if result:            
            if not silent:
                print 'NatLink enabled, restart NatSpeak'
        else:
            if not silent:
                self.warning("failed to enable NatLink")
            

    def disableNatlink(self, silent=None):
        """only do the nssystem.ini setting
        """
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        # trick with None, see testConfigureFunctions...
        # this one disables NatLink:
        win32api.WriteProfileVal(section1, key1, None, nssystemini)
        if not silent:
            print 'NatLink disabled, restart NatSpeak'
            print 'Note natlink.dll is NOT UNREGISTERED, but this is not necessary either'
        
    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        return self.userregnl.get(key, None)

    def setVocolaUserDir(self, v):
        key = 'VocolaUserDirectory'
        if os.path.isdir(v):
            print 'set Vocola user dir to %s'% v
            self.userregnl[key] = v
        else:
            print 'not a valid directory: %s'% v

    def clearVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'was not set: %s'% key


    def getUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        return self.userregnl.get(key, None)

    def setUnimacroUserDir(self, v):
        key = 'UnimacroUserDirectory'
        if os.path.isdir(v):
            print 'set Unimacro user dir to %s'% v
            self.userregnl[key] = v
        else:
            print 'not a valid directory: %s'% v

    def clearUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'was not set: %s'% key

    def setUnimacroIniFilesEditor(self, v):
        key = "UnimacroIniFilesEditor"
        if v and os.path.isfile(v) and v.endswith(".exe"):
            self.userregnl[key] = v
        else:
            print 'invalid path, not a file or no .exe file: %s'% v
            
    def clearUnimacroIniFilesEditor(self):
        key = "UnimacroIniFilesEditor"
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'was not set: %s'% key
            
    def registerNatlinkDll(self, silent=None):
        """register natlink.dll

        if silent, do through win32api, and not report. This is done whenever NatLink is enabled.

        if NOT silent, go through os.system, and produce a message window.

        Also sets the pythonpath in the HKLM pythonpath section        
        """
        # give fatal error if Python is not OK...
        dummy, dummy = self.getHKLMPythonPathDict()        
        pythonVersion = self.getPythonVersion().replace(".", "")
        if int(pythonVersion) >= 25:
            DllPath = os.path.join(coreDir, 'natlink.pyd')
        else:
            DllPath = os.path.join(coreDir, 'natlink.dll')
        if not os.path.isfile(DllPath):
            fatal_error("Dll file not found in core folder: %s"% DllPath)

        baseDir = os.path.join(coreDir, '..')

        if silent:
            try:
                import win32api
            except:
                fatal_error("cannot import win32api, please see if win32all of Fordpython is properly installed")
            
            try:
                result = win32api.WinExec('regsvr32 /s "%s"'% DllPath)
                if result:
                    print 'failed to register %s (result: %s)'% (DllPath, result)
##                else:
##                    print 'registered %s '% DllPath
                    
            except:
                fatal_error("cannot register |%s|"% DllPath)                    
        else:
            # os.system:
            result = os.system('regsvr32 "%s"'% DllPath)
            if result:
                print 'failed to register %s (result: %s)'% (DllPath, result)
            else:
                print 'registered %s'% DllPath
                
        self.setNatlinkInPythonPathRegistry()

    def unregisterNatlinkDll(self, silent=None):
        """unregister explicit, should not be done normally
        """
        dummy, dummy = self.getHKLMPythonPathDict()        
        pythonVersion = self.getPythonVersion().replace(".", "")
        if int(pythonVersion) >= 25:
            DllPath = os.path.join(coreDir, 'natlink.pyd')
        else:
            DllPath = os.path.join(coreDir, 'natlink.dll')
        if os.path.isfile(DllPath):

            if silent:
                try:
                    import win32api
                except:
                    fatal_error("cannot import win32api, please see if win32all of Python is properly installed")
                
                try:
                    result = win32api.WinExec('regsvr32 /s /u "%s"'% DllPath)
                    if not result:
                        print 'failed to unregister %s, result %s'% (DllPath, result)
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
        """disables the NatLink debug output of loading of natlinkmain is given
        """
        key = "NatlinkmainDebugLoad"
        self.userregnl[key] = 0

    def enableDebugCallbackOutput(self):
        """setting registry key so debug output of callback functions of natlinkmain is given

        """
        key = "NatlinkmainDebugCallback"
        self.userregnl[key] = 1
        

    def disableDebugCallbackOutput(self):
        """disables the NatLink debug output of callback functions of natlinkmain
        """
        key = "NatlinkmainDebugCallback"
        self.userregnl[key] = 0
        
    def enableDebugOutput(self):
        """setting registry key so debug output is in NatSpeak logfile

        not included in configure GUI, as NatSpeak/Natlink.dll seems not to respond
        to this option...
        """
        key = "NatlinkDebug"
        self.userregnl[key] = 1
        

    def disableDebugOutput(self):
        """disables the NatLink lengthy debug output to NatSpeak logfile
        """
        key = "NatlinkDebug"
        self.userregnl[key] = 0

    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
        # also remove usc.vch from VocolaUserDirectory
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
                        oldUscFile = os.path.join(toFolder, oldUscFile)
                        if os.path.isfile(oldUscFile):
                            print 'remove old usc.vcl file: %s'% oldUscFile
                            os.remove(oldUscFile)
                        return
        mess = "could not copy file %s from %s to %s"%(uscFile, fromFolder, toFolder)
        print mess
        return mess
        

    def includeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """include the Unimacro wrapper support line into all Vocola command files
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        toFolder = self.getVocolaUserDir()
        if subDirectory:
            toFolder = os.path.join(toFolder, subDirectory)
            includeLine = 'include ..\\%s;\n'% uscFile
        else:
            includeLine = 'include %s;\n'%uscFile
        oldIncludeLines = ['include %s;'% oldUscFile,
                           'include ..\\%s;'% oldUscFile]
            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print mess
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                correct = 0
                Output = []
                for line in open(F, 'r'):
                    if line.strip() == includeLine.strip():
                        correct = 1
                    for oldLine in oldIncludeLines:
                        if line.strip() == oldLine:
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed or not correct:
                    # changes were made:
                    if not correct:
                        Output.insert(0, includeLine)
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                self.includeUnimacroVchLineInVocolaFiles(F)
        mess = 'changed %s files in %s'% (nFiles, toFolder)
        print mess

    def removeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """remove the Unimacro wrapper support line into all Vocola command files
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        if subDirectory:
            # for recursive call language subfolders:
            toFolder = subDirectory
        else:
            toFolder = self.getVocolaUserDir()
            
        oldIncludeLines = ['include %s;'% oldUscFile,
                           'include ..\\%s;'% oldUscFile,
                           'include %s;'% uscFile,
                           'include ..\\%s;'% uscFile,
                           'include ../%s;'% oldUscFile,
                           'include ../%s;'% uscFile
                           ]
            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print mess
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                Output = []
                for line in open(F, 'r'):
                    for oldLine in oldIncludeLines:
                        if line.strip() == oldLine:
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed:
                    # had break, so changes were made:
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                self.removeUnimacroVchLineInVocolaFiles(F)
        mess = 'removed include lines from %s files in %s'% (nFiles, toFolder)
        print mess


    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesLanguages"
        self.userregnl[key] = 1
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "VocolaTakesLanguages"
        self.userregnl[key] = 0
        
                



def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about NatLink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "iIeEgGyYxXDCVbBNOPlmMrRzZuq"
    shortArgOptions = "d:c:v:n:o:p:"
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
        self.prompt = '\nNatLink/Vocola/Unimacro config> '
        self.info = "type 'u' for usage"
        if Config:
            self.config = Config   # initialized instance of NatlinkConfig
        else:
            self.config = NatlinkConfig()
        self.config.checkNatlinkDllFile()
        self.config.checkPythonPathAndRegistry()
        self.config.checkIniFiles()
        self.checkedConfig = self.config.checkedUrgent
        for key in ObsoleteStatusKeys:
            # see at top of this file!            
            if self.config.userregnl.has_key(key):
                del self.config.userregnl[key]
        print
        print "Type 'u' for a usage message"

    def usage(self):
        """gives the usage of the command line options or options when
        the command line interface  (CLI) is used
        """
        print '-'*60
        print \
"""Use either from the command line like 'natlinkconfigfunctions.py -i'
or in an interactive session using the CLI (command line interface). 

[Status]

i       - info, print information about the NatLink status
I       - reginfo,  print information about the NatLink registry settings

[NatLink]

e/E     - enable/disable NatLink

g/G     - enable/disable debug output, which is sent to the NatSpeak log file
y/Y     - enable/disable debug callback output of natlinkmain 
x/X     - enable/disable debug load output     of natlinkmain

d/D     - set/clear DNSInstallDir, the directory where NatSpeak is installed
c/C     - set/clear DNSINIDir, where NatSpeak INI files are located

[Vocola]

v/V     - enable/disable Vocola by setting/clearing VocolaUserDir, the user
          directory for Vocola user files.

b/B     - enable/disable distinction between languages for Vocola user files

[Unimacro]

n/N     - enable/disable Unimacro by setting/clearing UserDirectory, the
          directory where user NatLink grammar files are located (e.g.,
          ...\My Documents\NatLink)

o/O     - set/clear UnimacroUserDir, where Unimacro user INI files are located
p/P     - set/clear path for program that opens Unimacro INI files.
l       - copy header file Unimacro.vch into Vocola User Directory
m/M     - insert/remove an include line for Unimacro.vch in all Vocola
          command files

[Repair]

r/R     - register/unregister NatLink, the natlink.dll (natlink.pyd) file
          (should not be needed)

z/Z     - silently enables NatLink and registers natlink.dll / disables NatLink
          and unregisters natlink.dll.
      
[Other]

u/usage - give this list
q       - quit

help <command>: give more explanation on <command>
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
currently set inside the NatLink system.

The command reginfo (I) gives all the registry settings
that are used by the NatLink system (HKCU\Software\Natlink).

They are set by either the NatLink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

Settings and registry settings are only "refreshed" into NatLink after
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
"""Set (d <path>) or clear (D) the directory where NatSpeak is installed.

Setting is only needed when NatSpeak is not found at one of the "normal" places.
So setting is often not needed.

When you have a pre-8 version of NatSpeak, setting this option might work.

After you clear this setting, NatLink will, at starting time, again
search for the NatSpeak install directory in the "normal" place(s).
"""
        print '='*60
    help_D = help_d

    # DNS INI directory-----------------------------------------
    def do_c(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Change NatSpeak INI files directory to: %s"% arg
            return self.config.setDNSIniDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    


    def do_C(self, arg):
            print "Clear NatSpeak INI files directory in registry"
            return self.config.clearDNSIniDir()
    def help_c(self):
        print '-'*60
        print \
"""Set (c <path>) or clear (C) the directory where NatSpeak INI file locations
(nssystem.ini and nsapps.ini) are located.

Only needed if these cannot be found in the normal place(s):
-if you have an "alternative" place where you keep your speech profiles
-if you have a pre-8 version of NatSpeak.

After Clearing this registry entry NatLink will, when it is started by NatSpeak,
again search for its INI files in the "default/normal" place(s).
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
            print "Set NatLink User Directory to %s"% arg
            self.config.setUserDirectory(arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def do_N(self, arg):
        print "Clears NatLink User Directory"
        self.config.clearUserDirectory()
    
    def help_n(self):
        print '-'*60
        print \
"""Sets (n <path>) or clears (N) the user directory of NatLink.
This will often be the folder where Unimacro is located.

When you clear this registry entry, you probably disable Unimacro, as
Unimacro is located in the NatLink user directory.

Vocola will still be on, BUT without the possibility to use
Unimacro shorthand commands and meta actions.
"""
        print '='*60
        
    help_N = help_n

    # Unimacro User directory and Editor for Unimacro INI files-----------------------------------
    def do_o(self, arg):
        if os.path.isdir(arg):
            print "Setting Unimacro user directory to %s"% arg
            self.config.setUnimacroUserDir(arg)
        else:
            print 'Please specify a valid path for UnimacroUserDirectory'
            
    def do_O(self, arg):
        print "Clearing Unimacro user directory, falling back to default: %s"% self.config.getUserDirectory()
        self.config.clearUnimacroUserDir()

    def help_o(self):
        print '-'*60
        print \
"""set/clear Unimacro user directory (o <path>/O)

If you specify this directory, your user INI files (and possibly other user
dependent files) will be put there.

If you clear this setting, the user INI files will be put in the
Unimacro directory itself: %s

"""% self.config.getUserDirectory()
        print '='*60

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    def do_p(self, arg):
        if os.path.isfile(arg) and arg.endswith(".exe"):
            print "Setting (path to) Unimacro INI Files editor to %s"% arg
            self.config.setUnimacroIniFilesEditor(arg)
        else:
            print 'Please specify a valid path for the Unimacro INI files editor, not |%s|'% arg
            
    def do_P(self, arg):
        print "Clear Unimacro INI file editor, go back to default Notepad"
        self.config.clearUnimacroIniFilesEditor()

    def help_p(self):
        print '-'*60
        print \
"""set/clear path to Unimacro INI files editor (p <path>/P)

By default (when you clear this setting) "notepad" is used, but:

You can specify a program you like, for example,
TextPad, NotePad++, UltraEdit, or win32pad

You can even specify Wordpad, maybe Microsoft Word...

"""
        print '='*60

    help_P = help_p

    # Unimacro Vocola features-----------------------------------------------
    # managing the include file wrapper business.
    # can be called from the Vocola compatibility button in the config GUI.
    def do_l(self, arg):
        print "Copy include file Unimacro.vch from Unimacro folder into Vocola User Directory"
        self.config.copyUnimacroIncludeFile()

    def help_l(self):
        print '-'*60
        print \
"""Copy Unimacro.vch header file into Vocola User Files directory      (l)

Insert/remove 'include Unimacro.vch' lines into/from each Vocola 
command file                                                        (m/M)

Using Unimacro.vch, you can call Unimacro shorthand commands from a
Vocola command.
"""
        print '='*60

    def do_m(self, arg):
        print 'Insert "include Unimacro.vch" line in each Vocola Command File'
        self.config.includeUnimacroVchLineInVocolaFiles()
    def do_M(self, arg):
        print 'Remove "include Unimacro.vch" line from each Vocola Command File'
        self.config.removeUnimacroVchLineInVocolaFiles()
    help_m = help_M = help_l

        
    # enable/disable NatLink------------------------------------------------
    def do_e(self, arg):
        print "Enabling NatLink:"
        self.config.enableNatlink()
    def do_E(self, arg):
        print "Disabling NatLink:"
        self.config.disableNatlink()

    def help_e(self):
        print '-'*60
        print \
"""Enable NatLink (e) or disable NatLink (E):

When you enable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are done.

After you restart NatSpeak, NatLink should start, opening a window entitled
'Messages from Python Macros'.

When you enable NatLink, the file natlink.dll is (re)registered silently.  Use
the commands r/R to register/unregister natlink.dll explicitly.
(see help r, but most often not needed)

When you disable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are cleared. 

After you restart NatSpeak, NatLink should NOT START ANY MORE
so the window 'Messages from Python Macros' is NOT OPENED.

Note: when you disable NatLink, the natlink.dll file is NOT unregistered.
It is not called any more by NatSpeak, as its declaration is removed from
the Global Clients section of nssystem.ini.
"""
        print "="*60
        
        
    help_E = help_e
  
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        if os.path.isdir(arg):
            print "Setting Vocola user directory to %s\nand (therefore) enabling Vocola:"% arg
            self.config.setVocolaUserDir(arg)
        else:
            print 'Please specify a valid path for the Vocola user directory (see help v)'
            
    def do_V(self, arg):
        print "Clearing Vocola user directory and (therefore) disabling Vocola:"
        self.config.clearVocolaUserDir()

    def help_v(self):
        print '-'*60
        print \
"""Enable/disable Vocola by setting/clearing the Vocola user directory
(v <path>/V).

Vocola is meant to be used with a Vocola user directory.  Therefore
natlinkmain will not enable Vocola if no Vocola user directory is set.

<path> must be an existing folder; NatLink\Vocola in My Documents is a
popular choice.  Thus, Sally under Windows XP might use:

  v C:\Documents and Settings\Sally\My Documents\NatLink\Vocola

You may have to manually create this folder first.
"""
        print '='*60

    help_V = help_v

    # Vocola Command Files Editor-----------------------------------------------
##    def do_w(self, arg):
##        if os.path.isfile(arg) and arg.endswith(".exe"):
##            print "Setting Setting Vocola Command Files editor to %s"% arg
##            self.config.setVocolaCommandFilesEditor(arg)
##        else:
##            print 'Please specify a valid path for Vocola command files editor: |%s|'% arg
##            
##    def do_W(self, arg):
##        print "Clear Vocola commands file editor, go back to default notepad"
##        self.config.clearVocolaCommandFilesEditor()
##
##    def help_w(self):
##        print '-'*60
##        print \
##"""set/clear Vocola  command files editor (w path/W)
##
##By default the editor "notepad" is used.
##
##You can specify a program you like, for example,
##TextPad, NotePad++, UltraEdit, or win32pad.
##
##"""
##    
##        print '='*60
##
##    help_W = help_w
    

    # enable/disable NatLink debug output...
    def do_g(self, arg):
        print "Enable NatLink debug output to NatSpeak logfile "
        self.config.enableDebugOutput()
    def do_G(self, arg):
        print "Disable NatLink debug output to NatSpeak logfile"
        self.config.disableDebugOutput()

    def help_g(self):
        print '-'*60
        print \
"""Enables (g)/disables (G) NatLink debug output (in the NatSpeak log file)
this can be a lot of lines, so preferably disable this one!

Currently it is not clear if this option does anything at all!
But the simplest thing is to keep it Disabled, so the setting
NatlinkDebug is kept to 0
"""
        print '='*60

    help_G = help_g
    # enable/disable NatLink debug output...
    def do_x(self, arg):
        print "Enable natlinkmain debug load output to messages of Python macros window"
        self.config.enableDebugLoadOutput()
    def do_X(self, arg):
        print "Disable natlinkmain debug load output to messages of Python macros window"
        self.config.disableDebugLoadOutput()
    # enable/disable NatLink debug output...
    def do_y(self, arg):
        print "Enable natlinkmain debug Callback output to messages of Python macros window"
        self.config.enableDebugCallbackOutput()
    def do_Y(self, arg):
        print "Disable natlinkmain debug Callback output to messages of Python macros window"
        self.config.disableDebugCallbackOutput()



    def help_x(self):
        print '-'*60
        print \
"""Enable (x)/disable (X) natlinkmain debug load output

Enable (y)/disable (Y) natlinkmain debug callback output

This sends sometimes lengthy debugging messages to the
"Messages from Python Macros" window.

Mainly used when you suspect problems with the working 
of NatLink, so keep off (X and Y) most of the time.
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
        print "Unregister natlink.dll and disable NatLink"
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkDll()
    def do_z(self, arg):
        """register silent and enable NatLink"""
        self.config.registerNatlinkDll(silent=1)
        self.config.enableNatlink(silent=1)
        
    def do_Z(self, arg):
        """(SILENT) Unregister natlink.dll and disable NatLink"""
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkDll(silent=1)

    def help_r(self):
        print '-'*60
        print \
"""Registers (r) / unregisters (R) natlink.dll explicitly.

(Registering is also done (silently) when you enable NatLink, so is mostly NOT
NEEDED!)

But if you do (-r or -R) a message dialog shows up to inform you what happened.
When you unregister, NatLink is also disabled.

If you want to (silently) enable NatLink and register silently use -z,
To disable NatLink and unregister (silently) use Z
"""
        print '='*60
    help_R = help_r
    help_z = help_r
    help_Z = help_r
    

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
"""Enable (b)/disable (B) different Vocola user directories

If enabled, Vocola will look into a subdirectory "xxx" of
VocolaUserDirectory IF the language code of the current user speech
profile is xxx and different from "enx".

So for English users this option will have no effect.

The first time a command file is opened in, for example, a
Dutch speech profile (language code "nld"), a subdirectory "nld" 
is made and all existing Vocola user files are copied into this folder.
"""
        print '='*60

    help_B = help_b

    # enable/disable NatLink debug output...


    def default(self, line):
        print 'no valid entry: %s, type u or usage for list of commands'% line
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

