"""
implements the path class, based upon pathlib/path

was before in utilsqh, but better do it here, in Natlink/Macrosystem/core
moving into the core directory natlink (with python3)

"""
import pathlib
import os
import shutil
import sys
import types
import glob
import re
import copy
import unicodedata
import win32file
import fnmatch
# for extended environment variables:
from win32com.shell import shell, shellcon
import time
import datetime

## environment variables:
reEnv = re.compile('(%([a-z0-9_]+)%)', re.I)

recentEnv = {}   # to be updated at end of module import

## functions for generating alternative paths in virtual drives
## uses reAltenativePaths, defined in the top of this module
## put in utilsqh.py! used in sitegen AND in _folders.py grammar of Unimacro:
# for alternatives in virtual drive definitions:
reAltenativePaths = re.compile(r"(\([^|()]+?(\|[^|()]+?)+\))")

class PathError(Exception):
    pass


def generate_alternatives(s):
    """generates altenatives if (xxx|yyy) is found, otherwise just yields s
    Helper for cross_loop_alternatives
    """
    m = reAltenativePaths.match(s)
    if m:
        alternatives = s[1:-1].split("|")
        for item in alternatives:
            yield item
    else:
        yield s
        
def cross_loop_alternatives(*sequences):
    """helper function for loop_through_alternative_paths
    """
    if sequences:
        for x in generate_alternatives(sequences[0]):
            for y in cross_loop_alternatives(*sequences[1:]):
                yield (x,) + y
    else:
        yield ()

def loop_through_alternative_paths(pathdefinition):
    """can hold alternatives (a|b)
    
>>> list(loop_through_alternative_paths("(C|D):/xxxx/yyyy"))
['C:/xxxx/yyyy', 'D:/xxxx/yyyy']
>>> list(loop_through_alternative_paths("(C:|D:|E:)/Do(kum|cum)ent(s|en)"))
['C:/Dokuments', 'C:/Dokumenten', 'C:/Documents', 'C:/Documenten', 'D:/Dokuments', 'D:/Dokumenten', 'D:/Documents', 'D:/Documenten', 'E:/Dokuments', 'E:/Dokumenten', 'E:/Documents', 'E:/Documenten']

    So "(C|D):/natlink" first yields "C:/natlink" and then "D:/natlink".
    More alternatives in one item are possible, see second example.
    """
    m = reAltenativePaths.search(pathdefinition)
    if m:
        result = reAltenativePaths.split(pathdefinition)
        result = [x for x in result if x and not x.startswith("|")]
        for pathdef in cross_loop_alternatives(*result):
            yield ''.join(pathdef)
    else:
        # no alternatives, simply yield the pathdefinition:
        yield pathdefinition

def getValidPath(variablePathDefinition):
    """check the different alternatives of the definition
    
    return the first valid path, None if not found
    """
    for p in loop_through_alternative_paths(variablePathDefinition):
        if os.path.exists(p):
            return path(p)

_ancestor = pathlib.WindowsPath if  os.name == 'nt' else pathlib.PosixPath
class path(_ancestor):
    """helper class for path functions, based on Path

    p.isdir (also p.is_dir), p.isfile (also p.is_file), p.exists, 
    p.split (in dirpart, filepart),  p.splitext (trunk, extension), but now better use p.suffix, p.name, p.
    
    p.splitall (dirpart, trunk, ext) ??
    
    p.isabs (absolute path, p.is_absolute), p.mtime (modification time),
    
    p.basename (filepart without directory),
    
    p.normpath, is now also
    p.remove, p.rename,
    p.rmtree (folder), p.mkdir,  p.copy, p.touch,
    p.chdir, p.getcwd (changing and getting the working directory),
    p.glob(pattern="*", keepAbs=1, makePath=1)
    p.listdir(makePath=0) (giving all files in folder p)
    p.walk(functionToDo, keepAbs=1, makePath=0)
    p.internetformat, p.unix (for internet filenames)
    p.encodePath, p.decodePath: file (dir)  (for gui)


# automatically try getValidPath if ( and ) are found:
###>>> p = path("(C:|D:)") # without a slash the working directory is given (Windows convention)

###>>> path('.') # fails

>>> p = path("(C:|D:)/")
>>> p
path('C:/')
>>> p.isdrive()
True
>>> p.isdir()     # equivalent to is_dir
True
>>> p.isfile()    # equivalent to is_file
False
>>> p.exists()
True

>>> x = path("X:") 
>>> x.exists()
False
>>> x.isdrive()
False

## PurePaths, non existing files:
>>> root = path("C:/")
>>> file = root/'subfolder'/'subsub'/'trunc.txt'
>>> str(file)
'C:/subfolder/subsub/trunc.txt'
>>> repr(file)
"path('C:/subfolder/subsub/trunc.txt')"

## split methods:
>>> file.split()
(path('C:/subfolder/subsub'), 'trunc.txt')
>>> file.splitall()
['C:', 'subfolder', 'subsub', 'trunc.txt']
>>> file.splitdirtrunkext()
(path('C:/subfolder/subsub'), 'trunc', '.txt')
>>> file.splitdirslisttrunkext()
(['C:', 'subfolder', 'subsub'], 'trunc', '.txt')

## properties:
>>> file.name
'trunc.txt'
>>> file.suffix
'.txt'
>>> file.stem
'trunc'

## parent property is ok, parents property is not fully implemented:
>>> file.parent
path('C:/subfolder/subsub')
>>> file.parents[0]
path('C:/subfolder/subsub')
>>> file.parents[1]
path('C:/subfolder')
>>> file.parents[2]
path('C:/')

>>> file.parts
('C:\\\\', 'subfolder', 'subsub', 'trunc.txt')
>>> file.anchor
'C:\\\\'
>>> file.drive
'C:'

>>> folder = path('folder')
>>> folder
path('folder')
>>> subfolder = folder/'subfolder/trunc.txt'
>>> subfolder
path('folder/subfolder/trunc.txt')

>>> joinedfolder = folder.joinpath('joinedfolder', 'another', 'file.jpg')
>>> repr(joinedfolder)
"path('folder/joinedfolder/another/file.jpg')"

### old, now user suffix!
>>> file.splitext()
('C:/subfolder/subsub/trunc', '.txt')
>>> file.suffix
'.txt'


    """
    _flavour = pathlib._windows_flavour if os.name == 'nt' else pathlib._posix_flavour
    # if _flavour.sep == "\\" and _flavour.altsep == "/":
    #     _flavour.sep, _flavour.altsep = "/", "\\"

    def __new__(cls, *args, **kwargs):
        """this is the constructor for a new instance!

### construct from list:
>>> str(path(['C:', 'projects']))
'C:/Projects'

small cases:
# >>> workingdirectory = os.getcwd()
# >>> path('.') == workingdirectory
# True
# >>> path('') == workingdirectory
# False
# >>> path('/')
# path('/')
# >>> path('../..')
# path('../..')
# >>> path('../../')
# path('../..')
# >>> p = path('C:/windows/../nonexistingdir/acties')
# >>> str(p)
# 'C:/nonexistingdir/acties'
# >>> q = p/".."
# >>> q
# path('C:/nonexistingdir')
# >>> p.is_dir()
# False

## "~" is in Windows the Documents directory:
>>> hometrick = path("~/.ssh/id_rsa.pub")
>>> str(hometrick)
'C:/Users/Gebruiker/Documents/.ssh/id_rsa.pub'
>>> hometrick.isfile()
True
>>> docsdir = hometrick/".."/".."
>>> docsdir
path('~')
>>> str(docsdir)
'C:/Users/Gebruiker/Documents'
>>> print(docsdir)
C:/Users/Gebruiker/Documents

# >>> hometrick.prefix
# '~'
# >>> hometrick.resolvedprefix
# 'C:/Users/Gebruiker/Documents'
# 
# ## If ".." in path after "~", no prefix is preserved, but the absolute path is returned all-right:
# >>> dropboxtrick = path("~/../Dropbox")
# >>> str(dropboxtrick)
# 'C:/Users/Gebruiker/Dropbox'
# >>> dropboxtrick.isdir()
# True
# >>> dropboxtrick.prefix
# ''
# >>> dropboxtrick.resolvedprefix
# ''

# ## working directory trick:
# >>> wdtrick = path(".")
# >>> wdtrick
# path('C:/projects/core')
# >>> wdtrick.isdir()
# True
# >>> wdtrick.prefix
# '.'
# >>> wdtrick.resolvedprefix
# 'C:/projects/core'
# 
# 
# ## subdirectory of working directory
# >>> wdtrick = path("./subdir")
# >>> wdtrick
# path('C:/projects/core/subdir')
# >>> wdtrick.isdir()
# False
# >>> wdtrick.prefix
# '.'
# >>> wdtrick.resolvedprefix
# 'C:/projects/core'
# 
# ## subdirectory of working directory but going up with ".."
# ## prefix and resolvedprefix are empty strings...
# >>> wdtrick = path("./../miscqh")
# >>> wdtrick
# path('C:/projects/miscqh')
# >>> wdtrick.isdir()
# True
# >>> wdtrick.prefix
# ''
# >>> wdtrick.resolvedprefix
# ''




## without slashes the working directory is taken in Windows:
>>> workingdirectory = os.getcwd()
>>> path('C:') == workingdirectory
True
>>> p = path("./../faunabescherming")

# # >>> str(p)
# # 'C:/NatlinkGIT/Natlink/MacroSystem/faunabescherming'

        """
        self = object.__new__(cls)
        self.prefix = self.resolvedprefix = ""
        if args and len(args) == 1 and type(args[0]) == cls:
            return args[0]
        if args and args[0] is None:
            Input = ""
        if type(args[0]) == list:
            args = ('/'.join(args[0]),)
        if args == (None,):    # vreemde fout bij HTMLgen BGsound
            Input = ""
        else:            
            Input = '/'.join(args)
        if Input.find("|") >= 0:
            validPath = getValidPath(Input)
            if validPath:
                return validPath
        drv, root, parts = self._parse_args(args)
        self._drv = drv
            
            
        # self._root = '/' if root == '\\' else root
        # if drv:
        #     self._parts = [parts[0]]
        #     self._parts.append('\\'.join(parts[1:]))
        # else:
        #     self._parts = [('\\'.join(parts))]
        # for Path objects, (init == True)
        self._parts = parts
        self._root = root
        if 'prefix' in kwargs:
            self.prefix = kwargs['prefix']
        if 'resolvedprefix' in kwargs:
            self.resolvedprefix = kwargs['resolvedprefix']

        self._init()
        if drv:
            isready = (win32file.GetLogicalDrives() >> (ord(drv[0].upper()) - 65) & 1) != 0
            if isready:
                try:
                    resolve = self.resolve()
                    # resolve.prefix = self.prefix  ## this is done in resolve itself
                    # resolve.resolvedprefix = self.resolvedprefix
                    return resolve
                except PermissionError:
                    pass
            # with a drive, but not resolved:
            return self
        # relative path:
        if not Input:
            # empty Input, return empty path (relative)
            return self
            # emptypath = self.resolve()
            # return emptypath
        # relative, but not office temporary file:
        if Input == "~":
            homedir = self.expanduser()
            homedir.prefix = "~"
            homedir.resolvedprefix = str(homedir)
            return homedir
        elif Input.startswith("~") and not Input.startswith("~$"):
            expanded = path(self.expanduser().normpath())
            homedir = str(path("~"))
            if str(expanded).startswith(str(homedir)):
                expanded.prefix = "~"
                expanded.resolvedprefix = homedir
            else:
                expanded.prefix = expanded.resolvedprefix = ""
            return expanded
        elif Input == ".":
            curdir = path(os.getcwd())
            curdir.prefix = "."
            curdir.resolvedprefix = str(curdir)
            return curdir
        elif Input.startswith(".") and Input[1] in "/\\":
            curdir = path(".")
            expanded = path(curdir/Input[2:])
            expanded = path(expanded.normpath())
            if str(expanded).startswith(str(curdir)):
                expanded.prefix = "."
                expanded.resolvedprefix = str(curdir)
            else:
                expanded.prefix = expanded.resolvedprefix = ""
            return expanded
        elif reEnv.match(Input):
            ## here use the extended trick of the folder environment variable,
            ## enhanced with extended Library Folders (also Dropbox)
            if not recentEnv:
                recentEnv.update(getAllFolderEnvironmentVariables())
                try:
                    from natlinkcore import natlinkstatus
                    recentEnv.update(natlinkstatus.AddNatlinkEnvironmentVariables())
                except ModuleNotFoundError:
                    pass
                if not recentEnv:
                    print("path %s, cannot expand Input, no recentEnv dict"% recentEnv)
            
            m = reEnv.match(Input)
            envVar = m.group(2)   # a riddle to me!!
            envVarComplete = m.group(1)  # with %xxxx%
            lenEnvVarComplete = len(envVarComplete)
            if envVar in recentEnv:
                result = recentEnv[envVar]
            else:
                result = getFolderFromLibraryName(envVar)
                if not result:
                    print("Could not expand  %%%s%% in %s"% (envVar, Input))
                    return self
            result = path(result)
            rest = Input[lenEnvVarComplete+1:]
            expanded = result/rest
            # expanded = path(expanded).normpath()
            if str(expanded).startswith(str(result)):
                expanded.prefix = envVarComplete
                expanded.resolvedprefix = str(result)
            else:
                expanded.prefix = expanded.resolvedprefix = ""
            return expanded
        else:
            pass
        
        # all other cases:
        return self

    def resolve(self):
        """Empty string should not resolve to working directory
        
        Really, the resolve step is done in initiatlisation, and is unneeded (and unwanted) as additional call
        
        By default of pathlib, other relative paths remain unchanged, but the empty string resolves to wd by default.
        This is overridden here at initialisation time of this class.
        
>>> p = path("")
>>> p.resolve()
path('')
>>> p = path("relative")
>>> p.resolve()
path('relative')
>>> p = path("C:/temp")
>>> p.resolve()
path('C:/temp')
        """
        if str(self) == "":
            return self
        resolved = _ancestor.resolve(self)
        resolved.prefix = self.prefix
        resolved.resolvedprefix = self.resolvedprefix
        return resolved
        

    # @classmethod
    # def _from_parsed_parts(cls, drv, root, parts, init=True):
    #     self = object.__new__(cls)
    #     self._drv = drv
    #     self._root = '/' if root == '\\' else root
    #     if drv:
    #         self._parts = [parts[0]]
    #         self._parts.append('/'.join(parts[1:]))
    #     else:
    #         self._parts = [('/'.join(parts[1:]))]
    # 
    #     
    #     if init:
    #         self._init()
    #     return self

    def __truediv__(self, key):
        """also a list can be passed after the /
>>> p = path('')
>>> p.resolve()
path('')
>>> q = p/'testaap'
>>> q
path('testaap')
>>> r = q/'..'/'testmonkey'
>>> r
path('testmonkey')
        
        make an extra call to path, in order to always return a normpathed instance...
        """
        if type(key) in (list, tuple):
            key = '/'.join(key)
        child = self._make_child((key,))
        if child.drive:
            pass
        else:
            ## resolve '..' here immediately:
            ## note: if relative path resolves to '', we want an empty path, not the current directory:
            normalised_path = os.path.normpath(str(child))
            if normalised_path == os.path.normpath(''):
                child = path('')
            else:
                child = path(normalised_path)
        
        child.prefix = self.prefix
        child.resolvedprefix = self.resolvedprefix
        return child

    def __eq__(self, other):
        """compare paths
>>> start = path('foo/bar')
>>> next = 'Foo\\Bar' # windows!
>>> print(start == next)
True
        """
        if not isinstance(other, self.__class__):
            other = path(other)
        return super().__eq__(other)
    
    def __str__(self):
        """Return the string representation of the path, empty if Input was empty"""
        try:
            result = self._str
        except AttributeError:
            result  = self._format_parsed_parts(self._drv, self._root,
                                                  self._parts)
        if result.find('..') > 0 and self.drive:
            result = os.path.normpath(result)
        resultslash = result.replace("\\", "/")
        return resultslash
  
    def __repr__(self):
        short = self.nicestr()
        return "path('%s')"% short
    
    
    def __len__(self):
        return len(str(self))

    def __getitem__(self, i):
        return str(self)[i]

    def nicestr(self):
        """give return the shorthands in the path
>>> p = path("~")
>>> str(p)
'C:/Users/Gebruiker/Documents'
>>> p.nicestr()
'~'

        """
        s = str(self)
        try:
            if self.prefix and self.resolvedprefix:
                if s.startswith(self.resolvedprefix):
                    s = s.replace(self.resolvedprefix, self.prefix)
        except AttributeError:
            ## when calling internal functions, this might go wrong
            ## for example when calling parents().
            ## the .parent property is allright
            pass
            # print("problem with nicestr: %s"% s)
        return s


## make methods and properties match with prefix and resolvedprefix
##
    def joinpath(self, *kw):
        """overload to pathlib, and insert prefix and resolvedprefix
        
        """
        joined = _ancestor.joinpath(self, *kw)
        joined.prefix = self.prefix
        joined.resolvedprefix = self.resolvedprefix
        return joined

    @property
    def parent(self):
        """The logical parent of the path."""
        drv = self._drv
        root = self._root
        parts = self._parts
        if len(parts) == 1 and (drv or root):
            return self
        P = self._from_parsed_parts(drv, root, parts[:-1])
        P.prefix, P.resolvedprefix = self.prefix, self.resolvedprefix
        return P

    ## this one is too deep for me to tackle:
    # @property
    # def parents(self):
    #     """A sequence of this path's logical parents."""
    #     PP = pathlib._PathParents(self)
    #     return PP
        

    ## str operations on path:  
    def find(self, searchstring):
        """treat as string"""
        if isinstance(searchstring, self.__class__):
            searchstring = str(searchstring)
        return str(self).find(str(searchstring))
    
    def endswith(self, searchstring):
        """treat as string"""
        if isinstance(searchstring, self.__class__):
            searchstring = str(searchstring)
        return str(self).endswith(searchstring)

    def startswith(self, searchstring):
        """treat as string"""
        if isinstance(searchstring, self.__class__):
            searchstring = str(searchstring)
        return str(self).startswith(searchstring)
    
    def strip(self):
        """treat as a string"""
        return str(self).strip()
    def lower(self):
        """returns a string"""
        return str(self).lower()
    def upper(self):
        """returns a string"""
        return str(self).upper()

    def __add__(self, other):
        """implement addition
        """
        return path(str(self)+str(other), prefix=self.prefix, resolvedprefix=self.resolvedprefix)

    def __radd__(self, other):
        """implement right addition
        
        can happen if start with a relative path and add "." or drive in front of it.
        see unittest
        """
        start = path(other)
        return path(str(other) + str(self), prefix=start.prefix, resolvedprefix=start.resolvedprefix)
   
    def strdefaultstyle(self):
        """return the string with backslashes in windows,
        
        As path adopts forward slashes by default, in some cases this method can be useful,
        """
        return super().__str__()
        
   
    @classmethod
    def getValidDirectory(cls):
        """return an instance with the first valid directory and the rest going steps back
        
        a two length tuple (valid, rest) is returned.
        if the directory is valid, the rest is ""
        now converted into an automatic part of the construct!
### needs elaboration (TODOQH)
###         
### >>> path(testdrive)
### ('C:/natlink/natlink/pytest/testutilsqh', '')
### >>> path(testdrive + r"/a/bcd.txt").getValidDirectory()
### ('C:/natlink/natlink/pytest/testutilsqh', 'a/bcd.txt')
### 
### # this one needs attention!!!  also see below:
### >>> path("(C:|D:)/aba/cada/bra").getValidDirectory()
### ('', 'D:/aba/cada/bra')
### 
### ## does not take C: drive here, but the "fall off" of the possibilities:
### >>> path("(C|D):/testfile with (19) brackets.jpg").getValidDirectory()
### ('', 'D:/testfile with (19) brackets.jpg')
### 
### >>> path("testfile with (19) brackets.jpg").getValidDirectory()
### ('', 'testfile with (19) brackets.jpg')
### 
        """
        if self.isdir():
            return self, ""
        parts = self.splitall()
        popped = []
        while parts:
            popped.insert(0, parts.pop())
            newdir = '\\'.join(parts)
            if os.path.isdir(newdir):
                return path(newdir), "\\".join(popped)
            else:
                validP = getValidPath(newdir)
                if validP:
                    return validP, "\\".join(popped)
                
        return path(""), "\\".join(popped)

    def isdir(self):
        """wrapper for os.path functions"""
        return self.is_dir()

    def isdrive(self):
        """test if letter is a valid drive"""
        return os.path.isdir(str(self)[0]+":/")
    
    # def exists(self):
    #     """wrapper for os.path functions"""
    #     return os.path.exists(self)
    def isfile(self):
        """wrapper for os.path functions"""
        # return os.path.isfile(self)
        return self.is_file()

    def isabs(self):
        """wrapper for os.path functions"""
        return os.path.isabs(self)
    
    def split(self):
        """wrapper for os.path.split, returns path(first) and second
        """
        s = os.path.split(str(self))
        return path(s[0]), s[1]
    
    def splitdirslisttrunkext(self):
        """split into a list of directory parts, the file trunk and the file extension>>> startpath = "C:/this/is/a/test/file.txt)"
>>> startpath = "C:/this/is/a/test/file.txt"
>>> path(startpath).splitdirslisttrunkext()
(['C:', 'this', 'is', 'a', 'test'], 'file', '.txt')
        
        """
        L = self.splitall()
        if not L:
            return [], "", ""
        if len(L) == 1:
            trunk, ext = os.path.splitext(L[0])
            return [], trunk, ext
        else:
            trunk, ext = os.path.splitext(L[-1])
            return L[:-1], trunk, ext


    def splitdirtrunkext(self):
        """split into directory part, the file trunk and the file extension
>>> startpath = "C:/this/is/a/test/file.txt)"
>>> path(startpath).splitdirtrunkext()
(path('C:/this/is/a/test'), 'file', '.txt)')
>>> path('abstract.txt').splitdirtrunkext()
('', 'abstract', '.txt')
        """
        L = self.splitall()
        if not L:
            return "", "", ""
        if len(L) == 1:
            trunk, ext = os.path.splitext(L[0])
            return "", trunk, ext
        else:
            trunk, ext = os.path.splitext(L[-1])
            return path(L[:-1]), trunk, ext
            
    def splitext(self):
        return os.path.splitext(str(self))

    
    def splitall(self):
        """return list of all parts
>>> startpath = "C:/this/is/a/test/file.txt)"
>>> List = path(startpath).splitall()
>>> List
['C:', 'this', 'is', 'a', 'test', 'file.txt)']

# the list can be used as a constructor for the path again:
>>> pathagain = path(List)
>>> pathagain
path('C:/this/is/a/test/file.txt)')

>>> startpath == pathagain
True
        """
        L = str(self).split('/')
        return L
    
    def basename(self):
        """gives basename, identical to property "name"

>>> p = path("C:/dropbox/19.jpg")
>>> p.basename()
'19.jpg'
>>> p.name
'19.jpg'
        """
        return self.name

    def mtime(self):
        """give last modified time of path
        (doctest, see touch)
        """
        if self.exists():
            return self.stat().st_mtime
        else:
            return 0

    def mtimestr(self, format=None):
        """give last modified time of path in date format
        
        pass in a format if you want different from '%Y-%m-%d-%H:%M'
        
        (doctest, see touch)
        """
        if format is None:
            format = '%Y-%m-%d-%H:%M'
        if self.exists():
            t = self.stat().st_mtime
            t_str = datetime.datetime.fromtimestamp(t).strftime(format)
            return t_str
        else:
            return 'file does not exist'

    def relpath(self, startPath):
        """get relative path, starting with startPath
        
        compare with utilsqh/relpathdirs and relpathfiles
        TODOQH
                
>>> testpath = path("(C|D):/projects/unittest")
>>> startpath = path("(C|D):/projects")
>>> testpath.relpath("C:\projects")
'unittest'


# >>> testpath.relpath(startpath)
# 'unittest'

        """
        if not isinstance(startPath, self.__class__):
            startPath = path(startPath)
        startString, selfString =str(startPath), str(self)
        lenStart = len(startString) + 1 # 1 for the / or \
        if selfString.startswith(startString):
            return selfString[lenStart:]
        else:
            return self

    def relpathto(self, newPath):
        """get relative path of newPath, truncating self
        
        see above, TODOQH
        
>>> testpath = path("(C|D):/projects/unittest")
>>> startpath = path("(C|D):/projects")
>>> startpath.relpathto(testpath)
'unittest'
>>> testpath.relpathto(startpath)
'C:/Projects'
>>> startpath.relpathto(u"F:/projects/unexisting")
'F:/projects/unexisting'

        """
        if not isinstance(newPath, self.__class__):
            newPath = path(newPath)
        startString, newString =str(self), str(newPath)
        lenStart = len(startString) + 1 # 1 for the / or \
        if newString.startswith(startString):
            return newString[lenStart:]
        else:
            return newString

    def normpath(self):
        """ return normalised path as string
>>> print(path("c:\\Windows/system/../SPEECH/engines").normpath())
C:\Windows\Speech\Engines

        """
        return os.path.normpath(str(self))

    def normcase(self):
        """ return normalised and normalised cased path as str

>>> print(path("c:\\Windows/system/../SPEECH/").normcase())
c:\windows\speech

        """
        return os.path.normcase(str(self))


    def remove(self):
        """removal of file
    
        ??
        """
        if self.isfile():
            os.remove(str(self))
        elif self.exists():
            raise PathError('remove only for files, not for: %s'% (self))

    def rename(self, other):
        """rename
        """
        os.rename(str(self), str(other))
    
    def rmtree(self, ignore=None):
        """remove whole folder tree
        possibly ignoring items from a list ([".svn"]) as folder names

        """
        if self.isdir():
            if ignore:
                for f in self.listdir():
                    f2 = self/f
                    if f2.isdir():
                        if f in ignore:
                            continue
                        else:
                            f2.rmtree(ignore=ignore)
                    else:
                        f2.remove()
            else:
                strself = str(self)
                try:
                    shutil.rmtree(str(self))
                except:
                    import traceback
                    print('rmtree failed: %s'% strself)
                    traceback.print_exc()
                    
        elif self.exists():
            raise PathError('rmtree only for folders, not for: %s'% (self))
        else:
            raise PathError('output folder does not exist: %s'% (self))



    def mkdir(self, newpath=None):
        """make new folder, only if it does not exist yet
    
        """
        if newpath:
            New = self/newpath
        else:
            New = self
        _ancestor.mkdir(New)
        return New
    

    def copy(self, out):
        """copy file"""
        if self.isfile():
            try:
                shutil.copy2(str(self), str(out))
            except OSError:
                raise PathError('cannot copy file %s to %s' % (self, out))
        elif self.isdir():
            if path(out).isdir():
                try:
                    shutil.rmtree(str(out))
                except OSError:
                    raise PathError('cannot remove previous dir: %s' % out)
            try:
                shutil.copytree(str(self), str(out))
            except OSError:
                raise PathError('cannot copy folder %s to %s' % (self, out))
            
    def move(self, out):
        """move file"""
        if self.isfile():
            if path(out).isdir():
                try:
                    shutil.move(str(self), str(out))
                except OSError:
                    raise PathError('cannot move file %s to %s' % (self, out))
            elif path(out).exists():
                raise PathError('cannot move file %s to %s, not a directory' % (self, out))
            else:
                try:
                    shutil.move(str(self), str(out))
                except OSError:
                    raise PathError('cannot move file %s to %s' % (self, out))
        elif not self.exists():
            raise PathError('sourcefile of move does not exist: %s'% self)
                
        elif self.isdir():
            raise PathError('move not implemented for source directories')
        else:
            raise PathError('move not implemented for else clause')
            

    def copywithoutsvn(self, outPath):
        """copy file, leave svn intact"""
        outPath = path(outPath)
        if outPath.isdir():
            outPath.rmtree(ignore=[".svn"])
        else:
            outPath.mkdir()

        allFiles = self.listdir()
        for f in allFiles:
            if (self/f).isdir():
                if f == '.svn':
                    continue
                subdir = self/f
                subOut = outPath/f
                subdir.copywithoutsvn(subOut)
            else:
                (self/f).copy(outPath/f)

    def touch(self, mode=0o666, exist_ok=True):
        """create file or touch file.
        
        Directories are not created...
        
        >>> p = path('C:/projects/unittest/aaa.txt')
        >>> p.touch()
        touch, C:/Projects/unittest/aaa.txt created
        >>> p.isfile()
        True
        >>> first = p.mtime()
        >>> now = datetime.datetime.now()
        >>> nowstr = f'{now:%Y-%m-%d-%H:%M}'
        >>> p.mtimestr() == nowstr
        True
        >>> print(f'touched right now: {time.time() - first:.1f}')
        touched right now: 0.0
        >>> time.sleep(1)
        >>> p.touch()
        touch, touched C:/Projects/unittest/aaa.txt, previous mtime was 1 seconds ago
        >>> second = p.mtime()
        >>> print(f'{second - first:.0f}')
        1
        >>> p.remove()
        >>> p.isfile()
        False
        >>> p.mtime()
        0
        >>> p.mtimestr()
        'file does not exist'
        """
        if self.exists():
            if self.isfile():
                t_before = self.mtime()
                super().touch(mode=mode, exist_ok=True)
                t_after = self.mtime()
                diff = t_after - t_before
                if diff:
                    print(f'touch, touched {self}, previous mtime was {diff:.0f} seconds ago')
                else:
                    print(f'touch did not work: {self}')
            else:
                print(f'pathqh, no touch for directory: {self}')
        else:
            super().touch(mode=mode, exist_ok=False)
            # t = self.mtime()
            print(f'touch, {self} created')
            
    def chdir(self):
        """change directory

        """
        os.chdir(str(self))

    def getcwd(self):
        """get working directory
    
        """
        return path(os.getcwd())

    def glob(self, pattern="*", makePath=1, keepAbs=0):
        """glob a path, default = "*"

        default options: give absolute paths as path instances
        See also walk...
        
        You can also use listdir if you want all files relative to the path,
        but glob without a pattern (or "*") will give the same.
        
>>> path("C:/Windows/Speech/Common/").glob("*")
[path('C:/Windows/Speech/Common/en-US'), path('C:/Windows/Speech/Common/sapisvr.exe')]

>>> path("C:/Windows/Speech").glob("*.dll", makePath=0)
['spchtel.dll', 'speech.dll', 'vcmshl.dll', 'Vdict.dll', 'VText.dll', 'WrapSAPI.dll', 'Xcommand.dll', 'Xlisten.dll', 'XTel.Dll', 'Xvoice.dll']

>>> path("C:/Windows/Speech").glob("*.dll", makePath=0)
['spchtel.dll', 'speech.dll', 'vcmshl.dll', 'Vdict.dll', 'VText.dll', 'WrapSAPI.dll', 'Xcommand.dll', 'Xlisten.dll', 'XTel.Dll', 'Xvoice.dll']

## note glob is case insensitive (see walk for case sensitive patterns)
>>> path("C:/Windows/Speech").glob("V*.dll", makePath=0, keepAbs=1)
['C:/Windows/Speech/vcmshl.dll', 'C:/Windows/Speech/Vdict.dll', 'C:/Windows/Speech/VText.dll']

        """
        if not self.isdir():
            raise PathError("glob must start with folder, not with: %s"% self)
        globpat = "%s/%s"% (self, pattern)
        L = glob.glob(globpat)
        if makePath:
            return [path(f) for f in L]
        else:
            if keepAbs:
                return [f.replace("\\", "/") for f in L]
            else:
                return [self._makePathRelative(item) for item in L]

    def listdir(self):
        """give list of directory relative to self
        
        listdir only gives a list of relative files and directories.
        
        If you want makePath or keepAbs, use glob without pattern (or "*")
        
        
>>> path("C:/Windows/Speech/Common/").listdir()
['en-US', 'sapisvr.exe']

        """
        if not self.isdir():
            raise PathError("listdir only works on folders, not with: %s"% self)
        L = os.listdir(self)
        return L


    def walk(self, *functionToDo, includeDirs=None, skipDirs=None,  includeFiles=None, skipFiles=None, makePath=1, keepAbs=0, topdown=True, onerror=None, followlinks=False):
        """return the complete walk
        
        Nearly obsolete, but if functionToDO is a valid function, this one is called for each file/dir combination
                functionToDo is the old fashioned function with arg as list being filled in the process.
                    assume arg is a list,
                    functionToDo must use exactly 3 parameters,
                    1 list "arg"
                    2 dirname
                    3 list of filenames
        
        A list of valid path instances, absolute path's (str), relative path's (str)
        is yielded, according to makePath and keepAbs variables.
        
        a complete path instance is the default (makePath == 1).
        if makePath == 0, the default is a str giving the path relative to self.
        
        When you specify makePath=0, keepAbs=1, absobulte paths as str's are yielded.

        *** Drop the previous "functionToDo" function. ***

        includeDirs, skipDirs, includeFiles, skipFiles can be a str or a sequence of str's.
        
        Each pattern is matched against the Dir part or File name, with the fnmatch function (same behaviour as the glob.glob function).
        
        So for example "*.txt" if different from "*". "*.*" is needed for matching all files.
        
        If all letters are lowercase, the comparisons are done caseInsensitive (Windows!).
        But if capitals are used, case sensitive matching is done by fnmatch
                
        First includeDirs is checked, then skipDirs, then for each file includeFiles and then skipFiles.
        *** see _acceptDirectoryWalk and _acceptFileWalk below for doctest examples ***


## example of the "old fashioned" function to be called...
>>> print(list(path("C:/Windows/Speech/Common").walk(WalkAllFiles)))
[path('C:/Windows/Speech/Common/sapisvr.exe'), path('C:/Windows/Speech/Common/en-US/sapisvr.exe.mui')]


>>> list(path("C:/Windows/Speech").walk(includeFiles="*.exe", makePath=0))
['vcmd.exe', 'Common/sapisvr.exe']

>>> list(path("C:/Windows/Speech").walk(includeFiles=["x*.dll", "*.exe"], includeDirs="Common"))
[path('C:/Windows/Speech/Common/sapisvr.exe')]

        ====
        Recaoitulate, the optional parameters:
        includeDirs, skipDirs, includeFiles, skipFiles: see above
        
        makePath, keepAbs, see above.
        
        topdown, onerror and followlinks, the optional parameters of os.walk.
      
        See testing in unittestPath.py and two examples above...

        """
        arg = []
        if not self.isdir():
            raise PathError("walk must start with folder, not with: %s"% self)
        # if functionToDo:
        #     arg = []
        #     for directory, subdirs, files in os.walk(str(self)):
        #         print("functionToDo: %s"% functionToDo)
        #         functionToDo(arg, directory, files)
        #     return arg
        
        
        for directory, subdirs, files in os.walk(str(self)):
            if _acceptDirectoryWalk(directory, includeDirs, skipDirs):
                reducedFiles = [f for f in files if _acceptFileWalk(f, includeFiles, skipFiles)]
                if reducedFiles:
                    if makePath:
                        directory = path(directory)
                        FilesListed = [directory/f for f in reducedFiles]
                    else:
                        FilesListed = [os.path.normpath(os.path.join(directory, f)) for f in reducedFiles]
                        FilesListed = [item.replace("\\", "/") for item in FilesListed]
                        if not keepAbs:
                            lenOrg = len(self)
                            strOrg = str(self)
                            FilesListed = [self._makePathRelative(item) for item in FilesListed]
                    for item in FilesListed:
                        yield item

    def removeEmptyFolders(self, debug=0):
        """a special walk, which iterates through empty folders

The calling folder remains, even if all subfolders are removed

See unittestPath for more testing and examples.
        """
        round = 0
        while True:
            round += 1
            hadChange = False
            if debug > 1: print("removeEmptyFolders, round %s"% round)
            # print("removeEmptyFolders, new round;;;;")
            for directory, dirs, files in os.walk(self, topdown=False):
                if self == directory:
                    continue
                # print("removeEmptyFolders: %s"% self._makePathRelative(directory))
                if dirs or files:
                    continue
                # now empty directory, remove:
                hadChange = True
                if debug: print("removeEmptyFolders: remove: %s"% self._makePathRelative(directory))
                path(directory).rmdir()
            if not hadChange:
                if debug > 1: print("removeEmptyFolders, no change in round %s"% round)
                break

        if debug > 1: print("removeEmptyFolders: ready in %s rounds"% round)
        pass
    
    
    def _makePathRelative(self, item):
        """helper function returning the path relative to self (the originating path)
        tested, in unittestPath.py
>>> path("C:/System/")._makePathRelative("C:/System/Control")
'Control'

Never needed, hopefully:
>>> path("C:/System/")._makePathRelative("C:/OtherSystem/Control")
'C:/OtherSystem/Control'
        
        """
        if not item:
            return ""
            # make relative:
        length = len(self)
        strPath = str(self)
        if not self.endswith("/"):
            length += 1
        if item.startswith(strPath):
            return item[length:]
        else:
            return item

    def internetformat(self):
        """convert to file:/// and fill with %20 etc
>>> p =  path("C:/a/b.html").internetformat()
>>> p = path("C:/with space/a and b.html").internetformat()
>>> print(p)
file:///C:/with%20space/a%20and%20b.html
>>> q = (path("C:/a")/"bc.html").internetformat()
>>> print(q)
file:///C:/a/bc.html
>>> type(q)
<class 'str'>

        see testing in testPath

        """
        return self.as_uri()
    
        if self.startswith("file:///"):
            return str(self)
        elif len(self) > 2 and self[1:3] == ":/":
            start, rest = self[0], self[3:]
            return 'file:///'+start.upper() + ":/" + self._quote_rest(rest)
        elif self.startswith("file:/") and len(self) > 9:
            start, letter, colonslash, rest = self[:5], self[6], self[7:9], self[9:]
            if str(letter).isalpha() and colonslash == ':/':
                return 'file:///' + letter.upper() + colonslash + self._quote_rest(rest)
            else:
                return str(self)
        else:
            return self._quote_rest(str(self))
        
    def _quote_rest(self, restofurl):
        """for internetformat above"""
        
        restList = restofurl.split("/")
        quotedList = list(map(urllib.parse.quote, restList))
        return "/".join(quotedList)

    def unix(self, glueChar="", lowercase=1, canHaveExtension=1, canHaveFolders=1):
        """convert to unixlike name

        no leading - or 0-9, put a _ in front
        no other characters than [a-zA-Z0-9_] allowed

        with lowercase = 0 uppercase is preserved. (Default = 1,
                           convert all to lowercase

        if there are folders (and canHaveFolders=1), the folder parts are always
        converted with canHaveExtension=0

        the extension is always converted to lowercase.
        also see toUnixName above.

# with e acute and a with dots acute \\ for doctest!!
>>> path('C:/fake/zzz \\u00E9U\\u00e4df').unix()
path('C:/fake/zzzeuadf')

>>> path('aap').unix()
path('aap')
>>> str(path('aap.jpg').unix())
'aap.jpg'
>>> str(path('AAP.jpg').unix())
'aap.jpg'
>>> str(path('AAP.JPG').unix(lowercase=0))      # extension is always converted
'AAP.jpg'
>>> str(path('A 800-34.jpg').unix())
'a800-34.jpg'

>>> p = path("C:/Ae\\u0301Bc/C- - +    98/A .txt").unix()

# path starting with a digit:
>>> path("C:/3d/4a.txt").unix()
path('C:/_3d/_4a.txt')

## is this needed, the _ ? (TODOQH)
>>> path("C:/-3d/-4a.txt").unix()
path('C:/_-3d/_-4a.txt')
        """
        visible = str(self)
        return path(toUnixName(str(self), glueChar=glueChar,
                               lowercase=lowercase,
                               canHaveExtension=canHaveExtension,
                               canHaveFolders=canHaveFolders))


    def replaceExt(self, ext):
        """replace extension, sometimes because of uppercase

        """
        return path(replaceExt(self, ext))

    def getExt(self):
        """return the extension (including the .) or empty string if no extension
        """
        return getExt(self)

    def hasExt(self):
        """return true if name has an extension
        """
        return getExt(self) != ""

    def encodePath(self):
        """encode to file (dir)

        used in gui inputoutput and kontrol (minimal)
>>> path("C:/Natlink/a/b.txt").encodePath()
'b.txt (C:/Natlink/a)'

## doubt if this is nice: (TODOQH)
# >>> path("b.txt").encodePath()
# 'b.txt (C:/projects/miscqh3)'

        """
        Folder, File = self.split()
        return '%s (%s)'% (File, Folder)

##    TODOQH!!! 
def decodePath(text):
    """decode to path (file or dir)
>>> 
>>> decodePath('b.txt (C:/a)')
path('C:/a/b.txt')
>>> decodePath('b.txt ()')
path('b.txt')
>>> decodePath(' (C:/)')
path('C:/')


Return a path instance
    """
    if '(' not in text:
        return str(text)

    t = str(text)
    File, Folder = t.split('(', 1)
    Folder = Folder.rstrip(')')
    Folder = Folder.strip()
    File = File.strip()
    return path(Folder)/File
    
# ##TODOQH
# def decodePathTuple(text):
#     """decode to path (file or dir) Total, Folder, File
# 
# >>> decodePathTuple('b.txt (C:/a)')
# (path('C:/a/b.txt'), path('C:/a'), path('b.txt'))
# >>> decodePathTuple('b.txt ()')
# (path('b.txt'), path('.'), path('b.txt'))
# >>> decodePathTuple(' (C:/)')
# (path('C:/'), path('C:/'), path('.'))
# 
# Return a path instance
#     """
#     if '(' not in text:
#         return str(text)
# 
#     t = str(text)
#     File, Folder = t.split('(', 1)
#     Folder = Folder.rstrip(')')
#     Folder = Folder.strip()
#     File = File.strip()
#     return path(Folder)/File, path(Folder), path(File)


# keep track of found env variables, fill, if you wish, with
# getAllFolderEnvironmentVariables.
# substitute back with substituteEnvVariableAtStart.
# and substite forward with expandEnvVariableAtStart
# in all cases a private envDict can be user, or the global dict recentEnv
#
# to collect all env variables, call getAllFolderEnvironmentVariables, see below
class EnvVariable():
    """this class resolves environment variables like HOME, DROPBOX
    
    In file specificators, they can be set as %HOME% (or ~), %DROPBOX%, etc
    
    In an instance, a cache of previous calls is maintained.
    If a call does not resolve to a folder, None is set.
    """
    def __init__(self):
        self._cache = {}
        self.fillCache()
        pass

# recentEnv = {}

    def addToCache(self, name, value):
        """to be filled for NATLINK variables from natlinkstatus
        """
        self._cache[name] = value

    def deleteFromCache(self, name):
        """to possibly delete from recentEnv, from natlinkstatus
        """
        if name in self._cache:
            del self._cache[name]

    def getFolderFromLibraryName(self, fName):
        """from windows library names extract the real folder
        
        the CabinetWClass and #32770 controls return "Documents", "Dropbox", "Desktop" etc.
        try to resolve these throug the extended env variables.
        """
        if fName.startswith("Docum"):  # Documents in Dutch and English
            return self.getExtendedEnv("PERSONAL")
        if fName in ["Muziek", "Music"]:
            return self.getExtendedEnv("MYMUSIC")
        if fName in ["Pictures", "Afbeeldingen"]:
            return self.getExtendedEnv("MYPICTURES")
        if fName in ["Videos", "Video's"]:
            return self.getExtendedEnv("MYVIDEO")
        if fName in ['OneDrive']:
            return self.getExtendedEnv("OneDrive")
        if fName in ['Desktop', "Bureaublad"]:
            return self.getExtendedEnv("DESKTOP")
        if fName == 'Dropbox':
            return getDropboxFolder()
        if fName in ['Download', 'Downloads']:
            personal = self.getExtendedEnv('PERSONAL')
            userDir = os.path.normpath(os.path.join(personal, '..'))
            if os.path.isdir(userDir):
                tryDir = os.path.normpath(os.path.join(userDir, fName))
                if os.path.isdir(tryDir):
                    return tryDir
        print('cannot find folder for Library name: %s'% fName)

    def getDropboxFolder(self, containsFolder=None):
        """get the dropbox folder, or the subfolder which is specified.
        
        Searching is done in all 'C:\\Users' folders, and in the root of "C:"
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

    def matchesStart(self, listOfDirs, checkDir, caseSensitive):
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
    
    def getExtendedEnv(self, var):
        """get from environ or windows CSLID
    
        HOME is environ['HOME'] or CSLID_PERSONAL
        ~ is HOME
    
        DROPBOX added via getDropboxFolder is this module (QH, December 1, 2018)
    
        As envDict for recent results either a private (passed in) dict is taken, or
        the global recentEnv.
    
        This is merely for "caching results"
    
        """
        if var in self._cache:
            return self._cache[var]
    ##    var = var.strip()
        var = var.strip("% ")
        var = var.upper()
        
        if var == "~":
            var = 'HOME'
    
        if var in self._cache:
            return self._cache[var]
    
        if var in os.environ:
            value = self._cache[var] = os.environ[var]
            return value
    
        if var == 'DROPBOX':
            result = getDropboxFolder()
            self._cache[var] = result            
            return result
    
        if var == 'NOTEPAD':
            windowsDir = getExtendedEnv("WINDOWS")
            notepadPath = os.path.join(windowsDir, 'notepad.exe')
            if os.path.isfile(notepadPath):
                self._cache[var] = notepadPath
                return notepadPath
            else:
                self._cache[var] = None
                return None
    
        # try to get from CSIDL system call:
        if var == 'HOME':
            var2 = 'PERSONAL'
        else:
            var2 = var
            
        try:
            CSIDL_variable =  'CSIDL_%s'% var2
            shellnumber = getattr(shellcon,CSIDL_variable, -1)
        except:
            print('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
            self._cache[var2] = None
            return None
        if shellnumber < 0:
            # on some systems have SYSTEMROOT instead of SYSTEM:
            if var == 'SYSTEM':
                result = self._cache['SYSTEMROOT']
                self._cache = result
                return result
        try:
            result = shell.SHGetFolderPath (0, shellnumber, 0, 0)
        except:
            return 
    
        
        result = str(result)
        result = os.path.normpath(result).replace('\\', '/')
        self._cache[var] = result
        # on some systems apparently:
        if var == 'SYSTEMROOT':
            result = self._cache['SYSTEM']        
        return result

    def clearCache(self):
        """for testing, clears the cache
        """
        self._cache.clear()

    def fillCache(self):
        """fill the _cache with CSIDL variables en os.environ variables.
        
        # Now also implemented:  Also include NATLINK, UNIMACRO, VOICECODE, DRAGONFLY, VOCOLAUSERDIR, UNIMACROUSERDIR
        # This is done by calling from natlinkstatus, see there and example in natlinkmain.
    
        # Optionally put them in recentEnv, if you specify fillRecentEnv to 1 (True)
        No return!
        """
        for k in dir(shellcon):
            if k.startswith("CSIDL_"):
                kStripped = k[6:]
                try:
                    v = self.getExtendedEnv(kStripped)
                except ValueError:
                    continue
                if v is None:
                    self._cache[kStripped] = v
                    continue
                if len(v) > 2 and os.path.isdir(v):
                    self._cache[kStripped] = v.replace("\\", "/")
                elif v == '.':
                    self._cache[kStripped] = os.getcwd()
        # os.environ overrules CSIDL:
        for k in os.environ:
            v = os.environ[k]
            if os.path.isdir(v):
                v = os.path.normpath(v).replace("\\", "/")
                if k in self._cache and self._cache[k] != v:
                    print('warning, CSIDL also exists for key: %s, take os.environ value: %s'% (k, v))
                self._cache[k] = v

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
    if envDict is None:
        envDict = recentEnv
    Keys = list(envDict.keys())
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
            print('invalid (extended) environment variable: %s'% envVar)
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

reUnix=re.compile(r'[^\w-]')
def toUnixName(t, glueChar="", lowercase=1, canHaveExtension=1, canHaveFolders=1, mayBeEmpty=False):
    """get rid of unwanted characters, only letters and '-'
    leading numbers get a _ in front

    this conversion of file names is used in QH's website programming a lot,
    and can also be called from path instances as .unix().
    The path class in this module uses this function.

    default: all to lowercase, if lowercase = 0: convert extension to lowercase anyway

    default: file can have extension and folders. If set to 0, also \\, / and . are removed from name.

    split into folder/file parts if needed.
    
    glueChar can be "_" or "-" as well ("_" for avp, michel)

    mayBeEmpty: by default False, can be set True (jva, auteur, isbn)

>>> toUnixName("Test ( met haakjes (en streepjes))", canHaveExtension=0, glueChar="-")
'test-met-haakjes-en-streepjes'

>>> toUnixName("Test. Met een punt", canHaveExtension=0)
'testmeteenpunt'

>>> toUnixName("Test. Met een punt", canHaveExtension=0, glueChar="_")
'test_met_een_punt'

>>> toUnixName('')
Traceback (most recent call last):
ValueError: toUnixName, name has no valid characters
>>> toUnixName('-abcd')
'_-abcd'

Unicode and diacritical characters:
>>> toUnixName('C:/abc.def/Thaddeus M\\u00fcller.html', glueChar="-")
'C:/abc-def/thaddeus-muller.html'

>>> toUnixName('niet aan elkaar', glueChar="_")
'niet_aan_elkaar'
>>> toUnixName('wel aan elkaar')
'welaanelkaar'

>>> toUnixName('a.b-99? .d')
'ab-99.d'
>>> toUnixName('a.b-99? .d', canHaveExtension=0)
'ab-99d'
>>> toUnixName('.a^.jpg')
'a.jpg'
>>> toUnixName('6-barge.txt')
'_6-barge.txt'
>>> toUnixName('-6-barge.html')
'_-6-barge.html'

>>> toUnixName('C:/abc.def/-6-barge.html')
'C:/abcdef/_-6-barge.html'

>>> toUnixName('') # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: toUnixName, name has no valid characters

>>> toUnixName('', mayBeEmpty=True)
''

    """
    if glueChar == '-':
         pass
    inputT = t
    t = t.strip()
    if t.strip() in ('', ''):
        if mayBeEmpty:
            return ''
        raise ValueError("toUnixName, name has no valid characters")
    t = os.path.normpath(t)
    t = t.replace('\\', '/')
    if canHaveFolders and t.find('/') >= 0:
        L  = []
        parts = t.split('/')
        for part in parts:
            
            if part  != parts[ - 1]:
                canHaveExtension2 = 0 # folder parts never extension
            else:
                canHaveExtension2 = canHaveExtension
            if lowercase and not (len(part) == 2 \
                               and part[-1] == ":"):
                part = part.lower()
            sofar = path('/'.join(L))/part
            if sofar.isdir():
                # prevent "website name" from being converted
                L.append(part)
                continue
            L.append(toUnixName(part,lowercase=lowercase, canHaveFolders=0, glueChar=glueChar,
                                canHaveExtension=canHaveExtension2))
        return '/'.join(L)

    if len(t) == 2 and t.endswith(":"):
        return t.upper()
    if t == "..":
        return t
    if t == ".":
        return t
    # now for the dir/file part:
    if canHaveExtension:
        trunk, ext = os.path.splitext(t)
    else:
        # also remove . and / (and \)
        trunk, ext = t, ''
    if glueChar == "_":
        trunk = fixdotslashspace(trunk) # . --> _ and / -->> _ also space to "_"
    elif glueChar == "-":
        trunk = fixdotslashspacehyphen(trunk) # . --> _ and / -->> _ also space to "-"
    elif glueChar:
        raise ValueError('toUnixName, glueChar may only be "" or "_" or "-", not "%s"'% glueChar)
    else:
        trunk = fixdotslash(trunk) # . --> _ and / -->> _
        trunk = trunk.replace(' ', '')
        
    if glueChar == '-':
        pass
    trunk = normalizeaccentedchars(trunk)
    trunk = translate_non_alphanumerics(trunk, translate_to=glueChar)
    if lowercase:
        trunk = trunk.lower()
    trunk = trunk.replace("__", "_")
    trunk = trunk.replace("_.", ".")
    
    
    if glueChar:
        doubleGlue = glueChar*2
        while trunk.find(doubleGlue) > 0:
            trunk = trunk.replace(doubleGlue, glueChar)
        trunk = trunk.rstrip(glueChar)
    pass

    # remove possible invalid chars from extension:
    if ext and ext[0] == ".":
        ext = "." + normalizeaccentedchars(ext[1:])
        ext = ext.lower()  # always to lowercase

    if not trunk:
        raise ValueError("toUnixName, name has no valid characters: |%s|"% trunk)
    if trunk[0] in '-0123456789':
        trunk = "_" + trunk
    return trunk + ext

str2unix = toUnixName


# helper string functions:
def replaceExt(fileName, ext):
    """change extension of file

>>> replaceExt("a.psd", ".jpg")
'a.jpg'
>>> replaceExt("a/b/c/d.psd", "jpg")
'a/b/c/d.jpg'
    """
    if not ext.startswith("."):
        ext = "." + ext
    fileName = str(fileName)
    a, extOld = os.path.splitext(fileName)
    return a + ext

def getExt(fileName):
    """return the extension of a file

>>> getExt(u"a.psd")
'.psd'
>>> getExt("a/b/c/d.psd")
'.psd'
>>> getExt("abcd")
''
>>> getExt("a/b/xyz")
''
    """
    a, ext = os.path.splitext(fileName)
    return str(ext)

## 
def fixdotslash(to_translate):
    """quick find and replace function
    
    used by toUnixNamefor paths, . and / to _
    """
    if not to_translate:
        return to_translate
    dotslash = './'
    translate_to = '_'
    translate_table = dict((ord(char), translate_to) for char in dotslash)
    return to_translate.translate(translate_table)




def fixdotslashspace(to_translate):
    """quick find and replace functions, used by toUnixName
    
    for paths, . and / to _, also space to _
    """
    dotslash = './ '
    translate_to = '_'
    translate_table = dict((ord(char), translate_to) for char in dotslash)
    return to_translate.translate(translate_table)

def fixdotslashspacehyphen(to_translate):
    """quick find and replace functions, used by toUnixName
    
    for paths, . and / to _, also space to "-"
    """
    dotslash = './ '
    translate_to = '-'
    translate_table = dict((ord(char), translate_to) for char in dotslash)
    return to_translate.translate(translate_table)


def normalizeaccentedchars(to_translate):
    """change acutechars to ascii 
    
>>> s1 = "cafnon\u00e9"   # single char e acute
>>> normalizeaccentedchars(s1)  
'cafnone'
>>> s2 = "CafCombe\u0301"   # combining char e acute   0301 is the combining code
>>> normalizeaccentedchars(s2)   # combining char e acute
'CafCombe'
>>> len(s1), len(s2)
(7, 9)

    (from Fluent Python)
    """
    norm_txt = unicodedata.normalize('NFD', to_translate)
    shaved = ''.join(c for c in norm_txt if not unicodedata.combining(c))
    return shaved

## unicode translator function:
def translate_non_alphanumerics(to_translate, translate_to='_'):
    """bijna alle non letters or digits to _
    
    let op - blijft gehandhaafd!!!!
    gebruik NA de split van een padnaam en evt na splitext van de extensie.
    
    """
    not_letters_or_digits = '!"#%\'()*+,./:;<=>?@[\]^_`{|}&~$'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits if char != translate_to)
    translate_table[8217] = translate_to
    translate_table[8364] = translate_to
    return to_translate.translate(translate_table)


def _acceptDirectoryWalk(Dir, includeDirs, skipDirs):
    """private function for path.walk, to accept or reject a directory

    Dir is path or str instance of a directory path.
    
    See examples that show you how to specify a wanted directory:
    
    includeDirs and skipDirs are None or pattern(s) which should or
    should not match Dir. If no slashes are in pattern, *\ and \* are added,
    so normally only one subdirectory on the path is tested...
    
    If no uppercase letters are used in a pat, do case insensitive testing.
    
    They are str of a sequence of str's (or False, if no decision has to be taken)
    
    returns True if Dir is accepted, None otherwise

>>> _acceptDirectoryWalk("C:/Windows/System/Common", "Common", None)
True

Next six examples all return True (Note all forward slashes are changed into backslashes for the fnmatch call...)

>>> _acceptDirectoryWalk(path("C:/Windows/System/Common"), "System", None)
True
>>> _acceptDirectoryWalk("C:/Windows/System/Common", "/System/", None)
True
>>> _acceptDirectoryWalk("C:/Windows/System/Common", "*\\System\\*", None)
True
>>> _acceptDirectoryWalk("C:/Windows/System/Common", "*/System/*", None)
True
>>> _acceptDirectoryWalk("C:/Windows/System/Common", "/system/", None)
True
>>> _acceptDirectoryWalk("C:/Windows/System/Common", "*s*", None)
True

Next one fails:
>>> _acceptDirectoryWalk(path("C:/Windows/System/Common"), ["*z*", "*ysta*"], None)

Now the skipDirs, the "skipDirs" variable hits, so the directory is rejected:
>>> _acceptDirectoryWalk("C:/Windows/System/Common", None, "system")

These two patterns of "skipDirs" do not hit, so the directory is accepted:
>>> _acceptDirectoryWalk("C:/Windows/System/Common", None, ["syste", "/abacadabra/"])
True
    """
    if isinstance(Dir, path):
        Dir = str(Dir)
    if includeDirs:
        if type(includeDirs) == str:
            includeDirs = [includeDirs]
        for pat in includeDirs:
            if pat == pat.lower():
                DirNorm = os.path.normcase(Dir)
            else:
                DirNorm = os.path.normpath(Dir)
            
            if not DirNorm.endswith("\\"):
                DirNorm += "\\"
            
            if pat.find("/") >= 0:
                pat = pat.replace("/", "\\")
            if pat.find("\\") == -1:
                pat = "*\\%s\\*"% pat
            elif pat.startswith("\\") and pat.endswith("\\"):
                pat = "*" + pat + "*"
            if fnmatch.fnmatch(DirNorm, pat):
                break
        else:
            return
    if skipDirs:    
        if type(skipDirs) == str:
            skipDirs = [skipDirs]
        for pat in skipDirs:
            if pat == pat.lower():
                DirNorm = os.path.normcase(Dir)
            else:
                DirNorm = os.path.normpath(Dir)
            if not DirNorm.endswith("\\"):
                DirNorm += "\\"
                
            if pat.find("/") >= 0:
                pat = pat.replace("/", "\\")
            if pat.find("\\") == -1:
                pat = "*\\%s\\*"% pat
            elif pat.startswith("\\") and pat.endswith("\\"):
                pat = "*" + pat + "*"
            if fnmatch.fnmatch(DirNorm, pat):
                # pattern matches, reject the Directory
                return
    # all tests pass:
    return True
 
def _acceptFileWalk(File, includeFiles, skipFiles):
    """helper function for _selectFilesWalk (of path.walk), to return if a name matches
    
    returns True is File is accepted

    """
    # test for includeFiles, return is test fails
    if includeFiles:
        if type(includeFiles) == str:
            includeFiles = [includeFiles]
        for pat in includeFiles:
            if fnmatch.fnmatch(File, pat):
                break
        else:
            return
    # test for skipFiles, return if test passes
    if skipFiles:    
        if type(skipFiles) == str:
            skipFiles = [skipFiles]
        for pat in skipFiles:
            if fnmatch.fnmatch(File, pat):
                return
    # now pass the tests!
    return True
    

def collectPsdFiles(arg, dir, files):
    """collect only .psd files"""
    ext = '.psd'
    for f in files:
        dirplusf = path(dir)/f
        if dirplusf.isdir():
            continue

        if dirplusf.lower().endswith(ext):
            # in case .PSD instead of .psd:
            dirplusf.replaceExt(ext)
            arg.append(dirplusf)

def WalkAllFiles(arg, dir, files):
    """touch all files in folder"""
    dir = path(dir)
    # touch(dir, files)
    for f in files:
        arg.append(dir/f)
        
        
def touchAllFiles(arg, dir, files):
    """touch all files in folder"""
    dir = path(dir)
    touch(dir, files)
    for f in files:
        arg.append(dir/f)

def collectTifFiles(arg, dir, files):
    """collect only .tif files"""
    ext = '.tif'
    for f in files:
        dirplusf = path(dir)/f
        if dirplusf.isdir():
            continue

        if dirplusf.lower().endswith(ext):
            # in case .PSD instead of .psd:
            dirplusf.replaceExt(ext)
            arg.append(dirplusf)

## for sitegen, also used in Unimacro, folders grammar (for sites, QH specific) and virtualdrive mechanism
## test! TODOQH
def getValidPath(variablePathDefinition):
    """check the different alternatives of the definition
    
    return the first valid path, None if not found
    """
    for p in loop_through_alternative_paths(variablePathDefinition):
        if os.path.exists(p):
            return path(p)

def walkZfiles(directory):
    for Dir, subdirList, filesList in os.walk(directory):
        for f in filesList:
            if f.startswith("Z") and f.endswith(".csv"):
                yield os.path.join(Dir, f)

## the %XXX% variables, to be kept in recentEnv:

def getAllFolderEnvironmentVariables():
    """return, as a dict, all the environ AND all CSLID variables that result into a folder
    
    Now also implemented:  Also include NATLINK, UNIMACRO, VOICECODE, DRAGONFLY, VOCOLAUSERDIR, UNIMACROUSERDIR
    This is done by calling from natlinkstatus, see there and example in natlinkmain.

    Optionally put them in recentEnv, if you specify fillRecentEnv to 1 (True)

    """
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
                print('warning, CSIDL also exists for key: %s, take os.environ value: %s'% (k, v))
            D[k] = v
    return D

def getExtendedEnv(var, envDict=None, displayMessage=1):
    """get from environ or windows CSLID

    HOME is environ['HOME'] or CSLID_PERSONAL
    ~ is HOME

    DROPBOX added via getDropboxFolder is this module (QH, December 1, 2018)

    As envDict for recent results either a private (passed in) dict is taken, or
    the global recentEnv.

    This is merely for "caching results"

    """
    if envDict is None:
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
        print('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
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
            print('getExtendedEnv, cannot find in environ or CSIDL: "%s"'% var2)
        return ''

    
    result = str(result)
    result = os.path.normpath(result)
    myEnvDict[var] = result
    # on some systems apparently:
    if var == 'SYSTEMROOT':

        myEnvDict['SYSTEM'] = result
    return result

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
            print('invalid (extended) environment variable: %s'% envVar)
        else:
            # OK, found:
            filepart = filepath[len(envVar)+1:]
            filepart = filepart.strip('/\\ ')
            return os.path.normpath(os.path.join(folderpart, filepart))
    # no match
    return filepath

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
    if envDict is None:
        envDict = recentEnv
    Keys = list(envDict.keys())
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


def getFolderFromLibraryName(fName):
    """from windows library names extract the real folder
    
    the CabinetWClass and #32770 controls return "Documents", "Dropbox", "Desktop" etc.
    try to resolve these throug the extended env variables.
    """
    fName = fName.lower()
    if fName.startswith("docum"):  # Documents in Dutch and English
        return getExtendedEnv("PERSONAL")
    if fName in ["muziek", "music"]:
        return getExtendedEnv("MYMUSIC")
    if fName in ["pictures", "afbeeldingen"]:
        return getExtendedEnv("MYPICTURES")
    if fName in ["videos", "video's"]:
        return getExtendedEnv("MYVIDEO")
    if fName in ['onedrive']:
        return getExtendedEnv("OneDrive")
    if fName in ['desktop', "bureaublad"]:
        return getExtendedEnv("DESKTOP")
    if fName in ['quick access', 'snelle toegang']:
        templatesfolder = getExtendedEnv('TEMPLATES')
        if os.path.isdir(templatesfolder):
            QuickAccess = os.path.normpath(os.path.join(templatesfolder, "..", "Libraries"))
            if os.path.isdir(QuickAccess):
                return QuickAccess
    if fName == 'dropbox':
        return getDropboxFolder()
    if fName in ['download', 'downloads']:
        personal = getExtendedEnv('PERSONAL')
        userDir = os.path.normpath(os.path.join(personal, '..'))
        if os.path.isdir(userDir):
            tryDir = os.path.normpath(os.path.join(userDir, fName))
            if os.path.isdir(tryDir):
                return tryDir
    usersHome = os.path.normpath(os.path.join(r"C:\Users", fName))
    if os.path.isdir(usersHome):
        return usersHome
    if fName in ["this pc", "deze pc"]:
        return "\\"
    
    print('cannot find folder for Library name: %s'% fName)

def getDropboxFolder(containsFolder=None):
    """get the dropbox folder, or the subfolder which is specified.
    
    Searching is done in all 'C:\\Users' folders, and in the root of "C:"
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


# recentEnv.update(getAllFolderEnvironmentVariables())


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    # print("is_dir: %s"% p.is_dir())
    # print("isdir: %s"% p.isdir())
    # envvars = EnvVariable()
    # printAllEnvVariables()
    # p = path("%COMMON_APPDATA%/Etta en Quintijn")
    # p = path("%DROPBOX%/Etta en Quintijn")
    # p = path('../../test/onetwo/../three')
    _test()
