#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
"""natlinkcorefunctions.py

 Quintijn Hoogenboom, January 2008/September 2015

These functions are used by natlinkstatus.py,
and can also used by all the modules,
as the core folder will be in the python path
when natlink is running.

The first function is also, hopefully identical, in
natlinkconfigfunctions, in the configurenatlinkvocolaunimacro folder

getBaseFolder: returns the folder from the calling module
fatalError: raises error again, if new_raise is set, otherwise continues executing
getExtendedEnv(env): gets from os.environ, or from window system calls (CSIDL_...) the
                     environment. Take PERSONAL for HOME and ~
getAllFolderEnvironmentVariables: get a dict of all possible HOME and CSIDL variables,
           that result in a valid folder path
substituteEnvVariableAtStart: substitute back into a file/folder path an environment variable

Note: for extension with %NATLINK% etc. see natlinkstatus.py
    (call getAllEnv, this one first takes NatLink variables and then these extended env variables)

""" 
import os, sys, re, copy
from win32com.shell import shell, shellcon
# import win32api
# for extended environment variables:
reEnv = re.compile('(%[A-Z_]+%)', re.I)
from inivars import IniVars

def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
##        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
##        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder or baseFolder == '.':
        baseFolder = os.getcwd()
##        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

# the NatLink Core directory:
thisBaseFolder = getBaseFolder()


# report function:
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print 'natlinkconfigfunctions fails because of fatal error:'
    print
    print message
    print
    print 'Exit Dragon and run the configurenatlink program (via start_configurenatlink.py)'
    print 
    if new_raise:
        raise new_raise
    else:
        raise

# keep track of found env variables, fill, if you wish, with
# getAllFolderEnvironmentVariables.
# substitute back with substituteEnvVariableAtStart.
# and substite forward with expandEnvVariableAtStart
# in all cases a private envDict can be user, or the global dict recentEnv
#
# to collect all env variables, call getAllFolderEnvironmentVariables, see below
recentEnv = {}

def addToRecentEnv(name, value):
    """to be filled for NATLINK variables from natlinkstatus
    """
    recentEnv[name] = value

def deleteFromRecentEnv(name):
    """to possibly delete from recentEnv, from natlinkstatus
    """
    if name in recentEnv:
        del recentEnv[name]

def getFolderFromLibraryName(fName):
    """from windows library names extract the real folder
    
    the CabinetWClass and #32770 controls return "Documents", "Dropbox", "Desktop" etc.
    try to resolve these throug the extended env variables.
    """
    if fName.startswith("Docum"):  # Documents in Dutch and English
        return getExtendedEnv("PERSONAL")
    if fName in ["Muziek", "Music"]:
        return getExtendedEnv("MYMUSIC")
    if fName in ["Pictures", "Afbeeldingen"]:
        return getExtendedEnv("MYPICTURES")
    if fName in ["Videos", "Video's"]:
        return getExtendedEnv("MYVIDEO")
    if fName in ['OneDrive']:
        return getExtendedEnv("OneDrive")
    if fName in ['Desktop', "Bureaublad"]:
        return getExtendedEnv("DESKTOP")
    if fName == 'Dropbox':
        return getDropboxFolder()
    if fName in ['Download', 'Downloads']:
        personal = getExtendedEnv('PERSONAL')
        userDir = os.path.normpath(os.path.join(personal, '..'))
        if os.path.isdir(userDir):
            tryDir = os.path.normpath(os.path.join(userDir, fName))
            if os.path.isdir(tryDir):
                return tryDir
    print 'cannot find folder for Library name: %s'% fName
def getDropboxFolder(containsFolder=None):
    """get the dropbox folder, or the subfolder which is specified.
    
    Searching is done in all 'C:\Users' folders, and in the root of "C:"
    (See DirsToTry)
    
    raises IOError if more folders are found (should not happen, I think)
    if containsFolder is not passed, the dropbox main folder is returned
    if containsFolder is passed, this folder is returned if it is found in the dropbox folder
    
    otherwise None is returned.
    """
    results = []
    root = 'C:\\Users'
    dirsToTry = [ os.path.join(root, s) for s in os.listdir(root) if os.path.isdir(os.path.join(root,s)) ]
    dirsToTry.append('C:\\')
    for root in dirsToTry:
        if not os.path.isdir(root):
            continue
        try:
            subs = os.listdir(root)
        except WindowsError:
            continue
        if 'Dropbox' in subs:
            subAbs = os.path.join(root, 'Dropbox')
            subsub = os.listdir(subAbs)
            if not ('.dropbox' in subsub and os.path.isfile(os.path.join(subAbs,'.dropbox'))):
                continue
            elif containsFolder:
                result = matchesStart(subsub, containsFolder, caseSensitive=False)
                if result:
                    results.append(os.path.join(subAbs,result))
            else:
                results.append(subAbs)
    if not results:
        return
    if len(results) > 1:
        raise IOError('getDropboxFolder, more dropbox folders found: %s')
    return results[0]                 

def matchesStart(listOfDirs, checkDir, caseSensitive):
    """return result from list if checkDir matches, mostly case insensitive
    """
    if not caseSensitive:
        checkDir = checkDir.lower()
    for l in listOfDirs:
        if not caseSensitive:
            ll = l.lower()
        else:
            ll = l
        if ll.startswith(checkDir):
            return l
        
        
            

def getExtendedEnv(var, envDict=None, displayMessage=1):
    """get from environ or windows CSLID

    HOME is environ['HOME'] or CSLID_PERSONAL
    ~ is HOME

    DROPBOX added via getDropboxFolder is this module (QH, December 1, 2018)

    As envDict for recent results either a private (passed in) dict is taken, or
    the global recentEnv.

    This is merely for "caching results"

    """
    if envDict == None:
        myEnvDict = recentEnv
    else:
        myEnvDict = envDict
##    var = var.strip()
    var = var.strip("% ")
    var = var.upper()
    
    if var == "~":
        var = 'HOME'

    if var in myEnvDict:
        return myEnvDict[var]

    if var in os.environ:
        myEnvDict[var] = os.environ[var]
        return myEnvDict[var]

    if var == 'DROPBOX':
        result = getDropboxFolder()
        if result:
            return result
        raise ValueError('getExtendedEnv, cannot find path for "DROPBOX"')

    if var == 'NOTEPAD':
        windowsDir = getExtendedEnv("WINDOWS")
        notepadPath = os.path.join(windowsDir, 'notepad.exe')
        if os.path.isfile(notepadPath):
            return notepadPath
        raise ValueError('getExtendedEnv, cannot find path for "NOTEPAD"')

    # try to get from CSIDL system call:
    if var == 'HOME':
        var2 = 'PERSONAL'
    else:
        var2 = var
        
    try:
        CSIDL_variable =  'CSIDL_%s'% var2
        shellnumber = getattr(shellcon,CSIDL_variable, -1)
    except:
        print 'getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2
        return ''
    if shellnumber < 0:
        # on some systems have SYSTEMROOT instead of SYSTEM:
        if var == 'SYSTEM':
            return getExtendedEnv('SYSTEMROOT', envDict=envDict)
        return ''
        # raise ValueError('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
    try:
        result = shell.SHGetFolderPath (0, shellnumber, 0, 0)
    except:
        if displayMessage:
            print 'getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2
        return ''

    
    result = str(result)
    result = os.path.normpath(result)
    myEnvDict[var] = result
    # on some systems apparently:
    if var == 'SYSTEMROOT':

        myEnvDict['SYSTEM'] = result
    return result

def clearRecentEnv():
    """for testing, clears above global dictionary
    """
    recentEnv.clear()

def getAllFolderEnvironmentVariables(fillRecentEnv=None):
    """return, as a dict, all the environ AND all CSLID variables that result into a folder
    
    Now also implemented:  Also include NATLINK, UNIMACRO, VOICECODE, DRAGONFLY, VOCOLAUSERDIR, UNIMACROUSERDIR
    This is done by calling from natlinkstatus, see there and example in natlinkmain.

    Optionally put them in recentEnv, if you specify fillRecentEnv to 1 (True)

    """
    global recentEnv
    D = {}

    for k in dir(shellcon):
        if k.startswith("CSIDL_"):
            kStripped = k[6:]
            try:
                v = getExtendedEnv(kStripped, displayMessage=None)
            except ValueError:
                continue
            if len(v) > 2 and os.path.isdir(v):
                D[kStripped] = v
            elif v == '.':
                D[kStripped] = os.getcwd
    # os.environ overrules CSIDL:
    for k in os.environ:
        v = os.environ[k]
        if os.path.isdir(v):
            v = os.path.normpath(v)
            if k in D and D[k] != v:
                print 'warning, CSIDL also exists for key: %s, take os.environ value: %s'% (k, v)
            D[k] = v
    if fillRecentEnv:
        recentEnv = copy.copy(D)
    return D

#def setInRecentEnv(key, value):
#    if key in recentEnv:
#        if recentEnv[key] == value:
#            print 'already set (the same): %s, %s'% (key, value)
#        else:
#            print 'already set (but different): %s, %s'% (key, value)
#        return
#    print 'setting in recentEnv: %s to %s'% (key, value)
#    recentEnv[key] = value

def substituteEnvVariableAtStart(filepath, envDict=None): 
    """try to substitute back one of the (preused) environment variables back

    into the start of a filename

    if ~ (HOME) is D:\My documents,
    the path "D:\My documents\folder\file.txt" should return "~\folder\file.txt"

    pass in a dict of possible environment variables, which can be taken from recent calls, or
    from  envDict = getAllFolderEnvironmentVariables().

    Alternatively you can call getAllFolderEnvironmentVariables once, and use the recentEnv
    of this module! getAllFolderEnvironmentVariables(fillRecentEnv)

    If you do not pass such a dict, recentEnv is taken, but this recentEnv holds only what has been
    asked for in the session, so no complete list!

    """
    if envDict == None:
        envDict = recentEnv
    Keys = envDict.keys()
    # sort, longest result first, shortest keyname second:
    decorated = [(-len(envDict[k]), len(k), k) for k in Keys]
    decorated.sort()
    Keys = [k for (dummy1,dummy2, k) in decorated]
    for k in Keys:
        val = envDict[k]
        if filepath.lower().startswith(val.lower()):
            if k in ("HOME", "PERSONAL"):
                k = "~"
            else:
                k = "%" + k + "%"
            filepart = filepath[len(val):]
            filepart = filepart.strip('/\\ ')
            return os.path.join(k, filepart)
    # no hit, return original:
    return filepath
       
def expandEnvVariableAtStart(filepath, envDict=None): 
    """try to substitute environment variable into a path name

    """
    filepath = filepath.strip()

    if filepath.startswith('~'):
        folderpart = getExtendedEnv('~', envDict)
        filepart = filepath[1:]
        filepart = filepart.strip('/\\ ')
        return os.path.normpath(os.path.join(folderpart, filepart))
    elif reEnv.match(filepath):
        envVar = reEnv.match(filepath).group(1)
        # get the envVar...
        try:
            folderpart = getExtendedEnv(envVar, envDict)
        except ValueError:
            print 'invalid (extended) environment variable: %s'% envVar
        else:
            # OK, found:
            filepart = filepath[len(envVar)+1:]
            filepart = filepart.strip('/\\ ')
            return os.path.normpath(os.path.join(folderpart, filepart))
    # no match
    return filepath
    
def expandEnvVariables(filepath, envDict=None): 
    """try to substitute environment variable into a path name,

    ~ only at the start,

    %XXX% can be anywhere in the string.

    """
    filepath = filepath.strip()
    
    if filepath.startswith('~'):
        folderpart = getExtendedEnv('~', envDict)
        filepart = filepath[1:]
        filepart = filepart.strip('/\\ ')
        filepath = os.path.normpath(os.path.join(folderpart, filepart))
    
    if reEnv.search(filepath):
        List = reEnv.split(filepath)
        #print 'parts: %s'% List
        List2 = []
        for part in List:
            if not part: continue
            if part == "~" or (part.startswith("%") and part.endswith("%")):
                try:
                    folderpart = getExtendedEnv(part, envDict)
                except ValueError:
                    folderpart = part
                List2.append(folderpart)
            else:
                List2.append(part)
        filepath = ''.join(List2)
        return os.path.normpath(filepath)
    # no match
    return filepath

def printAllEnvVariables():
    for k in sorted(recentEnv.keys()):
        print("%s\t%s"% (k, recentEnv[k]))

class InifileSection(object):
    """simulate a part of the registry through inifiles
    
        basic file is natlinkstatus.ini
        basic section is usersettings
        
        So one instance operates only on one section of one ini file!
        
        Now uses the inivars module of Quintijn instead of GetProfileVal system calls.
        
        Only use for readonly or for one section if you want to rewrite data!!
        
        methods:
        set(key, value): set a key=value entry in the section
        get(key, defaultValue=None): get the associated value with
                 key in the current section.
                 if empty or not there, the defaultValue is returned
                 if value = "0" or "1" the integer value 0 or 1 is returned
        delete(key): deletes from section
        keys(): return a list of keys in the section
        __repr__: give contents of a section
        
    """
    def __init__(self, section, filename):
        """open a section in a inifile
        
        """
        self.section = section
        self.ini = IniVars(filename) # want strings to be returned
          
    def __repr__(self):
        """return contents of sections
        """
        L = ["[%s]"% self.section ]
        for k in self.ini.get(self.section):
            v = self.ini.get(self.section, k)
            L.append("%s=%s"% (k, v))
        return '\n'.join(L)
    
    def __iter__(self):
        for item in self.ini.get(self.section):
            yield item         
            
    def get(self, key, defaultValue=None):
        """get an item from a key
        
        """
        if defaultValue is None:
            defaultValue = ''
        else:
            defaultValue = str(defaultValue)
        value = self.ini.get(self.section, key, defaultValue)

        # value = win32api.GetProfileVal(self.section, key, defaultValue, self.filename)
##        if value:
##            print 'get: %s, %s: %s'% (self.section, key, value)
        if value in (u"0", u"1"):
            return int(value)
        return value

    def set(self, key, value):
        """set an item for akey
        
        0 or empty deletes automatically
        
        """
##        print 'set: %s, %s: %s'% (self.section, key, value)
        if value in [0, "0"]:
            self.delete(key)
        elif not value:
            self.ini.delete(self.section, key)
        else:
            self.ini.set(self.section, key, value)
            self.ini.write()
            pass
            # win32api.WriteProfileVal( self.section, key, str(value), self.filename)
            # checkValue = win32api.GetProfileVal(self.section, key, 'nonsens', self.filename)
            # if not (checkValue == value or \
            #                   value in [0, 1] and checkValue == str(value)):
            #     print 'set failed:  %s, %s: %s, got %s instead'% (self.section, key, value, checkValue)
            
    def delete(self, key):
        """delete an item for a key (really set to "")
        
        """
        self.ini.delete(self.section, key)
        self.ini.write()
        pass
        # print 'delete: %s, %s'% (self.section, key)
        # value = win32api.WriteProfileVal( self.section, key, None,
        #                                self.filename)
        # checkValue = win32api.GetProfileVal(self.section, key, 'nonsens', self.filename)
        # if checkValue != 'nonsens':
        #     print 'delete failed:  %s, %s: got %s instead'% (self.section, key, checkValue)

    def keys(self):
        Keys = self.ini.get(self.section)
        # Keys =  win32api.GetProfileSection( self.section, self.filename)
        # Keys = [k.split('=')[0].strip() for k in Keys]
        # #print 'return Keys: %s'% Keys
        return Keys

defaultFilename = "natlinkstatus.ini"
defaultSection = 'usersettings'
class NatlinkstatusInifileSection(InifileSection):
    """subclass with fixed filename and section"""
    
    def __init__(self):
        """get the default inifile:
        In baseDirectory (this directory) the ini file natlinkstatus.ini
        with section defaultSection
        """        
        dirName = getBaseFolder()
        if not os.path.isdir(dirName):
            raise ValueError("starting inifilesection, invalid directory: %s"%
                            dirName)
        filename = os.path.join(dirName, defaultFilename)
        InifileSection.__init__(self, section=defaultSection, filename=filename)


if __name__ == "__main__":
    print 'this module is in folder: %s'% getBaseFolder(globals())
    vars = getAllFolderEnvironmentVariables()
    for k in sorted(vars):
        print '%s: %s'% (k, vars[k])
        if not os.path.isdir(vars[k]):
            print '----- not a directory: %s (%s)'% (vars[k], k)

    print 'testing       expandEnvVariableAtStart'
    print 'also see expandEnvVar in natlinkstatus!!'
    for p in ("D:\\natlink\\unimacro", "~/unimacroqh",
              "%HOME%/personal",
              "%WINDOWS%\\folder\\strange testfolder"):
        expanded = expandEnvVariableAtStart(p)
        print 'expandEnvVariablesAtStart: %s: %s'% (p, expanded)
    print 'testing       expandEnvVariables'  
    for p in ("%DROPBOX%/QuintijnHerold/jachthutten", "D:\\%username%", "%NATLINK%\\unimacro", "%UNIMACROUSER%",
              "%HOME%/personal", "%HOME%", "%personal%"
              "%WINDOWS%\\folder\\strange testfolder"):
        expanded = expandEnvVariables(p)
        print 'expandEnvVariables: %s: %s'% (p, expanded)

    # testIniSection = NatlinkstatusInifileSection()
    # print testIniSection.keys()
    # testIniSection.set("test", "een test")
    # testval = testIniSection.get("test")
    # print 'testval: %s'% testval
    # testIniSection.delete("test")
    # testval = testIniSection.get("test")
    # print 'testval: %s'% testval
    print 'recentEnv: %s'% len(recentEnv)
    np = getExtendedEnv("NOTEPAD")
    print np
    for lName in ['Documenten', 'Documents', 'Muziek', 'Afbeeldingen', 'Dropbox', 'OneDrive', 'Desktop', 'Bureaublad']:
        f = getFolderFromLibraryName(lName)
        print 'folder from library name %s: %s'% (lName, f)