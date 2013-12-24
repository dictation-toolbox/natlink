import os, sys


if sys.version.find("64 bit") >= 0:
    print '============================================='
    print 'You installed a 64 bit version of Python.'
    print 'NatLink cannot run with this version, please uninstall and'
    print 'install a 32 bit version of python, see http://qh.antenna.nl/unimacro,,,'
    print '============================================='
    time.sleep(30)
    sys.exit()


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
