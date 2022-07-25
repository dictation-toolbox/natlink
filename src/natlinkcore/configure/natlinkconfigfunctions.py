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
import subprocess
import getopt
import cmd
from pathlib import Path
import configparser
# from win32com.shell import shell
from natlinkcore import natlinkstatus
from natlinkcore import config
from natlinkcore import loader
from natlinkcore import readwritefile
from natlinkcore import wxdialogs

isfile, isdir, join = os.path.isfile, os.path.isdir, os.path.join

class NatlinkConfig:
    """performs the configuration tasks of Natlink
    
    setting UserDirectory, UnimacroDirectory and options, VocolaDirectory and options,
    Autohotkey options (ahk), and Debug option of Natlink.

    Changes are written in the config file, from which the path is taken from the loader instance.
    """
    def __init__(self):
        self.DNSName = 'Dragon'
        self.config_path = self.get_check_config_locations()
        self.config_dir = str(Path(self.config_path).parent)
        self.status = natlinkstatus.NatlinkStatus()
        self.getConfig()  # gets self.config and self.config_encoding
        self.check_config()

    def get_check_config_locations(self):
        """check the location/locations as given by the loader
        """
        config_path, fallback_path = loader.config_locations()
        
        if not isfile(config_path):
            config_dir = Path(config_path).parent
            if not config_dir.is_dir():
                config_dir.mkdir(parents=True)
            shutil.copyfile(fallback_path, config_path)
        return config_path

    def check_config(self):
        """check config_file for unwanted settings
        """
        self.config_remove(section='directories', option='default_config')

    def getConfig(self):
        """return the config instance
        """
        rwfile = readwritefile.ReadWriteFile()
        config_text = rwfile.readAnything(self.config_path)
        self.config = configparser.ConfigParser()
        self.config.read_string(config_text)
        self.config_encoding = rwfile.encoding

    def config_get(self, section, option):
        """set a setting into the natlink ini file

        """
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None
 
    def config_set(self, section, option, value):
        """set a setting into an inifile (possibly other than natlink.ini)
    
        Set the setting in self.config.
        
        Then write with the setting included to config_path with config_encoding.
        When this encoding is ascii, but there are (new) non-ascii characters,
        the file is written as 'utf-8'.

        """
        if not value:
            return self.config_remove(section, option)
        
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.config_write()
        self.status.__init__()
        return True
    
    def config_write(self):
        """write the (changed) content to the ini (config) file
        """
        try:
            with open(self.config_path, 'w', encoding=self.config_encoding) as fp:
                self.config.write(fp)   
        except UnicodeEncodeError as exc:
            if self.config_encoding != 'ascii':
                print(f'UnicodeEncodeError, cannot encode with encoding "{self.config_encoding}" the config data to file "{self.config_path}"')
                raise UnicodeEncodeError from exc
            with open(self.config_path, 'w', encoding='utf-8') as fp:
                self.config.write(fp)   

    def config_remove(self, section, option):
        """removes from config file
        
        same effect as setting an empty value
        """
        if not self.config.has_section(section):
            return
        self.config.remove_option(section, option)
        if not self.config.options(section):
            if section not in ['directories', 'settings', 'userenglish-directories', 'userspanish-directories']:
                self.config.remove_section(section)
        self.config_write()
        self.status.__init__()
    # def setUserDirectory(self, arg):
    #     self.setDirectory('UserDirectory', arg)
    # def clearUserDirectory(self, arg):
    #     self.clearDirectory('UserDirectory')
        
    def setDirectory(self, option, dir_path, section=None):
        """set the directory, specified with "key", to dir_path
        
        If dir_path None or invalid, go via GetDirFromDialog
        """
        section = section or 'directories'
        if not dir_path:
            prev_path = self.config_get('previous settings', option) or self.config_dir
            dir_path = wxdialogs.GetDirFromDialog(f'Please choose a "{option}"', prev_path)
            if not dir_path:
                print('No valid directory specified')
                return
        dir_path = dir_path.strip()
        directory = createIfNotThere(dir_path, level_up=1)
        if not (directory and Path(directory).is_dir()):
            if directory is False:
                directory = config.expand_path(dir_path)
            if dir_path == directory:
                print(f'Cannot set "{option}", the given path is invalid: "{directory}"')
            else:
                print(f'Cannot set "{option}", the given path is invalid: "{directory}" ("{dir_path}")')
            return
        self.config_set(section, option, dir_path)
        self.config_remove('previous settings', option)
        if section == 'directories':
            print(f'Set option "{option}" to "{dir_path}"')
        else:
            print(f'Set in section "{section}", option "{option}" to "{dir_path}"')
        return
        
    def clearDirectory(self, option, section=None):
        """clear the setting of the directory designated by option
        """
        section = section or 'directories'
        old_value = self.config_get(section, option)
        if not old_value:
            print(f'The "{option}" was not set, nothing changed...')
            return
        if isValidDir(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        print(f'cleared "{option}"')
 
    def setFile(self, option, file_path, section):
        """set the file, specified with "key", to file_path
        
        If file_path None or invalid, go via GetFileFromDialog
        """
        if not file_path:
            prev_path = self.config_get('previous settings', option) or ""
            file_path = wxdialogs.GetFileFromDialog(f'Please choose a "{option}"', prev_path)
            if not file_path:
                print('No valid file specified')
                return
        file_path = file_path.strip()
        if not Path(file_path).is_file():
            print(f'No valid file specified ("{file_path}")')
            
        self.config_set(section, option, file_path)
        self.config_remove('previous settings', option)
        print(f'Set in section "{section}", option "{option}" to "{file_path}"')
        return
        
    def clearFile(self, option, section):
        """clear the setting of the directory designated by option
        """
        old_value = self.config_get(section, option)
        if not old_value:
            print(f'The "{option}" was not set, nothing changed...')
            return
        if isValidFile(old_value):
            self.config_set('previous settings', option, old_value)
        else:
            self.config_remove('previous settings', option)
            
        self.config_remove(section, option)
        print(f'cleared "{option}"')
  

    def enableDebugOutput(self):
        """setting registry key so debug output of loading of natlinkmain is given

        """
        key = "log_level"
        settings = 'settings'
        old_value = self.config_get(settings, key)
        if old_value:
            if old_value == 'DEBUG':
                print(f'enableDebugOutput, setting is already "{old_value}"')
                return True
            if old_value is not None:
                self.config_set('previous settings', key, old_value)
        self.config_set(settings, key, 'DEBUG')
        return True

    def disableDebugOutput(self):
        """disables the Natlink debug output
        """
        key = 'log_level'
        section = 'settings'
        old_value = self.config_get('previous settings', key)
        if old_value:
            self.config.remove_option('previous settings', key)
            if old_value == 'DEBUG':
                old_value = 'INFO'
        else:
            old_value = 'INFO'
        self.config_set(section, key, old_value)
        return True

    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        # also remove usc.vch from VocolaUserDirectory
        unimacroDir = Path(self.status.getUnimacroDirectory())
        fromFolder = Path(unimacroDir)/'Vocola_compatibility'
        toFolder = Path(self.status.getVocolaUserDirectory())
        if not unimacroDir.is_dir():
            mess = f'copyUnimacroIncludeFile: unimacroDir "{str(unimacroDir)}" is not a directory'
            print(mess)
            return
        fromFile = fromFolder/uscFile
        if not fromFile.is_file():
            mess = f'copyUnimacroIncludeFile: file "{str(fromFile)}" does not exist (is not a valid file)'
            print(mess)
            return
        if not toFolder.is_dir():
            mess = f'copyUnimacroIncludeFile: vocolaUserDirectory does not exist "{str(toFolder)}" (is not a directory)'
            print(mess)
            return
        
        toFile = toFolder/uscFile
        if toFolder.is_file():
            print(f'remove previous "{str(toFile)}"')
            try:
                os.remove(toFile)
            except:
                mess = f'copyUnimacroIncludeFile: Could not remove previous version of "{str(toFile)}"'
                print(mess)
        try:
            shutil.copyfile(fromFile, toFile)
            print(f'copied "{uscFile}" from "{str(fromFolder)}" to "{str(toFolder)}"')
        except:
            mess = f'Could not copy new version of "{uscFile}", from "{str(fromFolder)}" to "{str(toFolder)}"'
            print(mess)
            return
        return

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
        mess = f'changed {nFiles} files in {toFolder}'
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
            toFolder = self.status.getVocolaUserDirectory()
            
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
        self.disableVocolaTakesUnimacroActions()
        mess = f'removed include lines from {nFiles} files in {toFolder}'
        print(mess)

        return True

    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "vocolatakeslanguages"
        self.config_set('vocola', key, 'True')
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "vocolatakeslanguages"
        self.config_set('vocola', key, 'False')

    def enableVocolaTakesUnimacroActions(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "vocolatakesunimacroactions"
        self.config_set('vocola', key, 'True')
        

    def disableVocolaTakesUnimacroActions(self):
        """disables so Vocola does not take Unimacro Actions
        """
        key = "vocolatakesunimacroactions"
        self.config_set('vocola', key, 'False')

    def openConfigFile(self):
        """open the natlink.ini config file
        """
        os.startfile(self.config_path)
        print(f'opened "{self.config_path}" in a separate window')
        return True

    def setAhkExeDir(self, arg):
        """set ahkexedir to a valid folder
        """
        key = 'ahkexedir'
        self.setDirectory(key, arg, section='autohotkey')

    def clearAhkExeDir(self):
        """set ahkexedir to a valid folder
        """
        key = 'ahkexedir'
        self.clearDirectory(key, section='autohotkey')

    def setAhkUserDir(self, arg):
        """set ahkuserdir to a valid folder
        """
        key = 'ahkuserdir'
        self.setDirectory(key, arg, section='autohotkey')

    def clearAhkUserDir(self):
        """clear Autohotkey user directory
        """
        key = 'ahkuserdir'
        self.clearDirectory(key, section='autohotkey')

    def printPythonPath(self):
        raise NotImplementedError 


def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about Natlink
             etc., usage above...

    """
    cli = CLI()
    cli.Config = NatlinkConfig()
    shortOptions = "DVNOPHKaAiIxXbBlmMuq"
    shortArgOptions = "d:v:n:o:p:h:k:"
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
            print("Type 'u' for usage ")

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
I       - show the natlink.ini file (in Notepad), you can manually edit.
j       - print PythonPath variable

[Natlink]

x/X     - enable/disable debug output of Natlink

[Vocola]

v/V     - enable/disable Vocola by setting/clearing VocolaUserDirectory,
          where the Vocola Command Files (.vcl) will be located.
          (~ or %HOME% are allowed, for example "~/.natlink/VocolaUser")

b/B     - enable/disable distinction between languages for Vocola user files
a/A     - enable/disable the possibility to use Unimacro actions in Vocola

[Unimacro]

o/O     - enable/disable Unimacro, by setting/clearing the UnimacroUserDirectory, where
          the Unimacro user INI files are located, and several other directories (~ or %HOME% allowed)
p/P     - set/clear path for program that opens Unimacro INI files.
l       - copy header file Unimacro.vch into Vocola User Directory
m/M     - insert/remove an include line for Unimacro.vch in all Vocola
          command files

[DragonflyDirectory]
d/D     - enable/disable the DragonflyDirectory, the directory where
          you can put your Dragonfly scripts (UserDirectory can also be used)
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
        self.Config.status.__init__()
        S = self.Config.status.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart Dragon'
        print(S)
    def do_I(self, arg):
        # inifile natlinkstatus.ini settings:
        self.Config.status.__init__()
        self.Config.openConfigFile()
    def do_j(self, arg):
        # print PythonPath:
        self.Config.printPythonPath()

    def help_i(self):
        print('-'*60)
        print("""The command info (i) gives an overview of the settings that are
currently set inside the Natlink system.

With command (I), you open the file "natlink.ini"

The command (j) gives the PythonPath variable which should contain several
Natlink directories after the config GUI runs succesfully

Settings are set by either the Natlink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

After you change settings, restart Dragon.
""")
        print('='*60)
    help_j = help_I = help_i
    
    # User Directory, Dragonfly directory -------------------------------------------------
    # for easier remembering, change n to d (DragonFly)
    def do_d(self, arg):
        self.Config.setDirectory('DragonflyUserDirectory', arg)
    
    def do_D(self, arg):
        self.Config.clearDirectory('DragonflyUserDirectory')

    def do_n(self, arg):
        self.Config.setDirectory('UserDirectory', arg)
    
    def do_N(self, arg):
        self.Config.clearDirectory('UserDirectory')
    
    def help_n(self):
        print('-'*60)
        print('''Sets (n [<path>]) or clears (N) the "UserDirectory" of Natlink.
This is the folder where your own python grammar files are/will be located.
''')
    def help_d(self):
        print('-'*60)
        print('''Sets (d [<path>]) or clears (D) the "DragonflyUserDirectory".
This is the folder where your own Dragonfly python grammar files are/will be located.
''')
        
    help_N = help_n
    help_D = help_d
    
    # Unimacro User directory and Editor or Unimacro INI files-----------------------------------
    def do_o(self, arg):
        
        unimacro_user_dir = self.Config.status.getUnimacroUserDirectory()
        if unimacro_user_dir and isdir(unimacro_user_dir):
            print(f'UnimacroUserDirectory is already defined: "{unimacro_user_dir}"\n\tto change, first clear (option "O") and then set again')
            print('\nWhen you want to upgrade Unimacro, also first clear ("O"), then choose this option ("o") again.\n')
            return

        uni_dir = self.Config.status.getUnimacroDirectory()
        if uni_dir:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "unimacro"])
            except subprocess.CalledProcessError as e:
                print('====\ncould not pip install --upgrade unimacro\n====\n')
                return
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "unimacro"])
            except subprocess.CalledProcessError as e:
                print('====\ncould not pip install unimacro\n====\n')
                return
        self.Config.status.refresh()   # refresh status
        uni_dir = self.Config.status.getUnimacroDirectory()

        self.Config.setDirectory('UnimacroUserDirectory', arg, section='unimacro')
        unimacro_user_dir = self.Config.config_get('unimacro', 'UnimacroUserDirectory')
        if not unimacro_user_dir:
            return
        uniGrammarsDir = self.Config.status.getUnimacroGrammarsDirectory()
        self.Config.setDirectory('UnimacroDirectory', uni_dir)
        self.Config.setDirectory('UnimacroGrammarsDirectory', uniGrammarsDir)
            
    def do_O(self, arg):
        self.Config.clearDirectory('UnimacroUserDirectory', section='unimacro')
        self.Config.config_remove('directories', 'unimacrogrammarsdirectory')
        self.Config.config_remove('directories', 'unimacrodirectory')
        self.Config.status.refresh()

    def help_o(self):
        print('-'*60)
        print(r"""set/clear UnimacroUserDirectory (o <path>/O)


Setting this directory also enables Unimacro. Clearing it disables Unimacro

In this directory, your user INI files (and possibly other user
dependent files) will be put.

You can use (if entered through the CLI) "~" for user home directory, or
another environment variable (%%...%%). (example: "o ~\Documents\.natlink\\UnimacroUser")
""")
        print('='*60)

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    def do_p(self, arg):
        self.message = "Set Unimacro INI file editor"
        print(f'do action: {self.message}')
        key = "UnimacroIniFilesEditor"
        self.Config.setFile(key, arg, section='unimacro')
            
    def do_P(self, arg):
        self.message = "Clear Unimacro INI file editor, go back to default Notepad"
        print(f'do action: {self.message}')
        key = "UnimacroIniFilesEditor"
        self.Config.clearFile(key, section='unimacro')

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
        print(f'do action: {self.message}')
        self.Config.includeUnimacroVchLineInVocolaFiles()
        print('and do action: enableVocolaTakesUnimacroActions')
        self.Config.enableVocolaTakesUnimacroActions()
        
    def do_M(self, arg):
        self.message = 'Remove "include Unimacro.vch" line from each Vocola Command File'
        print(f'do action: {self.message}')
        self.Config.removeUnimacroVchLineInVocolaFiles()
        print('and do action: disableVocolaTakesUnimacroActions')
        self.Config.disableVocolaTakesUnimacroActions()
        
    help_m = help_M = help_l
    
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        """specify the VocolaUserDirectory,
        
        but the config needs also the VocolaDirectory and the VocolaGrammarsDirectory
        """
        vocola_user_dir = self.Config.status.getVocolaUserDirectory()
        if vocola_user_dir and isdir(vocola_user_dir):
            print(f'VocolaUserDirectory is already defined: "{vocola_user_dir}"\n\tto change, first clear (option "V") and then set again')
            print('\nWhen you want to upgrade Vocola (vocola2), also first clear ("V"), then choose this option ("v") again.\n')
            return

        voc_dir = self.Config.status.getVocolaDirectory()
        if voc_dir:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "vocola2"])
            except subprocess.CalledProcessError as e:
                print('====\ncould not pip install --upgrade vocola2\n====\n')
                return
        else:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "vocola2"])
            except subprocess.CalledProcessError as e:
                print('====\ncould not pip install vocola2\n====\n')
                return
        self.Config.status.refresh()   # refresh status
        voc_dir = self.Config.status.getVocolaDirectory()

        self.Config.setDirectory('VocolaUserDirectory', arg, section='vocola')
        vocola_user_dir = self.Config.config_get('vocola', 'VocolaUserDirectory')
        if not vocola_user_dir:
            return
        vocGrammarsDir = self.Config.status.getVocolaGrammarsDirectory()
        self.Config.setDirectory('VocolaDirectory', voc_dir)
        self.Config.setDirectory('VocolaGrammarsDirectory', vocGrammarsDir)

            
    def do_V(self, arg):
        self.Config.clearDirectory('VocolaUserDirectory', section='vocola')
        self.Config.config_remove('directories', 'vocolagrammarsdirectory')
        self.Config.config_remove('directories', 'vocoladirectory')
        self.Config.status.refresh()

    def help_v(self):
        print('-'*60)
        print(r"""Enable/disable Vocola by setting/clearing the VocolaUserDirectory
(v <path>/V).

In this VocolaUserDirectory your Vocola Command File are/will be located.

if <path> does not exist, but "one up" does, the sub directory is created.
""")
        print('='*60)

    help_V = help_v
    

    # enable/disable Natlink debug output...
    def do_x(self, arg):
        self.message = 'Print debug output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.Config.enableDebugOutput()
    def do_X(self, arg):
        self.message = 'Disable printing debug output to "Messages from Natlink" window'
        print('do action: %s'% self.message)
        self.Config.disableDebugOutput()

    def help_x(self):
        print('-'*60)
        print("""Enable (x)/disable (X) Natlink debug output

This sends (sometimes lengthy) debug messages to the
"Messages from Natlink" window.
""")
        print('='*60)

    help_X = help_x
    
    # # register natlink.pyd
    # def do_r(self, arg):
    #     self.message = "(Re) register and enable natlink.pyd is done from the installer program"
    #     
    # def do_R(self, arg):
    #     self.message = 'Unregister natlink.pyd and disable Natlink is done from the installer program,\nyou can uninstall Natlink via "Add or remove Programs" in Windows'
    #     
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
        self.message = 'set user directory for AutoHotkey scripts to: %s'% arg
        print('do action: %s'% self.message)
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

def isValidDir(path):
    """return the path, as str, if valid directory
    
    otherwise return ''
    """
    result = isValidPath(path, wantDirectory=True)
    return result        

def isValidFile(path):
    """return the path, as str, if valid file
    
    otherwise return ''
    """
    result = isValidPath(path, wantFile=True)
    return result        

def isValidPath(path, wantDirectory=None, wantFile=None):
    """return the path, as str, if valid
    
    otherwise return ''
    """
    if not path:
        return ''
    path = Path(path)
    path_expanded = Path(config.expand_path(str(path)))
    if wantDirectory:
        if path_expanded.is_dir():
            return str(path_expanded)
    elif wantFile:
        if path_expanded.is_file():
            return str(path_expanded)
    elif path.exists():
        return str(path_expanded)
    return ''


def createIfNotThere(path_name, level_up=None):
    """if path_name does not exist, but one up does, create.
    
    return the valid path (str) or
    False, if not a valid path
    if level_up, can create more step upward ( specify > 1)
    """
    level_up = level_up or 1
    dir_path = isValidDir(path_name)
    if dir_path:
        return dir_path
    start_path = config.expand_path(path_name)
    up_path = Path(start_path)

    level = level_up
    while level:
        up_path = up_path.parent
        if up_path.is_dir():
            break
        level -= 1
    else:
        print(f'cannot create directory, {level_up} level above should exist: "{str(up_path)}"')
        return False              
    Path(start_path).mkdir(parents=True)
    if path_name == start_path:
        print(f'created directory: "{start_path}"')
    else:
        print(f'created directory "{path_name}": "{start_path}"')
        
    return start_path

def main_cli():
    if len(sys.argv) == 1:
        Cli = CLI()
        Cli.Config = NatlinkConfig()
        Cli.info = "type u for usage"
        try:
            Cli.cmdloop()
        except (KeyboardInterrupt, SystemExit):
            pass

main_cli() if __name__ == __name__ == "__main__" else _main()
