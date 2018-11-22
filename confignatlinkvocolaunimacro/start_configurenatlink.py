#! python3
from __future__ import print_function

import os
import sys
import time

from future import standard_library
standard_library.install_aliases()
from future.builtins import next
from future.builtins import object

if not sys.version.startswith('2.'):
    print('This script should start with python2, not with %s'% sys.version)
    time.sleep(30)
    sys.exit()

try:
    import wx
except KeyError:
    print('Unable to run the GUI configuration program of NatLink/Unimacro/Vocola')
    print('because module wx was not found.  This probably')
    print('means that wxPython is not installed correct:')
    print()
    print('Please try to install wxPython via pip, see https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html')
    time.sleep(30)
    sys.exit()

try:
    from win32api import ShellExecute, GetVersionEx
except ImportError:
    print('Unable to start the configuration program of NatLink/Unimacro/Vocola')
    print('because the module "win32api" is not found.  This probably')
    print('means that the win32 extensions package, pywin32, is not installed (properly).')
    print()
    print('Please try to install pywin32 via pip, see https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html')
    print()
    print('In some rare cases this install did not finish correct.')
    print('You can then try to run the batch script "start_postinstallscript_pywin32.cmd" in')
    print('Admin mode, in order to finish the installation. Hopefully this helps.')
    print('This file can be found in the "confignatlinkvocolaunimacro" subdirectory of your NatLink directory.')
    time.sleep(30)
    sys.exit()

try:
    import natlinkconfigfunctions
except ImportError:
    print('Unable to start the configuration program of NatLink/Unimacro/Vocola:')
    print('the python module natlinkconfigfunctions.py gives an error.')
    print()
    print('Please report this error message to the NatLink developers,')
    print('preferably to q.hoogenboom@antenna.nl')
    print()
    import traceback
    traceback.print_exc()
    
    time.sleep(30)
    sys.exit()


try:
    # see natlinkstatus.py for windows versions (getWindowsVersion)
    wversion = GetVersionEx()
    if wversion[3] == 2 and wversion[0] >= 6:
        # Vista and later, run as administrator, so elevated mode:
        openpar = "runas"
    else:
        openpar = "open"
        
    pathToPythonW = os.path.join(sys.prefix, "pythonw.exe")
    if not os.path.isfile(pathToPythonW):
        print("cannot find the Pythonw exectutable: %s"% pathToPythonW)
    time.sleep(30)
    sys.exit()
        
    configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
    if not os.path.isfile(configPath):
        print("cannot find the NatLink/Unimacro/Vocola configuration program: %s"% configPath)
    time.sleep(30)
    sys.exit()


    #print('run with "%s": %s'% (openpar, configPath)
    #print('sys.version: ', sys.version
    #time.sleep(5)
    ShellExecute(0, openpar, pathToPythonW, configPath, "", 1)
except:
    import traceback
    traceback.print_exc()
    time.sleep(60)