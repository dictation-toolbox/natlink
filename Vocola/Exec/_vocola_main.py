# _vocola_main.py - NatLink support for Vocola
#
# Contains:
#    - "Built-in" voice commands
#    - Autoloading of changed command files
#
# This file is copyright (c) 2002-2005 by Rick Mohr. It may be redistributed
# in any way as long as this copyright notice remains.

import sys
import os               # access to file information
import os.path          # to parse filenames
import time             # print time in messages
from stat import *      # file statistics

import natlink
from natlinkutils import *

# The Vocola translator is a perl program. By default we use the precompiled
# executable vcl2py.exe, which doesn't require installing perl.
# To instead use perl and vcl2py.pl, set the following variable to 1:
usePerl = 0

# C module "simpscrp" defines Exec(), which runs a program in a minimized
# window and waits for completion. Since such modules need to be compiled
# separately for each python version we need this careful import:

NatLinkFolder = os.path.split(
    sys.modules['natlinkmain'].__dict__['__file__'])[0]
pydFolder = NatLinkFolder + '\\..\\Vocola\\Exec\\' + sys.version[0:3]
sys.path.append(pydFolder)
import simpscrp

class ThisGrammar(GrammarBase):

    gramSpec = """
        <NatLinkWindow>     exported = [Show] (NatLink|Vocola) Window;
        <loadAll>           exported = Load All [Voice] Commands;
        <loadCurrent>       exported = Load [Voice] Commands;
        <loadGlobal>        exported = Load Global [Voice] Commands;
        <edit>              exported = Edit [Voice] Commands;
        <editMachine>       exported = Edit Machine [Voice] Commands;
        <editGlobal>        exported = Edit Global [Voice] Commands;
        <editGlobalMachine> exported = Edit Global Machine [Voice] Commands;
    """

    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()
        self.setNames()
        # Don't set callback just yet or it will be clobbered
        self.needToSetCallback = 1

    def gotBegin(self,moduleInfo):
        self.currentModule = moduleInfo
        if self.needToSetCallback:
            # Replace NatLink's "begin" callback function with ours (see below)
            natlink.setBeginCallback(vocolaBeginCallback)
            self.needToSetCallback = 0

    # Set member variables -- important folders and computer name
    def setNames(self):
        self.VocolaFolder = NatLinkFolder + r'\..\Vocola'
        self.commandFolder = self.VocolaFolder + r'\Commands'
        if os.environ.has_key('COMPUTERNAME'):
            self.machine = string.lower(os.environ['COMPUTERNAME'])
        else: self.machine = 'local'

    # Get app name by stripping folder and extension from currentModule name
    def getCurrentApplicationName(self):
        return string.lower(os.path.splitext(os.path.split(self.currentModule[0]) [1]) [0])

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
        self.loadSpecificFiles('_vocola')

    # Load all command files
    def loadAllFiles(self, options):
        self.runVocolaTranslator(self.commandFolder, options)

    # Load command files for specific application
    def loadSpecificFiles(self, module):
        prefix = self.commandFolder + '\\' + module
        success1 = self.loadFile(prefix + '.vcl')
        success2 = self.loadFile(prefix + '@' + self.machine + '.vcl')
        if not success1 and not success2:
            print "Found no Vocola command files for '" + module + "'"

    # Load a specific command file, returning false if not present
    def loadFile(self, file):
        try:
            os.stat(file)
            self.runVocolaTranslator(file, '-f')
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
        logName = self.commandFolder + r'\vcl2py_log.txt'
        try:
            log = open(logName, 'r')
            print log.read()
            log.close()
        except IOError:  # no log file means no Vocola errors
            return

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
    def openCommandFile(self, file, comment):
        file = self.commandFolder + '\\' + file
        try: os.stat(file)
        except OSError:  # file not found -- create one
            new = open(file, 'w')
            new.write('# ' + comment + '\n\n')
            new.close()
        if os.name == 'nt':  opener = 'cmd /c'
        else:                opener = 'start'
        call = opener + ' "' + file + '"'
        # Win98SE return 'nt', but still requires 'start'
        if simpscrp.Exec(call, 0) != 0:
            opener = 'start'
            call = opener + ' "' + file + '"'
            simpscrp.Exec(call, 0)


thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None


# When speech is heard this function will be called before any others.
#   - Load any changed Vocola command files
#   - Invoke the standard NatLink callback

from natlinkmain import beginCallback

def vocolaBeginCallback(moduleInfo):
    thisGrammar.loadAllFiles('')
    beginCallback(moduleInfo)

