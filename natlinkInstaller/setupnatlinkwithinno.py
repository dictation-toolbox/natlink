#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# setupnatlinkwithinno.py
#   This module does makes the installer.  Mind the steps to be taken below:
#   wxPython GUI
#
#  (C) Copyright Quintijn Hoogenboom, 2008-2009
#
#----------------------------------------------------------------------------
# A setup script for NatLink/Vocola/Unimacro, with inno
# 1. choose new release name and change in __version__ of natlinkstatus
# 2. Commit NatLink and Unimacro
# 3. SVN export both NatLink and Unimacro to a new folder (eg D:\NatLink\releases\natlink3.2 if your release number is natlink3.2)
# 4. run this utility FROM THAT FOLDER\NatLink\natlinkInstaller.
#
GrammarsToDisable = ['_brackets.py', '_editcomments.py', '_number.py',
                     '_keystrokes.py', '_oops.py', '_setpriority.py',
                     '_tags.py', '_unimacrotest.py', '_modes.py',
                     'winword_styles_unimacro.py']

ExtensionsToIgnore = [".wmv"]
#--------- two utility functions:
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
    """get the NatLink core folder, relative from the current folder

    This folder should be relative to this with ../MacroSystem/core
    and should contain natlinkmain.py and natlink.dll and
    natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'MacroSystem', 'core') )
    if not os.path.isdir(coreFolder):
        print 'not a directory: %s'% coreFolder
        return thisDir
## dllPath version dependent, so skip this check:
##    dllPath = os.path.join(coreFolder, 'natlink.dll')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
##    if not os.path.isfile(dllPath):
##        print 'natlink.dll not found in core directory: %s'% coreFolder
##        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module"""
    print 'natlinkconfigfunctions fails because of fatal error:'
    print message
    print
    print 'This can (hopefully) be solved by (re)installing NatLink'
    print 
    if new_raise:
        raise new_raise
    else:
        raise

import os, sys, shutil
thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
trunkDir = os.path.normpath(os.path.join(thisDir, '..', '..'))
print 'trunkDir: %s'% trunkDir

if thisDir == coreDir:
    raise IOError('setupnatlinkwithinno cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(coreDir) in sys.path:
    print 'inserting %s to pythonpath...'% coreDir
    sys.path.insert(0, coreDir)
import natlinkstatus
_version = natlinkstatus.__version__
os.chdir(trunkDir)

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    pass
##    sys.argv.append("py2exe")
##    sys.argv.append("-x")

import os

class InnoScript:
    def __init__(self,
                 name,
                 dist_dir,
                 version = _version):
        self.dist_dir = dist_dir
        self.name = name # NatLink
        self.version = version # version from natlinkstatus

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]

    def create(self, pathname="dist\\natlink.iss"):
        self.pathname = pathname
        self.site = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by setupnatlinkwithinno"
        print >> ofi, "; will be overwritten the next time this module is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"OutputDir=."
        self.outputFilename = "setup-natlink-%s"% self.version
        print >> ofi, r"OutputBaseFilename=%s"% self.outputFilename
        print >> ofi, r"AppName=%s"% self.name
        print >> ofi, r"AppVerName=%s version %s (including Vocola 2.6.3I and Unimacro)" % (self.name, self.version)
        print >> ofi, r"DefaultDirName=C:\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi, r"LicenseFile=..\NatLink\COPYRIGHT.txt"
##        print >> ofi, "DisableDirPage=yes"
        print >> ofi, "UsePreviousAppDir=yes"
        print >> ofi, "ChangesAssociations=yes"

        print >> ofi
        print >> ofi, r'[Registry]'
        print >> ofi, 'Root: HKCR; Subkey: ".vcl"; ValueType: string; ValueName: ""; ValueData: "Vocola_command_file"; Flags: uninsdeletevalue'
        print >> ofi, 'Root: HKCR; Subkey: ".vch"; ValueType: string; ValueName: ""; ValueData: "Vocola_include_file"; Flags: uninsdeletevalue'

        print >> ofi, r'Root: HKCR; Subkey: "Vocola_command_file"; ValueType: string; ValueName: ""; ValueData: "Vocola command file"; Flags: uninsdeletekey'
        print >> ofi, r'Root: HKCR; Subkey: "Vocola_include_file"; ValueType: string; ValueName: ""; ValueData: "Vocola include file"; Flags: uninsdeletekey'

        notepad = os.path.join(os.getenv('WINDIR'), 'notepad.exe')
        print >> ofi, r'Root: HKCR; Subkey: "Vocola_command_file\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """' + notepad + '"" ""%1"""'
        print >> ofi, r'Root: HKCR; Subkey: "Vocola_include_file\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """' + notepad + '"" ""%1"""'

        print >> ofi
        print >> ofi, r'[Languages]'
        print >> ofi, r'Name: "en"; MessagesFile: "..\NatLink\natlinkInstaller\Natlink.isl"'

        print >> ofi
        print >> ofi, r"[Files]"
        natlink_files = getAllFiles('NatLink')
        unimacro_files = getAllFiles('Unimacro')
        
        for path in natlink_files:
            print >> ofi, r'Source: "..\NatLink\%s"; DestDir: "{app}\NatLink\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        for path in unimacro_files:
            if filter(None, [path for ext in ExtensionsToIgnore if path.endswith(ext)]):
                print 'ignoring because of extension: %s'% path
                continue
            if filter(None, [path == f for f in GrammarsToDisable]):
                print >> ofi, r'Source: "..\Unimacro\%s"; DestDir: "{app}\Unimacro\DisabledGrammars\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
            else:
                print >> ofi, r'Source: "..\Unimacro\%s"; DestDir: "{app}\Unimacro\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))

        print >> ofi



        print >> ofi, r"[Icons]"
        Path = r'..\NatLink\confignatlinkvocolaunimacro\start_configurenatlink.bat'
        print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\NatLink\%s"' % \
              ("Configure NatLink via GUI", Path)
        Path = r'..\NatLink\confignatlinkvocolaunimacro\start_natlinkconfigfunctions.bat'
        print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\NatLink\%s"' % \
              ("Configure NatLink via command line interface", Path)


        # run GUI after install:
        print >> ofi, r"[Run]"
        Path = r'NatLink\confignatlinkvocolaunimacro\configurenatlink.py'

##        print >> ofi, r'Filename: "{app}\%s"; Description: "Launch NatLink configuration GUI"; Flags: postinstall'% \
##              Path
        
    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api.", self.pathname
                win32api.ShellExecute(0, "compile",
                                                self.pathname,
                                                None,
                                                None,
                                                0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                                                      self.pathname,
                                                      None,
                                                      None,
                                                      0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################
################################################################
def run():
    # name for installation:
    dist_dir = os.path.join(trunkDir, 'dist')
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
    os.mkdir(dist_dir)
    # create the Installer, using the files py2exe has created.
    # uitleg is included in this generation of the exe file...
    script = InnoScript("NatLink",
                        dist_dir)
                        
    print "*** creating the inno setup script***"
    script.create()
    print "*** compiling the inno setup script***"
    script.compile()
################################################################

##setup(
##    options = options,
##    # The lib directory contains everything except the executables and the python dll.
##    zipfile = zipfile,
##    windows = [sitegen],
##    # use out build_installer class as extended py2exe build command
##    cmdclass = {"py2exe": build_installer}
##    )
# get files, and strip directory part:
def getAllFiles(startDir):
    files = []
    if startDir.endswith(os.sep) or startDir.endswith('/'):
        startDir = startDir[:-1]
    os.path.walk(startDir, _getallfiles, files)
    
    files = stripStart(files, startDir)
    return files

def _getallfiles(arg, dirname, filenames):
    if dirname.endswith("CVS"):
        raise IOError("found a CVS folder, you should have released Unimacro and NatLink first!")
    for f in filenames:
        if f.endswith(".pyc"):
            continue
        
        Path = os.path.join(dirname, f)
        if os.path.isdir(Path):
            continue
        
        arg.append(Path)

def stripStart(lijst, start):
    l = []
    ll = len(start)+1
    for f in lijst:
        l.append(f[ll:])
    return l

    
if __name__ == "__main__":
    run()
