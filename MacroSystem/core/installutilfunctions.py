#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# installutilfunctions.py
#
# Quintijn Hoogenboom, January 2008:
# this module should both be (and identical) in
# -- the core folder of natlink (where natlinkmain is started from natspeak when natlink
#                                is enabled
# -- the configurenatlinkvocolaunimacro folder, from
#    which configuration of natlink/vocola/unimacro is performed
#
# getBaseFolder: returns the folder from the calling module
# getCoreDir: returns the core folder of natlink, relative to the configure directory
# fatalError: raises error again, if new_raise is set, otherwise continues executing
# getExtendedEnv(env): gets from os.environ, or from window system calls the
#                      environment.
#  
import os, sys

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

# report function:
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print 'natlinkconfigfunctions fails because of fatal error:'
    print message
    print
    print 'This can (hopefully) be solved by (re)installing natlink'
    print 
    if new_raise:
        raise new_raise
    else:
        raise

# helper function:
def getFromRegdict(regdict, key, fatal=None):
    """get a key from the regdict, which was collected earlier.

    if fails, do fatal error is fatal is set,
    if fatal is not set, only print warning.

    """
    value = None
    try:
        value = regnl[key]
    except KeyError:
        mess = 'cannot find key %s in registry dictionary'% key
        if fatal:
            fatal_error(mess, new_raise = Exception)
        else:
            print mess
            return ''
    else:
        return value
    
def getExtendedEnv(var):
    """get from environ or windows CSLID

    HOME is environ['HOME'] or CSLID_PERSONAL
    ~ is HOME

    """
    global recentEnv
    var = var.strip()
    var = var.strip("%")
    
    if var in recentEnv:
        return recentEnv[var]
    
    if var == "~":
        var = 'HOME'

    # try to get from CSIDL system call:
    if var == 'HOME':
        var2 = 'PERSONAL'
    else:
        var2 = var
        
    try:
        CSIDL_variable =  'CSIDL_%s'% var2
        shellnumber = getattr(shellcon,CSIDL_variable, -1)
    except:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
    if shellnumber < 0:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
    try:
        result = shell.SHGetFolderPath (0, shellnumber, 0, 0)
    except:
        raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)

    result = str(result)
    result = os.path.normpath(result)
    recentEnv[var] = result
    return result

def getAllFolderEnvironmentVariables():
    """get all the environ AND all CSLID variables that result into a folder

    """
    D = {}
    for k in os.environ:
        v = os.environ[k]
        if os.path.isdir(v):
            D[k] = v
    for k in dir(shellcon):
        if k.startswith("CSIDL_"):
            kStripped = k[6:]
            try:
                v = getExtendedEnv(kStripped)
            except ValueError:
                continue
            if len(v) > 2 and os.path.isdir(v):
                D[kStripped] = v
            elif v == '.':
                D[kStripped] = os.getcwd()
    return D

def substituteEnvVariableAtStart(filepath): 
    """try to substitute back one of the (preused) environment variables back

    into the start of a filename

    if ~ (HOME) is D:\My documents,
    the path "D:\My documents\folder\file.txt" should return "~\folder\file.txt"

    

    """
    Keys = recentEnv.keys()
    # sort, longest result first, shortest keyname second:
    decorated = [(-len(recentEnv[k]), len(k), k) for k in Keys]
    decorated.sort()
    Keys = [k for (dummy1,dummy2, k) in decorated]
    for k in Keys:
        val = recentEnv[k]
        if filepath.lower().startswith(val.lower()):
            if k in ("HOME", "PERSONAL"):
                k = "~"
            else:
                k = "%" + k + "%"
            return k + filepath[len(val):]
    return filepath
       

if __name__ == "__main__":
    print 'this module is in folder: %s'% getBaseFolder(globals())