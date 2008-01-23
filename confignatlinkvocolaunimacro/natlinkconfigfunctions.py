"""

With the functions in this module natlink can be configured.

This can be done in three ways:
-Through the command line interface (CLI) which is started automatically
 when this module is run (with Pythonwin, IDLE, or command line of python)
-On the command line, using one of the different command line options 
-Through the configure GUI, which calls into this module

When natlink is installed properly, there should be keys set in 
the registry HKLM (LOCAL_MACHINE) in section Software\Natlink:

NatlinkInstallPath
    - Will be set when installing natlink.  Points to the folder where natlink
      is installed.  Can be changed by reinstalling natlink.

NatlinkCorePath
    - Will be set when installing natlink.  Points to the folder where
      natlinkmain.py and natlinkstatus.py are located (among other files)
      NatlinkCorePath is always in macrosystem\core in relation to
      NatlinkInstallPath

NatlinkVersion
    - to be done, should keep track of the last install number.


Afterwards can be set:

DNSInstallDir
    - if not found in one of the predefined subfolders of %PROGRAMFILES%,
      this directory can be set in HKLM\Software\Natlink.
      Functions: setDNSInstallDir(path) and clearDNSInstallDir(),
      --- call with CLI or command line option:
      -d path or --setdnsinstalldir path (to set)
      -D or --cleardnsinstalldir to clear and fall back into default
      
DNSIniDir
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKLM\Software\Natlink.
      Functions: setDNSIniDir(path) and clearDNSIniDir()
      --- call with CLI or command line option:
      -i path or --setdnsinidir path (to set)
      -I or --cleardnsinidir  (to clear)

When the module starts, natlink.dll is registered with
      win32api.WinExec("regsrvr32 /s pathToNatlinkdll") (silent)

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (-e or --enablenatlink)
disableNatlink() (-E or --disablenatlink)

enableVocola()   (-v or --enablevocola)
disableVocola()  (-V or --disablevocola)

setNatlinkUserDir (-u path or --setnatlinkuserdir path)
    
getStatusDict
     get status info in a dict


"""


import RegistryDict, win32con
import os, os.path, sys, getopt, cmd, types, string
NatlinkCorePath = None
NatlinkInstallPath = None
NatlinkVersion = None # later...


# from previous modules, needed or not...
NATLINK_CLSID  = "{dd990001-bb89-11d2-b031-0060088dc929}"
defaultNatLinkDLLFile  = r"NatLink\macrosystem\core\natlink.dll"



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
    value = None
    try:
        value = regnl[key]
    except KeyError:
        mess = 'cannot find key %s in registry dictionary'% key
        if fatal:
            fatal_error(mess, new_raise = Exception)
        else:
            print mess
            return ''
    else:
        return str(value)

# collect the registry settings of HKLM\Software\Natlink in dict regnl:            
try:
    group = "SOFTWARE\Natlink"
    regnl = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, group)
except KeyError:
    regnl = None
    fatal_error('Cannot find registry settings for Natlink in: HKEY_LOCAL_MACHINE\\%s'% group)
# collect the registry settings of Current_User in dict userregnl
try:
    group = "SOFTWARE\Natlink"
    userregnl = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER, group)
except KeyError:
    userregnl = None
    print 'warning: cannot find registry settings for this user: HKEY_CURRENT_USER\\%s'% group
         
                
# set in regnl...
NatlinkInstallPath = getFromRegdict(regnl, 'NatlinkInstallPath', fatal=1)
NatlinkCorePath = getFromRegdict(regnl, 'NatlinkCorePath', fatal=1)
NatlinkVersion = getFromRegdict(regnl, 'NatlinkVersion')  # may fail for the moment

# appending to path if necessary:
if not os.path.normpath(NatlinkCorePath) in sys.path:
    print 'appending %s to pythonpath...'% NatlinkCorePath
    sys.path.append(NatlinkCorePath)

##    for p in sys.path:
##        print p

# register natlink.dll:
try:
    import win32api
except:
    fatal_error("cannot import win32api, please see if win32all of python is properly installed")
try:
    os.system('regsvr32 "%s"'% os.path.join(NatlinkCorePath, "natlink.dll"))
##    win32api.WinExec('regsvr32 /s "%s"'% os.path.join(NatlinkCorePath, "natlink.dll"))
except:
    fatal_error("cannot register natlink.dll, please see if natlink.dll is in the core folder")                    

import natlinkstatus
from natlinkstatus import *

## ok, imported ok, natlink is installed

def getStatusDict():
    """get the relevant variables from natlinkstatus, return in a dict"""
    
    D = {}
    D['DNSInstallDir'] = getDNSInstallDir()
    D['DNSIniDir'] = getDNSIniDir()
    D['DNSVersion'] = getDNSVersion()      # integer!
    D['WindowsVersion'] = getWindowsVersion()
    D['NatlinkInstallPath'] = NatlinkInstallPath
    D['NatlinkCorePath'] = NatlinkCorePath
    D['NatlinkIsEnabled'] = NatlinkIsEnabled()
    return D    

def setDNSdirectory(new_dir):
    """set in registry local_machine\natlink\natlinkcore

    """
    key = 'NatspeakInstallPath'
    if os.path.isdir(new_dir):
        regnl[key] = new_dir
    else:
        raise IOError("setDNSdirectory, not a valid directory: %s"% new_dir)
    
def clearDNSdirectory():
    """clear in registry local_machine\natlink\natlinkcore

    """
    key = 'NatspeakInstallPath'
    if key in regnl:
        del regnl[key]
    else:
        print 'NatSpeak directory was not set in registry, natlink part'

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

    -s, --natspeakdir: set the directory where NatSpeak is installed
    -S, --clearnatspeakdir: clear above registry setting

    """

def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info
             -r, --reginfo: give the info in the registry about natlink
             -s, --natspeakdir: set natspeak install dir
             -S, --clearnatspeakdir: clear registry item which contains the natspeak install dir

    """
    shortOptions = "iISs:"
    longOptions = ["info", "reginfo", "clearnatspeakdir", "natspeakdir="]
    if Options:
        if type(Options) == types.StringType:
            Options = Options.split(" ", 1)
        Options = map(string.strip, Options)                
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, "iISs:")
    except getopt.GetoptError:
        print 'invalid option: %s'% `options`
        usage()
        
    print "options: %s"% options
    if args:
        print 'should not have extraneous arguments: %s'% `args`
    for o, v in options:
        if o == "-i":
            D = getStatusDict()
            Keys = D.keys()
            Keys.sort()
            for k in Keys:
                print "%s:\t%s"% (k, D[k])
          
        elif o == "-I":
            print "LOCAL_MACHINE\\Natlink registry settings:"
            Keys = regnl.keys()
            Keys.sort()
            for k in Keys:
                print "\t%s:\t%s"% (k, regnl[k])

            print "CURRENT_USER\\Natlink registry settings:"
            Keys = userregnl.keys()
            Keys.sort()
            for k in userregnl:
                print "\t%s:\t%s"% (k, userregnl[k])
            print "-"*60
        elif o == "-s":
            print "Change NatSpeak directory to: %s"% v
            setDNSdirectory(v)
        elif o == "-S":
            print "Clear NatSpeak directory in registry"
            clearDNSdirectory()

class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '> '

    def do_info(self, arg):
        _main('-i')

    def help_info(self):
        print "The command info (i) gives an overview of the settings that are currently set"
        print "inside the natlink system"

    def do_reginfo(self, arg):
        _main('-I')

    def help_reginfo(self):
        print "The command reginfo (I) gives all the registry settings" 
        print "that are used by the natlink system."
        print "They are set by either the natlink/vocola/unimacro installer or by"
        print "functions inside this module and this CLI." 
        print "These functions can also be called by the configure gui (wxPython)"

    def do_natspeakdir(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            _main('-s '+arg)
        else:
            print 'not a valid folder: %s'% arg
    
    def help_natspeakdir(self):
        print "Set the directory where natspeak is installed, in case"
        print "the normal place(s) cannot find it"
        print "normally not needed, only if natspeak is installed on an unexpected location"

    def do_clearnatspeakdir(self, arg):
        _main('-S')
    
    def help_clearnatspeakdir(self):
        print "Clears the registry entry where of the directory where natspeak is installed."
        print "Natlink will again search for NatSpeak install directory in the normal place(s)"

    def default(self, line):
        print 'no valid entry: %s'% line
        print
        print usage
        print
        print 'type help or help command for more information'

    def do_quit(self, arg):
        sys.exit()

    # shortcuts:
    do_i = do_info
    do_I = do_reginfo
    do_q = do_quit
    do_s = do_natspeakdir
    do_S = do_clearnatspeakdir
    help_i = help_info
    help_I = help_reginfo
    help_s = help_natspeakdir
    help_S = help_clearnatspeakdir
    
        
if __name__ == "__main__":
    cli = CLI()
    cli.cmdloop()
         
