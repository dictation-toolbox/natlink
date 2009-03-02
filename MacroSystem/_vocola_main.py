# _vocola_main.py - NatLink support for Vocola
# -*- coding: latin-1 -*-
#
# Contains:
#    - "Built-in" voice commands
#    - Autoloading of changed command files
#
# This file is copyright (c) 2002-2009 by Rick Mohr. It may be redistributed
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
import os               # access to file information
import os.path          # to parse filenames
import time             # print time in messages
from stat import *      # file statistics
import re
import natlink
from natlinkutils import *
import natlinkstatus
import natlinkcorefunctions
import win32api  # for opening command files if own editor is specified
status = natlinkstatus.NatlinkStatus()
##
##try:
##    # The following files are only present if Scott's installer is being used:
##    import RegistryDict
##    import win32con
##    installer = True
##except ImportError:
##    installer = False

# Returns the date on a file or 0 if the file does not exist        
def vocolaGetModDate(file):
    try: return os.stat(file)[ST_MTIME]
    except OSError: return 0        # file not found

    
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
<edit>              exported = (Eddit|Bewerk) [stem|vojs] (Commandoos|Commands);
<editMachine>       exported = (Eddit|Bewerk) Machine [stem|vojs] (Commandoos|Commands);
<editGlobal>        exported = (Eddit|Bewerk) (Global|globale) [stem|vojs] (Commandoos|Commands);
<editGlobalMachine> exported = (Eddit|Bewerk) (Global|globale) Machine [stem|vojs] (Commandoos|Commands);
    """
    else:
        gramSpec = """
<NatLinkWindow>     exported = [Show] (NatLink|Vocola) Window;
<loadAll>           exported = Load All [Voice] Commands;
<loadCurrent>       exported = Load [Voice] Commands;
<loadGlobal>        exported = Load Global [Voice] Commands;
<discardOld>        exported = Discard Old [Voice] Commands;
<edit>              exported = Edit [Voice] Commands;
<editMachine>       exported = Edit Machine [Voice] Commands;
<editGlobal>        exported = Edit Global [Voice] Commands;
<editGlobalMachine> exported = Edit Global Machine [Voice] Commands;
    """

    def initialize(self):

        # remove previous Vocola/Python compilation output as it may be out
        # of date (e.g., new compiler, source file deleted, partially
        # written due to crash, new machine name, etc.):
        self.purgeOutput()
        self.editedCommandFiles = []       
        self.newCommandFile = 0 # to notice when a new command file is opened    

        self.setNames()

        if self.vocolaEnabled:        

            self.loadAllFiles('')

            self.load(self.gramSpec)
            self.activateAll()
            # Don't set callback just yet or it will be clobbered
    ##        self.needToSetCallback = 1
        else:
            print 'vocola not active'
                

    def gotBegin(self,moduleInfo):
        self.currentModule = moduleInfo
##        if self.needToSetCallback:
##            # Replace NatLink's "begin" callback function with ours (see below)
##            natlink.setBeginCallback(vocolaBeginCallback)
##            self.needToSetCallback = 0

                                      
    # Set member variables -- important folders and computer name
    def setNames(self):
        self.VocolaFolder = os.path.normpath(os.path.join(NatLinkFolder, '..', 'Vocola'))
        self.commandFolders = [os.path.join(self.VocolaFolder, '\Commands')]
##        
##        if installer:
##            r = RegistryDict.RegistryDict(win32con.HKEY_CURRENT_USER,
##                                          "Software\NatLink")             
##            if r:                                                         
##                userCommandFolder = r.get("VocolaUserDirectory", None)
##                self.vocolaEnabled = (userCommandFolder and os.path.isdir(userCommandFolder))
##                if self.vocolaEnabled:
##                    self.commandFolders.insert(0, userCommandFolder)
        userCommandFolder = status.getVocolaUserDirectory()
            
        self.vocolaEnabled = (userCommandFolder and os.path.isdir(userCommandFolder))
        if self.vocolaEnabled:
            self.commandFolders.insert(0, userCommandFolder)                
            if status.getVocolaTakesLanguages():
                self.language = status.getLanguage()
                print '_vocola_main started with language: %s'% language
                if self.language != 'enx':
                    userCommandFolder2 = os.path.join(userCommandFolder, self.language)
                    if not os.path.isdir(userCommandFolder2):
                        print 'creating userCommandFolder for language %s'% self.language
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
                if vocolaGetModDate(s)>0: continue

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
        self.openCommandFile(file, comment)

    # "Edit Machine Commands" -- open command file for current app & machine
    def gotResults_editMachine(self, words, fullResults):
        app = self.getCurrentApplicationName()
        file = app + '@' + self.machine + '.vcl'
        comment = 'Voice commands for ' + app + ' on ' + self.machine
        self.openCommandFile(file, comment)

    # "Edit Global Commands" -- open global command file
    def gotResults_editGlobal(self, words, fullResults):
        file = '_vocola.vcl'
        comment = 'Global voice commands'
        self.openCommandFile(file, comment)

    # "Edit Global Machine Commands" -- open global command file for machine
    def gotResults_editGlobalMachine(self, words, fullResults):
        file = '_vocola@' + self.machine + '.vcl'
        comment = 'Global voice commands on ' + self.machine
        self.openCommandFile(file, comment)

    # Open a Vocola command file (using the application associated with ".vcl")
    
    def FindExistingCommandFile(self, file):
        for commandFolder in self.commandFolders:
            f = commandFolder + '\\' + file
            if os.path.isfile(f): return f

        return ""
    
    def openCommandFile(self, file, comment):
        path = self.FindExistingCommandFile(file)
        wantedPath = os.path.join(self.commandFolders[0], file)

        self.newCommandFile = 1

        if not path:
            path = self.commandFolders[0] + '\\' + file
            new = open(path, 'w')
            new.write('# ' + comment + '\n\n')
            new.close()
        elif path == wantedPath:
            self.newCommandFile = 0
        else:
            # copy from other location
            if wantedPath.startswith(path) and len(wantedPath) - len(path) == 3:
                print 'copy enx version to language version %s'% self.language
                self.copyVclFileLanguageVersion(path, wantedPath)
            else:
                print 'copy from other location'
                self.copyVclFile(path, wantedPath)
            path = wantedPath   
        if not path in self.editedCommandFiles:
            self.editedCommandFiles.append(path)

	try:
	    os.startfile(path)
	except WindowsError, e: 
	    print
	    print "Unable to open voice command file: " + str(e)

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
        output.write("# vocola file for alternate language: %s\n"% self.language)
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



            
    def getLastVocolaModTime(self):
        """get the time of the last edited vocola file
        """
        if self.editedCommandFiles:
            times = [vocolaGetModDate(f) for f in self.editedCommandFiles]
            return max(times)
        else:
            return 0


# When speech is heard this function will be called before any others.
#   - Compile any changed Vocola command files
##   - Remove any vocola output files without corresponding source files
#   - Make sure NatLink sees any new output files
#   - Invoke the standard NatLink callback

##from natlinkmain import beginCallback
##from natlinkmain import findAndLoadFiles
##from natlinkmain import loadModSpecific

##lastNatLinkModTime = 0
##lastCommandFolderTime = 0
lastVocolaUserModTime = 0

thisGrammar = ThisGrammar()
thisGrammar.initialize()
lastVocolaUserModTime = thisGrammar.getLastVocolaModTime()

def vocolaBeginCallback(moduleInfo):
    global lastVocolaUserModTime
    #
    # now this callback is called from natlinkmain Before other grammars are called
    # 
##    global lastNatLinkModTime, lastCommandFolderTime
##    thisGrammar.loadAllFiles('')

#    source_changed = 0
#    for folder in thisGrammar.commandFolders:
#        if vocolaGetModDate(folder) > lastCommandFolderTime:
#            lastCommandFolderTime = vocolaGetModDate(folder)
#            source_changed = 1
#    if source_changed:
#        thisGrammar.deleteOrphanFiles()

##    if getCallbackDepth() < 2:
    grammar = thisGrammar
    if not grammar.vocolaEnabled:
        return
    current = grammar.getLastVocolaModTime()
##    print 'current: %s (number of files edited: %s)'% (current, len(grammar.editedCommandFiles))
    if current > lastVocolaUserModTime:
##        print 'newer vocola, newCommandfile: %s'% grammar.newCommandFile
        thisGrammar.loadAllFiles('')
        lastVocolaUserModTime = current
        return 1 + grammar.newCommandFile  # 1 for old files, 2 for new files (findAndLoadFiles needed!)
##    else:
##        print 'no change vocola'
##        # make sure NatLink sees any new .py files:
##        findAndLoadFiles()
##        loadModSpecific(moduleInfo)

##    beginCallback(moduleInfo)



def unload():
    global thisGrammar
##    natlink.setBeginCallback(beginCallback)
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
