# coding=latin-1
#
# natlinkconfigfunctions.py
#   This module performs the configuration functions.
#   called from natlinkconfig (a wxPython GUI),
#   or directly, see below
#
#   Quintijn Hoogenboom, January 2008 (...), April 2022
#
#pylint:disable=C0302, W0702, R0904, R0201, C0116, W0613, R0914, R0912
r"""
With the functions in this module Natlink can be configured.

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

When Natlink is enabled natlink.pyd is registered with
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
import getopt
import cmd
from pathlib import Path
import configparser
import subprocess
# from win32com.shell import shell
from natlink import natlinkstatus
from natlink import config
from natlink import loader
from natlink import readwritefile

class NatlinkConfig:
    """performs the configuration tasks of Natlink
    
    setting UserDirectory, UnimacroDirectory and options, VocolaDirectory and options,
    Autohotkey options (ahk), and Debug option of Natlink.

    Changes are written in the config file, from which the path is taken from the loader instance.
    """
    def __init__(self):
        self.DNSName = 'Dragon'
        self.status = natlinkstatus.NatlinkStatus()
        self.config_path = loader.config_locations()[0]
        self.getConfig()  # gets self.config and self.config_encoding
        
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

    def getConfig(self):
        """return the config instance
        """
        rwfile = readwritefile.ReadWriteFile()
        config_text = rwfile.readAnything(self.config_path)
        self.config = configparser.ConfigParser()
        self.config.read_string(config_text)
        self.config_encoding = rwfile.encoding

    def setconfigsetting(self, section, option, value):
        """set a setting into an inifile (possibly other than natlink.ini)
    
        Set the setting in self.config.
        
        Then write with the setting included to config_path with config_encoding.
        When this encoding is ascii, but there are (new) non-ascii characters,
        the file is written as 'utf-8'.

        """
        self.config.set(section, option, str(value))
        try:
            with open(self.config_path, 'w', encoding=self.config_encoding) as fp:
                self.config.write(fp)   
        except UnicodeEncodeError as exc:
            if self.config_encoding != 'ascii':
                print(f'UnicodeEncodeError, cannot encode with encoding "{self.config_encoding}" the config data to file "{self.config_path}"')
                raise UnicodeEncodeError from exc
            with open(self.config_path, 'w', encoding='utf-8') as fp:
                self.config.write(fp)   

    def setUserDirectory(self, v):  
        key = 'UserDirectory'
        if v and self.isValidPath(v):
            print("Setting the UserDirectory of Natlink to %s"% v)
            self.setconfigsetting('directories', key, v)
            # self.config.remove_option('directories', "Old"+key)
        else:
            print('Setting the UserDirectory of Natlink failed, not a valid directory: %s'% v)
            
        
    def clearUserDirectory(self):
        key = 'UserDirectory'
        old_value = self.config.get('directories', key)
        if not old_value:
            print('The UserDirectory of Natlink was not set, nothing changed...')
            return
        if self.isValidPath(old_value):
            self.config.set('previous directories', key, old_value)
        self.config.remove_option('directories', key)
        print('clearing UserDirectory of Natlink')
            
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
        return ''
        
    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        value = self.config.get(key, None)
        return value

    def setVocolaUserDir(self, v):
        key = 'VocolaUserDirectory'
        if self.isValidPath(v, wantDirectory=1):
            print("Setting VocolaUserDirectory %s and enable Vocola"% v)
            self.config.set(key, v)
            self.config.remove_option('previous directories', key)
            return True
        oldvocdir = self.config.get('previous directories', key)
        if oldvocdir and self.isValidPath(oldvocdir, wantDirectory=1):
            mess = 'not a valid directory: %s, Vocola remains enabled with VocolaUserDirectory: %s'% (v, oldvocdir)
        else:
            mess = 'not a valid directory: %s, Vocola remains disabled'% v
        return mess

    def clearVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        old_value = self.config.get('directories', key)
        if old_value and self.isValidPath(old_value):
            self.config.set('previous directories', key, old_value)
        if self.config.get('directories', key):
            self.config.remove_option('directories', key)
            print('clearing the VocolaUserDirectory and disable Vocola')
        else:
            mess = 'no valid VocolaUserDirectory, so Vocola was already disabled'
            return mess
        return True

    ## autohotkey (January 2014)
    def getAhkExeDir(self):
        key = 'AhkExeDir'
        value = self.config.get('directories', key)
        return value

    def setAhkExeDir(self, v):
        key = 'AhkExeDir'
        ahkexedir = self.isValidPath(v, wantDirectory=1)

        if not ahkexedir:
            mess = f'not a valid directory: "{v}"'
            return mess
        exepath = os.path.join(ahkexedir, 'autohotkey.exe')
        if not os.path.isfile(exepath):
            mess = f'path does not contain "autohotkey.exe": "{v}"'

        print('Set AutoHotkey Exe Directory (AhkExeDir) to %s'% v)
        self.config.set(key, v)
        self.config.remove_option('directories', 'Old'+key)
        return True

    def clearAhkUserDir(self):
        key = 'AhkUserDir'
        old_value = self.config.get('autohotkey', key)
        if old_value:
            if self.isValidPath(old_value):
                self.config.set('previous directories', key, old_value)
            self.config.remove_option('autohotkey', key)
            print('Clear AutoHotkey User Directory (AhkUserDir)')
            return True 
        print('AutoHotkey User Directory (AhkUserDir) was not set, do nothing')
        return True
                
    def getAhkUserDir(self):
        key = 'AhkUserDir'
        value = self.config.get('autohotkey', key)
        return value

    def setAhkUserDir(self, v):
        key = 'AhkUserDir'
        ahkuserdir = self.isValidPath(v, wantDirectory=1)
        if not ahkuserdir:
            mess = f'not a valid directory: "{v}"'
            return mess
        print(f'Set AutoHotkey User Directory (AhkUserDir) to "{v}"')
        self.config.set('autohotkey', key, v)
        self.config.remove_option('previous directories', key)
        return True

    def clearAhkExeDir(self):
        key = 'AhkExeDir'
        old_value = self.config.get('directories', key)
        if old_value and self.isValidPath(old_value):
            self.config.set('previous directories', key, old_value)
        if self.config.get('directories', key):
            self.config.remove_option('directories', key)
            print('Clear AutoHotkey Exe Directory (AhkExeDir)')
        else:
            mess = 'AutoHotkey Exe Directory (AhkExeDir) was not set, do nothing'
            return mess
        return True

    def getUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        return self.config.get(key, None)

    def setUnimacroUserDir(self, v):
        key = 'UnimacroUserDirectory'
        oldDir = self.getUnimacroUserDir()
        unimacrouserdir = self.isValidPath(v, wantDirectory=1)
        if not unimacrouserdir:
            mess = f'not a valid directory: {v}'
            return mess

        oldDir = self.isValidPath(oldDir, wantDirectory=1)
        if oldDir == unimacrouserdir:
            print('UnimacroUserDirectory is already set to "%s", Unimacro is enabled'% v)
            return True
        if oldDir:
            print('\n-----------\nConsider copying inifile subdirectories (enx_inifiles or nld_inifiles)\n' \
                  'from old UnimacroUserDirectory (%s) to \n' \
                  'new UnimacroUserDirectory (%s)\n--------\n'% (oldDir, unimacrouserdir))
        self.config.set('directories', key, v)
        self.config.remove_option('previous directories', key)
        return True

            
    def clearUnimacroUserDir(self):
        """clear but keep previous value"""
        key = 'UnimacroUserDirectory'
        oldValue = self.config.get('directories', key)
        self.config.remove_option('directories', key)
        oldDirectory = self.isValidPath(oldValue)
        if oldDirectory:
            self.config.set('previous directories', key, oldValue)
        else:
            print('UnimacroUserDirectory was already cleared, Unimacro remains disabled')

    def setUnimacroIniFilesEditor(self, v):
        key = "UnimacroIniFilesEditor"
        exefile = self.isValidPath(v, wantFile=1)
        if exefile and v.endswith(".exe"):
            self.config.set('unimacro', key, v)
            self.config.remove_option('previous directories', key)
            print(f'Set {key} to "{v}"')
            return True
        mess = f'not a valid .exe file: "{v}" (setting: "{key}")'
        return mess
            
    def clearUnimacroIniFilesEditor(self):
        key = "UnimacroIniFilesEditor"
        old_value = self.config.get('unimacro', key)
        oldexefile = self.isValidPath(old_value, wantFile=1)
        if oldexefile:
            self.config.set('previous directories', key, old_value)
        self.config.remove_option('unimacro', key)
        print('UnimacroIniFilesEditor cleared')
        return True
                
    def enableDebugOutput(self):
        """setting registry key so debug output of loading of natlinkmain is given

        """
        key = "NatlinkmainDebug"
        old_value = self.config.get('options', 'log_level')
        if old_value:
            if old_value == 'DEBUG':
                print(f'enableDebugOutput, setting already "{old_value}"')
                return True
            self.config.set('previous settings', key, old_value)
        self.config.set('options', 'log_level', 'DEBUG')
        return True

    def disableDebugLoadOutput(self):
        """disables the Natlink debug output of loading of natlinkmain is given
        """
        key = 'log_level'
        section = 'options'
        old_value = self.config.get('previous settings', key)
        if old_value:
            self.config.remove_option('previous settings', key)
        else:
            old_value = 'INFO'
        self.config.set(section, key, old_value)
        return True


    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        # also remove usc.vch from VocolaUserDirectory
        unimacroDir = self.status.getUnimacroDirectory()
        fromFolder = Path(unimacroDir)/'Vocola_compatibility'
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not unimacroDir.is_dir():
            mess = f'unimacroDir "{str(unimacroDir)}" is not a directory'
            return mess
        fromFile = fromFolder/uscFile
        if not fromFile.is_file():
            mess = f'file "{str(fromFile)}" does not exist (is not a valid file)'
            return mess
        if not toFolder.is_dir():
            mess = f'vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            return mess
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            print(f'remove previous "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'Could not remove previous version of "{str(toFile)}"'
                return mess
        try:
            shutil.copyfile(fromFile, toFile)
            print(f'copied "{uscFile}" from "{str(fromFolder)}" to "{str(toFolder)}"')
        except:
            mess = f'Could not copy new version of "{uscFile}", from "{str(fromFolder)}" to "{str(toFolder)}"'
            return mess
        return True

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
        toFolder = self.status.getVocolaUserDirectory()
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
        return True

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
        return True

    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesLanguages"
        self.config.set('vocola', key, 'True')
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "VocolaTakesLanguages"
        self.config.set('vocola', key, 'False')

    def enableVocolaTakesUnimacroActions(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesUnimacroActions"
        self.config.set('vocola', key, 'True')
        

    def disableVocolaTakesUnimacroActions(self):
        """disables so Vocola does not take Unimacro Actions
        """
        key = "VocolaTakesUnimacroActions"
        self.config.set('vocola', key, 'False')

    def openConfigFile(self):
        """open the natlink.ini config file
        """
        try:
            subprocess.run(self.config_path, check=True)
            print(f'opened the config file: "{self.config_path}"')
        except subprocess.CalledProcessError:
            mess = 'Could not open the config file "{self.config_path}"'
            return mess
        return True

    def printPythonPath(self):
        raise NotImplementedError 


def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about Natlink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "aAiIeEfFgGyYxXDCVbBNOPlmMrRzZuq"
    shortArgOptions = "d:c:v:n:o:p:"
    if Options:
        if isinstance(Options, str):
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
        self.prompt = '\nNatlink config> '
        self.info = "type 'u' for usage"
        self.Config = None
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

i       - info, print information about the Natlink status
I       - settings, print information about the config file of Natlink
j       - print PythonPath variable

[Natlink]

x/X     - enable/disable debug output of Natlink

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
          User Natlink grammar files are located (e.g., "~\UserDirectory")

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
        S = self.Config.status.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart Dragon'
        print(S)
    def do_I(self, arg):
        # inifile natlinkstatus.ini settings:
        self.Config.openConfigFile()
    def do_j(self, arg):
        # print PythonPath:
        self.Config.printPythonPath()

    def help_i(self):
        print('-'*60)
        print("""The command info (i) gives an overview of the settings that are
currently set inside the Natlink system.

The command settings (I) gives all the Natlink settings as got from natlinkstatus.py,
or from the config file of Natlink (overlap with (i))

The command (j) gives the PythonPath variable which should contain several
Natlink directories after the config GUI runs succesfully

Settings are set by either the Natlink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

After you change settings, restart Dragon.
""")
        print('='*60)
    help_j = help_I = help_i
    
    # User Directories -------------------------------------------------
    # for easier remembering, change n to d (DragonFly)
    def do_d(self, arg):
        if not arg:
            print('also enter a valid folder')
            return
        arg = arg.strip()
        directory = createIfNotThere(arg)
        if not directory:
            return
        self.Config.setUserDirectory(directory)
    
    def do_D(self, arg):
        self.message = "Clears Natlink User Directory"
        self.Config.clearUserDirectory()
    
    do_n = do_d
    do_N = do_D

    def help_n(self):
        print('-'*60)
        print("""Sets (n <path>) or clears (N) the UserDirectory of Natlink.
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
        self.Config.setUnimacroUserDir(arg)
            
    def do_O(self, arg):
        self.message = "Clearing Unimacro user directory, and disable Unimacro"
        print('do action: %s'% self.message)
        self.Config.clearUnimacroUserDir()

    def help_o(self):
        print('-'*60)
        userDir = self.Config.getUserDirectory()
        print(r"""set/clear UnimacroUserDirectory (o <path>/O)

And enable/disable Unimacro.

In this directory, your user INI files (and possibly other user
dependent files) will be put.

You can use (if entered through the CLI) "~" (or %%HOME%%) for user home directory, or
another environment variable (%%...%%). (example: "o ~\Natlink\\Unimacro")

Setting this directory also enables Unimacro. Clearing it disables Unimacro
""")
        print('='*60)

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    def do_p(self, arg):
        if os.path.isfile(arg) and arg.endswith(".exe"):
            self.message = "Setting (path to) Unimacro INI Files editor to %s"% arg
            print('do action: %s'% self.message)
            self.Config.setUnimacroIniFilesEditor(arg)
        else:
            print('Please specify a valid path for the Unimacro INI files editor, not |%s|'% arg)
            
    def do_P(self, arg):
        self.message = "Clear Unimacro INI file editor, go back to default Notepad"
        print('do action: %s'% self.message)
        self.Config.clearUnimacroIniFilesEditor()

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
        self.Config.copyUnimacroIncludeFile()

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
        self.Config.includeUnimacroVchLineInVocolaFiles()
    def do_M(self, arg):
        self.message = 'Remove "include Unimacro.vch" line from each Vocola Command File'
        print('do action: %s'% self.message)
        self.Config.removeUnimacroVchLineInVocolaFiles()
    help_m = help_M = help_l

        
    # enable/disable Natlink------------------------------------------------
    def do_e(self, arg):
        self.message = "Enabling Natlink:"
        print('do action: %s'% self.message)
        self.Config.enableNatlink()
    def do_E(self, arg):
        self.message = "Disabling Natlink:"
        self.Config.disableNatlink()

    def help_e(self):
        print('-'*60)
        print("""Enable Natlink (e) or disable Natlink (E):

When you enable Natlink, the necessary settings in nssystem.ini and nsapps.ini
are done.

These options require elevated mode and probably Dragon be closed.

After you restart %s, Natlink should start, opening a window titled
'Messages from Natlink - ...'.

When you enable Natlink, the file natlink.pyd is (re)registered silently.  Use
the commands r/R to register/unregister natlink.pyd explicitly.
(see help r, but most often not needed)

When you disable Natlink, the necessary settings in nssystem.ini and nsapps.ini
are cleared. 

After you restart %s, Natlink should NOT START ANY MORE
so the window 'Messages from Natlink' is NOT OPENED.

Note: when you disable Natlink, the natlink.pyd file is NOT unregistered.
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
        tryPath = self.Config.isValidPath(arg)
        if not tryPath:
            self.message = "do_v, not a valid path: %s"% arg
            return
        self.message =  'Set VocolaUserDirectory to "%s" and enable Vocola'% arg
        print('do action: %s'% self.message)
        self.Config.setVocolaUserDir(arg)
            
    def do_V(self, arg):
        self.message = "Clear VocolaUserDirectory and (therefore) disable Vocola"
        print('do action: %s'% self.message)
        self.Config.clearVocolaUserDir()

    def help_v(self):
        print('-'*60)
        print("""Enable/disable Vocola by setting/clearing the VocolaUserDirectory
(v <path>/V).

In this VocolaUserDirectory your Vocola Command File are/will be located.

<path> must be an existing folder; Natlink\Vocola in My Documents is a
popular choice.

You may have to manually create this folder first.
""")
        print('='*60)

    help_V = help_v
    

    # enable/disable Natlink debug output...
    def do_x(self, arg):
        self.message = 'Enable natlinkmain giving debug output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.Config.enableDebugLoadOutput()
    def do_X(self, arg):
        self.message = 'Disable natlinkmain from giving debug output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.Config.disableDebugLoadOutput()

    def help_x(self):
        print('-'*60)
        print("""Enable (x)/disable (X) Natlink debug output

Nearly obsolete options.

This sends sometimes lengthy debugging messages to the
"Messages from Natlink" window.

Mainly used when you suspect problems with the working 
of Natlink, so keep off (X and Y) most of the time.
""")
        print('='*60)

    help_y = help_x
    help_X = help_x
    help_Y = help_x
    
    # register natlink.pyd
    def do_r(self, arg):
        self.message = "(Re) register and enable natlink.pyd is done from the installer program"
        
    def do_R(self, arg):
        self.message = 'Unregister natlink.pyd and disable Natlink is done from the installer program,\nyou can uninstall Natlink via "Add or remove Programs" in Windows'
        
    def do_z(self, arg):
        """register silent and enable Natlink"""
        self.message('this function is obsolete')
        
    def do_Z(self, arg):
        """(SILENT) Unregister natlink.pyd and disable Natlink"""
        self.message('this function is obsolete')

    # different Vocola options
    def do_b(self, arg):
        self.message = "Enable Vocola different user directories for different languages"
        print('do action: %s'% self.message)
        self.Config.enableVocolaTakesLanguages()
    def do_B(self, arg):
        self.message = "Disable Vocola different user directories for different languages"
        print('do action: %s'% self.message)
        self.Config.disableVocolaTakesLanguages()

    def do_a(self, arg):
        self.message = "Enable Vocola taking Unimacro actions"
        print('do action: %s'% self.message)
        self.Config.enableVocolaTakesUnimacroActions()
    def do_A(self, arg):
        self.message = "Disable Vocola taking Unimacro actions"
        print('do action: %s'% self.message)
        self.Config.disableVocolaTakesUnimacroActions()

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
        self.Config.setAhkExeDir(arg)

    def do_H(self, arg):
        self.message = 'clear directory of AutoHotkey.exe, return to default'
        print('do action: %s'% self.message)
        self.Config.clearAhkExeDir()

    def do_k(self, arg):
        arg = self.stripCheckDirectory(arg)  # also quotes
        if not arg:
            return
        self.message = 'set user directory for AutoHotkey scripts to: %s'% arg
        self.Config.setAhkUserDir(arg)

    def do_K(self, arg):
        self.message = 'clear user directory of AutoHotkey scripts, return to default'
        print('do action: %s'% self.message)
        self.Config.clearAhkUserDir()
            
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

    # enable/disable Natlink debug output...

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

def createIfNotThere(path_name):
    """if path_name does not exist, but one up does, create.
    
    return the valid path (str) or
    False, if not a valid path
    """
    path = Path(config.expand_path(path_name))
    if path.is_dir():
        return str(path)
    if path.exists():
        print(f'path exists, but is not a directory: "{str(path)}"')
        return False
    one_up = path.parent
    if one_up.is_dir():
        path.mkdir()
        if path.is_dir():
            return str(path)
    print(f'could not create directory: "{str(path)}"')
    return False              
        
if __name__ == "__main__":
    if len(sys.argv) == 1:
        Cli = CLI()
        natlinkConfig = NatlinkConfig()
        Cli.Config = natlinkConfig
        Cli.info = "type u for usage"
        try:
            li.cmdloop()
        except (KeyboardInterrupt, SystemExit):
            pass
    else:
        _main()
