# coding=latin-1
#
# natlinkconfigfunctions.py
#   This module performs the configuration functions.
#   called from natlinkconfig (a wxPython GUI),
#   or directly, see below
#
#   Quintijn Hoogenboom, January 2008 (...), April 2022
#
#pylint:disable=C0302, W0702, R0904, R0201, C0116, W0613
r"""
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

When NatLink is enabled natlink.pyd is registered with
      win32api.WinExec("regsvr32 /s pathToNatlinkPyd") (silent)

It can be unregistered through function unregisterNatlinkPyd() see below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (e)/disableNatlink() (E)

setUserDirectory(path) (n path) or clearUserDirectory() (N)
etc.

More at the bottom, with the CLI description...

"""
import os
import shutil
import sys
import traceback
import getopt
import cmd
from pathlib import Path
# from win32com.shell import shell
from natlink import natlinkstatus
from natlink import config
from natlink import loader
import win32con

try:
    from win32ui import MessageBox
    def windowsMessageBox(message, title="NatLink configure program"):
        """do messagebox from windows, no wx needed
        """
        MessageBox(message, title)
except:
    import ctypes
    MessageBoxA = ctypes.windll.user32.MessageBoxA
    def windowsMessageBox(message, title="NatLink configure program"):
        """do messagebox from windows, no wx needed
        for old versions of python
        """
        MessageBoxA(None, message, title, 0)

class NatlinkConfig:
    """performs the configuration tasks of NatLink

    SpecialFilenl got from natlinkstatus, as a Class (not instance) variable, so
    should be the same among instances of this class...
    
    the checkCoreDirectory function is automatically performed at start, to see if the initialisation does not
    take place from another place as the registered natlink.pyd...
    
    
    """
    def __init__(self):
        self.DNSName = 'Dragon'
        self.status = natlinkstatus.NatlinkStatus()
        self.config = config.NatlinkConfig.from_first_found_file(loader.config_locations())
        self.message = ''
        
    def warning(self,text):
        """is currently overloaded in GUI"""
        if type(text) in (bytes, str):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print('-'*60)
        print(T)
        print('='*60)
        return T
    
    def error(self,text):
        """is currently overloaded in GUI"""
        if type(text) in (bytes, str):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print('-'*60)
        print(T)
        print('='*60)
        return T
    

    def message(self, text):
        """prints message, can be overloaded in configureGUI
        """
        
        if type(text) in (bytes, str):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print('-'*60)
        print(T)
        print('='*60)


    def setUserDirectory(self, v):
        key = 'UserDirectory'
        if v and self.isValidPath(v):
            print("Setting the UserDirectory of NatLink to %s"% v)
            self.config.set(key, v)
            self.config.delete("Old"+key)
        else:
            print('Setting the UserDirectory of NatLink failed, not a valid directory: %s'% v)
            
        
    def clearUserDirectory(self):
        key = 'UserDirectory'
        oldvalue = self.config.get(key)
        if oldvalue and self.isValidPath(oldvalue):
            self.config.set("Old"+key, oldvalue)
        if self.config.get(key):
            self.config.delete(key)
            print('clearing UserDirectory of NatLink')
        else:
            print('The UserDirectory of NatLink was not set, nothing changed...')
            
    def alwaysIncludeUnimacroDirectoryInPath(self):
        """set variable so natlinkstatus knows to include Unimacro in path
        
        This is only used when userDirectory is set to another directory as Unimacro.
        Unimacro is expected at ../../Unimacro relative to the Core directory
        """
        key = 'IncludeUnimacroInPythonPath'
        Keys = list(self.config.keys())
        print('set %s'% key)
        self.config.set(key, 1)

    def isValidPath(self, path, wantDirectory=None, wantFile=None):
        """return the path, as str, if valid
        
        otherwise return ''
        """
        if not path:
            return ''
        path = Path(path)
        if wantDirectory:
            if path.is_dir():
                return str(path)
        if wantFile:
            if path.is_file():
                return str(path)
        if path.exists():
            return str(path)
        
    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        value = self.config.get(key, None)
        return value

    def setVocolaUserDir(self, v):
        key = 'VocolaUserDirectory'
        if self.isValidPath(v, wantDirectory=1):
            print("Setting VocolaUserDirectory %s and enable Vocola"% v)
            self.config.set(key, v)
            self.config.delete("Old"+key)
        else:
            oldvocdir = self.config.get(key)
            if oldvocdir and self.isValidPath(oldvocdir, wantDirectory=1):
                mess = 'not a valid directory: %s, Vocola remains enabled with VocolaUserDirectory: %s'% (v, oldvocdir)
            else:
                mess = 'not a valid directory: %s, Vocola remains disabled'% v
            return mess

    def clearVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        oldvalue = self.config.get(key)
        if oldvalue and self.isValidPath(oldvalue):
            self.config.set("Old"+key, oldvalue)
        if self.config.get(key):
            self.config.delete(key)
            print('clearing the VocolaUserDirectory and disable Vocola')
        else:
            mess = 'no valid VocolaUserDirectory, so Vocola was already disabled'
            return mess

    ## autohotkey (January 2014)
    def getAhkExeDir(self):
        key = 'AhkExeDir'
        value = self.config.get(key)
        return value

    def setAhkExeDir(self, v):
        key = 'AhkExeDir'
        ahkexedir = self.isValidPath(v, wantDirectory=1)

        if ahkexedir:
            exepath = os.path.join(ahkexedir, 'autohotkey.exe')
            if os.path.isfile(exepath):
                print('Set AutoHotkey Exe Directory (AhkExeDir) to %s'% v)
                self.config.set(key, v)
                self.config.delete('Old'+key)
                return
            else:
                mess = 'path does not contain "autohotkey.exe": %s'% v
        else:
            mess = 'not a valid directory: %s'% v
        return mess

    def clearAhkUserDir(self):
        key = 'AhkUserDir'
        oldvalue = self.config.get(key)
        if oldvalue and self.isValidPath(oldvalue):
            self.config.set("Old"+key, oldvalue)
        if self.config.get(key):
            self.config.delete(key)
            print('Clear AutoHotkey User Directory (AhkUserDir)')
        else:
            mess = 'AutoHotkey User Directory (AhkUserDir) was not set, do nothing'
            return mess
        
    def getAhkUserDir(self):
        key = 'AhkUserDir'
        value = self.config.get(key, None)
        return value

    def setAhkUserDir(self, v):
        key = 'AhkUserDir'
        ahkuserdir = self.isValidPath(v, wantDirectory=1)
        if ahkuserdir:
            print('Set AutoHotkey User Directory (AhkUserDir) to %s'% v)
            self.config.set(key, v)
            self.config.delete('Old'+key)
            return
        else:
            mess = 'not a valid directory: %s'% v
        return mess

    def clearAhkExeDir(self):
        key = 'AhkExeDir'
        oldvalue = self.config.get(key)
        if oldvalue and self.isValidPath(oldvalue):
            self.config.set("Old"+key, oldvalue)
        if self.config.get(key):
            self.config.delete(key)
            print('Clear AutoHotkey Exe Directory (AhkExeDir)')
        else:
            mess = 'AutoHotkey Exe Directory (AhkExeDir) was not set, do nothing'
            return mess


    def getUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        return self.config.get(key, None)

    def setUnimacroUserDir(self, v):
        key = 'UnimacroUserDirectory'
        oldDir = self.getUnimacroUserDir()
        unimacrouserdir = self.isValidPath(v, wantDirectory=1)
        if unimacrouserdir:
            oldDir = self.isValidPath(oldDir, wantDirectory=1)
            if oldDir == unimacrouserdir:
                print('UnimacroUserDirectory is already set to "%s", Unimacro is enabled'% v)
                return
                print('Set UnimacroUserDirectory to %s, enable Unimacro'% v)
            if oldDir:
                print('\n-----------\nConsider copying inifile subdirectories (enx_inifiles or nld_inifiles)\n' \
                      'from old UnimacroUserDirectory (%s) to \n' \
                      'new UnimacroUserDirectory (%s)\n--------\n'% (oldDir, unimacrouserdir))
            self.config.set(key, v)
            self.config.delete('Old'+key)
            return
        else:
            mess = 'not a valid directory: %s, '% v
        return mess

            
    def clearUnimacroUserDir(self):
        """clear but keep previous value"""
        key = 'UnimacroUserDirectory'
        oldValue = self.config.get(key)
        self.config.delete(key)
        oldDirectory = self.isValidPath(oldValue)
        if oldDirectory:
            keyOld = 'Old' + key
            self.config.set(keyOld, oldValue)
        else:
            print('UnimacroUserDirectory was already cleared, Unimacro remains disabled')

    def setUnimacroIniFilesEditor(self, v):
        key = "UnimacroIniFilesEditor"
        exefile = self.isValidPath(v, wantFile=1)
        if exefile and v.endswith(".exe"):
            self.config.set(key, v)
            self.config.delete("Old"+key)
            print('Set UnimacroIniFilesEditor to "%s"'% v)
        else:
            print('not a valid .exe file: %s'% (key, v))
            
    def clearUnimacroIniFilesEditor(self):
        key = "UnimacroIniFilesEditor"
        oldvalue = self.config.get(key)
        oldexefile = self.isValidPath(oldvalue, wantFile=1)
        if oldexefile:
            self.config.set("Old"+key, oldvalue)
        self.config.delete(key)
        print('UnimacroIniFilesEditor cleared')
                
    def enableDebugLoadOutput(self):
        """setting registry key so debug output of loading of natlinkmain is given

        """
        key = "NatlinkmainDebugLoad"
        self.config.set(key, 1)

    def disableDebugLoadOutput(self):
        """disables the NatLink debug output of loading of natlinkmain is given
        """
        key = "NatlinkmainDebugLoad"
        self.config.delete(key)


    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
        # also remove usc.vch from VocolaUserDirectory
        fromFolder = os.path.normpath(os.path.join(thisDir, '..', '..',
                                                   'Unimacro',
                                                   'Vocola_compatibility'))
        toFolder = self.getVocolaUserDir()
        if os.path.isdir(fromFolder):
            fromFile = os.path.join(fromFolder,uscFile)
            if os.path.isfile(fromFile):
                if os.path.isdir(toFolder):
                    
                    toFile = os.path.join(toFolder, uscFile)
                    if os.path.isfile(toFile):
                        print('remove previous %s'% toFile)
                        try:
                            os.remove(toFile)
                        except:
                            pass
                    print('copy %s from %s to %s'%(uscFile, fromFolder, toFolder))
                    try:
                        shutil.copyfile(fromFile, toFile)
                    except:
                        pass
                    else:
                        oldUscFile = os.path.join(toFolder, oldUscFile)
                        if os.path.isfile(oldUscFile):
                            print('remove old usc.vcl file: %s'% oldUscFile)
                            os.remove(oldUscFile)
                        return
        mess = "could not copy file %s from %s to %s"%(uscFile, fromFolder, toFolder)
        print(mess)
        return mess
        

    def includeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """include the Unimacro wrapper support line into all Vocola command files
        
        as a side effect, set the variable for Unimacro in Vocola support:
        VocolaTakesUnimacroActions...
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
                           'include ..\\%s;'% oldUscFile,
                           'include %s;'% uscFile.lower(),
                           'include ..\\%s;'% uscFile.lower(),
                           ]
            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print(mess)
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
                # subdirectory, recursive
                self.includeUnimacroVchLineInVocolaFiles(F)
        self.enableVocolaTakesUnimacroActions()
        mess = 'changed %s files in %s, and set the variable "%s"'% (nFiles, toFolder,
                                                                     "VocolaTakesUnimacroActions")
        
        print(mess)

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
                           'include ../%s;'% uscFile,
                           'include %s;'% uscFile.lower(),
                           'include ..\\%s;'% uscFile.lower(),
                           'include ../%s;'% uscFile.lower(),
                           ]

            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print(mess)
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
        print(mess)


    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesLanguages"
        self.config.set(key, 1)
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "VocolaTakesLanguages"
        self.config.set(key, 0)

    def enableVocolaTakesUnimacroActions(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesUnimacroActions"
        self.config.set(key, 1)
        

    def disableVocolaTakesUnimacroActions(self):
        """disables so Vocola does not take Unimacro Actions
        """
        key = "VocolaTakesUnimacroActions"
        self.config.set(key, 0)
        
                



def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about NatLink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "aAiIeEfFgGyYxXDCVbBNOPlmMrRzZuq"
    shortArgOptions = "d:c:v:n:o:p:"
    if Options:
        if type(Options) == bytes:
            Options = Options.split(" ", 1)
        Options = [_.strip() for _ in  Options]
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, shortOptions+shortArgOptions)
    except getopt.GetoptError:
        print('invalid option: %s'% repr(Options))
        cli.usage()
        return

    if args:
        print('should not have extraneous arguments: %s'% repr(args))
    for o, v in options:
        o = o.lstrip('-')
        funcName = 'do_%s'% o
        func = getattr(cli, funcName, None)
        if not func:
            print('option %s not found in cli functions: %s'% (o, funcName))
            cli.usage()
            continue
        if o in shortOptions:
            func(None) # dummy arg
        elif o in shortArgOptions:
            func(v)
        else:
            print('options should not come here')
            cli.usage()


          
class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self, Config=None):
        cmd.Cmd.__init__(self)
        self.prompt = '\nNatLink config> '
        self.info = "type 'u' for usage"
        self.config = Config   # initialized instance of NatlinkConfig
        self.message = ''
        if __name__ == "__main__":
            print("Type 'u' for a usage message")

    def stripCheckDirectory(self, dirName):
        """allow quotes in input, and strip them.
        
        Return "" if directory is not valid
        """
        if not dirName:
            return ""
        n = dirName.strip()
        while n and n.startswith('"'):
            n = n.strip('"')
        while n and n.startswith("'"):
            n = n.strip("'")
        if n:
            n.strip()
        
        if os.path.isdir(n):    
            return n
        else:
            print('not a valid directory: %s (%s)'% (n, dirName))
            return ''

    def usage(self):
        """gives the usage of the command line options or options when
        the command line interface  (CLI) is used
        """
        print('-'*60)
        print(r"""Use either from the command line like 'natlinkconfigfunctions.py -i'
or in an interactive session using the CLI (command line interface). 

[Status]

i       - info, print information about the NatLink status
I       - settings, print information about the natlinkstatus.ini settings
j       - print PythonPath variable

[NatLink]

e/E     - enable/disable NatLink

y/Y     - enable/disable debug callback output of natlinkmain 
x/X     - enable/disable debug load output     of natlinkmain

d/D     - set/clear DNSInstallDir, the directory where NatSpeak/Dragon is installed
c/C     - set/clear DNSINIDir, where NatSpeak/Dragon INI files are located

[Vocola]

v/V     - enable/disable Vocola by setting/clearing VocolaUserDir, the user
          directory for Vocola user files (~ or %HOME% allowed).

b/B     - enable/disable distinction between languages for Vocola user files
a/A     - enable/disable the possibility to use Unimacro actions in Vocola

[Unimacro]

o/O     - enable/disable Unimacro, by setting/clearing the UnimacroUserDirectory, where
          the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)
p/P     - set/clear path for program that opens Unimacro INI files.
l       - copy header file Unimacro.vch into Vocola User Directory
m/M     - insert/remove an include line for Unimacro.vch in all Vocola
          command files

[UserDirectory]
n/N     - enable/disable UserDirectory, the directory where
          User NatLink grammar files are located (e.g., ...\My Documents\NatLink)

[Repair]
r/R     - register/unregister NatLink, the natlink.pyd (natlink.pyd) file
          (should not be needed)
z/Z     - silently enables NatLink and registers natlink.pyd / disables NatLink
          and unregisters natlink.pyd.
[AutoHotkey]
h/H     - set/clear the AutoHotkey exe directory.
k/K     - set/clear the User Directory for AutoHotkey scripts.
[Other]

u/usage - give this list
q       - quit

help <command>: give more explanation on <command>
        """)
        print('='*60)

    # info----------------------------------------------------------
    def do_i(self, arg):
        S = self.config.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart %s'% self.DNSName
        print(S)
    def do_I(self, arg):
        # inifile natlinkstatus.ini settings:
        self.config.printInifileSettings()
    def do_j(self, arg):
        # print PythonPath:
        self.config.printPythonPath()

    def help_i(self):
        print('-'*60)
        print("""The command info (i) gives an overview of the settings that are
currently set inside the NatLink system.

The command settings (I) gives all the NatLink settings, kept in
natlinkstatus.ini (overlap with (i))

The command (j) gives the PythonPath variable which should contain several
NatLink directories after the config GUI runs succesfully

Settings are set by either the NatLink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

After you change settings, restart %s.
"""% self.DNSName)
        print('='*60)
    help_j = help_I = help_i

    # DNS install directory------------------------------------------
    def do_d(self, arg):
        if not arg:
            self.message = "please enter a directory"
            return
        self.message = "Change Dragon directory to: %s"% arg
        return self.config.setDNSInstallDir(arg)

    def do_D(self, arg):
        self.message = "Clear DNS directory in registry"
        print('do action: %s'% self.message)
        return self.config.clearDNSInstallDir()

    def help_d(self):
        print('-'*60)
        print("""Set (d <path>) or clear (D) the directory where %s is installed.

Setting is only needed when %s is not found at one of the "normal" places.
So setting is seldom not needed.

When you have a pre-8 version of NatSpeak, setting this option might work.

After you clear this setting, NatLink will, at starting time, again
search for the %s install directory in the "normal" place(s).
"""% (self.DNSName, self.DNSName, self.DNSName))
        print('='*60)
    help_D = help_d

    # DNS INI directory-----------------------------------------
    def do_c(self, arg):
        arg = self.stripCheckDirectory(arg)  # also quotes
        if not arg:
            return
        self.message = "Change %s INI files directory to: %s"% (self.DNSName, arg)
        return self.config.setDNSIniDir(arg)
    


    def do_C(self, arg):
        self.message = "Clear %s INI files directory in registry"% self.DNSName
        print('do action: %s'% self.message)
        return self.config.clearDNSIniDir()
    def help_c(self):
        print('-'*60)
        print("""Set (c <path>) or clear (C) the directory where %s INI file locations
(nssystem.ini and nsapps.ini) are located.

Only needed if these cannot be found in the normal place(s):
-if you have an "alternative" place where you keep your speech profiles
-if you have a pre-8 version of NatSpeak.

After Clearing this registry entry NatLink will, when it is started by %s,
again search for its INI files in the "default/normal" place(s).
"""% (self.DNSName, self.DNSName))
        print('='*60)
    help_C = help_c
    
    # User Directories -------------------------------------------------
    def do_n(self, arg):
        if not arg:
            print('also enter a valid folder')
            return
        arg = arg.strip()
        self.config.setUserDirectory(arg)
    
    def do_N(self, arg):
        self.message = "Clears NatLink User Directory"
        self.config.clearUserDirectory()

    # def do_f(self, arg):
    #     self.message = "Include UnimacroDirectory in PythonPath even if Unimacro is disabled"
    #     print 'do action: %s'% self.message
    #     self.config.alwaysIncludeUnimacroDirectoryInPath()
    # def do_F(self, arg):
    #     self.message = "Do NOT include UnimacroDirectory in PythonPath when Unimacro is disabled"
    #     self.config.ignoreUnimacroDirectoryInPathIfNotUserDirectory()
    
    def help_n(self):
        print('-'*60)
        print("""Sets (n <path>) or clears (N) the UserDirectory of NatLink.
This is the folder where your own python grammar files are/will be located.

Note this should NOT be the BaseDirectory (Vocola is there) of the Unimacro directory.
""")
        print('='*60)
        
    help_N = help_n
    
    # Unimacro User directory and Editor or Unimacro INI files-----------------------------------
    def do_o(self, arg):
        arg = self.stripCheckDirectory(arg)  # also quotes
        if not arg:
            return
        self.config.setUnimacroUserDir(arg)
            
    def do_O(self, arg):
        self.message = "Clearing Unimacro user directory, and disable Unimacro"
        print('do action: %s'% self.message)
        self.config.clearUnimacroUserDir()

    def help_o(self):
        print('-'*60)
        userDir = self.config.getUserDirectory()
        print(r"""set/clear UnimacroUserDirectory (o <path>/O)

And enable/disable Unimacro.

In this directory, your user INI files (and possibly other user
dependent files) will be put.

You can use (if entered through the CLI) "~" (or %%HOME%%) for user home directory, or
another environment variable (%%...%%). (example: "o ~\NatLink\\Unimacro")

Setting this directory also enables Unimacro. Clearing it disables Unimacro
""")
        print('='*60)

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    def do_p(self, arg):
        if os.path.isfile(arg) and arg.endswith(".exe"):
            self.message = "Setting (path to) Unimacro INI Files editor to %s"% arg
            print('do action: %s'% self.message)
            self.config.setUnimacroIniFilesEditor(arg)
        else:
            print('Please specify a valid path for the Unimacro INI files editor, not |%s|'% arg)
            
    def do_P(self, arg):
        self.message = "Clear Unimacro INI file editor, go back to default Notepad"
        print('do action: %s'% self.message)
        self.config.clearUnimacroIniFilesEditor()

    def help_p(self):
        print('-'*60)
        print("""set/clear path to Unimacro INI files editor (p <path>/P)

By default (when you clear this setting) "notepad" is used, but:

You can specify a program you like, for example,
TextPad, NotePad++, UltraEdit, or win32pad

You can even specify Wordpad, maybe Microsoft Word...

""")
        print('='*60)

    help_P = help_p

    # Unimacro Vocola features-----------------------------------------------
    # managing the include file wrapper business.
    # can be called from the Vocola compatibility button in the config GUI.
    def do_l(self, arg):
        self.message = "Copy include file Unimacro.vch into Vocola User Directory"
        print('do action: %s'% self.message)
        self.config.copyUnimacroIncludeFile()

    def help_l(self):
        print('-'*60)
        print("""Copy Unimacro.vch header file into Vocola User Files directory      (l)

Insert/remove 'include Unimacro.vch' lines into/from each Vocola 
command file                                                        (m/M)

Using Unimacro.vch, you can call Unimacro shorthand commands from a
Vocola command.
""")
        print('='*60)

    def do_m(self, arg):
        self.message = 'Insert "include Unimacro.vch" line in each Vocola Command File'
        print('do action: %s'% self.message)
        self.config.includeUnimacroVchLineInVocolaFiles()
    def do_M(self, arg):
        self.message = 'Remove "include Unimacro.vch" line from each Vocola Command File'
        print('do action: %s'% self.message)
        self.config.removeUnimacroVchLineInVocolaFiles()
    help_m = help_M = help_l

        
    # enable/disable NatLink------------------------------------------------
    def do_e(self, arg):
        self.message = "Enabling NatLink:"
        print('do action: %s'% self.message)
        self.config.enableNatlink()
    def do_E(self, arg):
        self.message = "Disabling NatLink:"
        self.config.disableNatlink()

    def help_e(self):
        print('-'*60)
        print("""Enable NatLink (e) or disable NatLink (E):

When you enable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are done.

These options require elevated mode and probably Dragon be closed.

After you restart %s, NatLink should start, opening a window titled
'Messages from NatLink - ...'.

When you enable NatLink, the file natlink.pyd is (re)registered silently.  Use
the commands r/R to register/unregister natlink.pyd explicitly.
(see help r, but most often not needed)

When you disable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are cleared. 

After you restart %s, NatLink should NOT START ANY MORE
so the window 'Messages from NatLink' is NOT OPENED.

Note: when you disable NatLink, the natlink.pyd file is NOT unregistered.
It is not called any more by %s, as its declaration is removed from
the Global Clients section of nssystem.ini.
"""% (self.DNSName, self.DNSName, self.DNSName))
        print("="*60)
        
        
    help_E = help_e
  
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        if not arg:
            self.message = "do_v should have an argument"
            return
        tryPath = self.config.isValidPath(arg)
        if not tryPath:
            self.message = "do_v, not a valid path: %s"% arg
            return
        self.message =  'Set VocolaUserDirectory to "%s" and enable Vocola'% arg
        print('do action: %s'% self.message)
        self.config.setVocolaUserDir(arg)
            
    def do_V(self, arg):
        self.message = "Clear VocolaUserDirectory and (therefore) disable Vocola"
        print('do action: %s'% self.message)
        self.config.clearVocolaUserDir()

    def help_v(self):
        print('-'*60)
        print("""Enable/disable Vocola by setting/clearing the VocolaUserDirectory
(v <path>/V).

In this VocolaUserDirectory your Vocola Command File are/will be located.

<path> must be an existing folder; NatLink\Vocola in My Documents is a
popular choice.

You may have to manually create this folder first.
""")
        print('='*60)

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
    
## testing:
    def do_s(self, arg):
        pydPath = r"C:\natlink\natlink\macrosystem\core\natlink.pyd"
        print('registered?: %s'% self.config.PydIsRegistered(pydPath))
        pass
    def do_g(self, arg):
        print('no valid option')
        pass
    def do_G(self, arg):
        print('no valid option')

    def help_g(self):
        print('-'*60)
        print("""not a valid option
""")
        print('='*60)

    help_G = help_g
    # enable/disable NatLink debug output...
    def do_x(self, arg):
        self.message = 'Enable natlinkmain giving debugLoad output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.config.enableDebugLoadOutput()
    def do_X(self, arg):
        self.message = 'Disable natlinkmain giving debugLoad output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.config.disableDebugLoadOutput()
    # enable/disable NatLink debug output...
    def do_y(self, arg):
        self.message = 'Enable natlinkmain giving debugCallback output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.config.enableDebugCallbackOutput()
    def do_Y(self, arg):
        self.message = 'Disable natlinkmain giving debugCallback output to messages of "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.config.disableDebugCallbackOutput()



    def help_x(self):
        print('-'*60)
        print("""Enable (x)/disable (X) natlinkmain debug load output

Enable (y)/disable (Y) natlinkmain debug callback output

Nearly obsolete options.

This sends sometimes lengthy debugging messages to the
"Messages from NatLink" window.

Mainly used when you suspect problems with the working 
of NatLink, so keep off (X and Y) most of the time.
""")
        print('='*60)

    help_y = help_x
    help_X = help_x
    help_Y = help_x
    
    # register natlink.pyd
    def do_r(self, arg):
        self.message = "(Re) register and enable natlink.pyd is done from the installer program"
        
    def do_R(self, arg):
        self.message = 'Unregister natlink.pyd and disable NatLink is done from the installer program,\nyou can uninstall Natlink via "Add or remove Programs" in Windows'
        
    def do_z(self, arg):
        """register silent and enable NatLink"""
        self.message('this function is obsolete')
        
    def do_Z(self, arg):
        """(SILENT) Unregister natlink.pyd and disable NatLink"""
        self.message('this function is obsolete')

    # different Vocola options
    def do_b(self, arg):
        self.message = "Enable Vocola different user directories for different languages"
        print('do action: %s'% self.message)
        self.config.enableVocolaTakesLanguages()
    def do_B(self, arg):
        self.message = "Disable Vocola different user directories for different languages"
        print('do action: %s'% self.message)
        self.config.disableVocolaTakesLanguages()

    def do_a(self, arg):
        self.message = "Enable Vocola taking Unimacro actions"
        print('do action: %s'% self.message)
        self.config.enableVocolaTakesUnimacroActions()
    def do_A(self, arg):
        self.message = "Disable Vocola taking Unimacro actions"
        print('do action: %s'% self.message)
        self.config.disableVocolaTakesUnimacroActions()

    def help_a(self):
        print('-'*60)
        print("""----Enable (a)/disable (A) Vocola taking Unimacro actions.
        
These actions (Unimacro Shorthand Commands) and "meta actions" are processed by
the Unimacro actions module.

If Unimacro is NOT enabled, it will also
be necessary that the UnimacroDirectory is put in the python path.
The special option for that is (f).

Note this option (f) is only needed when you use Vocola with Unimacro actions,
but you do not use Unimacro.
""")
        print('='*60)
        
    def help_b(self):
        print('-'*60)
        print("""----Enable (b)/disable (B) different Vocola User Directories

If enabled, Vocola will look into a subdirectory "xxx" of
VocolaUserDirectory IF the language code of the current user speech
profile is "xxx" and  is NOT "enx".

So for English users this option will have no effect.

The first time a command file is opened in, for example, a
Dutch speech profile (language code "nld"), a subdirectory "nld" 
is created, and all existing Vocola Command files for this Dutch speech profile are copied into this folder.

When you use your English speech profile again, ("enx") the Vocola Command files in the VocolaUserDirectory are taken again.
""")
        print('='*60)

    help_B = help_b
    help_A = help_a

    # autohotkey settings:
    def do_h(self, arg):
        self.message = 'set directory of AutoHotkey.exe to: %s'% arg
        print('do action: %s'% self.message)
        self.config.setAhkExeDir(arg)

    def do_H(self, arg):
        self.message = 'clear directory of AutoHotkey.exe, return to default'
        print('do action: %s'% self.message)
        self.config.clearAhkExeDir()

    def do_k(self, arg):
        arg = self.stripCheckDirectory(arg)  # also quotes
        if not arg:
            return
        self.message = 'set user directory for AutoHotkey scripts to: %s'% arg
        self.config.setAhkUserDir(arg)

    def do_K(self, arg):
        self.message = 'clear user directory of AutoHotkey scripts, return to default'
        print('do action: %s'% self.message)
        self.config.clearAhkUserDir()
            
    def help_h(self):
        print('-'*60)
        print("""----Set (h)/clear (return to default) (H) the AutoHotkey exe directory.
       Assume autohotkey.exe is found there (if not AutoHotkey support will not be there)
       If set to a invalid directory, AutoHotkey support will be switched off.
       
       Set (k)/clear (return to default) (K) the User Directory for AutoHotkey scripts.
       
       Note: currently these options can only be run from the natlinkconfigfunctions.py script.
""")
        print('='*60)

    help_H = help_k = help_K = help_h

    # enable/disable NatLink debug output...

    def default(self, line):
        print(f'no valid entry: "{line}", type "u" or "usage" for list of commands')
        print()

    def do_quit(self, arg):
        sys.exit()
    do_q = do_quit
    def do_usage(self, arg):
        self.usage()
    do_u = do_usage
    def help_u(self):
        print('-'*60)
        print("""u and usage give the list of commands
lowercase commands usually set/enable something
uppercase commands usually clear/disable something
Informational commands: i and I
""")
    help_usage = help_u
    

        
if __name__ == "__main__":
    if len(sys.argv) == 1:
        cli = CLI()
        cli.info = "type u for usage"
        try:
            cli.cmdloop()
        except (KeyboardInterrupt, SystemExit):
            pass
    else:
       _main()

