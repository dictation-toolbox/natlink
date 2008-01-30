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
      Functions: setDNSInstallDir(path) and clearDNSInstallDir(),
      --- call with CLI or command line option:
      -d path or --setdnsinstalldir path (to set)
      -D or --cleardnsinstalldir to clear and fall back into default
      
DNSIniDirectory
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKCU\Software\Natlink.
      Functions: setDNSIniDir(path) and clearDNSIniDir()
      --- call with CLI or command line option:
      -i path or --setdnsinidir path (to set)
      -I or --cleardnsinidir  (to clear)

When natlink is enabled natlink.dll is registered with
      win32api.WinExec("regsrvr32 /s pathToNatlinkdll") (silent)
It can be unregistered through function below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (-e or --enablenatlink)
disableNatlink() (-E or --disablenatlink)

enableVocola()   (-v or --enablevocola)  (to be done)
disableVocola()  (-V or --disablevocola) (to be done)

setUserDirectory (-u path or --setnatlinkuserdir path)
    
getStatusDict
     get status info in a dict

More at the bottom, with the CLI description...     

"""

import installutilfunctions, os, sys, win32api
thisDir = installutilfunctions.getBaseFolder(globals())
coreDir = installutilfunctions.getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'appending %s to pythonpath...'% coreDir
    sys.path.append(coreDir)

# from core directory, use registry entries from CURRENT_USER/Software/Natlink:
import natlinkstatus
userregnl = natlinkstatus.userregnl

import os, os.path, sys, getopt, cmd, types, string, win32con
### from previous modules, needed or not...
##NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"

def getStatusDict():
    """get the relevant variables from natlinkstatus, return in a dict"""
    
    D = {}
    D['DNSInstallDir'] = natlinkstatus.getDNSInstallDir()
    D['DNSIniDir'] = natlinkstatus.getDNSIniDir()
    D['DNSVersion'] = natlinkstatus.getDNSVersion()      # integer!
    D['WindowsVersion'] = natlinkstatus.getWindowsVersion()
    D['userDirectory'] = natlinkstatus.getUserDirectory()
    D['VocolaUserDirectory'] = natlinkstatus.getVocolaUserDirectory()
    
    return D    

def printStatusDict():
    """print the relevant variables from natlinkstatus"""
    D = getStatusDict()
    Keys = D.keys()
    Keys.sort()
    for k in Keys:
      print '%s\t%s'% (k, D[k])


def setDNSInstallDir(new_dir):
    """set in registry local_machine\natlink

    """
    key = 'DNSInstalDir'
    if os.path.isdir(new_dir):
        userregnl[key] = new_dir
    else:
        raise IOError("setDNSInstallDir, not a valid directory: %s"% new_dir)
    
def clearDNSInstallDir():
    """clear in registry local_machine\natlink\natlinkcore

    """
    key = 'DNSInstalDir'
    if key in userregnl:
        del userregnl[key]
    else:
        print 'NatSpeak directory was not set in registry, natlink part'

def setDNSIniDir(new_dir):
    """set in registry local_machine\natlink

    """
    key = 'DNSIniDir'
    if os.path.isdir(new_dir):
        userregnl[key] = new_dir
    else:
        raise IOError("setDNSIniDir, not a valid directory: %s"% new_dir)
    
def clearDNSIniDir():
    """clear in registry local_machine\natlink\

    """
    key = 'DNSIniDir'
    if key in userregnl:
        del userregnl[key]
    else:
        print 'NatSpeak ini directory was not set in registry, natlink part'

def setUserDirectory(v):
    key = 'UserDirectory'
    if os.path.isdir(v):
        print 'set natlinkuserdir to %s'% v
        userregnl[key] = v
    else:
        print 'no a valid directory: %s'% v
        
    
def clearUserDirectory():
    key = 'UserDirectory'
    if key in userregnl:
        print 'clearing natlink user directory...'
        del userregnl[key]
    else:
        print 'natlink user directory key was not set...'
        
  
def enableNatlink():
    """register natlink.dll and set settings in nssystem.ini and nsapps.ini

    """
    registerNatlinkDll(silent=1)
    nssystemini = natlinkstatus.getNSSYSTEMIni()
    section1 = natlinkstatus.section1
    key1 = natlinkstatus.key1
    value1 = natlinkstatus.value1
    win32api.WriteProfileVal(section1, key1, value1, nssystemini)
    nsappsini = natlinkstatus.getNSAPPSIni()
    section2 = natlinkstatus.section2
    key2 = natlinkstatus.key2
    value2 = natlinkstatus.value2
    win32api.WriteProfileVal(section2, key2, value2, nsappsini)
    print 'natlink enabled, restart NatSpeak'

def disableNatlink():
  
    nssystemini = natlinkstatus.getNSSYSTEMIni()
    section1 = natlinkstatus.section1
    key1 = natlinkstatus.key1
    # trick with None, see testConfigureFunctions...
    # this one disables natlink:
    win32api.WriteProfileVal(section1, key1, None, nssystemini)
    
    nsappsini = natlinkstatus.getNSAPPSIni()
    section2 = natlinkstatus.section2
    key2 = natlinkstatus.key2
    win32api.WriteProfileVal(section2, key2, None, nsappsini)
    # leaving empty section, sorry, did not find the way to delete a section...
    print 'natlink disabled, natlink.dll NOT unregistered here'

def enableVocola():
  print 'enableVocola, coming'
def disableVocola():
  print 'disableVocola, coming'


def getVocolaUserDir():
    key = 'VocolaUserDirectory'
    return userregnl[key]

def setVocolaUserDir(v):
    key = 'VocolaUserDirectory'
    if os.path.isdir(v):
        print 'set vocola user dir to %s'% v
        userregnl[key] = v
    else:
        print 'not a valid directory: %s'% v

def clearVocolaUserDir():
    key = 'VocolaUserDirectory'
    if key in userregnl:
        del userregnl[key]
    else:
        print 'was not set: %s'% key

        
def registerNatlinkDll(silent=None):
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

def unregisterNatlinkDll():
    """unregister explicit, should not be done normally
    """
    os.system('regsvr32 /u "%s"'% os.path.join(coreDir, "natlink.dll"))
##
##            enableVocola()
##            disableVocola()
##            setVocolaUserDir(v)
##            registerNatlinkDll()
##            uregisterNatlinkDll()
def enableDebugOutput():
    """setting registry key so debug output is in natspeak logfile
    """
    key = "NatlinkDebug"
    userregnl[key] = 1
    

def disableDebugOutput():
    """disables the natlink lengthy debug output to natspeak logfile
    """
    key = "NatlinkDebug"
    userregnl[key] = 0
    
  
            


def usage():
    """gives the usage of the command line options or options when
    the command line interface  (CLI) is used
    """
    print """
    usage either as With command line options like '-i' or '--info', or in an interactive
    session using the CLI ( command line interface).

    When using the CLI no - or -- are inserted before the command letters

    -i, --info:          print information about the natlink status
    -I, --reginfo:     print information about the registry settings

    -d, --setdnsinstalldir: set the directory where NatSpeak is installed
    -D, --cleardnsinidir: clear above registry setting

    -c, --setdnsinidir: set the directory where NatSpeak ini files are located
    -C, --cleardnsinidir: clear above registry setting

    -e, --enablenatlink: enable natlink, by setting the correct ini file settings
    -E, --disablenatlink: disable natlink, by clearing above ini file settings

    -u, --setnatlinkuserdir: set user directory for natlink
    -U, --clearnatlinkuserdir: clears this directory, no grammars will be searched there any more

    -v, --enablevocola: enable vocola, by switching on _vocola_main.py in base directory
    -V, --disablevocola: disable vocola, by switching off _vocola_main.py

    -w, --setvocoloauserdir: set the user directory for vocola user files
    -W, --clearvocoloauserdir: clears this setting

    -r, --registernatlink: register natlink.dll
    -R, --unregisternatlink: unregister natlink.dll (should not be necessary)

    -g, --enabledebugoutput: natlink debug output in natlink log file (not advised)
    -G, --disabledebugoutput: natlink debug output NOT in natlink log file
    

    """

def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about natlink
             etc., usage above...

    """
    shortOptions = "iIDCeEUdvVc:u:w:WrRgG"
    longOptions = ["info", "reginfo",
                   "setdnsinstalldir=", "cleardnsinstalldir",
                   "setdnsinidir=", "cleardnsinidir"
                   "enablenatlink", "disablenatlink",
                   "enablevocola", "disablevocola",
                   "setvocoloauserdir=", "clearvocoladir",
                   "registernatlink", "unregisternatlink",
                   "enabledebugoutput", "disabledebugoutput" ]
    if Options:
        if type(Options) == types.StringType:
            Options = Options.split(" ", 1)
        Options = map(string.strip, Options)                
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, shortOptions, longOptions)
    except getopt.GetoptError:
        print 'invalid option: %s'% `Options`
        usage()
        return

    if args:
        print 'should not have extraneous arguments: %s'% `args`
    for o, v in options:
        if o == "-i":
            printStatusDict()
          
        elif o == "-I":
            # registry settings:
            print "CURRENT_USER\\Natlink registry settings:"
            Keys = userregnl.keys()
            Keys.sort()
            for k in userregnl:
                print "\t%s:\t%s"% (k, userregnl[k])
            print "-"*60
        elif o == "-d":
            print "Change NatSpeak directory to: %s"% v
            setDNSIniDir(v)
        elif o == "-D":
            print "Clear NatSpeak directory in registry"
            clearDNSIniDir()
        elif o == "-c":
            print "Change NatSpeak Ini files directory to: %s"% v
            setDNSIniDir(v)
        elif o == "-C":
            print "Clear NatSpeak Ini files directory in registry"
            clearDNSIniDir()
        elif o == "-e":
            print "Enable natlink"
            enableNatlink()
        elif o == "-E":
            print "Disable Natlink"
            disableNatlink()
        elif o == "-u":
            print "Set Natlink User Directory to %s"% v
            setUserDirectory(v)
        elif o == "-U":
            print "Clears Natlink User Directory"
            clearUserDirectory()
        elif o == "-v":
            print "Enable Vocola"
            enableVocola()
        elif o == "-V":
            print "Disable Vocola"
            disableVocola()
        elif o == "-w":
            print "Set Vocola User Directory to: %s"% v
            setVocolaUserDir(v)
        elif o == "-W":
            print "Clears the Vocola User Directory"
            clearVocolaUserDir()
        elif o == "-r":
            print "(Re) register natlink.dll"
            registerNatlinkDll()
        elif o == "-R":
            print "Unregister natlink.dll"
            uregisterNatlinkDll()
        elif o == "-g":
            print "enable natlink debug output to natspeak logfile "
            enableDebugOutput()
        elif o == "-G":
            print "Disable natlink debug output to natspeak logfile"
            disableDebugOutput()
        else:
            print "forgotten some option: %s"% o
            
          
class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '> '

    # info----------------------------------------------------------
    def do_i(self, arg):
        _main('-i')

    def help_i(self):
        print "The command info (i) gives an overview of the settings that are currently set"
        print "inside the natlink system"

    def do_I(self, arg):
        _main('-I')

    def help_I(self):
        print "The command reginfo (I) gives all the registry settings" 
        print "that are used by the natlink system."
        print "They are set by either the natlink/vocola/unimacro installer or by"
        print "functions inside this module and this CLI." 
        print "These functions can also be called by the configure gui (wxPython)"

    do_info = do_i
    do_reginfo = do_I
    help_info = help_i
    help_reginfo = help_I

    # DNS install directory------------------------------------------
    def do_d(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            _main('-d '+arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_d(self):
        print "Set the directory where natspeak is installed, in case"
        print "the normal place(s) cannot find it"
        print "normally not needed, only if natspeak is installed on an unexpected location"

    def do_D(self, arg):
        _main('-D')
    
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
            _main('-c '+arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_c(self):
        print "Set the directory where natspeak ini file locations"
        print " (nssystem.ini and nsapps.ini) are located."
        print "Only needed if they cannot be found in the normal place(s)"

    def do_C(self, arg):
        _main('-D')
    
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
            _main('-u '+arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_u(self):
        print "Sets the user directory of natlink."
        print "This will often be the folder where unimacro is located."

    def do_U(self, arg):
        _main('-U')
    
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
        _main('-e')
    def do_E(self, arg):
        _main('-E')

    def help_e(self):
        print "set the necessary registry settings in nssystem.ini and nsapps.ini"
        print "after you restart natspeak, natlink should start, showing "
        print "the window 'Messages from Python Macros'"
        
    def help_E(self):
        print "clears the necessary registry settings in nssystem.ini and nsapps.ini"
        print "after you restart natspeak, natlink should NOT START ANY MORE."
        print "the window 'Messages from Python Macros' is NOT SHOWN"
        print "Note: the natlink.dll file is NOT disabled, but is not called any more"
        print "as natspeak does not call natlinkmain any more"
        
        
        
    do_enablenatlink = do_e
    do_disablenatlink = do_E
    help_enablenatlink = help_e
    help_disablenatlink = help_E
  
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        _main('-v')
    def do_V(self, arg):
        _main('-V')

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
        _main('-w ' + arg)
    def do_W(self, arg):
        _main('-W')
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
        _main('-g')
    def do_G(self, arg):
        _main('-G')

    def help_g(self):
        print "enables natlink debug output (in the natspeak log file)"
        print "this can be a lot of lines, so preferably disable this one!"
        
    def help_G(self):
        print "disables natlink debug output (in the natspeak log file)"
        print "It is advised to keep this setting disabled"

    do_enabledebugoutput = do_g
    do_disabledebutoutput = do_G
    help_enabledebugoutput = help_g
    help_disabledebugoutput = help_G


    # register natlink.dll
    def do_r(self, arg):
        _main('-r')
    def do_R(self, arg):
        _main('-R')

    def help_r(self):
        print "registers natlink.dll explicitly."
        print "this is also done (silent) when you enable natlink, so is mostly NOT NEEDED!"
        print "It shows a message dialog to inform you what happened."
        
    def help_R(self):
        print "unregisters natlink.dll explicit. Is not necessary to do so..."
        print "But if you do, a message dialog shows up to inform you what happened."

    do_registernatlink = do_r
    do_unregisternatlink = do_R
    help_registernatlink = help_r
    help_unregisternatlink = help_R


    def default(self, line):
        print 'no valid entry: %s'% line
        print
        print usage()
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

