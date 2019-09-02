#! python2
from __future__ import print_function
import six
import os
import sys
import time

if six.PY2: ModuleNotFoundError = ImportError

print('Starting start_natlinkconfigfunctions.py,')
print('Try to run natlinkconfigfunctions.py in Elevated mode...')
print()

if not sys.version.startswith('2.'):
    print('This script should start with python3, not with %s'% sys.version)
    time.sleep(30)
    sys.exit()

try:
    from future import standard_library
except ModuleNotFoundError:
    print('Cannot find module "future", consider pip install future')
    time.sleep(30)
else:
    standard_library.install_aliases()
    from future.builtins import next
    from future.builtins import object


if sys.version.find("64 bit") >= 0:
    print('=============================================')
    print('You installed a 64 bit version of Python.')
    print('Natlink cannot run with this version, please uninstall and')
    print('install a 32 bit version of python, see https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html')
    print('=============================================')
    time.sleep(30)
    sys.exit()

try:
    from win32api import ShellExecute, GetVersionEx
except ImportError:
    print('Unable to start the configuration program of')
    print('Natlink/Unimacro/Vocola, because the')
    print('bmodule "win32api" is not found.  This probably')
    print('means that the windowns extensions package for (pywin32) is not installed (properly).')

    print('')
    print('Please try to install this package via pip')
    time.sleep(30)
    sys.exit()



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
    time.sleep(30)
    sys.exit()    
try:
    import natlinkconfigfunctions
except:
    print('Unable to start the command line interface configuration program of')
    print('Natlink/Unimacro/Vocola:')
    print('the python module natlinkconfigfunctions.py gives an error.')
    print('')
    print('Please report this error message to the Natlink developers,')
    print('preferably to q.hoogenboom@antenna.nl')
    import traceback
    traceback.print_exc()
    
    time.sleep(30)
    sys.exit()
  
configFunctionsPath = os.path.join(os.path.dirname(__file__), "natlinkconfigfunctions.py")
if not os.path.isfile(configFunctionsPath):
    print("cannot find the CLI configuration program: %s"% configFunctionsPath)
    time.sleep(30)
    sys.exit()


# print('run with "%s": %s'% (openpar, configFunctionsPath)
ShellExecute(0, openpar, pathToPython, configFunctionsPath, "", 1)
