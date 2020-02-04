#
#
# unittestClipboard.py (part of the Natlink project)
#
# this module tests the clipboard module, natlinkclipboard in natlink/macrosystem/core,
# as developed by Christo Butcher clipboard.py for Dragonfly,
# improved and augmented by Quintijn Hoogenboom 2019.
#
#
import sys
import unittest
import types
import os
import os.path
import time
# use utilities of Unimacro:
import readwritefile
import natlinkutilsqh
import actions
import TestCaseWithHelpers
import natlink
import natlinkclipboard  # module we are testing, adapted version of Christo's clipboard.py

natconnectOption = 0 # no difference for these test, I presume

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

thisDir = getBaseFolder(globals())
logFileName = os.path.join(thisDir, "testresult.txt")
unimacroDir = os.path.normpath(os.path.join(thisDir, "..", "..", "Unimacro"))
if os.path.isdir(unimacroDir):
    if not unimacroDir in sys.path:
        print('inserting %s to pythonpath...'% unimacroDir)
        sys.path.insert(0, unimacroDir)
        create_files()
else:
    print('error, wrong unimacroDir: %s'% unimacroDir)


#---------------------------------------------------------------------------
# These tests should be run after we call natConnect
class UnittestClipboard(TestCaseWithHelpers.TestCaseWithHelpers):
    def setUp(self):
        self.connect()
        self.thisHndle = natlink.getCurrentModule()[2]
        self.org_text = "Xyz"*3
        natlinkclipboard.Clipboard.set_system_text(self.org_text)
        # self.setupWindows()
        # self.setupTextFiles() # should be done "by hand"
        print('thisHndle: %s'% self.thisHndle)
        # take txt files from test_clipboardfile subdirectory, a sorted list of txt files, see at bottom of module
        # take docx files etc. 
        self.allWindows = {}
            

    def tearDown(self):
        print('----------- tearDown')
        natlinkutilsqh.SetForegroundWindow(self.thisHndle)
        # close if they were opened in the start of a test:
        for hndle in self.allWindows: 
            print('closing: %s (allWindows: %s)'% (hndle, self.allWindows[hndle]))
            if hndle:
                self.closeWindow(hndle)
            else:
                print('how can this be? hndle %s of window: %s'% (hndle, self.allWindows[hndle]))
        self.disconnect()
        pass

        
    def connect(self):
        # start with 1 for thread safety when run from pythonwin:
        natlink.natConnect(natconnectOption)

    def disconnect(self):
        natlink.natDisconnect()

    def openTestFile(self, filePath, app=None, waitingTime=0.05):
        """open a file in its default window, for testing clipboard.
        
        waitingTime could be needed larger eg for word documents...
        
        Return the handle
        """
        natlinkutilsqh.rememberWindow()
        # app = r"C:\Program Files (x86)\Frescobaldi\frescobaldi.exe"
        # app = r"C:\Program Files (x86)\ActiveState Komodo IDE 11\komodo.exe"
        print('opening %s (app: %s) sleeptime: %s'% (filePath, app, waitingTime))
        result = actions.UnimacroBringUp(app=app, filepath=filePath)
        natlinkutilsqh.waitForNewWindow(debug=True, waitingTime=waitingTime)
        # time.sleep(2)
        fileName = os.path.split(filePath)[-1]
        if not natlinkutilsqh.waitForWindowTitle(fileName, waitingTime=waitingTime):
            print('could not fileName in window title: %s'% fileName)
            natlinkutilsqh.returnToWindow()
            return
        
        curmod = natlinkutilsqh.getCurrentModuleSafe() # try a few times if it fails first
        print('opened %s: %s'% (curmod[2], filePath))
        natlinkutilsqh.returnToWindow()
        return curmod[2]

    def closeWindow(self, hndle):
        """close the test files
        """
        curmod = natlinkutilsqh.getCurrentModuleSafe() # try a few times if it fails first
        if curmod[2] != hndle:
            natlinkutilsqh.SetForegroundWindow(hndle, debug=True)
        curmod = natlinkutilsqh.getCurrentModuleSafe() # try a few times if it fails first
        if curmod[2] == hndle:
            actions.do_KW()

    def tttestCopyClipboardCautious(self):
        """test the copying of the clipboard, with waiting times
        """
        ## open the txtFiles (are closed in tearDown)
        for txtFile in txtFiles:
            hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', txtFile))
            if hndle:
                self.allWindows[hndle] = txtFile
            else:
                print('could not open %s'% txtFile)

        cb = natlinkclipboard.Clipboard(save_clear=True)

        ## empty file:
        expTextPrev = ""
        for hndle, txtFile in self.allWindows.items():
            filePath = os.path.join(thisDir, 'test_clipboardfiles', txtFile)
            encoding, bom, expText = readwritefile.readAnything(filePath)
            if txtFile == "emptytest.txt":
                # now the clipboard remains unchanged...
                expText = expTextPrev
            else:
                # now save for empty file:
                expTextPrev = expText
            natlinkutilsqh.SetForegroundWindow(hndle)
            time.sleep(0.5)
            if txtFile == "emptytest.txt":
                time.sleep(3)
            natlink.playString("{ctrl+a}{ctrl+c}")
            
            # cb.copy_from_system(waiting_interval=0.05)
            # natlinkutilsqh.SetForegroundWindow(self.thisHndle)
            # print 'cb text: %s'% cb
            got = cb.get_text(waiting_interval=0.05)
            if txtFile == "emptytest.txt":
                self.assert_equal(expTextPrev, got, "testing empty txt file %s, result not as expected"% txtFile)
            else:
                self.assert_equal(expPrev, got, "testing txt file %s, result not as expected"% txtFile)

        # cb.restore()  #should be done automatically when varable is destroid

    def tttestCopyClipboardQuick(self):
        """test the copying of the clipboard, without waiting times
        """
        ## open the txtFiles (are closed in tearDown)
        for txtFile in txtFiles:
            hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', txtFile))
            if hndle:
                self.allWindows[hndle] = txtFile
            else:
                print('did not open testfile: %s'% txtFile)


        cb = natlinkclipboard.Clipboard(save_clear=True)

        ## empty file:
        expTextPrev = ""
        for hndle, txtFile in self.allWindows.items():
            filePath = os.path.join(thisDir, 'test_clipboardfiles', txtFile)
            encoding, bom, expText = readwritefile.readAnything(filePath)
            if txtFile == "emptytest.txt":
                expText = expTextPrev
            else:
                expTextPrev = expText
            natlinkutilsqh.SetForegroundWindow(hndle)
            natlink.playString("{ctrl+a}{ctrl+c}")
            cb.copy_from_system()
            # natlinkutilsqh.SetForegroundWindow(self.thisHndle)
            # print 'cb text: %s'% cb
            got = cb.get_text()
            self.assert_equal(expText, got, "testing txt file %s, result not as expected"% txtFile)


            # also test the class method (direct call)
            got = natlinkclipboard.Clipboard.get_system_text()
            self.assert_equal(expText, got, "testing txt file %s, with class method, result not as expected"% txtFile)

        cb.restore()


    def testCopyClipboardWord(self):
        """test the copying of the clipboard word documents
        """
        ## open the txtFiles (are closed in tearDown)
        for docxFile in docxFiles:
            hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', docxFile), waitingTime=0.5)
            if hndle:
                self.allWindows[hndle] = docxFile
            else:
                print('could not open test file %s'% docxFile)

        cb = natlinkclipboard.Clipboard(save_clear=True)

        ## empty file:
        expTextPrev = ""
        nCycles = 2   # make it 10 or 50 to do a longer test
        for i in range(nCycles):
            for hndle, docxFile in self.allWindows.items():
                print('trying %s (%s) (cycle %s)'% (hndle, docxFile, i+1))
                natlinkutilsqh.SetForegroundWindow(hndle)
                time.sleep(0.2)  # word needs a little time before keystrokes are accepted...
                natlink.playString("{ctrl+home}{shift+end}{shift+down 3}{ctrl+c}")
                # cb.copy_from_system(waiting_interval=0.005)
                # natlinkutilsqh.SetForegroundWindow(self.thisHndle)
                gotall = cb.get_text(waiting_interval=0.05)
                lengotall = len(gotall)
                got = gotall
                expText = "A small word document.\n\nWith only a few lines\n\n"
                if not got:
                    print('no text, file: %s'% docxFile)
                self.assert_equal(expText, got, "testing docx file %s, result not as expected"% docxFile)

                # also test the class method (direct call)
                got = natlinkclipboard.Clipboard.get_system_text()
                self.assert_equal(expText, got, "testing docx file %s, with class method, result not as expected"% docxFile)

        pass    

    def tttestSwitchingWindows(self):
        """test the opening of more explorer windows, word windows and notepad windows
        
        switching back and forth, using natlinkutilsqh.SetForegroundWindow!!!
        
        nCycles can be adapted to make test quicker or slower
        """
        ## open the txtFiles (are closed in tearDown)
        print('------------ testSwitchingWindows----------------------------------')

        for explDir in explDirectories:
            hndle = self.openTestFile(explDir)
            if hndle:
                self.allWindows[hndle] = explDir
            else:
                raise IOError('could not open test directory %s'%  explDir)
        for txtFile in txtFiles:
            hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', txtFile))
            if hndle:
                self.allWindows[hndle] = txtFile
            else:
                print('could not open %s'% txtFile)
        for docxFile in docxFiles:
            hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', docxFile), waitingTime=0.5)
            if hndle:
                self.allWindows[hndle] = docxFile
            else:
                print('could not open %s'% docxFile)

        allKeys = sorted(self.allWindows.keys())
        print('go with allKeys: %s'% allKeys)

        nCycles = 20
        for i in range(nCycles):
            for hndle in allKeys:
                target = self.allWindows[hndle]
                print('try to get %s (%s)'% (hndle, target))
                result = natlinkutilsqh.SetForegroundWindow(hndle, debug=True)
                if not result:
                    print('failed to set foreground window %s'% hndle)
                    continue
                curMod = natlinkutilsqh.getCurrentModuleSafe()
                self.assert_equal(hndle, curMod[2], "hndle not as expected after SetForegroundWindow %s (got: %s) (target is: %s)"% (hndle, curMod[2], target))

        time.sleep(1)
        pass

    def tttestCopyingFromExplorerWindows(self):
        """test the getting of explorer items
        
        dialog windows #32770 now also work.
        een
        The testing is not stable. But probably these are only testing issues.
        """
        cb = natlinkclipboard.Clipboard()
        ## open the txtFiles (are closed in tearDown)
        for explDir in explDirectories:
            hndle = self.openTestFile(explDir)
            if hndle:
                self.allWindows[hndle] = explDir
            else:
                raise IOError('could not open test directory %s'%  explDir)
        # for txtFile in txtFiles:
        #     hndle = self.openTestFile(os.path.join(thisDir, 'test_clipboardfiles', txtFile))
        #     if hndle:
        #         self.allWindows[hndle] = txtFile
        #     else:
        #         print 'did not open testfile: %s'% txtFile

        nCycles = 2
        for i in range(nCycles):
            for hndle in list(self.allWindows.keys()):
                steps = (i % 4) + 2
                expDir = self.allWindows[hndle]
                print('try to get %s (%s) (cycle %s)'% (hndle, expDir, i+1))
                result = natlinkutilsqh.SetForegroundWindow(hndle, debug=True)
                if not result:
                    print('could not get %s in the foreground after SetForegroundWindow %s'% (expDir, hndle))
                    continue
                curMod = natlinkutilsqh.getCurrentModuleSafe()
                print('doing %s lines of directory'% (steps+1,))
                expDNr = self.allWindows[hndle]
                if hndle != curMod[2]:
                    pass
                self.assert_equal(hndle, curMod[2], "hndle not as expected after SetForegroundWindow %s (%s)"% (hndle, expDir))
                testChild = (curMod[0].find("notepad") > 0)
                if testChild:
                    natlink.playString("{ctrl+o}")
                    time.sleep(0.2)
                    natlink.playString("{alt+d}%s{enter}"% testFilesDir)
                    time.sleep(0.2)

                actions.do_RMP(1, 0.5, 0.5) # click on middle of window

                time.sleep(1)

                natlink.playString("{home}{shift+down %s}"% steps, 0x200)
                
                time.sleep(1)
                
                natlink.playString("{ctrl+c}", 0x200)

                time.sleep(1)


                if testChild:
                    time.sleep(0.1)
                    natlink.playString("{esc}")
                    time.sleep(0.1)
                
                time.sleep(0.5)
                if testChild:
                    pass
                got = cb.get_folderinfo(waiting_interval=0.1)
                
                exp = ()
                lenexp = steps
                if testChild:
                    lenexp = steps + 1
                    
                gotclassmethod = natlinkclipboard.Clipboard.Get_folderinfo()


                print('got: %s'% repr(got))
                print('gotclassmethod: %s'% repr(gotclassmethod))
                if got is None:
                    pass
                self.assert_equal(got, gotclassmethod, "getting folderinfo should be the same from class method and instance method")
                self.assert_equal(type(exp), type(got), "result should be at least a tupl, testChild is: %s"% testChild)
                self.assert_equal(lenexp, len(got), "expect length of 2, but: %s, testChild is: %s"% (repr(got), testChild))

                formats = natlinkclipboard.Clipboard.Get_clipboard_formats()
                self.assertTrue(type(formats) == list, "list of formats should be a list, not: %s"% repr(formats))
                gotclassmethod = natlinkclipboard.Clipboard.Get_folderinfo()
                self.assert_equal(got, gotclassmethod, "getting folderinfo should be the same from class method and instance method")

        time.sleep(1)
        # cb.restore()
        pass

## create if necessary test directory and test files:
testDirName = 'test_clipboardfiles'
testFilesDir = os.path.join(thisDir, 'test_clipboardfiles')
if not os.path.isdir(testFilesDir):
    os.path.mkdir(testFilesDir)
    print('Created test directory: %s'% testFilesDir)
    print('Please put test files in this directory! .txt, .docx')
    sys.exit()

testFiles = os.listdir(testFilesDir)
if testFiles:
    print('testFiles: ', testFiles)
    txtFiles = sorted([f for f in testFiles if f.endswith(".txt")])
    docxFiles = sorted([f for f in testFiles if f.endswith(".docx") and not f.startswith("~")])
    print('%s txtFiles: %s'% (len(txtFiles), repr(txtFiles)))
    print('%s docxFiles: %s'% (len(docxFiles), repr(docxFiles)))
explDirectories = [testFilesDir, os.path.normpath(os.path.join(testFilesDir, "..", "..", "MiscScripts"))]

def log(t):
    print(t)

def run():
    log('starting UnittestClipboard')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def test....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    suite = unittest.makeSuite(UnittestClipboard, 'test')
    result = unittest.TextTestRunner().run(suite)
    print(result)
if __name__ == "__main__":
    natlink.natConnect()
    run()
