import os, sys
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
    raise IOError("cannot find the python executable")
    
    
configFunctionsPath = os.path.join(os.path.dirname(__file__), "natlinkconfigfunctions.py")
print 'run with "%s": %s'% (openpar, configFunctionsPath)
ShellExecute(0, openpar, pathToPython, configFunctionsPath, "", 1)
