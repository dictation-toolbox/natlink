import os, sys, time


if sys.version.find("64 bit") >= 0:
    print '============================================='
    print 'You installed a 64 bit version of Python.'
    print 'NatLink cannot run with this version, please uninstall and'
    print 'install a 32 bit version of python, see http://qh.antenna.nl/unimacro,,,'
    print '============================================='
    while True:
        pass
    raise


try:
    import win32api
except ImportError:
    print 'Unable to start the configuration program of NatLink/Unimacro/Vocola'
    print 'because the module "win32api" is not found.  This probably'
    print 'means that the windowns extensions package for python (32 bits) is not installed (properly).'

    print
    print 'A version of this package suitable for use with NatLink can be obtained from'
    print 'http://sourceforge.net/projects/natlink/files/pythonfornatlink/' 
    print '(choose the python version you are using right now: %s)'% sys.version[:3]
    print
    while True:
        pass
    raise

from win32api import ShellExecute, GetVersionEx



# see natlinkstatus.py for windows versions (getWindowsVersion)
wversion = GetVersionEx()
if wversion[3] == 2 and wversion[0] >= 6:
    # Vista and later
    openpar = "runas"
else:
    openpar = "open"
    
pathToPython = os.path.join(sys.prefix, "python.exe")
if not os.path.isfile(pathToPython):
    print "cannot find the python executable: %s"% pathToPython
    while True:
        pass
    raise
    
try:
    import natlinkconfigfunctions
except ImportError:
    print 'Unable to start the command line interface configuration program of NatLink/Unimacro/Vocola:'
    print 'the python module natlinkconfigfunctions.py gives an error.'
    print
    print 'Please report this error message to the NatLink developers,'
    print 'preferably to q.hoogenboom@antenna.nl'
    print
    import traceback
    traceback.print_exc()
    
    while True:
        pass
    raise



    
configFunctionsPath = os.path.join(os.path.dirname(__file__), "natlinkconfigfunctions.py")
if not os.path.isfile(configFunctionsPath):
    print "cannot find the CLI configuration program: %s"% configFunctionsPath
    while True:
        pass
    raise


print 'run with "%s": %s'% (openpar, configFunctionsPath)
ShellExecute(0, openpar, pathToPython, configFunctionsPath, "", 1)
