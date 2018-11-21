#! python3
import os
import sys
import time

if not sys.version.startswith('2.'):
    print('This script should start with python3, not with %s'% sys.version)
    time.sleep(10)
    sys.exit()

if sys.version.find("64 bit") >= 0:
    print('=============================================')
    print('You installed a 64 bit version of Python.')
    print('Natlink cannot run with this version, please uninstall and')
    print('install a 32 bit version of python, see https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html')
    print('=============================================')
    while True:
        pass
    raise

try:
    import win32api
except ImportError:
    print('Unable to start the configuration program of NatLink/Unimacro/Vocola')
    print('because the module "win32api" is not found.  This probably')
    print('means that the windowns extensions package for (pywin32) is not installed (properly).')

    print('')
    print('Please try to install this package via pip')
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
    print("cannot find the python executable: %s"% pathToPython)
    while True:
        pass
    raise
    
try:
    import natlinkconfigfunctions
except ImportError:
    print('Unable to start the command line interface configuration program of NatLink/Unimacro/Vocola:')
    print('the python module natlinkconfigfunctions.py gives an error.')
    print('')
    print('Please report this error message to the NatLink developers,')
    print('preferably to q.hoogenboom@antenna.nl')
    import traceback
    traceback.print_exc()
    
    while True:
        pass
    raise
  
configFunctionsPath = os.path.join(os.path.dirname(__file__), "natlinkconfigfunctions.py")
if not os.path.isfile(configFunctionsPath):
    print("cannot find the CLI configuration program: %s"% configFunctionsPath)
    while True:
        pass
    raise


# print('run with "%s": %s'% (openpar, configFunctionsPath)
ShellExecute(0, openpar, pathToPython, configFunctionsPath, "", 1)
