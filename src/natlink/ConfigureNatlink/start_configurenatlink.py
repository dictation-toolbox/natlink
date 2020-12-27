#! python3
import os
import sys
import time
import re

#
print('Starting start_configurenatlink.py,')
print('Try to run configurenatlink.py, the Natlink Config GUI, in Elevated mode...')
print()

if sys.version.find("64 bit") >= 0:
    print('''=============================================\n
You run this module from a 64 bit version of Python.\n
Natlink cannot run with this version, please be sure to \n
install a 32 bit version of python, and run from there.\n
See https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html\n
=============================================''')
    time.sleep(30)
    sys.exit()

try:
    import wx
    from win32api import ShellExecute, GetVersionEx
except (Exception, e):
    print(f'''Unable to run the GUI configuration program of Natlink/Unimacro/Vocola\n
because a module was not found.  An error occurred during import.  This is probably due to a missing or incorrect prequisite.\n
Please run 'pip install -r requirements.txt in {thisDir}\n
More information https://qh.antenna.nl/unimacro/installation/problemswithinstallation.html\n\n
Exception Details:\n{e}''')
    time.sleep(30)
    sys.exit()

try:
    import natlinkconfigfunctions
except ImportError:
    print('''Unable to start the configuration program of Natlink/Unimacro/Vocola:\n
the python module natlinkconfigfunctions.py gives an error.\n
Please report this error message to the Natlink developers,\n
preferably to q.hoogenboom@antenna.nl\n''')
    import traceback
    traceback.print_exc()

    # time.sleep(30)
    sys.exit()


try:
    # see natlinkstatus.py for windows versions (getWindowsVersion)
    wversion = GetVersionEx()
    if wversion[3] == 2 and wversion[0] >= 6:
        # Vista and later, run as administrator, so elevated mode:
        openpar = "runas"
    else:
        openpar = "open"
    #python and pythonw.exe may be in a scripts directory in virtualenvs.  
    #to find the path of the python executable, 
    pathToPythonExecutables="\\".join(sys.executable.split('\\')[0:-1])

    pathToPythonW = f"{pathToPythonExecutables}\\pythonw.exe" 
    if not os.path.isfile(pathToPythonW):
        print("cannot find the Pythonw exectutable: %s"% pathToPythonW)
        # time.sleep(30)
        sys.exit()

    configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
    if not os.path.isfile(configPath):
        print("cannot find the Natlink/Unimacro/Vocola configuration program: %s"% configPath)
        # time.sleep(30)
        sys.exit()


    #print('run with "%s": %s'% (openpar, configPath)
    #print('sys.version: ', sys.version
    #time.sleep(5)
    ShellExecute(0, openpar, pathToPythonW, configPath, "", 1)
    import traceback
    traceback.print_exc()
except:
    import traceback
    traceback.print_exc()
    time.sleep(60)
