
import sys

try:
    import wx
except ImportError:
    print 'Unable to run the GUI configuration program of NatLink/Unimacro/Vocola'
    print 'because module wx was not found.  This probably'
    print 'means that wxPython is not installed correct:'
    print 'You should do this with "Run as administrator" (right click on executable)'

    print
    print 'Either install wxPython (recommended) or use the CLI (Command Line Interface)'
    print 'NatLink configuration program.'
    print
    print 'A version of this package suitable for use with NatLink can be obtained from'
    print 'http://sourceforge.net/projects/natlink/files/pythonfornatlink/' 
    print '(choose the python version you are using right now: %s)'% sys.version[:3]
    print
    while True:
        pass
    raise

try:
    import win32api
except ImportError:
    print 'Unable to start the configuration program of NatLink/Unimacro/Vocola'
    print 'because the module "win32api" is not found.  This probably'
    print 'means that the win32 extensions package for python (32 bits) is not installed (properly).'
    print 'You should do this with "Run as administrator" (right click on executable)'
    print
    print 'A version of this package suitable for use with NatLink can be obtained from'
    print 'http://sourceforge.net/projects/natlink/files/pythonfornatlink/' 
    print '(choose the python version you are using right now: %s)'% sys.version[:3]
    print
    while True:
        pass
    raise



try:
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
        print "cannot find the Pythonw exectutable: %s"% pathToPythonW
        while True:
            pass
        raise

        
    configPath = os.path.join(os.path.dirname(__file__), "configurenatlink.pyw")
    if not os.path.isfile(configPath):
        print "cannot find the NatLink/Unimacro/Vocola configuration program: %s"% configPath
        while True:
            pass
        raise


    #print 'run with "%s": %s'% (openpar, configPath)
    #print 'sys.version: ', sys.version
    #time.sleep(5)
    ShellExecute(0, openpar, pathToPythonW, configPath, "", 1)
except:
    import traceback
    traceback.print_exc()
    time.sleep(60)