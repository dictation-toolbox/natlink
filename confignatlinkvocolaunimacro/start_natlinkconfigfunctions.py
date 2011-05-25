import os
from win32api import ShellExecute, GetVersionEx

# see natlinkstatus.py for windows versions (getWindowsVersion)
wversion = GetVersionEx()
if wversion[3] == 2 and wversion[0] >= 6:
    # Vista and later
    openpar = "runas"
else:
    openpar = "open"
path = os.path.join(os.path.dirname(__file__), "start_natlinkconfigfunctions.bat")
print 'run with "%s": %s'% (openpar, path)
ShellExecute(0, openpar, path, None, "", 1)
