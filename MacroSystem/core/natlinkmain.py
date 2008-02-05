#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc..
#
# natlinkmain.py
#   Base module for the Python-based command and control subsystem
#
# Febr 2008 (QH)
#   - made special arrangements for _vocola_main, so it calls back before
#     anything else is done, see doVocolaFirst, vocolaModule and vocolaIsLoaded.
#     These 3 variables control all. Moreover VocolaUserDirectory must be given,
#     otherwise vocola will not switch on.
#
# Jan 2008 (QH)
#   - adapted to natlinkstatus, which gives info about natlink, both by
#     this module and by the natlink config functions.
#     Note: status is now a class instance of natlinkstatus.NatlinkStatus
#
# QH, May 22, 2007:
#    extended range of possible filenames, (nearly) arbitrary characters may appear after
#    "_" in global grammar names or after
#    "mod_" in specific grammar names  (request of Mark Lillibridge)
# Quintijn Hoogenboom (QH), May 1, 2007
# changes for compatibility with unimacro:
# extra information reported (language version, natspeak version, windows version etc)
# checking not at each utterance (option, see below)
# always printing a line when natlinkmain started (option)
# see in documentation below, and unittestNatlink.py in folder PyTest...
#
#
# April 1, 2000
#   - fixed a bug where we did not unload files when we noticed that they
#     were deleted
#   - fixed a bug where we would load .pyc files without a matching .py
#
# TODO - known bug: if you change the name of a user while it is active we
# throw an exception!

############################################################################
__version__ = "$Revision$, $Date$, $Author$"
#
# natlinkmain
#
# This Python module comprises the core of the Python based command and 
# control subsystem for Dragon NaturallySpeaking.  Python programs should 
# should not import this module.  Instead, this module is automatically
# imported when the Python compatibility module starts.
#
# The basic logic is as follows:
#
# (1) redirect stdout and stderr so we see messages in the dialog box which
#   natlink.dll creates
#
# (2) compute the directory we are running from, by looking at this modules
#   path as known to Python
#
# (3) load all filenames in our directory which begin with an underscore
#
# (4) install callbacks for user/mic changes and beginning of utterance
#
# A few print statements are commented out.  Remove the pound sign during
# debugging to print information about when a module is loaded.
#

import sys, time
import string
import os               # access to file information
import os.path          # to parse filenames
import imp              # module reloading
import re               # regular expression parsing    
import traceback        # for printing exceptions
##import RegistryDict   # all in natlinkstatus now
##import win32api # win32api for getting ini file values
from stat import *      # file statistics
from natlink import *   
import glob             # new way to collect the grammar files
import pprint
import natlinkstatus    # for extracting status info (QH)
# status now a class:
status = natlinkstatus.NatlinkStatus()

debugLoad= status.getDebugLoad()
cmdLineStartup=0
debugTiming=0
debugCallback = status.getDebugCallback()
#
# This redirects stdout and stderr to a dialog box.
#
doVocolaFirst = '_vocola_main'
vocolaIsLoaded = None  # 1 or None
vocolaModule = None    # pointer to the module...

reVocolaModuleName = re.compile(r'_vcl[0-9]?$')


class NewStdout:
    softspace=1
    def write(self,text):
        displayText(text, 0)

class NewStderr:
    softspace=1
    def write(self,text):
        displayText(text, 1)

if not cmdLineStartup:
    sys.stdout = NewStdout()
    sys.stderr = NewStderr()

if debugLoad:
    print 'do extra output at (re)loading time: %s'% debugLoad
if debugCallback:
    print 'do extra output at callback time: %s'% debugCallback

# QH added:checkForGrammarChanges is set when calling "edit grammar ..." in the control grammar,
# otherwise no grammar change checking is performed, only at microphone toggle
checkForGrammarChanges = 0

def setCheckForGrammarChanges(value):
    """switching on or off (1 or 0), for continuous checking or only a mic toggle"""
    global checkForGrammarChanges
    checkForGrammarChanges = value

# start silent, set this to 0:
natlinkmainPrintsAtEnd = 1
## << QH added

    

#
# This is the directory where the Python modules all reside.
#

# the base directory is one level above the core directory.
# vocola grammar files are located here.
baseDirectory = ''
DNSuserDirectory = ''   # folder of the current user speech profiles...
#
# This is the current user directory. (of natspeak, the user files are located there...
#

userName = ''
# this is now the natlink user directory, which can be configured
# this folder may be empty, or points to the folder where user-defined grammars
# are, for example the unimacro grammars.
userDirectory = ''  

# if userDirectory is NOT set, searchImportDirs only contains the base directory.
# set in findAndLoadFiles:
searchImportDirs = []

DNSdirectory = ''
DNSversion = -1
WindowsVersion = ''
DNSmode = 0  # can be changed in grammarX by the setMode command to
             # 1 dictate, 2 command, 3 numbers, 4 spell
             # commands currently from _general7,
             # is reset temporarily in DisplayMessage function.
             # it is only safe when changing modes is performed through
             # this setMode function

# at start and at changeCallback (new user) get the current language:
language = ''

# service to trainuser.py:
BaseModel = ''
BaseTopic = ''
#<<QH

#
# We maintain a dictionary of all the modules which we have loaded.  The key
# is the Python module name.  The value is the complete path to the loaded
# module.
#

loadedFiles = {}

#
# Module which was active last time we looked for module specific files
#

lastModule = ''


VocolaUserDirectory = ''
#
# This function will load another Python module, usually one which the user
# supplies.  This function will trap all execptions and report them so an
# error in this function will not prevent another module from being
# imported. This routine will also conditionaly reload a module if it has
# changed.
#

def loadFile(modName,searchPath,origName=None):
    
    try: fndFile,fndName,fndDesc = imp.find_module(modName, searchPath)
    except ImportError: return None     # module not found
    if origName:
        if fndName[-3:] != ".py":
            # not a Python source file
            fndFile.close()
            safelyCall(modName,'unload')
            return None
        if origName == fndName:
            sourceDate = getFileDate(fndName)
            objectDate = getFileDate(fndName+'c')
            if objectDate >= sourceDate:    
##                if debugLoad:
##                    print 'not changed: %s (%s, %s)'% (fndName, sourceDate, objectDate)
                fndFile.close()
                return origName
        if debugLoad: print "Reloading", modName

        # if we know we are reloading a module, we call the unload function
        # in that module first to release all objects
        safelyCall(modName,'unload')
    else:
        if fndName[-3:] != ".py":   
            # not a Python source file
            fndFile.close()
            return None
        if debugLoad: print "Loading", modName

    try:
        imp.load_module(modName,fndFile,fndName,fndDesc)
                                    
        fndFile.close()
        return fndName
    except:
        fndFile.close()
        sys.stderr.write('Error loading '+modName+' from '+fndName+'\n' )
        traceback.print_exc()
        return None

# Returns the date on a file or 0 if the file does not exist        

def getFileDate(modName):
    try: return os.stat(modName)[ST_MTIME]
    except OSError: return 0        # file not found

# Calls the unload member function of a given module.  Does not make the call
# if the function does not exist and cleans up in the case of errors.

def safelyCall(modName,funcName):
    try: 
        func = getattr(sys.modules[modName], funcName)
    except AttributeError:
        # unload function does not exist
        return None
    try:
        apply(func, [])
    except:
        sys.stderr.write( 'Error calling '+modName+'.'+funcName+'\n' )
        traceback.print_exc()
        return None

#
# This routine loads two types of files.  If curModule is empty then we will
# load the global files which are all the files which begin with an
# underscore in the current directory.  If curModule is not empty then we
# load all the module specific files file all begin with the module name
# followed by an optional underscore.
#
# Sample global files:
#   _macro.py
#   _other_stuff.py
#
# Sample module specific files (for curModule=wordpad)
#   wordpad.py
#   wordpad_extra.py
#

def findAndLoadFiles(curModule=None):
    global loadedFiles, searchImportDirs, vocolaIsLoaded, vocolaModule


    if curModule:
        curModuleEscaped = re.escape(curModule)
        pat = re.compile(r"""
            ^(%s        # filename must match module name
##            (_\w+)?)    # optional underscore followed by text (old)
            (_.*)?)    # optional underscore followed by anything (or nothing) (QH)
            [.]py$      # extension .py
          """%curModuleEscaped, re.VERBOSE|re.IGNORECASE)
    else:
        pat = re.compile(r"""
            ^(_         # filename must start with an underscore
##            \w+)        # remainder of filename (old)
             .+)        # remainder of filename (anything) (QH)
            [.]py$      # extension .py
          """, re.VERBOSE|re.IGNORECASE)

    searchImportDirs = []
    filesToLoad = {}
    if userDirectory != '':
        searchImportDirs.append(userDirectory)
        userDirFiles = [x for x in os.listdir(userDirectory) if x.endswith('.py')]
        for x in userDirFiles:
            res = pat.match(x)
            if res: filesToLoad[ res.group(1) ] = None
    # baseDirectory:           
    searchImportDirs.append(baseDirectory)
    baseDirFiles = [x for x in os.listdir(baseDirectory) if x.endswith('.py')]

    # if present, load _vocola_main first, it can generate grammar files
    # before proceeding:
    vocolaEnabled = (doVocolaFirst and VocolaUserDirectory and doVocolaFirst+'.py' in baseDirFiles)
    if debugLoad:
        print 'vocolaEnabled: %s'% vocolaEnabled
    if vocolaEnabled and not vocolaIsLoaded:
        x = doVocolaFirst
        origName = loadedFiles.get(x, None)
        loadedFiles[x] = loadFile(x, searchImportDirs, origName)
        vocolaIsLoaded = 1
        vocolaModule = sys.modules[doVocolaFirst]
        # repeat the base directory, as vocola just had the chance to rebuild python grammar files:
        baseDirFiles = [x for x in os.listdir(baseDirectory) if x.endswith('.py')]

    for x in baseDirFiles:
        res = pat.match(x)
        if res: filesToLoad[ res.group(1) ] = None

    # Try to (re)load any files we find
    if debugLoad: print 'filesToLoad: %s'% filesToLoad.keys()
    for x in filesToLoad:
        if x == doVocolaFirst: continue
        if not vocolaEnabled and reVocolaModuleName.search(x):
            if debugLoad:
                print 'skipping %s, vocola not enabled'% x
            continue
        origName = loadedFiles.get(x, None)
        loadedFiles[x] = loadFile(x, searchImportDirs, origName)

    # Unload any files which have been deleted
    for name, path in loadedFiles.items():
        if path and not getFileDate(path):
            safelyCall(name,'unload')
            del loadedFiles[name]

#
# This function is called when we change users.  It calls the unload member
# function in each loaded module.
#

def unloadEverything():
    global loadedFiles, vocolaIsLoaded
    for x in loadedFiles:
        if loadedFiles[x]:
            safelyCall(x,'unload')
            if x == doVocolaFirst:
                vocolaIsLoaded = None
                vocolaModule = None
    loadedFiles = {}

#
# Compute the name of the current module and load all files which are
# specific to that module.
#

def loadModSpecific(moduleInfo,onlyIfChanged=0):
    """load program specific grammars

    onlyIfChanged: default 0: check always. 1: check only if new module.
    So in beginCallback you can call this one with onlyIfChanged=1 in order to
    minimise the reloadings.
    """    
    global lastModule
    # this extracts the module base name like "wordpad"
    curModule = os.path.splitext(os.path.split(moduleInfo[0])[1])[0]
    if curModule and not (onlyIfChanged and curModule==lastModule):
        findAndLoadFiles(curModule)
        lastModule = curModule

#
# When a new utterance begins we check all the loaded modules for changes.
# After that, we check to see whether we have to load a new module based on
# the currently active Windows executable.
#
# If reloading a module fails, we do not remove it from the list of modules
# to check in this session so the user can correct any problems and get the
# module to reload again in the future.
#
# Note that we do not reload existing modules when we are in a nested
# callback since that callback may be coming from code in the module we are
# trying to reload (consider recognitionMimic).
#
def vocolaActive():
    """active if grammar is loaded and VocolaUserDirectory exists
    """
    if doVocolaFirst in loadedFiles and VocolaUserDirectory:
        return 1

prevModInfo = None
def beginCallback(moduleInfo, checkAll=None):
    global loadedFiles, prevModInfo
    cbd = getCallbackDepth()
    if debugCallback:
        print 'beginCallback, cbd: %s, checkAll: %s, checkForGrammarChanges: %s'% \
              (cbd, checkAll, checkForGrammarChanges)
    # maybe should be 1...
    if getCallbackDepth() > 2:
        return
    t0 = time.time()
    
    if vocolaIsLoaded:
        result = vocolaModule.vocolaBeginCallback(moduleInfo)
        if result == 2:
            if debugCallback:
                print 'vocola made new module, load all python files'
            findAndLoadFiles()
            loadModSpecific(moduleInfo)
        elif result == 1:
            if debugCallback:
                print 'vocola changed a python module, check'
            checkAll = 1
        else:
            if debugCallback:
                print 'no changes vocola user files'
                
    if checkAll or checkForGrammarChanges:
        if debugCallback:
            print 'check for changed files (all files)...'
        for x in loadedFiles.keys():
            loadedFiles[x] = loadFile(x, searchImportDirs, loadedFiles[x])
        loadModSpecific(moduleInfo)  # in checkAll or checkForGrammarChanges mode each time
    else:
        if debugCallback:
            print 'check for changed files (only specific)'
        loadModSpecific(moduleInfo, 1)  # only if changed module
    if debugTiming:
        print 'checked all grammar files: %.6f'% (time.time()-t0,)
        
#
# This callback is called when the user changes or when the microphone
# changes state.  We check for changes when the microphone is turned on.
#
# Note: getCurrentModule can raise the BadWindow except and if that happens
# we ignore the callback.
#

def changeCallback(type,args):
    global userName, DNSuserDirectory, language, BaseModel, BaseTopic, DNSmode
    if debugCallback:
        print 'changeCallback, type: %s, args: %s'% (type, args)
    if type == 'mic' and args == 'on':
        if debugCallback:
            print 'findAndLoadFiles...'
        moduleInfo = getCurrentModule()
        findAndLoadFiles()
        beginCallback(moduleInfo, checkAll=1)
        loadModSpecific(moduleInfo)
    if type == 'user' and userName != args[0]:
        userName, DNSuserDirectory = args
        moduleInfo = getCurrentModule()
        if debugCallback:
            print "changeCallback, User changed to", userName
        unloadEverything()
## this is not longer needed here, as we fixed the userDirectory
##        changeUserDirectory()
        status.setUserInfo(args)
        language = status.getLanguage()
        if debugCallback:
            print 'usercallback, language: %s'% language
        BaseModel, BaseTopic = status.getBaseModelBaseTopic()
        # changed next two lines QH:
        findAndLoadFiles()        
        beginCallback(moduleInfo, checkAll=1)
        loadModSpecific(moduleInfo)
    #ADDED BY BJ, possibility to finish exclusive mode by a grammar itself
    # the grammar should include a function like:
    #def changeCallback():
    #    if thisGrammar:
    #        thisGrammar.cancelMode()
    # and the grammar should have a cancelMode function that finishes exclusive mode.
    # see _oops, _repeat, _control for examples
    if not ((type == 'mic') and (args=='on')):
        changeCallbackLoadedModules(type,args)
##    else:
##        # possibility to do things when changeCallBack with mic on: (experiment)
##        changeCallbackLoadedModulesMicOn(type, args)


def changeCallbackLoadedModules(type,args):
    """BJ added, in order to intercept in a grammar (oops, repeat, control) in eg mic changed

    in those cases the cancelMode can be called, so exclusiveMode is finished
    """    
    global loadedFiles
    sysmodules = sys.modules
    for x in loadedFiles.keys():
        if loadedFiles[x]:
            try: func = getattr(sysmodules[x], 'changeCallback')
            except AttributeError: pass
            else:
##                print 'call changeCallback for: %s'% x
                apply(func, [type,args])

def changeCallbackLoadedModulesMicOn(type,args):
    """QH, special behaviour implemented in eg control, if the mic goes on!

    """    
    global loadedFiles
    sysmodules = sys.modules
    for x in loadedFiles.keys():
        if loadedFiles[x]:
            try: func = getattr(sysmodules[x], 'changeCallbackMicOn')
            except AttributeError: pass
            else:
##                print 'call changeCallback for: %s'% x
                apply(func, [type,args])


############################################################################
#
# Here is the initialization code.
#

try:
    # compute the directory where this module came from

    #print "\n".join(["%s=%s" % (k,v) for k, v in sys.modules ])
    #print "\n".join(sys.modules.keys())
    if cmdLineStartup:
        modname='natlink'
    else:
        modname='natlinkmain'
        
    baseDirectory = os.path.split(
       sys.modules[modname].__dict__['__file__'])[0]
    
    

    if debugLoad: print "NatLink dll dir " + baseDirectory
    baseDirectory = os.path.normpath(os.path.abspath(os.path.join(baseDirectory,"..")))
    if debugLoad: print "NatLink base dir" + baseDirectory
    
    # get the current user information from the natlink module
    userDirectory = status.getUserDirectory()
    # for unimacro, in order to reach unimacro files to be imported:
    if not userDirectory in sys.path:
        print 'add userDirectory: %s to sys.path!'% userDirectory
        sys.path.append(userDirectory)
    # get invariant variables:
    DNSversion = status.getDNSVersion()
    WindowsVersion = status.getWindowsVersion()
    VocolaUserDirectory = status.getVocolaUserDirectory()
    
    # init things identical to when user changes:
    changeCallback('user', getCurrentUser())

##    BaseModel, BaseTopic = status.getBaseModelBaseTopic()
    print 'Starting natlinkmain with language: %s (DNSversion: %s, WindowsVersion: %s)'% \
          (language, DNSversion, WindowsVersion)
    if debugLoad:
        print 'natlinkmain CVS version: %s'% __version__.replace("$", "").strip()
        print 'complete path: %s'% __file__
    else:
        v = __version__.split(',')[0]
        v = v.strip("$Revision: ")
        print 'natlinkmain CVS version: %s'% v

    # load all global files in user directory and current directory
    findAndLoadFiles()

    # initialize our callbacks
    setBeginCallback(beginCallback)
    setChangeCallback(changeCallback)

except:
    sys.stderr.write( 'Error initializing natlinkmain\n' )
    traceback.print_exc()

if debugLoad:
    print "userDirectory: %s\nbaseDirectory: %s"% (userDirectory, baseDirectory)
    print "natlinkmain imported-----------------------------------"
elif natlinkmainPrintsAtEnd:
    print 'natlinkmain started (imported)'
