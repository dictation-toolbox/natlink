import os, time
from win32api import ShellExecute, GetVersionEx
import sys
# see natlinkstatus.py for windows versions (getWindowsVersion)
wversion = GetVersionEx()
if wversion[3] == 2 and wversion[0] >= 6:
    # Vista and later, run as administrator, so elevated mode:
    openpar = "runas"
else:
    openpar = "open"
    
pathToPythonW = os.path.join(sys.prefix, "pythonw.exe")
if not os.path.isfile(pathToPythonW):
    raise IOError("cannot find the pythonw executable")

    
configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
#print 'run with "%s": %s'% (openpar, configPath)
#print 'sys.version: ', sys.version
#time.sleep(5)
ShellExecute(0, openpar, pathToPythonW, configPath, "", 1)
