#pylint:disable=C0302, C0321
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc..
#
# natlinkmain.py
#   Base module for the Python-based command and control subsystem
#
# August 2020 (QH):
#     - streamline code
#     - improve the loading and updating of module specific grammars
#       (with testing in unittestNatlink, testNatlinkmain)
# May 2020: adaptations for python3
#     -loadedFiles items are now tuple (origPath, origDate)
#     -fix the wrongFiles, in the same way
#
# July 2015 (QH): assume Unimacro at fixed place, extend macro files to BaseDirectory (Vocola),
#    UnimacroDirectory, UserDirectory
# August 2011 (QH): added function reorderKeys, which influences the order
#   of the grammars to load. Hardcoded are _tasks.py (first) and _control (last)
#   _vocola_main could be set here too, but already has a special treatment.
#   This is done because _control needs to know about other Unimacro grammars
#   and _lines can call functions in _tasks, so the tasks grammar must exist before
#   lines is loaded
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
#     These 3 variables control all. Moreover` `VocolaUserDirectory must be given,
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
# known bug: if you change the name of a user while it is active we
# throw an exception!
############################################################################
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
#   (this has been changed to loading the module redirect_output.py, only
#    from natlink.pyd, July 2020, Jan Scheffczyk)
#
# (2) compute the directory we are running from, by looking at this modules
#   path as known to Python
#
# (3) load all filenames in our directory which begin with an underscore
#
# (4) install callbacks for user/mic changes and beginning of utterance
#
# (3 and 4 are now done by calling a changeCallback to the current user, from which
#  the relevant data are set and the relevant grammars are loaded, Augus 2020, QH)
#
# A few print statements are commented out.  Remove the pound sign during
# debugging to print information about when a module is loaded.
"""natlinkmain module, imported from natlink.pyd

working version without natlink.pyd starting start_natlink.py
this is the previous way for starting natlink
"""

import sys
import traceback
import time
import copy
import os
import os.path
import shutil
import imp              # module reloading
import re     
from stat import ST_MTIME      # file statistics
import natlink
import natlinkpydebug as pd  #this will load debug and possibly start it and the time of load

    # print("at start of natlinkmain, after redirect stderr and stdout")

import natlinkstatus    # for extracting status info (QH)
status = natlinkstatus.NatlinkStatus()


debugTiming=0
# bookkeeping for Vocola:
vocolaEnabled = 1  # first time try, is set to 0 if _vocola_main signals it is not active
doVocolaFirst = '_vocola_main'
        
   
vocolaIsLoaded = None  # 1 or None
vocolaModule = None    # pointer to the module...

reVocolaModuleName = re.compile(r'_vcl[0-9]?$')

debugLoad = debugCallback = True
canStartNatlink = True
if status.getDNSInstallDir() == -1:
    print('DNSInstallDir not valid, please run the Natlink config GUI to fix this')
    canStartNatlink = False
if status.getDNSIniDir() == -1:
    print('DNSIniDir not valid, please run the Natlink config GUI to fix this')
    canStartNatlink = False
if canStartNatlink:
    status.checkSysPath()
    debugLoad = status.getDebugLoad()
    debugCallback = status.getDebugCallback()
    if debugLoad:
        print('do extra output at (re)loading time: %s'% debugLoad)
    if debugCallback:
        print('do extra output at callback time: %s'% debugCallback)

ApplicationFrameHostTitles = {}
ApplicationFrameHostTitles["Photos"] = "photos"
ApplicationFrameHostTitles["Foto's"] = "photos"
ApplicationFrameHostTitles["Calculator"] = "calc"
ApplicationFrameHostTitles["Rekenmachine"] = "calc"
        
## always set as global variables:
# baseDirectory = status.getBaseDirectory()    ## MacroSystem folder
natlinkDirectory = status.getNatlinkDirectory()
userDirectory = status.getUserDirectory()
unimacroDirectory = status.getUnimacroDirectory()
unimacroGrammarsDirectory = status.getUnimacroGrammarsDirectory()
vocolaDirectory = status.getVocolaDirectory()
vocolaGrammarsDirectory = status.getVocolaGrammarsDirectory()
DNSVersion = status.getDNSVersion()
windowsVersion = status.getWindowsVersion()
unimacroIsEnabled = status.UnimacroIsEnabled()
vocolaIsEnabled = status.VocolaIsEnabled()

#at this point, see if remote debugging is to be enabled at startup
pd.debug_check_on_startup()

# QH added:checkForGrammarChanges is set when calling "edit grammar ..." in the control grammar,
# otherwise no grammar change checking is performed, only at microphone toggle
checkForGrammarChanges = 0

def getCurrentApplicationName(moduleInfo):
    """get the module name from currentModule info
    
    normally: the application name from currentModule[0] 

    if this is applicationframhost, try from title in above dict, ApplicationFrameHostTitles
    """
    #pylint:disable=W0702
    
    # return os.path.splitext(
    #     os.path.split(self.currentModule[0]) [1]) [0].lower()

    try:
        curModule = os.path.splitext(os.path.split(moduleInfo[0])[1])[0]
    except:
        print(f'getCurrentApplicationName: invalid modulename, skipping moduleInfo: {moduleInfo}')
        return None
    if not curModule:
        return None
    
    progname = curModule.lower()
    if curModule == 'ApplicationFrameHost':
        title = moduleInfo[1]
        for progname in title.split()[0], title.split()[-1]:
            # print(f'ApplicationFrameHost, try title word: {progname}')
            if progname in ApplicationFrameHostTitles:
                progname = ApplicationFrameHostTitles[progname]
                # print(f'ApplicationFrameHost, found progname: {progname}')
                break
        else:
            print(f'ApplicationFrameHost with title: {title} not found in titles, enter in configuration')
            return None
        # print(f'getCurrentApplicationName,  from ApplicationFrameHost, return progName: {progname}')
    # print(f'getCurrentApplicationName,  return progName: {progname}')
        
    return progname

def setCheckForGrammarChanges(value):
    """switching on or off (1 or 0), for continuous checking or only a mic toggle"""
    #pylint:disable=W0603, W0601
    global checkForGrammarChanges
    checkForGrammarChanges = value

# start silent, set this to 0:
natlinkmainPrintsAtStart = 1
natlinkmainPrintsAtEnd = 1

#
# These are the directories where the Python modules all reside (defined above)
# - baseDirectory (MacroSystem, mainly for Vocola)
# - unimacroDirectory
# - userDirectory (Dragonfly and descendants and user defined grammar files)
# print('sys.path except for importdirs')
# pprint(sys.path)

for _name in ['DNSuserDirectory', 'userName',
             'windowsVersion', 'BaseModel', 'BaseTopic',
             'language', 'userLanguage', 'userTopic']:
    if not _name in globals():
        globals()[_name] = ''
    else:
        if debugCallback:
            print('natlinkmain starting, global variable was already set: %s: %s'% (_name, globals()[_name]))
# set in findAndLoadFiles:
try: searchImportDirs
except NameError: searchImportDirs = []
DNSVersion = status.getDNSVersion()
try: DNSmode
except NameError: DNSmode = 0
# above is obsolete, could be inspected again!! (QH, 2020)
# can be changed in grammarX by the setMode command to
# 1 dictate, 2 command, 3 numbers, 4 spell
# commands currently from _general7,
# is reset temporarily in DisplayMessage function.
# it is only safe when changing modes is performed through
# this setMode function

# at start and at changeCallback (new user) get the current language:
language = ''
shiftkey = ''  # {shift} or different in some other languages,
               # will be changed at changecallback when a speech profile opens.
               # for example tp {umschalt} for german speech profiles.
               # Is used by natlinkutils.playString.
               # shiftkey is error prone and obsolete...(2020)
#
# We maintain a dictionary of all the modules which we have loaded.  The key
# is the Python module name.  The value is a tuple,
#  (complete path to the loaded module, timestamp of the python file)
#
try: loadedFiles
except NameError: loadedFiles = {}
try: wrongFiles
except NameError:  wrongFiles = {} # path and timestamp of files with an error in it...
#
# Module which was active last time we looked for module specific files
#
try: lastModule
except NameError: lastModule = ''

# for information printing only
try: changeCallbackUserFirst
except NameError: changeCallbackUserFirst = 1

def unloadModule(modName):
    """calls the 'unload' function of the module.

    used in _control for specific unloading and reloading of modules
    """
    #pylint:disable=W0603
    global lastModule, loadedFiles
    safelyCall(modName, 'unload')
    if modName in loadedFiles:
        del loadedFiles[modName]
    ## this is strange, a module can have more loadedFiles
    if modName == lastModule:
        lastModule = ''

#
# This function will load another Python module, usually one which the user
# supplies.  This function will trap all exceptions and report them so an
# error in this function will not prevent another module from being
# imported. This routine will also conditionaly reload a module if it has
# changed.
#
def loadModule(modName):
    """load a single module

    mostly this goes with findAndLoadFiles, this is for a single module,
    called from _control (Unimacro)
    """
    #pylint:disable=W0603
    global loadedFiles
    result = loadFile(modName)
    if result:
        loadedFiles[modName] = result
    else:
        print('loading module %s failed, put in "wrongFiles"'% modName)

def loadFile(modName, origPath=None, origDate=None):
    """load a module
    """
    #pylint:disable=W0603, R0911, R0912, W0702
    global wrongFiles  # keep track of non edited files with errors
    try: fndFile,fndName,fndDesc = imp.find_module(modName, searchImportDirs)
    except ImportError: return None     # module not found
    
    sourceDate = getFileDate(fndName)
    
    # if debugLoad:
    #     print('loadFile if changed modName %s, fndName: %s, origPath: %s'% (modName, fndName, origPath))

    if origPath:
        if fndName[-3:] != ".py":
            # not a Python source file
            fndFile.close()
            safelyCall(modName,'unload')
            return None
        if origPath == fndName:
            # if debugLoad:
            #     print('not changed: %s (%s, %s)'% (fndName, sourceDate, origDate))
            if origDate >= sourceDate:
                fndFile.close()
                return origPath, origDate
        if debugLoad:
            print(f'Reloading {modName}')

        # if we know we are reloading a module, we call the unload function
        # in that module first to release all objects
        safelyCall(modName,'unload')
    else:
        if fndName[-3:] != ".py":
            # not a Python source file
            fndFile.close()
            return None
        if debugLoad:
            pass
            # print(f'Loading {modName}') 

    if modName in wrongFiles:
        wrongPath, sourceDate = wrongFiles[modName]
        newDate = getFileDate(wrongPath)
        if not newDate:
            print('-- wrong grammar file removed: %s'% fndName)
            del wrongFiles[modName]
            return None
        if newDate <= sourceDate:
            print('-- skip unchanged wrong grammar file: %s'% wrongPath)
            return None
        print('-- retry changed grammar: %s'% modName)

    try:
        imp.load_module(modName,fndFile,fndName,fndDesc)
        fndFile.close()
        if fndName in wrongFiles:
            del wrongFiles[fndName]  # release that
        return fndName, sourceDate
    except:
        fndFile.close()
        sys.stderr.write('Error loading '+modName+' from '+fndName+'\n' )
        traceback.print_exc()
        sourceDate = getFileDate(fndName)
        wrongFiles[modName] = fndName, sourceDate
        return None

# Returns the date on a file or 0 if the file does not exist

def getFileDate(modName):
    """get date of file, zero if non existing
    """
    try: return os.stat(modName)[ST_MTIME]
    except OSError: return 0        # file not found

# Calls the unload member function of a given module.  Does not make the call
# if the function does not exist and cleans up in the case of errors.

def safelyCall(modName,funcName):
    """check if modName and funcName are valid, then call
    """
    #pylint:disable=W0702
    try:
        func = getattr(sys.modules[modName], funcName)
    except AttributeError:
        # unload function does not exist
        return 
    try:
        func(*[])
    except:
        sys.stderr.write( 'Error calling '+modName+'.'+funcName+'\n' )
        traceback.print_exc()
        return 

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
    """find grammar files and load, global or for curModule only
    """
    #pylint:disable=W0603, R0914, R0912, R0915
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
            if res:
                modName = res.group(1)
                addToFilesToLoad( filesToLoad, modName, userDirectory, moduleHasDot )

    unimacroDirFiles = []
    # unimacroGrammarDirFiles = []

    ## unimacro, the main file, _control:
    if unimacroIsEnabled:
        if unimacroDirectory:
            unimacroDirFiles = [x for x in os.listdir(unimacroDirectory) if x.endswith('.py')]
            for x in unimacroDirFiles:
                res = pat.match(x)
                if res:
                    modName = res.group(1)
                    addToFilesToLoad( filesToLoad, modName, unimacroDirectory, moduleHasDot )
    
        ## the unimacro grammars:
        if unimacroGrammarsDirectory:
            unimacroGrammarFiles = [x for x in os.listdir(unimacroGrammarsDirectory) if x.endswith('.py')]
            for x in unimacroGrammarFiles:
                res = pat.match(x)
                if res:
                    modName = res.group(1)
                    addToFilesToLoad( filesToLoad, modName, unimacroGrammarsDirectory, moduleHasDot )

    # # baseDirectory:
    # if baseDirectory:
    #     baseDirFiles = [x for x in os.listdir(baseDirectory) if x.endswith('.py')]
    # else:
    #     baseDirFiles = []
    # 
    ## _vocola_main:
    if debugLoad:
        print(f'_natlinkmain, vocolaDirectory: {vocolaDirectory}')
    VocolaDirFiles = []
    vocolaGrammarFiles = []

    if vocolaIsEnabled:
        if vocolaDirectory:
            VocolaDirFiles = [x for x in os.listdir(vocolaDirectory) if x.endswith('.py')]
            for x in VocolaDirFiles:
                res = pat.match(x)
                if res:
                    modName = res.group(1)
                    addToFilesToLoad( filesToLoad, modName, vocolaDirectory, moduleHasDot )

        doVocolaFirstModuleName = doVocolaFirst + '.py'
        if VocolaDirFiles and doVocolaFirstModuleName in VocolaDirFiles:
            if debugLoad:
                print(f'natlinkmain, load {doVocolaFirst}')
            x = doVocolaFirst
            loadedFile = loadedFiles.get(x, None)
            if loadedFile:
                origPath, origDate = loadedFile
                loadedFiles[x] = loadFile(x, origPath, origDate)
            else:
                loadedFiles[x] = loadFile(x)
            vocolaModule = sys.modules[doVocolaFirst]
            vocolaIsLoaded = True
            if not vocolaModule.VocolaEnabled:
                # vocola module signals vocola is not enabled:
                vocolaEnabled = 0
                del loadedFiles[x]
                if debugLoad: print('Vocola is disabled...')
                vocolaIsLoaded = False
    
        if vocolaGrammarsDirectory:
            vocolaGrammarFiles = [x for x in os.listdir(vocolaGrammarsDirectory) if x.endswith('.py')]
            nVocolaGrammars = 0
            for x in vocolaGrammarFiles:
                res = pat.match(x)
                if res:
                    nVocolaGrammars += 1
                    modName = res.group(1)
                    addToFilesToLoad( filesToLoad, modName, vocolaGrammarsDirectory, moduleHasDot )
            if debugLoad:
                print(f"natlinkmain: {nVocolaGrammars} Vocola Compiled grammars checking to load")

    # for x in baseDirFiles:
    #     res = pat.match(x)
    #     if res:
    #         modName = res.group(1)
    #         if debugLoad and curModule:
    #             print("application specific, baseDirFile MATCH: %s, group1: %s"% (x, modName))
    #         addToFilesToLoad( filesToLoad, modName, baseDirectory, moduleHasDot )

    keysToLoad = list(filesToLoad.keys())
    if debugLoad:
        print(f'natlinkmain: {len(keysToLoad)} grammars checking load')
    for x in keysToLoad:
        if x == doVocolaFirst:
            continue
        if debugLoad: print(f"loading {x}")
        loadedFile = loadedFiles.get(x, None)
        if loadedFile:
            origPath, origDate = loadedFile
            loadedFiles[x] = loadFile(x, origPath, origDate)
        else:
            loadedFiles[x] = loadFile(x)

    # Unload any files which have been deleted
    filesToUnload = []
    for name, loadedFile in loadedFiles.items():
        if loadedFile:
            origPath, origDate = loadedFile
            if origPath and not getFileDate(origPath):
                filesToUnload.append(name)

    for name in filesToUnload:
        if debugLoad:
            print("natlinkmain, file is deleted, unload %s"% name)
        unloadFile(name)

def reorderKeys(modulesKeys):
    """here is the chance to influence the order of loading

    for Unimacro do _control last and _tasks first
    
    and doVocolaFirst is excluded here, because it has a special treatment anyway...

    """
    L = copy.copy(modulesKeys)
    gramsLast = ['_control']
    gramsFirst = ['_tasks']
    for g in gramsFirst:
        if g in L:
            L.remove(g)
            L.insert(0, g)
    for g in gramsLast:
        if g in L:
            L.remove(g)
            L.append(g)
    if modulesKeys == L:
        return L
    if debugLoad:
        print('reordered list of grammars to load:\n===old: %s\nnew: %s'% (modulesKeys, L))
    return L


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



def unloadFile(name):
    """unload the grammar and remove from loadedFiles
    
    some special treatment of vocola
    """
    #pylint:disable=W0603
    global loadedFiles, vocolaIsLoaded, vocolaModule
    if name in loadedFiles:
        safelyCall(name, 'unload')
        del loadedFiles[name]
        if name == doVocolaFirst:
            vocolaIsLoaded = None
            vocolaModule = None
    else:
        print(f'??? unloadFile({name}) loadedFiles is False???')
#
# This function is called when we change users.  It calls the unload member
# function in each loaded module.
#

def unloadEverything():
    """onload all loaded files
    """
    #pylint:disable=W0603
    global loadedFiles
    for x in list(loadedFiles.keys()):
        unloadFile(x)
    if loadedFiles:
        print("after unloadEverything, loadedFiles not empty: %s"% loadedFiles)
        print("make it empty NOW")
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
    #pylint:disable=W0603
    global lastModule

    curModule = getCurrentApplicationName(moduleInfo)

    if curModule and not (onlyIfChanged and curModule==lastModule):
        findAndLoadFiles(curModule)
        lastModule = curModule


def setSearchImportDirs():
    """set the global list of import dirs, to be used for import
    
    and add them to sys.path if needed...

    either [userDirectory, unimacroDirectory, ] or less (if no userDirectory or no unimacroDirectory)

    """
    #pylint:disable=W0603, R0912
    global searchImportDirs
    searchImportDirs = []
    if vocolaIsEnabled:
        if debugLoad:
            print('include Vocola in grammars to load')
        if vocolaDirectory and os.path.isdir(vocolaDirectory):
            searchImportDirs.append(vocolaDirectory)
        if vocolaGrammarsDirectory and os.path.isdir(vocolaGrammarsDirectory):
            searchImportDirs.append(vocolaGrammarsDirectory)
    else:
        print('Vocola is disabled')
    if unimacroIsEnabled:
        if debugLoad:
            print('include Unimacro in grammars to load')
        if unimacroDirectory and os.path.isdir(unimacroDirectory):
            searchImportDirs.append(unimacroDirectory)
        if unimacroGrammarsDirectory and os.path.isdir(unimacroGrammarsDirectory):
            searchImportDirs.append(unimacroGrammarsDirectory)
    else:
        print('Unimacro is disabled')
    if userDirectory and os.path.isdir(userDirectory):
        if debugLoad:
            print(f'include UserDirectory: "{userDirectory}" in grammars to load')
        searchImportDirs.append(userDirectory)
    else:
        print("no UserDirectory specified")
    _added = False
    for searchdir in reversed(searchImportDirs):
        if not searchdir in sys.path:
            if debugLoad:
                print('from setSearchImportDirs add to path: %s'% searchdir)
            sys.path.insert(0, searchdir)
            _added = True
    # if added:
    #     print('from setSearchImportDirs: ')
    #     pprint(sys.path)

#
# When a new utterance begins we check all the loaded modules for changes.
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
    """callback at begin of utterance
    """
    #pylint:disable=W0603, R0912
    global loadedFiles, prevModInfo
    cbd = natlink.getCallbackDepth()
    if debugCallback:
        print('beginCallback, cbd: %s'% cbd)
        # print 'beginCallback, cbd: %s, checkAll: %s, checkForGrammarChanges: %s'% \
        #       (cbd, checkAll, checkForGrammarChanges)
    # maybe should be 1...
    if natlink.getCallbackDepth() > 1:
        return
    t0 = time.time()

    if vocolaEnabled and vocolaIsLoaded:
        result = vocolaModule.vocolaBeginCallback(moduleInfo)
        if result == 2:
            if debugCallback:
                print('Vocola made new module, load all Python files')
            findAndLoadFiles()
            loadModSpecific(moduleInfo)
        elif result == 1:
            if debugCallback:
                print('Vocola changed a Python module, check')
            checkAll = 1
        else:
            if debugCallback:
                print('no changes Vocola user files')

    if checkAll or checkForGrammarChanges:
        if debugCallback:
            print('check for changed files (all files)...')
        for x, loadedFile in loadedFiles.items():
            if loadedFile:
                origPath, origDate = loadedFile
                loadedFiles[x] = loadFile(x, origPath, origDate)
            else:
                loadedFiles[x] = loadFile(x)
        loadModSpecific(moduleInfo)  # in checkAll or checkForGrammarChanges mode each time
    else:
        if debugCallback:
            print('check for changed files (only specific)')
        loadModSpecific(moduleInfo, 1)  # only if changed module
    if debugTiming:
        print('checked all grammar files: %.6f'% (time.time()-t0,))

#
# This callback is called when the user changes or when the microphone
# changes state.  We check for changes when the microphone is turned on.
#
# Note: getCurrentModule can raise the BadWindow except and if that happens
# we ignore the callback.
#

def changeCallback(Type,args):
    """callback at change of microphone or user profile
    """
    #pylint:disable=W0603, R0915, W0601, W0612
    global userName, DNSuserDirectory, language, userLanguage, userTopic, \
            BaseModel, BaseTopic, DNSmode, changeCallbackUserFirst, shiftkey

    # if debugCallback:
    print('changeCallback, Type: %s, args: %s'% (Type, args))
    if Type == 'mic' and args == 'on':
        if debugCallback:
            print('findAndLoadFiles...')
        moduleInfo = natlink.getCurrentModule()
        findAndLoadFiles()
        beginCallback(moduleInfo, checkAll=1)
        loadModSpecific(moduleInfo)

    ## user: at start and at user switch:
    if Type == 'user' and userName != args[0]:
        ## update userInfo
        ## other user, setUserInfo in status:
        # print(f'setUserInfo in status to {args}')
        prevLanguage = language
        # status.clearUserInfo()
        status.setUserInfo(args)
        language = status.getLanguage()
        print(f'after setting userInfo: language: {language}, prev: {prevLanguage}')
        # print(f'old language: {prevLanguage}, new language: {language}')
        # print(f'userLanguage: {status.getUserLanguage()}')
        if debugCallback:
            print('callback user, args: %s'% repr(args))
        moduleInfo = natlink.getCurrentModule()
        if debugCallback:
            print("---------changeCallback, User changed to", args[0])
        elif not changeCallbackUserFirst:
            # first time, no print message, but next time do...
            print("\n--- user changed to: %s"% args[0])
            changeCallbackUserFirst = False
        if language == prevLanguage:
            print(f'changeCallback language: {language}, prevLanguage: {prevLanguage}')
            return 

        unloadEverything()
## this is not longer needed here, as we fixed the userDirectory
##        changeUserDirectory()
        DNSuserDirectory = status.getDNSuserDirectory()
        userLanguage = status.getUserLanguage()
        userTopic = status.getUserTopic()
        baseTopic = status.getBaseTopic() # obsolescent, 2018, DPI15
        baseModel = status.getBaseModel() # osbolescent, 2018, DPI 15
        userName = status.getUserName()
        shiftkey = status.getShiftKey()
        if debugCallback:
            print('setting shiftkey to: %s (language: %s)'% (shiftkey, language))

        if debugCallback:
            print('usercallback, language: %s'% language)

        # initialize recentEnv in natlinkcorefunctions (new 2018, 4.1uniform)
        natlinkstatus.AddExtendedEnvVariables()
        natlinkstatus.AddNatlinkEnvironmentVariables(status=status)
    
        # changed, at each call, not only the first one:
        # natlinkstartup.start()
        # done now in natlinkvocolastartup.py of vocola repository

        # changed next two lines QH:
        findAndLoadFiles()
        beginCallback(moduleInfo, checkAll=1)
        loadModSpecific(moduleInfo)
        # # give a warning for BestMatch V , only for Dragon 12:
        BaseModel = status.getBaseModel()
        # BaseTopic = status.getBaseTopic(userTopic=userTopic)
        BaseTopic = status.getBaseTopic()
        if debugCallback:
            print('language: %s (%s)'% (language, type(language)))
            print('userLanguage: %s (%s)'% (userLanguage, type(userLanguage)))
            print('DNSuserDirectory: %s (%s)'% (DNSuserDirectory, type(DNSuserDirectory)))
        else:
            ## end of user info message:
            if language != 'enx':
                print('--- userLanguage: %s\n'% language)

    #ADDED BY BJ, possibility to finish exclusive mode by a grammar itself (around 2002)
    # the grammar should include a function like:
    #def changeCallback():
    #    if thisGrammar:
    #        thisGrammar.cancelMode()
    # and the grammar should have a cancelMode function that finishes exclusive mode.
    # see _oops, _repeat, _control for examples
    changeCallbackLoadedModules(Type,args)

    # if debugCallback:
    #     print('=== debugCallback info ===')
    #     for name in ['natlinkDirectory', 'baseDirectory', 'DNSuserDirectory', 'userName',
    #      'unimacroDirectory', 'userDirectory',
    #      'windowsVersion', 'BaseModel', 'BaseTopic',
    #      'language', 'userLanguage', 'userTopic']:
    #         if not name in globals():
    #             print('natlinkmain, changeCallback, not in globals: %s'% name)
    #         else:
    #             print('natlinkmain changeCallback, global variable: %s: %s'% (name, globals()[name]))

def changeCallbackLoadedModules(Type,args):
    """BJ added, in order to intercept in a grammar (oops, repeat, control) in eg mic changed

    in those cases the cancelMode can be called, so exclusiveMode is finished
    """
    #pylint:disable=W0603
    global loadedFiles
    sysmodules = sys.modules
    for x in list(loadedFiles.keys()):
        if loadedFiles[x]:
            try: func = getattr(sysmodules[x], 'changeCallback')
            except AttributeError: pass
            else:
##                print 'call changeCallback for: %s'% x
                func(*[Type,args])

# ### try here a adapted recognitionMimic function
# def recognitionMimic(mimicList):
#     """for Dragon 12, try execScript HeardWord
#     """
#     if DNSVersion >= 12:
#         script = 'HeardWord "%s"'% '", "'.join(mimicList)
#         natlink.execScript(script)
#     else:
#         natlink.recognitionMimic(mimicList)

def start_natlink(doNatConnect=None):
    """do the startup of the python macros system
    
    Better not use doNatConnect, but ensure this is done before calling, and with a finally: natlink.natDisconnect() call
    """
    #pylint:disable=W0603, R0912, R0915
    global loadedFiles
    print('--')
    nGrammarsLoaded = len(loadedFiles)
    if nGrammarsLoaded:
        if debugLoad:
            print("unload everything, %s grammars loaded"% nGrammarsLoaded)
        unloadEverything()
    else:
        if debugLoad:
            print("no grammars loaded yet")

    if natlinkmainPrintsAtStart:
        print('-- natlinkmain starting...')

    if not natlink.isNatSpeakRunning():
        print('start Dragon first, then rerun the script natlinkmain...')
        time.sleep(10)
        return

    if not doNatConnect is None:
        if doNatConnect:
            print('start_natlink, do natConnect with option 1, threading')
            natlink.natConnect(1) # 0 or 1, should not be needed when automatic startup
        else:
            print('start_natlink, do natConnect with option 0, no threading')
            natlink.natConnect(0) # 0 or 1, should not be needed when automatic startup

        print("----natlink.natConnect succeeded")

    # get the current user information from the Natlink module
    if userDirectory and os.path.isdir(userDirectory):
        if not userDirectory in sys.path:
            sys.path.insert(0,userDirectory)
            if debugLoad:
                print('insert userDirectory: %s to sys.path!'% userDirectory)
        else:
            if debugLoad:
                print('userDirectory: %s'% userDirectory)
    else:
        if debugLoad:
            print('no userDirectory')

    # for unimacro, in order to reach unimacro files to be imported:
    if unimacroDirectory and os.path.isdir(unimacroDirectory):
        if status.UnimacroIsEnabled():
            if not unimacroDirectory in sys.path:
                sys.path.insert(0,unimacroDirectory)
                if debugLoad:
                    print('insert unimacroDirectory: %s to sys.path!'% unimacroDirectory)
            else:
                if debugLoad:
                    print('unimacroDirectory: %s'% unimacroDirectory)
        else:
            if debugLoad:
                print('Unimacro not enabled')

    else:
        if debugLoad:
            print('no unimacroDirectory')

    # setting searchImportDirs, also insert at front of sys.path if not in the list yet.
    setSearchImportDirs()


##    BaseModel, BaseTopic = status.getBaseModelBaseTopic()

    # load all global files in user directory and current directory
    # findAndLoadFiles() is done in the changeCallback function
    changeCallback('user', natlink.getCurrentUser())

    # initialize our callbacks
    natlink.setBeginCallback(beginCallback)
    natlink.setChangeCallback(changeCallback)

    # init things identical to when user changes:
    # skip this at startup, first mic on hits a changeCallback...
    # changeCallback('user', natlink.getCurrentUser())

    print(('natlinkmain started from %s:\n  Natlink version: %s\n  DNS version: %s\n  Python version: %s\n  Windows Version: %s'% \
              (status.getNatlinkDirectory(), status.getInstallVersion(),
               DNSVersion, status.getPythonVersion(), windowsVersion, )))

    if debugLoad:
        print("userDirectory: %s\nvocolaDirectory: %s\nunimacroDirectory: %s\n"% (userDirectory, vocolaDirectory, unimacroDirectory))
        print("loadedFiles: %s"% loadedFiles)
        print("natlinkmain imported-----------------------------------")
    elif natlinkmainPrintsAtEnd:
        if status.UnimacroIsEnabled():
            print('Unimacro enabled, UnimacroUserDirectory:\n  %s'% status.getUnimacroUserDirectory())
        if status.VocolaIsEnabled():
            print('Vocola enabled, VocolaUserDirectory:\n  %s'% status.getVocolaUserDirectory())
        if userDirectory:
            print("User defined macro's enabled, UserDirectory:\n  %s"% userDirectory)
        print('-'*40)
    #else:
    #    natlinkLogMessage('natlinkmain started (imported)\n')
    if status.hadWarning:
        print('='*30)
        print(status.getWarningText())
        print('='*30)
        status.emptyWarning()

###################################################################
#
# Here is the initialization code.
#

# when you want to start natlink modules interactive from this module, set Testing to True
# natlinkmain (which is the name of natlink.pyd when started from Dragon)
# will then not start all natlink modules. Whenever you change this value, you need
# to restart Dragon...
Testing = False

def run():
    """run natlink
    """
    #pylint:disable=C0415, W0611



    if not Testing:
        import redirect_output
        start_natlink()
    else:
        print("natlinkmain is in testing mode...")

if __name__ == "natlinkmain":
    if canStartNatlink:
        if Testing is False:
            #sys.stdout = NewStdout()  # this is done at the top already
            #sys.stderr = NewStderr()
            start_natlink()
        else:
            print('natlinkmain imported only, Testing in progress')
            print('\nDo not forget to put "Testing = False" again near bottom of natlinkmain.py in order to resume normal use...')
            print('\n... and then restart Dragon.')
    else:
        print('Cannot start Natlink')
elif __name__  == "__main__":
    if Testing:
        print("starting all Natlink stuff from natlinkmain.py")
        natlink.natConnect(1)
        try:
            print("start_natlink starting...")
            start_natlink()
            print("after start_natlink...")
        finally:
            print("finally do natDisconnect()")
            natlink.natDisconnect()
    else:
        print("run interactive, do nothing, enable Testing if you want to start Natlink from this module")
