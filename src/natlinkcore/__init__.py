"""natlinkcore"""

__version__ = '5.0.0'  # 

"""utility functions, to get calling directory of module (in site-packages),

...and to check the existence of a directory, for example .natlink in the home directory.

Note: -as user, having pipped the package, the scripts run from the site-packages directory
      -as developer, you have to clone the package, then `build_package` and,
       after a `pip uninstall natlinkcore`, `flit install --symlink`.
       See instructions in the file README.md in the source directory of the package.

getThisDir: can be called in the calling module like:

```
try:
    from dtactions.__init__ import getThisDir, checkDirectory
except ModuleNotFoundError:
    print(f'Run this module after "build_package" and "flit install --symlink"\n')
    raise

thisDir = getThisDir(__file__)
```

checkDirectory(dirpath, create=True)
    create `dirpath` if not yet exists.
    when create=False is passed, no new directory is created, but an error is thrown if
    the directory does not exist.
"""

def getThisDir(fileOfModule):
    """get directory of calling module, if possible in site-packages
    
    call at top of module with "getThisDir(__file__)
    
    Check for symlink and presence in site-packages directory (in this case work is done on this repository)
    """
    thisFile = fileOfModule
    thisDir = os.path.split(thisFile)[0]
    thisDir = findInSitePackages(thisDir)
    return thisDir

def findInSitePackages(cloneDir):
    """get corresponding directory in site-packages 
    
    This directory should be a symlink, otherwise there was no "flit install --symlink" yet.
    
    GOOD: When the package is "flit installed --symlink", so you can work in your clone and
    see the results happen in the site-packages directory. Only for developers
    
    If not found, return the input directory (cloneDir)
    If not "coupled" return the input directory, but issue a warning
    """
    cloneDir = str(cloneDir)
    if cloneDir.find('\\src\\') < 0:
        return cloneDir
        # raise IOErrorprint(f'This function should only be called when "\\src\\" is in the path')
    commonpart = cloneDir.split('\\src\\')[-1]
    spDir = os.path.join(sys.prefix, 'Lib', 'site-packages', commonpart)
    if os.path.isdir(spDir):
        spResolve = os.path.realpath(spDir)
        if spResolve == spDir:
            print(f'corresponding site-packages directory is not a symlink: {spDir}.\nPlease use "flit install --symlink" when you want to test this package')
        elif spResolve == cloneDir:
            # print(f'directory is symlink: {spDir} and resolves to {cloneDir} all right')
            return spDir
        else:
            print(f'directory is symlink: {spDir} but does NOT resolve to {cloneDir}, but to {spResolve}')
    else:
        print('findInSitePackages, not a valid directory in site-packages, no "flit install --symlink" yet: {spDir}')
    return cloneDir        

def checkDirectory(newDir, create=True):
    """check existence of directory path
    
    create if not existent yet... if create == True
    if create == False, raise an error if directory is not there
    raise OSError if something strange happens...
    """
    if os.path.isdir(newDir):
        return
    elif create is False:
        raise OSError(f'Cannot find directory {newDir}, but it should be there.')
    if os.path.exists(newDir):
        raise OSError(f'path exists, but is not a directory: {newDir}')
    os.makedirs(newDir)
    if os.path.isdir(newDir):
        print('created directory: {newDir}')
    else:
        raise OSError(f'did not manage to create directory: {newDir}')
                      