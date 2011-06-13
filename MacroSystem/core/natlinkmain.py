#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc..
#
# natlinkmain.py
#   Base module for the Python-based command and control subsystem
#
# June 2011 (QH):
#   improved the include or exclude mechanism of Vocola (_vocola_main). In
#   _vocola_main the compiled .py and .pyc grammar files from Vocola command files
#   are automatically purged if Vocola not active (first time after a deactivate of Vocola)
#   vocolaEnabled is set at start, but made false if Vocola is not active.
# December 2010 (QH): keep track of grammar files with errors, so they only reload when
#                     changes are made (wrongFiles global dict)
# March 2010 (QH) loading (in findAndLoadFiles) _control.py last, the
#            Unimacro control grammar (for introspection)
#August 17, 2009
#   - added throughWords in SelectGramBase, see natlinkutils.py (Quintijn)
#
# Febr 2008 (QH)
#   - userDirectory inserted at front of sys.path (was appended)
#   - made special arrangements for _vocola_main, so it calls back before
#     anything else is done, see doVocolaFirst, vocolaModule and vocolaIsLoaded.
#     These 3 variables control all. Moreover VocolaUserDirectory must be given,
#     otherwise Vocola will not switch on.
#
# Jan 2008 (QH)
#   - adapted to natlinkstatus, which gives info about NatLink, both by
#     this module and by the NatLink config functions.
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
__version__ = ""   #changed with SVN
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
import os, shutil       # access to file information
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
cmdLineStartup=0
debugTiming=0
#
# This redirects stdout and stderr to a dialog box.
#
# bookkeeping for Vocola:
vocolaEnabled = 1  # first time try, is set to 0 if _vocola_main signals it is not active
doVocolaFirst = '_vocola_main'
vocolaIsLoaded = None  # 1 or None
vocolaModule = None    # pointer to the module...

reVocolaModuleName = re.compile(r'_vcl[0-9]?$')

class NewStdout:
    softspace=1
    def write(self,text):
        displayText(text, 0)
    def flush(self):
        pass

class NewStderr:
    softspace=1
    def write(self,text):
        displayText(text, 1)
    def flush(self):
        pass

if not cmdLineStartup:
    sys.stdout = NewStdout()
    sys.stderr = NewStderr()

# status:
status = natlinkstatus.NatlinkStatus()
status.checkSysPath()
debugLoad = status.getDebugLoad()
debugCallback = status.getDebugCallback()
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
# Vocola grammar files are located here.
baseDirectory = ''
DNSuserDirectory = ''   # folder of the current user speech profiles...
#
# This is the current user directory. (of natspeak, the user files are located there...
#

userName = ''
# this is now the NatLink user directory, which can be configured
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

wrongFiles = {} # timestamp of files with an error in it...
#
# Module which was active last time we looked for module specific files
#

lastModule = ''

# for information printing only
changeCallbackUserFirst = 1

def unloadModule(modName):
    """calls the 'unload' function of the module.
    
    used in _control for specific unloading and reloading of modules
    """
    global lastModule, loadedFiles
    safelyCall(modName, 'unload')
    if modName in loadedFiles:
        del loadedFiles[modName]
    if modName == lastModule:
        lastModule = ''
        
#
# This function will load another Python module, usually one which the user
# supplies.  This function will trap all execptions and report them so an
# error in this function will not prevent another module from being
# imported. This routine will also conditionaly reload a module if it has
# changed.
#
def loadModule(modName):
    """load a single module
    
    mostly this goes with findAndLoadFiles, this is for a single module,
    called from _control (Unimacro)
    """
    global loadedFiles
    result = loadFile(modName)
    if result:
        loadedFiles[modName] = result
    else:
        print 'loading module %s failed, put in "wrongFiles"'% modName


def loadFile(modName, origName=None):
    global wrongFiles  # keep track of non edited files with errors
    try: fndFile,fndName,fndDesc = imp.find_module(modName, searchImportDirs)
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

    if fndName in wrongFiles:
        sourceDate = getFileDate(fndName)
        if not sourceDate:
            print '-- wrong grammar file removed: %s'% fndName
            del wrongFiles[fndName]
            return
        elif sourceDate <= wrongFiles[fndName]:
            print '-- skip unchanged wrong grammar file: %s'% fndName
            return

    try:
        imp.load_module(modName,fndFile,fndName,fndDesc)
                                    
        fndFile.close()
        if fndName in wrongFiles:
            del wrongFiles[fndName]  # release that 
        return fndName
    except:
        fndFile.close()
        sys.stderr.write('Error loading '+modName+' from '+fndName+'\n' )
        traceback.print_exc()
        sourceDate = getFileDate(fndName)
        wrongFiles[fndName] = sourceDate
        return

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
    global loadedFiles, vocolaIsLoaded, vocolaModule, vocolaEnabled

    moduleHasDot = None
    if curModule:
        # special case, encountered with Vocola modules with . in name:
        moduleHasDot = curModule.find(".") >= 0
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

    filesToLoad = {}
    if userDirectory != '':
        userDirFiles = [x for x in os.listdir(userDirectory) if x.endswith('.py')]
        for x in userDirFiles:
            res = pat.match(x)
            if res: addToFilesToLoad( filesToLoad, res.group(1), userDirectory, moduleHasDot )
    # baseDirectory:           
    baseDirFiles = [x for x in os.listdir(baseDirectory) if x.endswith('.py')]

    # if present, load _vocola_main first, it can generate grammar files
    # before proceeding:
    vocolaEnabled = (vocolaEnabled and doVocolaFirst and doVocolaFirst+'.py' in baseDirFiles)
    if debugLoad:
        print 'vocolaEnabled: %s'% vocolaEnabled
    if vocolaEnabled and not vocolaIsLoaded:
        x = doVocolaFirst
        origName = loadedFiles.get(x, None)
        loadedFiles[x] = loadFile(x, origName)
        vocolaIsLoaded = 1
        vocolaModule = sys.modules[doVocolaFirst]
        if not vocolaModule.VocolaEnabled:
            # vocola module signals vocola is not enabled:
            vocolaEnabled = 0
            del loadedFiles[x]
            if debugLoad: print 'Vocola is disabled...'
        # repeat the base directory, as Vocola just had the chance to rebuild Python grammar files:
        baseDirFiles = [x for x in os.listdir(baseDirectory) if x.endswith('.py')]
    for x in baseDirFiles:
        res = pat.match(x)
        if res: addToFilesToLoad( filesToLoad, res.group(1), baseDirectory, moduleHasDot )

    # Try to (re)load any files we find
    if debugLoad: print 'filesToLoad: %s'% filesToLoad.keys()
    # to Unimacro grammar control last:
    controlModule = None
    for x in filesToLoad.keys():
        if x == doVocolaFirst:
            continue
        if x == '_control':
            if debugLoad: print 'skipping _control'
            controlModule = x
            continue
        origName = loadedFiles.get(x, None)
        loadedFiles[x] = loadFile(x, origName)

    # if unimacro module _control exists, load it last:
    if controlModule:
        if debugLoad:
            print 'loading _control last'
        origName = loadedFiles.get(controlModule, None)
        loadedFiles[controlModule] = loadFile(controlModule, origName)
        
    # Unload any files which have been deleted
    for name, path in loadedFiles.items():
        if path and not getFileDate(path):
            safelyCall(name,'unload')
            del loadedFiles[name]

def addToFilesToLoad( filesToLoad, modName, modDirectory, moduleHasDot=None):
    """add to the dict of filesToLoad,

    if moduleHasDot (module name for example aaa.bbb), replace aaa.bbb to aaa_dot_bbb and
    check the Python files accordingly. Fix for Vocola command files that have a . (dot)
    in the module name. Also user grammar files can be written according to this trick.

    Note: if manual changes have to be done, the aaa.bbb_ccc.py file MUST exist, never change
    alone in aaa_dot_bbb_ccc.py
    (Quintijn 29/11/2008)
    
    """
    if not moduleHasDot:
        filesToLoad[modName] = None
        return
    # special case, check for special name and take that one instead of modName
    newModName = modName.replace(".", "_dot_")
    inFile = os.path.join(modDirectory, modName + ".py")
    outFile = os.path.join(modDirectory, newModName + ".py")
    dotDate = getFileDate(inFile)
    _dot_Date = getFileDate(outFile)
    if dotDate >= _dot_Date:
        # aaa.bbb.py -->> aaa_dot_bbb.py, only if it outdated.
##        print 'copy: %s to %s'% (inFile, outFile)
        shutil.copyfile(inFile, outFile)
    # set newModName to this one:
    filesToLoad[newModName] = None
##    print 'set newModName: %s'% newModName

    
#
# This function is called when we change users.  It calls the unload member
# function in each loaded module.
#

def unloadEverything():
    global loadedFiles, vocolaIsLoaded, vocolaModule
    for x in loadedFiles:
        if loadedFiles[x]:
            if debugLoad: print 'unload grammar %s'% x
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
    try:
        curModule = os.path.splitext(os.path.split(moduleInfo[0])[1])[0]
    except:
        print "loadModSpecific: invalid modulename, skipping (moduleInfo): %s"% `moduleInfo`
        curModule = ''
        
    if curModule and not (onlyIfChanged and curModule==lastModule):
        findAndLoadFiles(curModule)
        lastModule = curModule

def setSearchImportDirs():
    """set the global list of import dirs, to be used for import
    
    either [userDirectory, baseDirectory] or [baseDirectory] (if no userDirectory)
    """
    global searchImportDirs
    searchImportDirs = []
    if userDirectory != '':
        searchImportDirs.append(userDirectory)
    searchImportDirs.append(baseDirectory)


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

prevModInfo = None
def beginCallback(moduleInfo, checkAll=None):
    global loadedFiles, prevModInfo
    cbd = getCallbackDepth()
    if debugCallback:
        print 'beginCallback, cbd: %s, checkAll: %s, checkForGrammarChanges: %s'% \
              (cbd, checkAll, checkForGrammarChanges)
    # maybe should be 1...
    if getCallbackDepth() > 1:
        return
    t0 = time.time()
    
    if vocolaEnabled and vocolaIsLoaded:
        result = vocolaModule.vocolaBeginCallback(moduleInfo)
        if result == 2:
            if debugCallback:
                print 'Vocola made new module, load all Python files'
            findAndLoadFiles()
            loadModSpecific(moduleInfo)
        elif result == 1:
            if debugCallback:
                print 'Vocola changed a Python module, check'
            checkAll = 1
        else:
            if debugCallback:
                print 'no changes Vocola user files'
                
    if checkAll or checkForGrammarChanges:
        if debugCallback:
            print 'check for changed files (all files)...'
        for x in loadedFiles.keys():
            loadedFiles[x] = loadFile(x, loadedFiles[x])
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
    global userName, DNSuserDirectory, language, BaseModel, BaseTopic, DNSmode, changeCallbackUserFirst
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
            print "---------changeCallback, User changed to", userName
        elif changeCallbackUserFirst:
            # first time, no print message, but next time do...
            changeCallbackUserFirst = 0
        else:
            print "\n------ user changed to: %s\n"% userName

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

except:
    sys.stderr.write( 'Error initializing natlinkmain\n' )
    traceback.print_exc()

if debugLoad:
    print "userDirectory: %s\nbaseDirectory: %s"% (userDirectory, baseDirectory)
    print "natlinkmain imported-----------------------------------"
elif natlinkmainPrintsAtEnd:
    print 'natlinkmain started (imported)\n'
