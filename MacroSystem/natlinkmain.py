#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# natlinkmain.py
#   Base module for the Python-based command and control subsystem
#
# April 1, 2000
#   - fixed a bug where we did not unload files when we noticed that they
#     were deleted
#   - fixed a bug where we would load .pyc files without a matching .py
#
# TODO - known bug: if you change the name of a user while it is active we
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

import sys
import string
import os               # access to file information
import os.path          # to parse filenames
import imp              # module reloading
import re               # regular expression parsing    
import traceback        # for printing exceptions
from stat import *      # file statistics
from natlink import *   

#
# This redirects stdout and stderr to a dialog box.
#

class NewStdout:
    softspace=1
    def write(self,text):
        displayText(text, 0)

class NewStderr:
    softspace=1
    def write(self,text):
        displayText(text, 1)

sys.stdout = NewStdout()
sys.stderr = NewStderr()

#
# This is the directory where the Python modules all reside.
#

baseDirectory = ''

#
# This is the current user directory.
#

userName = ''
userDirectory = ''

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

#
# Should we recurse directories when looking for macros
#
recurseDirectories = 1

# A store of all directories where loaded files are
globalSearchPath = {}

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
                # file has not changed
                fndFile.close()
                return origName
        #print "Reloading", modName

        # if we know we are reloading a module, we call the unload function
        # in that module first to release all objects
        safelyCall(modName,'unload')
    else:
        if fndName[-3:] != ".py":   
            # not a Python source file
            fndFile.close()
            return None
        #print "Loading", modName

    try:
        imp.load_module(modName,fndFile,fndName,fndDesc)
        fndFile.close()
        return fndName
    except:
        fndFile.close()
        sys.stderr.write( 'Error loading '+modName+' from '+fndName+'\n' )
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
#   BS: Added this method to enable recursive processing of grammar files 25/08/2003
#   This method simply takes the baseDir as a param and processes the whole tree
#   beneath it.  Ultimately this method is a new way of calling findAndLoadFiles()
#
def findAndLoadFilesRecursively(curModule=None, userDir='', baseDir=''):

    #traceback.print_stack()

    #Add this dir to the path so that we can import any modules from it
    sys.path.append(baseDir)    

    #Check out args to make sure they're set
    if (userDir== ''):
        userDir=userDirectory
    if (baseDir== ''):
        baseDir=baseDirectory

    #print ("userDir= " + userDir + "\n")
    #print ("baseDir= " + baseDir + "\n")

    #Get a list of files in the base directory        
    fileList = os.listdir(baseDir)

    #Recurse down dirs in this one and then drop out to process grammar files in this dir
    for file in fileList:
        lenBase = len(file)
        lastLetter = string.find(file, '$', (lenBase -1))        
        if (os.path.isdir(baseDir+ '\\' +file)!=0):
            #Any dir ending in the $ char, ignore (This dir is turned off by the user)
            if (lastLetter == -1):
                #file is now the new base directory
                findAndLoadFilesRecursively(curModule, userDir, (baseDir+ '\\' +file))

    #process grammar files in this dir
    findAndLoadFiles(curModule, userDir, baseDir)      


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

def findAndLoadFiles(curModule=None, userDir='', baseDir=''):
    global loadedFiles

    if curModule:
        pat = re.compile(r"""
            ^(%s        # filename must match module name
            (_\w+)?)    # optional underscore followed by text
            [.]py$      # extension .py
          """%curModule, re.VERBOSE|re.IGNORECASE)
    else:
        pat = re.compile(r"""
            ^(_         # filename must start with an underscore
            \w+)        # remainder of filename
            [.]py$      # extension .py
          """, re.VERBOSE|re.IGNORECASE)

    filesToLoad = {}
    if userDir != '':
        for x in os.listdir(userDir):
            res = pat.match(x)
            if res:
                filesToLoad[ res.group(1) ] = None
                globalSearchPath[userDir]=None

    for x in os.listdir(baseDir):
        res = pat.match(x)
        if res:
            globalSearchPath[baseDir]=None
            filesToLoad[ res.group(1) ] = None

    # Try to (re)load any files we find
    for x in filesToLoad.keys():
        if loadedFiles.has_key(x):
            origName = loadedFiles[x]
        else:
            origName = None
        loadedFiles[x] = loadFile(x, [userDir,baseDir], origName)

    # Unload any files which have been deleted
    for name,path in loadedFiles.items():
        if path and not getFileDate(path):
            safelyCall(name,'unload')
            del loadedFiles[name]

#
# This function is called when we change users.  It calls the unload member
# function in each loaded module.
#

def unloadEverything():
    global loadedFiles
    for x in loadedFiles.keys():
        if loadedFiles[x]:
            safelyCall(x,'unload')
    loadedFiles = {}

#
# Compute the name of the current module and load all files which are
# specific to that module.
#

def loadModSpecific(moduleInfo,onlyIfChanged=0):
    global lastModule
    
    # this extracts the module base name like "wordpad"
    curModule = os.path.splitext(os.path.split(moduleInfo[0])[1])[0]
    if curModule and not (onlyIfChanged and curModule==lastModule):
        if (recurseDirectories == 1):
            findAndLoadFilesRecursively(curModule, userDirectory, baseDirectory)
        else:
            findAndLoadFiles(curModule, userDirectory, baseDirectory)
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

def beginCallback(moduleInfo):
    global loadedFiles
    if getCallbackDepth() < 2:
        for x in loadedFiles.keys():
            loadedFiles[x] = loadFile(x, globalSearchPath.keys(), loadedFiles[x])
            #print "\"" + loadedFiles[x] + "\"\n" 
        loadModSpecific(moduleInfo,1)
        
#
# This callback is called when the user changes or when the microphone
# changes state.  We check for changes when the microphone is turned on.
#
# Note: getCurrentModule can raise the BadWindow except and if that happens
# we ignore the callback.
#

def changeCallback(type,args):
    global userName, userDirectory
    if type == 'mic' and args == 'on' and getCallbackDepth() < 2:
        moduleInfo = getCurrentModule()
        beginCallback(moduleInfo)
        if (recurseDirectories == 1):
            findAndLoadFilesRecursively(None, userDirectory, baseDirectory)
        else:
            findAndLoadFiles(None, userDirectory, baseDirectory)
        loadModSpecific(moduleInfo)
    if type == 'user' and userName != args[0]:
        userName, userDirectory = args
        moduleInfo = getCurrentModule()
        #print "User changed to", userName
        unloadEverything()
        if (recurseDirectories == 1):
            findAndLoadFilesRecursively(None, userDirectory, baseDirectory)
        else:
            findAndLoadFiles(None, userDirectory, baseDirectory)
        loadModSpecific(moduleInfo)

############################################################################
#
# Here is the initialization code.
#

try:
    # compute the directory where this module came from

    baseDirectory = os.path.split(
        sys.modules['natlinkmain'].__dict__['__file__'])[0]

    # get the current user information from the natlink module

    userName, userDirectory = getCurrentUser()

    # load all global files in user directory and current directory

    if (recurseDirectories == 1):
        findAndLoadFilesRecursively(None, userDirectory, baseDirectory)
    else:
        findAndLoadFiles(None, userDirectory, baseDirectory)

    # initialize our callbacks

    setBeginCallback(beginCallback)
    setChangeCallback(changeCallback)

except:
    sys.stderr.write( 'Error initializing natlinkmain\n' )
    traceback.print_exc()
