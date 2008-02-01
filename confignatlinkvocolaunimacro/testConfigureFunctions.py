import sys, unittest, win32api, os


file1 = os.path.join("C:\\", "testinifile.ini")

# need this bunch to get connection with the core folder...
#--------- two utility functions:
def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder:
        baseFolder = os.getcwd()
        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

def getCoreDir(thisDir):
    """get the natlink core folder, relative from the current folder

    This folder should be relative to this with ../macrosystem/core and should contain
    natlinkmain.py and natlink.dll and natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'macrosystem', 'core') )
    if not os.path.isdir(coreFolder):
        print 'not a directory: %s'% coreFolder
        return thisDir
    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
    if not os.path.isfile(dllPath):
        print 'natlink.dll not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
#-----------------------------------------------------

thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'appending %s to pythonpath...'% coreDir
    sys.path.append(coreDir)
# now we can import:::
import natlinkcorefunctions


class TestConfigureFunctions(unittest.TestCase):
    """test ini file functions from win32api

    and other functions used in the core of natlink


    first: the WriteProfileVal functions, for getting and setting and deleting
           inifile  values

    second: testing the natlinkcorefunctions:
            getExtendedEnv etc.

    
    """
    def setUp(self):
        # for setting getting values test:
        f1 = open(file1, 'w')
        f1.close()



    def tearDown(self):

        #  for setting getting values test:        
        if os.path.isfile(file1):
            os.remove(file1)
        



    def test_setting_values(self):
        """this test is needed, because deleting a key from inifile is not trivial.

        See below, deleting a section I couldn't get to work
        """
        f1 = open(file1, 'w')
        f1.close()
        win32api.WriteProfileVal('s1', 'k1','v1', file1)
        win32api.WriteProfileVal('s1', 'k2','v2', file1)
        win32api.WriteProfileVal('s2', 'kk1','vv1', file1)
        section = win32api.GetProfileSection('s1', file1)
        expected = ['k1=v1', 'k2=v2']
        self.assert_(expected == section, "section |%s| not as expected: |%s|"% (section, expected))

        # this call deletes a key:::::    
        win32api.WriteProfileVal('s1', 'k2',None, file1)
        section = win32api.GetProfileSection('s1', file1)
        expected = ['k1=v1']
        self.assert_(expected == section, "section |%s| after deleted keys is not as expected: |%s|"% (section, expected))
                
        
    def test_getExtendedEnv(self):
        """Test the different functions in natlinkcorefunctions that do environment variables

        """
        home = natlinkcorefunctions.getExtendedEnv("HOME")
        self.assert_(os.path.isdir(home), "home should be a folder, not: |%s|"% home)
        home2 = natlinkcorefunctions.getExtendedEnv("~")
        self.assert_(home == home2, "home2 (~) should be same as HOME (%s), not: |%s|"%
                     (home,home2))
        
        

                


def _run():
    unittest.main()
    

if __name__ == "__main__":
    _run()
