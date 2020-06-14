#
#
# unittestRegistryDict.py (part of the Natlink project)
#
# testing the RegistryDict module, which accesses the Registry in a dict way.
# Run this test program in elevated mode!!
#
import sys
import unittest
import types
import os
import os.path
import time
import winreg

from RegistryDictUserDictWinreg  import RegistryDict

def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print('baseFolder from argv: %s'% baseFolder)
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print('baseFolder from __file__: %s'% baseFolder)
    if not baseFolder or baseFolder == '.':
        baseFolder = os.getcwd()
        print('baseFolder was empty, take wd: %s'% baseFolder)
    return baseFolder

#---------------------------------------------------------------------------
class UnittestRegistryDict(unittest.TestCase):
    def setUp(self):
        """create own registry section in Local Machine for playing around
        """
        self.lm = RegistryDict(winreg.HKEY_LOCAL_MACHINE,"Software\TestRegistryDict", flags=None)
        pass            

    def tearDown(self):
        """remove test  registry section in Local Machine
        """
        # 
        # print('should start with empty dict: ', lm)
        # lm['test'] = "abcd"
        # print('should contain test/abcd: ', lm)
        # lm['test'] = "xxxx"
        # print('should contain test/xxxx: ', lm)
        # del lm['test']
        # print('should be empty again: ', lm)
        # del lm['dummy']
        # print('should be still empty: ', lm)
        # print('--- now test int values (REG_DWORD)')
        # lm['test'] = 1
        # print('should contain: test/1', lm)
        # lm['test'] = 0
        # print('should contain: test/1', lm)
        # del lm['test']
        # print('should be empty again: ', lm)
        # 
        # # now put a dict in:
        # lm['testdict'] = {"": "path/to/natlink", "Unimacro": "path/to/unimacro"}
        # print('should contain a dict with two items: ', lm)
        
        ls = RegistryDict(winreg.HKEY_LOCAL_MACHINE,"Software")
        del ls['TestRegistryDict']
        pass

    def testCreateSimpleItem(self):
        """test the working of the test suite and create an item.
        
        After tearDown this item should be removed again
        """
        print("start is empty: "% self.lm)
        self.lm['test'] = 'abcd'
        print("now lm is: %s"% self.lm)
        pass

def run():
    print('starting UnittestRegistryDict')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def test....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    suite = unittest.makeSuite(UnittestRegistryDict, 'test')
    result = unittest.TextTestRunner().run(suite)
    print(result)

if __name__ == "__main__":
    run()
