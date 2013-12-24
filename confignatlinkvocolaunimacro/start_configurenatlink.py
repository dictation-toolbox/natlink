import os, time
from win32api import ShellExecute, GetVersionEx
import sys
# see natlinkstatus.py for windows versions (getWindowsVersion)

if sys.version.find("64 bit") >= 0:
    print '============================================='
    print 'You installed a 64 bit version of Python.'
    print 'NatLink cannot run with this version, please uninstall and'
    print 'install a 32 bit version of python, see http://qh.antenna.nl/unimacro,,,'
    print '============================================='
   
    time.sleep(30)
    sys.exit()




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
