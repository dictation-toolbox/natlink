import os
from win32api import ShellExecute, GetVersionEx

# see natlinkstatus.py for windows versions (getWindowsVersion)
wversion = GetVersionEx()
if wversion[3] == 2 and wversion[0] >= 6:
    # Vista and later
    openpar = "runas"
else:
    openpar = "open"
configFunctionsPath = os.path.join(os.path.dirname(__file__), "natlinkconfigfunctions.py")
print 'run with "%s": %s'% (openpar, configFunctionsPath)
ShellExecute(0, openpar, "python.exe", configFunctionsPath, "", 1)
