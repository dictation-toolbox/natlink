'''Python portion of Natlink, a compatibility module for Dragon Naturally Speaking'''
__version__="5.2.0"
#pylint:disable=C0114, W0401
from typing import Optional
from pathlib import Path
import sys

# from .config import NoGoodConfigFoundException
# from .loader import NatlinkMain
# from .loader import run as run_loader
# from .redirect_output import redirect as redirect_all_output_to_natlink_window

# active_loader: Optional[NatlinkMain] = None

def getThisDir(fileOfModule, warnings=False):
    """get directory of calling module, if possible in site-packages
    
    call at top of module with `getThisDir(__file__)`
    
    If you want to get warnings (each one only once, pass `warnings = True`)
    
    More above and in the explanation of findInSitePackages.
    """
    thisFile = Path(fileOfModule)
    thisDir = thisFile.parent
    thisDir = findInSitePackages(thisDir, warnings=warnings)
    return thisDir

def findInSitePackages(directory, warnings):
    """get corresponding directory in site-packages 
    
    For users, just having pipped this package, the "directory" is returned, assuming it is in
    the site-packages.
    
    For developers, the directory is either
    --in a clone from github.
        The corresponding directory in site-packages should be a symlink,
        otherwise there was no "flit install --symlink" yet.
    --a directory in the site-packages. This directory should be a symlink to a cloned dir.
    
    The site-packages directory is returned, but the actual files accessed are in the cloned directory.
    
    To get this "GOOD" situation, you perform the steps as pointed out above (or in the README.md file)

    When problems arise, set warnings=True, in the call, preferably when calling getThisDir in the calling module.
    """
    dirstr = str(directory)
    if dirstr.find('\\src\\') < 0:
        if warnings:
            warning(f'directory {dirstr} not connected to a github clone directory, changes will not persist across updates...')
        return directory

    commonpart = dirstr.rsplit('\\src\\', maxsplit=1)[-1]
    spDir = Path(sys.prefix, 'Lib', 'site-packages', commonpart)
    if spDir.is_dir():
        spResolve = spDir.resolve()
        if spResolve == spDir:
            if warnings:
                warning(f'corresponding site-packages directory is not a symlink: {spDir}.\nPlease use "flit install --symlink" when you want to test this package')
        elif spResolve == directory:
            # print(f'directory is symlink: {spDir} and resolves to {directory} all right')
            ## return the symbolic link in the site-packages directory, that resolves to directory!!
            return spDir
        else:
            if warnings:
                warning(f'directory is symlink: {spDir} but does NOT resolve to {directory}, but to {spResolve}')
    else:
        if warnings:
            warning('findInSitePackages, not a valid directory in site-packages, no "flit install --symlink" yet: {spDir}')
    return directory        

warningTexts = []
def warning(text):
    """print warning only once, if warnings is set!
    
    warnings can be set in the calling functions above...
    """
    textForeward = text.replace("\\", "/")
    if textForeward in warningTexts:
        return
    warningTexts.append(textForeward)
    print(text)
    
