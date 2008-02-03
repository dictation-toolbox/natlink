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

*** the core directory is relative to this directory ... and will be searched for first.

Afterwards can be set:

DNSInstallDirectory
    - if not found in one of the predefined subfolders of %PROGRAMFILES%,
      this directory can be set in HKCU\Software\Natlink.
      Functions: setDNSInstallDir(path) (d path) and clearDNSInstallDir() (D)
      
DNSIniDirectory
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKCU\Software\Natlink.
      Functions: setDNSIniDir(path) (c path) and clearDNSIniDir() (C)

When natlink is enabled natlink.dll is registered with
      win32api.WinExec("regsrvr32 /s pathToNatlinkdll") (silent)

It can be unregistered through function unregisterNatlinkDll() see below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (e)/disableNatlink() (E)

enableVocola()   (v) disableVocola()  (V) (to be done)

setUserDirectory(path) (u path) or clearUserDirectory() (U)
    
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
    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
    if not os.path.isfile(dllPath):
        print 'natlink.dll not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
#-----------------------------------------------------

import os, sys, win32api
thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'appending %s to pythonpath...'% coreDir
    sys.path.append(coreDir)

# from core directory, use registry entries from CURRENT_USER/Software/Natlink:
import natlinkstatus, natlinkcorefunctions

import os, os.path, sys, getopt, cmd, types, string, win32con

class NatlinkConfig(natlinkstatus.NatlinkStatus):
    """performs the configuration tasks of natlink

    userregnl got from natlinkstatus, as a Class (not instance) variable, so
    should be the same among instances of this class...
    """
    def getStatusDict(self):
        """get the relevant variables from natlinkstatus, return in a dict"""
        
        D = {}
        D['DNSInstallDir'] = self.getDNSInstallDir()
        D['DNSIniDir'] = self.getDNSIniDir()
        D['DNSVersion'] = self.getDNSVersion()      # integer!
        D['WindowsVersion'] = self.getWindowsVersion()
        D['userDirectory'] = self.getUserDirectory()
        D['VocolaUserDirectory'] = self.getVocolaUserDirectory()
        
        return D    

    def printStatusDict(self):
        """print the relevant variables from natlinkstatus"""
        D = self.getStatusDict()
        Keys = D.keys()
        Keys.sort()
        for k in Keys:
            if D[k]:
                print '%s\t%s'% (k, D[k])
            else:
                print '%s\t%s'% (k, '(empty)')

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
        key = 'DNSInstalDir'
        if os.path.isdir(new_dir):
            self.userregnl[key] = new_dir
        else:
            raise IOError("setDNSInstallDir, not a valid directory: %s"% new_dir)
        
    def clearDNSInstallDir(self):
        """clear in registry local_machine\natlink\natlinkcore

        """
        key = 'DNSInstalDir'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'NatSpeak directory was not set in registry, natlink part'

    def setDNSIniDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSIniDir'
        if os.path.isdir(new_dir):
            self.userregnl[key] = new_dir
        else:
            raise IOError("setDNSIniDir, not a valid directory: %s"% new_dir)
        
    def clearDNSIniDir(self):
        """clear in registry local_machine\natlink\

        """
        key = 'DNSIniDir'
        if key in self.userregnl:
            del self.userregnl[key]
        else:
            print 'NatSpeak ini directory was not set in registry, natlink part'

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
            
      
    def enableNatlink(self):
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
        print 'natlink enabled, restart NatSpeak'

    def disableNatlink(self):
      
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
        print 'natlink disabled, restart NatSpeak'
        print 'Note natlink.dll is NOT UNREGISTERED, but this is not necessary either'
        
    def enableVocola(self):
      print 'enableVocola, coming'
    def disableVocola(self):
      print 'disableVocola, coming'


    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        return self.userregnl[key]

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
        else:
            print 'was not set: %s'% key

            
    def registerNatlinkDll(self, silent=None):
        """register natlink.dll

        if silent, do through win32api, and not report. This is done whenever natlink is enabled.

        if NOT silent, go through os.system, and produce a message window.
        """
        DllPath = os.path.join(coreDir, "natlink.dll")
        if not os.path.isfile(DllPath):
            fatal_error("Dll file not found in core folder: %s"% DllPath)
            
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

    def unregisterNatlinkDll(self):
        """unregister explicit, should not be done normally
        """
        os.system('regsvr32 /u "%s"'% os.path.join(coreDir, "natlink.dll"))

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
        
      
                



def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about natlink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "iIDCeEUdvVWrRgG"
    shortArgOptions = "c:u:w:"  
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
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'config > '
        self.config = NatlinkConfig()

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

u/U - set/clear userdirectory, the directory of the user grammar files of natlink (eg unimacro)

v/V - enable/disable vocola, currently not implemented, vocola is simply enabled
w/W - set/clear vocoloauserdir, the user directory for vocola user files

r/R - (un)registernatlink, the natlink.dll file(should not be necessary to do)
g/G - enable/disable debugoutput: natlink debug output in natlink log file

usage - give this list
q   - quit
help command: give more explanation on command
        """
        print '='*60

    # info----------------------------------------------------------
    def do_i(self, arg):
        self.config.printStatusDict()

    def help_i(self):
        print "The command info (i) gives an overview of the settings that are currently set"
        print "inside the natlink system"

    def do_I(self, arg):
        # registry settings:
        self.config.printRegistrySettings()

    def help_I(self):
        print \
"""The command reginfo (I) gives all the registry settings
that are used by the natlink system (HKCU\Software\Natlink)

They are set by either the natlink/vocola/unimacro installer or by
functions inside this module and this CLI. All calls of the configure GUI
go through CLI calls
"""

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
            self.config.setDNSIniDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_d(self):
        print "Set the directory where natspeak is installed, in case"
        print "the normal place(s) cannot find it"
        print "normally not needed, only if natspeak is installed on an unexpected location"

    def do_D(self, arg):
        print "Clear NatSpeak directory in registry"
        self.config.clearDNSIniDir()
    
    def help_D(self):
        print "Clears the registry entry where of the directory where natspeak is installed."
        print "Natlink will again search for NatSpeak install directory in the normal place(s)"

    do_setdnsinstalldir = do_d
    do_cleardnsinstalldir = do_D
    help_setdnsinstalldir = help_d
    help_cleardnsinstalldir = help_D


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
            self.config.setDNSIniDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_c(self):
        print "Set the directory where natspeak ini file locations"
        print " (nssystem.ini and nsapps.ini) are located."
        print "Only needed if they cannot be found in the normal place(s)"

    def do_C(self, arg):
            print "Clear NatSpeak Ini files directory in registry"
            clearDNSIniDir()
    
    def help_C(self):
        print "Clears the registry entry that holds the directory of the"
        print "natspeak ini (configuration) files. After it is cleared,"
        print "Natlink will again search for its ini files in the default/normal place(s)"

    do_setdnsinstalldir = do_c
    do_cleardnsinstalldir = do_C
    help_setdnsinstalldir = help_c
    help_cleardnsinstalldir = help_C

    # User Directories -------------------------------------------------
    def do_u(self, arg):
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
    
    def help_u(self):
        print "Sets the user directory of natlink."
        print "This will often be the folder where unimacro is located."

    def do_U(self, arg):
        print "Clears Natlink User Directory"
        self.config.clearUserDirectory()
    
    def help_U(self):
        print "Clears the registry entry that holds the Natlink User Directory"
        print "After it is cleared, natlink will only look for grammars in"
        print "the base directory, where normally Vocola is installed."

    do_setnatlinkuserdir = do_u
    do_clearnatlinkuserdir = do_U
    help_setnatlinkuserdir = help_u
    help_clearnatlinkuserdir = help_U
    
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
        print "Enable Vocola"
        self.config.enableVocola()
    def do_V(self, arg):
        print "Disable Vocola"
        self.config.disableVocola()

    def help_v(self):
        print "enables python files in the base directory of natlink, especially"
        print "_vocola_main.py. Toggle the microphone and Vocola should be in..."
        
    def help_V(self):
        print "renames _vocola_main.py in the base directory of natlink to"
        print " disabled_vocola_main.py."
        print "Also remove all .pyc files and all .py files generated by vocola in this directory."
        print "Toggle the microphone, or possibly restart NatSpeak."
    def help_w(self):
        print "Set the directory for vocola user files..."
        print "Defaults to My documents\\vocola"
    def help_W(self):
        print "Clears the directory for vocola user files..."

    def do_w(self, arg):
        print "Set Vocola User Directory to: %s"% arg
        self.config.setVocolaUserDir(arg)
    def do_W(self, arg):
        print "Clears the Vocola User Directory"
        self.config.clearVocolaUserDir()
    def help_w(self):
        print "set the directory where the Vocola User Files are/should be located"      
        
    do_enablevocola = do_v
    do_disablevocola = do_V
    do_setvocolauserdir = do_w
    help_enablevocola = help_v
    help_disablevocola = help_V
    help_setvocolauserdir = help_w

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

        
    do_enabledebugoutput = do_g
    do_disabledebutoutput = do_G
    help_enabledebugoutput = help_g
    help_disabledebugoutput = help_g
    help_G = help_g


    # register natlink.dll
    def do_r(self, arg):
        print "(Re) register natlink.dll"
        self.config.registerNatlinkDll()
    def do_R(self, arg):
        print "Unregister natlink.dll"
        self.config.unregisterNatlinkDll()

    def help_r(self):
        print '-'*60
        print \
"""registers (r)/ unregisters (R) natlink.dll explicitly.

Registring is also done (silent) when you enable natlink, so is mostly NOT NEEDED!
It shows a message dialog to inform you what happened.
        
But if you do (-r or -R) a message dialog shows up to inform you what happened.
If you restart NatSpeak after unregisering natlink.dll, you get a message:

Cannot load compatibility module support (GUID=
%s

If that happens, simply reregister with the -r option.
"""% self.config.NATLINK_CLSID
        print '='*60

    do_registernatlink = do_r
    do_unregisternatlink = do_R
    help_registernatlink = help_r
    help_unregisternatlink = help_r
    help_R = help_r


    def default(self, line):
        print 'no valid entry: %s'% line
        print
        print self.usage()
        print
        print 'type help or help command for more information'

    def do_quit(self, arg):
        sys.exit()

    # shortcuts:

    do_q = do_quit

    
    
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
      cli = CLI()
      cli.cmdloop()
    else:
      _main()

