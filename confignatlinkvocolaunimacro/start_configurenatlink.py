import os
from win32api import ShellExecute, GetVersionEx
import sys
# see natlinkstatus.py for windows versions (getWindowsVersion)
wversion = GetVersionEx()
if wversion[3] == 2 and wversion[0] >= 6:
    # Vista and later, run as administrator, so elevated mode:
    openpar = "runas"
else:
    openpar = "open"
configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
#print 'run with "%s": %s'% (openpar, configPath)
ShellExecute(0, openpar, "pythonw.exe", configPath, "", 1)
