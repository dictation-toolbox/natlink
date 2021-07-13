#! python3
#pylint:disable=C0415, W0611, W0703, W0702
"""starting the configure natlink gui program in elevated mode
"""
import os
import os.path
import sys
import time
# import re
import pathlib
thisDir = os.path.split(__file__)[0]

#all this code is in main so that it is possible for the package 
#to create a script in site-packages/scripts.
def main():
    """main module
    """
    #pylint:disable=E0611  ## the win32api imports ?!?
    #we have to add the current path and its parent to the search path.
    current_dir = pathlib.WindowsPath(__file__)
    parent_dir =current_dir.parent
    for p in (current_dir,parent_dir):
        sys.path.append(str(p))
    
    
    
    #
    print('Starting start_configurenatlink.py,')
    print('Try to run configurenatlink.py, the Natlink Config GUI, in Elevated mode...')

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
    except:
        print(f'''Unable to run the GUI configuration program of Natlink/Unimacro/Vocola/Dragonfly\n
    because a module was not found.  An error occurred during import.  This is probably due to a missing or incorrect prequisite.\n
    Please run 'pip install -r requirements.txt in {thisDir}\n
    ''')
        time.sleep(30)
        sys.exit()

    try:
        import natlinkconfigfunctions
    except ImportError:
        print('''Unable to start the configuration program of Natlink/Unimacro/Vocola/Dragonfly:\n
    the python module natlinkconfigfunctions.py gives an error.\n
    Please report this error message to the Natlink developers,\n
    preferably to q.hoogenboom@antenna.nl\n''')
        import traceback
        traceback.print_exc()

        # time.sleep(30)
        sys.exit()


    try:
        # see natlinkstatus.py for windows versions (getWindowsVersion)
        openpar = "runas"
        #python and pythonw.exe may be in a scripts directory in virtualenvs.  
        #to find the path of the python executable, 
        # pathToPythonExecutables="\\".join(sys.executable.split('\\')[0:-1])

        pathToPythonW = f'{sys.prefix}\\pythonw.exe'
        if not os.path.isfile(pathToPythonW):
            print(f'Cannot find the Pythonw exectutable: {pathToPythonW}')
            # time.sleep(30)
            sys.exit()

        configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
        if not os.path.isfile(configPath):
            print("cannot find the Natlink/Unimacro/Vocola/Dragonfly configuration program: %s"% configPath)
            # time.sleep(30)
            sys.exit()


        #print('run with "%s": %s'% (openpar, configPath)
        #print('sys.version: ', sys.version
        #time.sleep(5)
        ShellExecute(0, openpar, pathToPythonW, configPath, "", 1)
    except:
        import traceback
        traceback.print_exc()
        time.sleep(60)

main()
