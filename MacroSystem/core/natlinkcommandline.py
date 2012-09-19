from natlink import *
from natlinkmain import *
import time


def start_natlink():
    """start natlink from a command line, possibly needed for Dragon 12
    if the starting from Dragon itself is broken
    """
    baseDirectory = os.path.split(
       sys.modules[modname].__dict__['__file__'])[0]
    
    baseDirectory = os.path.normpath(os.path.abspath(os.path.join(baseDirectory,"..")))
    
    # get the current user information from the NatLink module
    userDirectory = status.getUserDirectory()
    # for unimacro, in order to reach unimacro files to be imported:
    if userDirectory and os.path.isdir(userDirectory) and not userDirectory in sys.path:
        if debugLoad:
            print 'insert userDirectory: %s to sys.path!'% userDirectory
        sys.path.insert(0,userDirectory)
        

    # setting searchImportDirs:
    setSearchImportDirs()

    # get invariant variables:
    DNSversion = status.getDNSVersion()
    WindowsVersion = status.getWindowsVersion()
    if not isNatSpeakRunning():
        print 'start Dragon first, the rerun this script...'
        time.sleep(10)
        return
    natConnect(1)
    
    # init things identical to when user changes:
    changeCallback('user', getCurrentUser())

##    BaseModel, BaseTopic = status.getBaseModelBaseTopic()
    print 'Starting natlinkmain from %s:\n  NatLink version: %s\n  DNS version: %s\n  Python version: %s\n  Windows Version: %s\n'% \
              (status.getCoreDirectory(), status.getInstallVersion(),
               DNSversion, status.getPythonVersion(), WindowsVersion)
        
    # load all global files in user directory and current directory
    findAndLoadFiles()

    # initialize our callbacks
    setBeginCallback(beginCallback)
    setChangeCallback(changeCallback)
    try:
        while 1:
            waitForSpeech(0)
            print 'waited for speech'
    finally:
        natDisconnect()
        print 'natlink disconnected'


if __name__ == '__main__':
    start_natlink()