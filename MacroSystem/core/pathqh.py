"""
implements the path class, based upon pathlib/path

was before in utilsqh, but better do it here.
testing inside qh for the moment
moving into the core directory of the python 3 branch
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
# for extended environment variables:
reEnv = re.compile('(%[A-Z_]+%)', re.I)

## functions for generating alternative paths in virtual drives
## uses reAltenativePaths, defined in the top of this module
## put in utilsqh.py! used in sitegen AND in _folders.py grammar of Unimacro:
# for alternatives in virtual drive definitions:
reAltenativePaths = re.compile(r"(\([^|()]+?(\|[^|()]+?)+\))")

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
    
    p.isabs (absolute path), p.mtime (modification time),
    
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

## PurePaths, non existing files:
>>> root = path("C:/")
>>> file = root/'subfolder'/'subsub'/'trunc.txt'
>>> str(file)
'C:/subfolder/subsub/trunc.txt'
>>> repr(file)
"path('C:/subfolder/subsub/trunc.txt')"
>>> file.split()
(path('C:/subfolder/subsub'), 'trunc.txt')
>>> file.name
'trunc.txt'
>>> file.suffix
'.txt'
>>> file.stem
'trunc'

>>> file.as_uri()
'file:///C:/subfolder/subsub/trunc.txt'

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
>>> windir = path("C:/Windows")
>>> windir.exists()
True
>>> windir.isdir()
True
>>> windir.isfile()
False


### old, now user suffix!
>>> file.splitext()
('C:/subfolder/subsub/trunc', '.txt')
>>> file.suffix
'.txt'

# >>> isStringLike(root)
# 1


# drive tests only first letter (Windows)
>>> path("C").isdrive()
True
>>> path("S").isdrive() # not existent
False
>>> path("C:/abacadabra").isdrive()
True
>>> path("C:/").isdrive()
True
>>> path("S:/abacadabra").isdrive()
False

# automatically try getValidPath if ( and ) are found:
>>> path("(C:|D:)").isdrive()
True
>>> path("(C|D):\\projects").isdir()
True
    """
    _flavour = pathlib._windows_flavour if os.name == 'nt' else pathlib._posix_flavour
    # if _flavour.sep == "\\" and _flavour.altsep == "/":
    #     _flavour.sep, _flavour.altsep = "/", "\\"

    def __new__(cls, *args):
        """this is the constructor for a new instance!

### construct from list:
>>> str(path(['C:', 'projects']))
'C:/projects'

small cases:
>>> workingdirectory = os.getcwd()
>>> path('.') == workingdirectory
True
>>> path('') == workingdirectory
True
>>> path('/')
path('/')
>>> path('../..')
path('../..')
>>> path('../../')
path('../..')
>>> p = path('C:/windows/../nonexistingdir/acties')
>>> str(p)
'C:/nonexistingdir/acties'
>>> p.is_dir()
False
>>> hometrick = path("~/.ssh/id_rsa.pub")

# # >>> str(hometrick)
# # 'C:/Users/Gebruiker/Documents/.ssh/id_rsa.pub'  
>>> hometrick.isfile()
True

## without slashes the working directory is taken in Windows:
>>> workingdirectory = os.getcwd()
>>> path('C:') == workingdirectory
True
>>> p = path("./../faunabescherming")

# # >>> str(p)
# # 'C:/NatlinkGIT/Natlink/MacroSystem/faunabescherming'


    
        """
        self = object.__new__(cls)
        if args and len(args) == 1 and type(args[0]) == cls:
            return args[0]
        if type(args[0]) == list:
            args = ('/'.join(args[0]),)
        if args == (None,):    # vreemde fout bij HTMLgen BGsound
            input = ""
        else:            
            input = '/'.join(args)
        if input.find("|") >= 0:
            validPath = getValidPath(input)
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
        self.path_prefix = ""
        self.path_resolve_prefix = ""

        self._init()
        if drv:
            # assume absolute
            return self.resolve()
        else:
            if not input:
                # empty input, return working directory (??? TODOQH)
                emptypath = self.resolve()
                return emptypath
            # relative, but not office temporary file:
            if input.startswith("~") and not input.startswith("~$"):
                expanded = self.expanduser()
                expanded.path_prefix = "~"
                homedir = str(expanded)[:(len(expanded)-len(input)+1)]
                expanded.path_resolve_prefix = homedir
                return expanded
            elif input == "." or (input[0] == '.' and input[1] in "/\\"):
                # expand "." to working directory
                # remember path_prefix and path_resolve_prefix
                abspath = self.resolve()
                if abspath.is_absolute():
                    abspath.path_prefix = "."
                    abspath.path_resolve_prefix = str(abspath)
                    return abspath
        # all other cases:
        return self

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
        """
        if type(key) in (list, tuple):
            key = '/'.join(key)
        return self._make_child((key,))

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
        return super().__str__().replace("\\", "/")
    
    def __len__(self):
        return len(str(self))

    ## str operations on path:   
    def find(self, searchstring):
        """treat as string"""
        return str(self).find(searchstring)
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
        """split into a list of directory parts, the file trunk and the file extension
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

>>> p = path(u"C:/dropbox/19.jpg")
>>> p.basename()
'19.jpg'
>>> p.name
'19.jpg'
        """
        return self.name

    def relpath(self, startPath):
        """get relative path, starting with startPath
>>> testpath = path("(C|D):/projects/unittest")
>>> startpath = path("(C|D):/projects")
>>> testpath.relpath("C:\projects")
'unittest'
>>> testpath.relpath(startpath)
'unittest'

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
        
>>> testpath = path("(C|D):/projects/unittest")
>>> startpath = path("(C|D):/projects")
>>> startpath.relpathto(testpath)
'unittest'
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
        """
        return os.path.normpath(str(self))


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

    def touch(self):
        """mark file or touch date
        
        # >>> p = path(getValidPath('(C|D)/projects/unittest/aaa.txt'))
        # >>> p.touch()
        # >>> p.isfile()
        # True
        # >>> p.remove()
        # >>> p.isfile()
        # False
        """
        touch(self)

    def chdir(self):
        """change directory

        """
        os.chdir(str(self))

    def getcwd(self):
        """get working directory
    
        """
        return path(os.getcwd())

    def glob(self, pattern="*", keepAbs=1, makePath=1):
        """glob a path, default = "*"

        default options: give absolute paths as path instances
        Use listdir if you want all files relative to the path

# later test TODOQH
# >>> folderName = path(testdrive + '/qhtemp')
# >>> makeEmptyFolder(folderName)
# >>> touch(folderName, 'a.ini', 'b.txt')
# >>> g = folderName.glob()
# >>> [f.replace(testdrive, 'XXX') for f in g]
# ['XXX/qhtemp/a.ini', 'XXX/qhtemp/b.txt']
# >>> type(g[0])
# <class 'utilsqh.path'>
# >>> g = folderName.glob('*.txt', keepAbs=0)
# >>> g
# ['b.txt']
# >>> type(g[0])
# <class 'utilsqh.path'>
# >>> g = folderName.glob('*.txt', keepAbs=0, makePath=0)
# >>> g
# ['b.txt']
# >>> type(g[0])
# <type 'unicode'>


        """
        if not self.isdir():
            raise PathError("glob must start with folder, not with: %s"% self)
        L = glob.glob(str(self/pattern))
        return self._manipulateList(L, keepAbs, makePath)

    def listdir(self):
        """give list relative to self, default unicodes, not path instances!
# later test (TODOQH)
# >>> folderName = path(testdrive + '/qhtemp')
# >>> makeEmptyFolder(folderName)
# >>> touch(folderName, 'a.ini', 'b.txt')
# >>> L = path(folderName).listdir()
# >>> L
# ['a.ini', 'b.txt']
# >>> type(L[0])
# <type 'unicode'>

        """
        if not self.isdir():
            raise PathError("listdir only works on folders, not with: %s"% self)
        L = os.listdir(self)
        # note keepAbs is a formality here, listdir gives relative files only:
        return L


    def walk(self, functionToDo, keepAbs=1, makePath=0):
        """return the arg list when walking self

        assume arg is a list,
        functionToDo must use exactly 3 parameters,
        1 list "arg"
        2 dirname
        3 list of filenames
        path(testdrive + "/projects").walk(testWalk, keepAbs=1, makePath=0)

        optional parameters:
        keepAbs: 1 (default) do nothing with the resulting paths
                 0: strip off the prefix, being the calling instance
        makePath 0 (default) do not to do this
                 1: make the resulting items path instances

        setting up the files:
# 
# >>> folderName = path(testdrive + '/qhtemp')
# >>> makeEmptyFolder(folderName)
# >>> makeEmptyFolder(folderName/"afolder")
# >>> makeEmptyFolder(folderName/"bfolder")
# >>> touch(folderName, 'f.ini', 'ff.txt')
# >>> touch(folderName/"afolder", 'aa.ini')
# >>> touch(folderName/"bfolder", 'b.ini', 'bb.txt')
# 
# trying the first test walk:
# 
# >>> L = folderName.walk(testWalk)
# >>> [f.replace(testdrive, 'XXX') for f in L]
# ['XXX/qhtemp', 'afolder', 'bfolder', 'f.ini', 'ff.txt', 'XXX/qhtemp/afolder', 'aa.ini', 'XXX/qhtemp/bfolder', 'b.ini', 'bb.txt']
# >>> L = folderName.walk(testWalk, keepAbs=0)
# Traceback (most recent call last):
# PathError: path._manipulateList with keepAbs: 0, 7 items of the list do not have XXX/qhtemp as start
# >>> L = folderName.walk(testWalk, keepAbs=1, makePath=1)
# >>> [f.replace(testdrive, 'XXX') for f in L]
# ['XXX/qhtemp', 'afolder', 'bfolder', 'f.ini', 'ff.txt', 'XXX/qhtemp/afolder', 'aa.ini', 'XXX/qhtemp/bfolder', 'b.ini', 'bb.txt']
# 
# trying the second test walk:
# 
# >>> L = folderName.walk(testWalk2, makePath=1)
# >>> [f.replace(testdrive, 'XXX') for f in L]
# ['XXX/qhtemp/afolder', 'XXX/qhtemp/bfolder', 'XXX/qhtemp/f.ini', 'XXX/qhtemp/ff.txt', 'XXX/qhtemp/afolder/aa.ini', 'XXX/qhtemp/bfolder/b.ini', 'XXX/qhtemp/bfolder/bb.txt']
# >>> L = folderName.walk(testWalk2, keepAbs=0, makePath=1)
# 
# >>> [f.replace(testdrive, 'XXX') for f in L]
# ['afolder', 'bfolder', 'f.ini', 'ff.txt', 'afolder/aa.ini', 'bfolder/b.ini', 'bfolder/bb.txt']
# 
# third test, skip folders, note the list is path instances now,
# converted back to strings or not by the parameter makePath:
# 
# >>> L = folderName.walk(walkOnlyFiles, makePath=1)
# >>> [f.replace(testdrive, 'XXX') for f in L]
# ['XXX/qhtemp/f.ini', 'XXX/qhtemp/ff.txt', 'XXX/qhtemp/afolder/aa.ini', 'XXX/qhtemp/bfolder/b.ini', 'XXX/qhtemp/bfolder/bb.txt']
# >>> folderName.walk(walkOnlyFiles, keepAbs=0, makePath=1)
# ['f.ini', 'ff.txt', 'afolder/aa.ini', 'bfolder/b.ini', 'bfolder/bb.txt']
# 

        """
        arg = []
        if not self.isdir():
            raise PathError("walk must start with folder, not with: %s"% self)
        os.walk(str(self), functionToDo, arg)
        return self._manipulateList(arg, keepAbs, makePath)

    def _manipulateList(self, List, keepAbs, makePath):
        """helper function for treating a result of listdir or glob
# needs testing!
#
#
# >>> folderName = path(testdrive + '/qhtemp')
# >>> makeEmptyFolder(folderName)
# >>> touch(folderName, 'a.ini', 'b.txt')
# >>> L = [folderName/'a.ini', folderName/'b.txt']
# >>> F = folderName._manipulateList(L, keepAbs=1, makePath=0)
# >>> [f.replace(testdrive, 'XXX') for f in F]
# ['XXX/qhtemp/a.ini', 'XXX/qhtemp/b.txt']
# >>> type(F[0])
# <type 'unicode'>
# >>> F = folderName._manipulateList(L, keepAbs=1, makePath=1)
# >>> [f.replace(testdrive, 'XXX') for f in F]
# ['XXX/qhtemp/a.ini', 'XXX/qhtemp/b.txt']
# 
# >>> type(F[0])
# <class 'utilsqh.path'>
# >>> F = folderName._manipulateList(L, keepAbs=0, makePath=0)
# >>> F
# ['a.ini', 'b.txt']
# >>> type(F[0])
# <type 'unicode'>
# >>> F = folderName._manipulateList(L, keepAbs=0, makePath=1)
# >>> F
# ['a.ini', 'b.txt']
# >>> type(F[0])
# <class 'utilsqh.path'>
# >>> L = [folderName/'a.ini', 'b.txt']
# >>> F = folderName._manipulateList(L, keepAbs=1, makePath=1)
# >>> [f.replace(testdrive, 'XXX') for f in F]
# ['XXX/qhtemp/a.ini', 'b.txt']

        """
        if not List:
            return List
        L = List[:]
        if not keepAbs:
            # make relative:
            length = len(self)
            unicodePath = str(self)
            if not self.endswith("/"):
                length += 1
            L = [k[length:] for k in L if k.find(unicodePath) == 0]
            if len(L) !=len(List):
                raise PathError("path._manipulateList with keepAbs: %s, %s items of the list do not have %s as start"%
                                (keepAbs, len(List)-len(L), self))

        if makePath:
            return list(map(path, L))
        else:
            return list(map(str, list(map(path, L))))

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

    # TODOQH!!! 
    # def decodePath(self):
    #     """decode to path (file or dir)
    # >>> 
    # >>> decodePath('b.txt (C:/a)')
    # path('C:/a/b.txt')
    # >>> decodePath('b.txt ()')
    # path('b.txt')
    # >>> decodePath(' (C:/)')
    # path('C:/')
    # 
    # 
    #         Return a path instance
    #     """
    #     if '(' not in text:
    #         return str(text)
    # 
    #     t = str(text)
    #     File, Folder = t.split('(', 1)
    #     Folder = Folder.rstrip(')')
    #     Folder = Folder.strip()
    #     File = File.strip()
    #     return path(Folder)/File
    
    ### TODOQH
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
    # 
    #         Return a path instance
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
    # 

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
    if envDict == None:
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
        print(("%s\t%s"% (k, recentEnv[k])))

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

def _test():
    import doctest
    return  doctest.testmod()

if __name__ == "__main__":
    # p = path("C:/Natlink")
    # print(p)
    # print(str(p))
    # print(repr(p))
    # print("is_dir: %s"% p.is_dir())
    # print("isdir: %s"% p.isdir())
    # envvars = EnvVariable()
    # getAllFolderEnvironmentVariables()
    # printAllEnvVariables()
    _test()
