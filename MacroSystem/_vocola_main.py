# _vocola_main.py - NatLink support for Vocola
# -*- coding: latin-1 -*-
#
# Contains:
#    - "Built-in" voice commands
#    - Autoloading of changed command files
#
# This file is copyright (c) 2002-2010 by Rick Mohr. It may be redistributed
# in any way as long as this copyright notice remains.
#
#
#
# Febr 4, 2008, QH:
# adapted to natlinkmain, which loads _vocola_main before other modules,
# and calls back also at begin Callback time before other modules to vocolaBeginCallback.
# If something changed within Vocola, report back to natlinkmain with
#  1 (change py file)
#  2 (new py file)
#

import sys, string
import win32api, win32gui, pywintypes
import os               # access to file information
import os.path          # to parse filenames
import time             # print time in messages
from stat import *      # file statistics
import re
import natlink
from natlinkutils import *
import natlinkstatus
import natlinkcorefunctions
status = natlinkstatus.NatlinkStatus()

want_unimacro = status.getVocolaTakesUnimacroActions()
if want_unimacro:
    try:
        import actions
    except ImportError:
        print 'WARNING: You want to use Unimacro actions in Vocola,'
        print 'but the Unimacro module "actions" cannot be imported.\n'
        print 'Either enable Unimacro, or switch on the '
        print 'option "Include Unimacro directory in PythonPath" in the '
        print 'config program or with '
        print 'the option "f" in the CLI (Command Line Interpreter).'
        want_unimacro = None
# Set to non-zero number of seconds to debug starting editors on
# Vocola source code:
debugSleepTime = 0

# The Vocola translator is a perl program. By default we use the precompiled
# executable vcl2py.exe, which doesn't require installing perl.
# To instead use perl and vcl2py.pl, set the following variable to 1:
usePerl = 0

# C module "simpscrp" defines Exec(), which runs a program in a minimized
# window and waits for completion. Since such modules need to be compiled
# separately for each python version we need this careful import:

NatLinkFolder = os.path.split(
    sys.modules['natlinkmain'].__dict__['__file__'])[0]

NatLinkFolder = re.sub(r'\core$', "", NatLinkFolder)

pydFolder = os.path.normpath(os.path.join(NatLinkFolder, '..', 'Vocola', 'Exec', sys.version[0:3]))
sys.path.append(pydFolder)
NatLinkFolder = os.path.abspath(NatLinkFolder)

import simpscrp

language = status.getLanguage()

class ThisGrammar(GrammarBase):
    if language == 'nld':
        gramSpec = """
<NatLinkWindow>     exported = Toon (NatLink|Vocola) venster;
<loadAll>           exported = (Laad|Lood) alle [stem|vojs] (Commandoos|Commands);
<loadCurrent>       exported = (Laad|Lood) [stem|vojs] (Commandoos|Commands);
<loadGlobal>        exported = (Laad|Lood) globale [stem|vojs] (Commandoos|Commands);
<discardOld>        exported = (Discard|Verwijder) (oude|oold) [stem|vojs] (Commandoos|Commands);
<edit>              exported = (Eddit|Bewerk|Sjoo|Toon) [stem|vojs] (Commandoos|Commands);
<editMachine>       exported = (Eddit|Bewerk|Sjoo|Toon) Machine [stem|vojs] (Commandoos|Commands);
<editGlobal>        exported = (Eddit|Bewerk|Sjoo|Toon) (Global|globale) [stem|vojs] (Commandoos|Commands);
<editGlobalMachine> exported = (Eddit|Bewerk|Sjoo|Toon) (Global|globale) Machine [stem|vojs] (Commandoos|Commands);
    """
    else:
        gramSpec = """
<NatLinkWindow>     exported = [Show] (NatLink|Vocola) Window;
<loadAll>           exported = Load All [Voice] Commands;
<loadCurrent>       exported = Load [Voice] Commands;
<loadGlobal>        exported = Load Global [Voice] Commands;
<discardOld>        exported = Discard Old [Voice] Commands;
<edit>              exported = (Edit|Show) [Voice] Commands;
<editMachine>       exported = (Edit|Show) Machine [Voice] Commands;
<editGlobal>        exported = (Edit|Show) Global [Voice] Commands;
<editGlobalMachine> exported = (Edit|Show) Global Machine [Voice] Commands;
    """

    def initialize(self):
        self.mayHaveCompiled = 0  # has the compiler been called?
        self.compilerError   = 0  # has a compiler error occurred?
        self.setNames()
        # remove previous Vocola/Python compilation output as it may be out
        # of date (e.g., new compiler, source file deleted, partially
        # written due to crash, new machine name, etc.):
        self.purgeOutput()

        if self.vocolaEnabled:        
            self.loadAllFiles('')

            self.load(self.gramSpec)
            self.activateAll()
        else:
            print 'vocola not active'


                

    def gotBegin(self,moduleInfo):
        self.currentModule = moduleInfo

                                      
    # Set member variables -- important folders and computer name
    def setNames(self):
        self.VocolaFolder = os.path.normpath(os.path.join(NatLinkFolder, '..', 'Vocola'))
        self.commandFolders = []
        self.systemCommandFolder = os.path.join(self.VocolaFolder, 'Commands')
        if os.path.isdir(self.systemCommandFolder):
            self.commandFolders.insert(0, self.systemCommandFolder)
        
        userCommandFolder = status.getVocolaUserDirectory()
            
        self.vocolaEnabled = (userCommandFolder and os.path.isdir(userCommandFolder))
        if self.vocolaEnabled:
            self.commandFolders.insert(0, userCommandFolder)                
            if status.getVocolaTakesLanguages():
                language = status.getLanguage()
                print '_vocola_main started with language: %s'% language
                if language != 'enx':
                    userCommandFolder2 = os.path.join(userCommandFolder, language)
                    if not os.path.isdir(userCommandFolder2):
                        print 'creating userCommandFolder for language %s'% language
                        self.createNewSubDirectory(userCommandFolder2)
                        self.copyToNewSubDirectory(userCommandFolder, userCommandFolder2)
                    self.commandFolders.insert(0, userCommandFolder2)                
        if os.environ.has_key('COMPUTERNAME'):
            self.machine = string.lower(os.environ['COMPUTERNAME'])
        else: self.machine = 'local'

    def createNewSubDirectory(self, subdirectory):
        os.mkdir(subdirectory)

    def copyToNewSubDirectory(self, trunk, subdirectory):
        for f in os.listdir(trunk):
            if f.endswith('.vcl'):
                self.copyVclFileLanguageVersion(os.path.join(trunk, f),
                                                os.path.join(subdirectory, f))
                                

    # Get app name by stripping folder and extension from currentModule name
    def getCurrentApplicationName(self):
        return string.lower(os.path.splitext(os.path.split(self.currentModule[0]) [1]) [0])

    def getSourceFilename(self, output_filename):
        m = re.match("^(.*)_vcl(\d*).pyc?$", output_filename)
        if not m: return None                    # Not a Vocola file
        if m.group(2) == "": return None         # old-style Vocola file
        name = m.group(1)
        i = int(m.group(2))
        if i > len(self.commandFolders): return None
        commandFolder = self.commandFolders[i]
        
        marker = "e_s_c_a_p_e_d__"
        m = re.match("^(.*)" + marker + "(.*)$", name)  # rightmost marker!
        if m:
            name = m.group(1)
            tail = m.group(2)
            tail = re.sub("__a_t__", "@", tail)
            tail = re.sub("___", "_", tail)
            name += tail

        name = re.sub("_@", "@", name)
        return commandFolder + "\\" + name + ".vcl"

    def deleteOrphanFiles(self):
        print "checking for orphans..."
        for f in os.listdir(NatLinkFolder):
            if not re.search("_vcl\d*.pyc?$", f): continue

            s = self.getSourceFilename(f)
            if s:
                if vocolaGetModTime(s)>0: continue

            f = os.path.join(NatLinkFolder, f)
            print "Deleting: " + f
            os.remove(f)

### Miscellaneous commands

    # "Show NatLink Window" -- print to output window so it appears
    def gotResults_NatLinkWindow(self, words, fullResults):
        print "This is the NatLink/Vocola output window"

### Loading Vocola Commands

    # "Load All Commands" -- translate all Vocola files
    def gotResults_loadAll(self, words, fullResults):
        self.loadAllFiles('-f')

    # "Load Commands" -- translate Vocola files for current application
    def gotResults_loadCurrent(self, words, fullResults):
        self.loadSpecificFiles(self.getCurrentApplicationName())

    # "Load Global Commands" -- translate global Vocola files
    def gotResults_loadGlobal(self, words, fullResults):
        self.loadSpecificFiles('')

    # "Discard Old [Voice] Commands" -- purge output then translate all files
    def gotResults_discardOld(self, words, fullResults):
        self.purgeOutput()
        self.loadAllFiles('-f')

    # Unload all commands, including those of files no longer existing
    def purgeOutput(self):
        pattern = re.compile("_vcl\d*\.pyc?$")
        [os.remove(os.path.join(NatLinkFolder,f)) for f in os.listdir(NatLinkFolder) if pattern.search(f)]

    # Load all command files
    def loadAllFiles(self, options):
        ## QH, I believe only 1 commandFolder should be done, numbered 0
        ## as the other numbers can be used for copying default files to your location if
        ## a new file is started...
        for i in range(len(self.commandFolders)):
            if i > 0: break    # only take 0
            suffix = "-suffix _vcl" + str(i) + " "
            self.runVocolaTranslator(self.commandFolders[i], suffix + options)

    # Load command files for specific application
    def loadSpecificFiles(self, module):
        special = re.compile(r'([][()^$.+*?{\\])')
        pattern = "^" + special.sub(r'\\\1', module)
        pattern += "(_[^@]*)?(@" + special.sub(r'\\\1', self.machine)
        pattern += ")?\.vcl$"
        p = re.compile(pattern)

        targets = []
        for i in range(len(self.commandFolders)):
            commandFolder = self.commandFolders[i]
            targets += [[os.path.join(commandFolder,f), i] for f in os.listdir(commandFolder) if p.search(f)]
        for target, i in targets:
            suffix = "-suffix _vcl" + str(i) + " "
            self.loadFile(target, suffix)
        if len(targets) == 0:
            print >> sys.stderr
            if module == "":
                print >> sys.stderr, "Found no Vocola global command files (for machine '" + self.machine + "')"
            else:
                print >> sys.stderr, "Found no Vocola command files for application '" + module + "' (for machine '" + self.machine + "')"

    # Load a specific command file, returning false if not present
    def loadFile(self, file, options):
        try:
            os.stat(file)
            self.runVocolaTranslator(file, options + ' -f')
            return 1
        except OSError:
            return 0   # file not found

    # Run Vocola translator, converting command files from "inputFileOrFolder"
    # and writing output to NatLink/MacroSystem
    def runVocolaTranslator(self, inputFileOrFolder, options):
        self.mayHaveCompiled = 1

        if usePerl: call = 'perl "' + self.VocolaFolder + r'\Exec\vcl2py.pl" '
        else:       call = '"'      + self.VocolaFolder + r'\Exec\vcl2py.exe" '
        call += options
        call += ' "' + inputFileOrFolder + '" "' + NatLinkFolder + '"'
        simpscrp.Exec(call, 1)

        for commandFolder in self.commandFolders:
            logName = commandFolder + r'\vcl2py_log.txt'
            if os.path.isfile(logName):
                try:
                    log = open(logName, 'r')
                    self.compilerError = 1
                    print  >> sys.stderr, log.read()
                    log.close()
                    os.remove(logName)
                except IOError:  # no log file means no Vocola errors
                    pass

### Editing Vocola Command Files

    # "Edit Commands" -- open command file for current application
    def gotResults_edit(self, words, fullResults):
        app = self.getCurrentApplicationName()
        file = app + '.vcl'
        comment = 'Voice commands for ' + app
        onlyShow = (words[0] in ['Show', 'Sjoo', 'Toon'])
        self.openCommandFile(file, comment, onlyShow=onlyShow)

    # "Edit Machine Commands" -- open command file for current app & machine
    def gotResults_editMachine(self, words, fullResults):
        app = self.getCurrentApplicationName()
        file = app + '@' + self.machine + '.vcl'
        comment = 'Voice commands for ' + app + ' on ' + self.machine
        onlyShow = (words[0] in ['Show', 'Sjoo', 'Toon'])
        self.openCommandFile(file, comment, onlyShow=onlyShow)

    # "Edit Global Commands" -- open global command file
    def gotResults_editGlobal(self, words, fullResults):
        file = '_vocola.vcl'
        comment = 'Global voice commands'
        onlyShow = (words[0] in ['Show', 'Sjoo', 'Toon'])
        self.openCommandFile(file, comment, onlyShow=onlyShow)

    # "Edit Global Machine Commands" -- open global command file for machine
    def gotResults_editGlobalMachine(self, words, fullResults):
        file = '_vocola@' + self.machine + '.vcl'
        comment = 'Global voice commands on ' + self.machine
        onlyShow = (words[0] in ['Show', 'Sjoo', 'Toon'])
        self.openCommandFile(file, comment, onlyShow=onlyShow)

    # Open a Vocola command file (using the application associated with ".vcl")
    
    def FindExistingCommandFile(self, file):
        for commandFolder in self.commandFolders:
            f = commandFolder + '\\' + file
            if os.path.isfile(f): return f

        return ""
    
    def openCommandFile(self, file, comment, onlyShow=None):
        """open a command file with Notepad.
        
        Create new if it did not exist before, possibly with include line
        to Unimacro.vch,
        
        If the file was called before in this NatSpeak session, try to
        switch to the previously opened window (using AppBringUp)
        
        If onlyShow is set, do NOT give focus, bring to foreground only.
        """
        path = self.FindExistingCommandFile(file)
        wantedPath = os.path.join(self.commandFolders[0], file)

        if not path:
            path = self.commandFolders[0] + '\\' + file
            new = open(path, 'w')
            # insert include line to Unimacro.vch:
            if want_unimacro:
                if language == 'enx' or not status.getVocolaTakesLanguages():
                    includeLine = 'include Unimacro.vch;\n'
                else:
                    includeLine = 'include ..\\Unimacro.vch;\n'
                new.write(includeLine)                    
            new.write('# ' + comment + '\n\n')
            new.close()

        elif path == wantedPath:
            pass
        else:
            # copy from other location
            if wantedPath.startswith(path) and len(wantedPath) - len(path) == 3:
                print 'copy enx version to language version %s'% language
                self.copyVclFileLanguageVersion(path, wantedPath)
            else:
                print 'copy from other location'
                self.copyVclFile(path, wantedPath)
            path = wantedPath   

        if not os.path.isfile(path):
            raise(IOError, "not an existing file: %s"% path)
        if debugSleepTime:
            print 'checking executable to open %s with (in %s seconds)'% (path, debugSleepTime)
            time.sleep(debugSleepTime)
        try:
            dummy, prog = win32api.FindExecutable(path)
        except: 
            if debugSleepTime:
                print 'cannot find executable to open %s with, try Notepad'% path
            prog = os.path.join(os.getenv('WINDIR'), 'notepad.exe')
        else:
            if not os.path.isfile(prog):
                prog = os.path.join(os.getenv('WINDIR'), 'notepad.exe')
        if not os.path.isfile(prog):
            raise IOError("Cannot find program to open %s (tried %s)"%
                          (path, prog))
        #path = win32api.GetShortPathName(path)
        if debugSleepTime:
            print 'open (ShellExecute) (after %s seconds) %s with program %s'% (debugSleepTime, path, prog)
            time.sleep(debugSleepTime)
        trunk, ext = os.path.splitext(file)
            
        appString = '%s %s'% (prog, path)
        appName = "vocolaedit%s"% trunk
        if onlyShow:
            appStyle = 4
        else:
            appStyle = 1
        print 'file: %s, appName: %s, appString: %s, appStyle: %s'% (
            file, appName, appString, appStyle)
        natlink.execScript('AppBringup "%s", "%s", %s'% (appName, appString, appStyle))
        
        #    
        #    win32api.ShellExecute(0, 'open', prog, path, "", 1)
        #    #os.spawnv(os.P_NOWAIT, prog, (prog, path))
        #except WindowsError, e: 
        #    print 'could not open %s, error message: %s'% (path, e)
        #else:
        #    time.sleep(0.1)
        #    hndle = win32gui.GetForegroundWindow()
        #    self.editedFilesHndles[file] = hndle
        #    print 'set remember hndle of %s to %s'% (file, hndle)

    def copyVclFileLanguageVersion(self, Input, Output):
        """copy to another location, keeping the include files one directory above
        """
        # QH, febr, 5, 2008
        # let include lines to relative paths point to the folder above ..\
        # so you can take the same include file for the alternate language.
        reInclude = re.compile(r'(include\s+)\w')
        Input = os.path.normpath(Input)
        Output = os.path.normpath(Output)
        input = open(Input, 'r').read()
        output = open(Output, 'w')
        output.write("# vocola file for alternate language: %s\n"% language)
        lines = map(string.strip, str(input).split('\n'))
        for line in lines:
            if reInclude.match(line):
                line = 'include ..\\' + line[8:]
            output.write(line + '\n')
        output.close()                

    def copyVclFile(self, Input, Output):
        """copy to another location
        """
        # QH, febr, 5, 2008
        Input = os.path.normpath(Input)
        Output = os.path.normpath(Output)

        input = open(Input, 'r').read()
        output = open(Output, 'w')
        output.write("# vocola file from a sample directory %s\n"% Input)
        lines = map(string.strip, str(input).split('\n'))
        for line in lines:
            output.write(line + '\n')
        output.close()                

            
thisGrammar = ThisGrammar()
thisGrammar.initialize()


# Returns the modification time of a file or 0 if the file does not exist
def vocolaGetModTime(file):
    try: return os.stat(file)[ST_MTIME]
    except OSError: return 0        # file not found

# Returns the newest modified time of any Vocola command folder file or
# 0 if none:
def getLastVocolaFileModTime():
    last = 0
    for folder in thisGrammar.commandFolders:
        last = max([last] +
                   [vocolaGetModTime(os.path.join(folder,f))
                    for f in os.listdir(folder)])
    return last


# When speech is heard this function will be called before any others.
#   - Compile any changed Vocola command files
##   - Remove any vocola output files without corresponding source files
#   - Make sure NatLink sees any new output files
#
# now this callback is called from natlinkmain before other grammars are called
# also, natlinkmain now guarantees we are not called with CallbackDepth>1
#

lastNatLinkModTime    = 0
lastCommandFolderTime = 0
lastVocolaFileTime    = 0

def vocolaBeginCallback(moduleInfo):
    global lastNatLinkModTime, lastCommandFolderTime, lastVocolaFileTime

    if not thisGrammar.vocolaEnabled:
        return 0

    current = getLastVocolaFileModTime()
    if current > lastVocolaFileTime:
        thisGrammar.loadAllFiles('')
    if not thisGrammar.compilerError:
        lastVocolaFileTime =  current
    else:
        thisGrammar.compilerError = 0      

#    source_changed = 0
#    for folder in thisGrammar.commandFolders:
#        if vocolaGetModTime(folder) > lastCommandFolderTime:
#            lastCommandFolderTime = vocolaGetModTime(folder)
#            source_changed = 1
#    if source_changed:
#        thisGrammar.deleteOrphanFiles()

    compiled = thisGrammar.mayHaveCompiled
    thisGrammar.mayHaveCompiled = 0
    current = vocolaGetModTime(NatLinkFolder)
    if current > lastNatLinkModTime:
        lastNatLinkModTime = current
        # make sure NatLink sees any new .py files:
        return 2
    return compiled



def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
